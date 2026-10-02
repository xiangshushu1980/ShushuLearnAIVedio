// Owner: Sean — durable run orchestration, restart recovery and shared GPU arbitration.
import { execFile } from 'node:child_process';
import { promisify, isDeepStrictEqual } from 'node:util';
import { unlinkSync, existsSync } from 'node:fs';
import { resolve, sep } from 'node:path';
import { validateRun, workflowTemplate, buildComfyWorkflow } from './catalog.mjs';
import { comfyUrl, comfyRequest, prepareComfy, submitComfy, readComfyResult, downloadComfy } from './adapters.mjs';
import { HttpError, now } from './store.mjs';

const exec = promisify(execFile);
const sleep = ms => new Promise(r => setTimeout(r, ms));
const active = new Map();
const ended = run => ['succeeded', 'failed', 'cancelled'].includes(run.status);

export function createRunService(store) {
  function recordedWorkflow(run) {
    const row = store.db.prepare('SELECT execution FROM runs WHERE id=?').get(run.id);
    return row.execution ? JSON.parse(row.execution).workflow : null;
  }
  function sameTemplate(run, model) {
    if (run.snapshot.model.id !== model.id || run.snapshot.model.version !== model.version) return false;
    if (run.snapshot.template.hash) return run.snapshot.template.hash === workflowTemplate(model.id).hash;
    // Early phase-one records predate template hashes. Require the entire submitted graph to match.
    const graph = recordedWorkflow(run);
    if (!graph) return false;
    const first = model.id === 'qwen-image-2.1' ? 10 : 30;
    const names = run.snapshot.references.map((_, index) => graph[String(first + index)]?.inputs.image);
    if (names.some(name => typeof name !== 'string')) return false;
    return isDeepStrictEqual(graph, buildComfyWorkflow(run.snapshot, names, run.id));
  }
  const resource = async (...args) => {
    const { stdout } = await exec('hive-resource', args, { timeout: 15_000 });
    return stdout;
  };
  function snapshot(entityId, body) {
    const { input, model, style } = validateRun(body);
    const entity = store.entity(entityId);
    if (input.sourceRunId) {
      const source = store.run(input.sourceRunId);
      if (source.entityId !== entityId) throw new HttpError(400, '历史工作流不属于当前实体');
      if (!sameTemplate(source, model))
        throw new HttpError(409, '历史工作流版本已变化，请明确选择当前模型后重新检查输入');
      if (source.snapshot.style.id === style.id && !isDeepStrictEqual(source.snapshot.style, style))
        throw new HttpError(409, '历史风格配置已变化，请明确选择当前模型后重新检查风格和提示词');
    }
    const references = input.references.map(assetId => {
      const asset = store.asset(assetId);
      if (asset.entityId !== entityId) throw new HttpError(400, '引用图片不属于当前实体');
      return { id: asset.id, hash: asset.hash, kind: asset.kind, name: asset.name, runId: asset.runId, createdAt: asset.createdAt };
    });
    const { endpoint, ...modelSnapshot } = model;
    return { owner: 'Sean', entity: { id: entity.id, name: entity.name, context: entity.context },
      model: modelSnapshot, style: structuredClone(style), prompt: input.prompt, purpose: input.purpose,
      effectivePrompt: [input.prompt, style.promptSuffix].filter(Boolean).join('\n\n'),
      parameters: input.parameters, references, ...(input.sourceRunId ? { sourceRunId: input.sourceRunId } : {}),
      template: { id: `${model.id}.${references.length}-refs`, version: model.version, hash: workflowTemplate(model.id).hash } };
  }
  function watchProgress(runId, clientId, state) {
    const url = comfyUrl.replace(/^http/, 'ws') + `/ws?clientId=${encodeURIComponent(clientId)}`;
    const ws = new WebSocket(url);
    state.ws = ws;
    ws.addEventListener('error', () => {});
    ws.addEventListener('message', ({ data }) => {
      if (typeof data !== 'string') return;
      try {
        const event = JSON.parse(data);
        const run = store.run(runId);
        if (ended(run) || event.data?.prompt_id !== run.promptId) return;
        if (event.type === 'progress' && event.data.max > 0) store.updateRun(runId, {
          status: 'running', progress: Math.min(99, 100 * event.data.value / event.data.max), phase: '正在采样' });
        if (event.type === 'executing' && event.data.node) store.updateRun(runId, { status: 'running', phase: '正在生成' });
      } catch { /* polling remains the authoritative completion check */ }
    });
  }
  async function saveOutputs(run, buffers, outputContext) {
    const stages = [];
    try {
      for (let i = 0; i < buffers.length; i++) stages.push(await store.stageImage(buffers[i], `概念图 ${run.id.slice(0, 8)} · ${i + 1}`,
        run.entityId, 'concept', run.id, { source: 'generation', template: run.snapshot.template,
          outputIndex: i, inputAssetIds: run.snapshot.references.map(r => r.id), ...outputContext }));
      store.transaction(() => {
        store.registerStages(stages);
        store.updateRun(run.id, { status: 'succeeded', progress: 100, phase: '生成完成 · 已加入历史', error: null, completed_at: now() });
      });
    } catch (error) { stages.forEach(store.discardStage); throw error; }
  }
  async function execute(runId, recovery = false) {
    if (active.has(runId)) return;
    const state = { leaseId: null, heartbeat: null, sampler: null, ws: null, sampledPeakVramMb: null };
    const sample = async () => {
      try {
        const snapshot = JSON.parse(await resource('resources', '--json', '--refresh', '--processes', '0'));
        const value = snapshot.resources?.['gpu:0']?.metrics?.memoryUsedMb;
        if (Number.isFinite(value)) state.sampledPeakVramMb = Math.max(state.sampledPeakVramMb ?? 0, value);
      } catch { /* observation failure must not lose a completed result */ }
    };
    active.set(runId, state);
    try {
      let run = store.run(runId);
      if (ended(run)) return;
      const executionRow = store.db.prepare('SELECT execution FROM runs WHERE id=?').get(runId);
      let execution = executionRow.execution ? JSON.parse(executionRow.execution) : null;
      if (recovery && !run.promptId) {
        // Submission may have reached Comfy before a crash. Do not blindly duplicate it.
        if (execution) throw new Error('提交期间服务重启，结果未知。请核对 ComfyUI 队列后显式重试。');
      }
      if (!run.promptId) {
        // Block starting a local job if another shared job already occupies the queue.
        const queue = await comfyRequest('/queue');
        if (queue.queue_running.length || queue.queue_pending.length) throw new Error('共享 ComfyUI 队列已有任务，请稍后重试');
      }
      let recoveredResult = null;
      if (recovery && run.promptId) {
        try { recoveredResult = await readComfyResult(run.promptId); }
        catch (error) { if (!/fetch failed|timeout|ECONNREFUSED/i.test(error.message)) throw error; }
      }
      // A completed job needs file recovery only; another worker's GPU lease cannot block it.
      if (recoveredResult?.state !== 'succeeded') {
        const occupancy = JSON.parse(await resource('occupancy', '--json'));
        const existingLease = Object.values(occupancy.leases || {}).find(lease => lease.owner === `reference:${runId}`);
        if (recovery && existingLease) {
          state.leaseId = existingLease.id;
          await resource('lease', 'heartbeat', state.leaseId, '--ttl', '600000');
        } else {
          const leaseOutput = await resource('lease', 'acquire', '--owner', `reference:${runId}`, '--resources', 'gpu:0', '--pid', String(process.pid), '--ttl', '600000');
          state.leaseId = leaseOutput.match(/租约\s+(\S+)\s+已授予/)?.[1];
        }
        if (!state.leaseId) throw new Error('未取得有效 GPU 资源租约');
        void sample();
        state.sampler = setInterval(sample, 5000);
        state.heartbeat = setInterval(() => {
          resource('lease', 'heartbeat', state.leaseId, '--ttl', '600000').catch(error => {
            console.error('Reference GPU lease heartbeat:', error.message);
          });
        }, 30_000);
      } else {
        // Release this completed run's surviving lease after assets have been recovered.
        try {
          const occupancy = JSON.parse(await resource('occupancy', '--json'));
          state.leaseId = Object.values(occupancy.leases || {}).find(lease => lease.owner === `reference:${runId}`)?.id || null;
        } catch { /* a resource-center outage cannot block CPU-only file recovery */ }
      }
      if (!run.promptId) {
        store.updateRun(runId, { phase: '准备所选引用图片' });
        execution = await prepareComfy(store, run);
        store.updateRun(runId, { execution: JSON.stringify(execution), phase: '提交到 ComfyUI' });
        let response;
        try { response = await submitComfy(execution); }
        catch (error) {
          if (/fetch failed|timeout|ECONNRESET/i.test(error.message)) throw new Error('提交结果未知，请先核对 ComfyUI 队列与历史，再决定是否重试。');
          throw error;
        }
        if (!response.prompt_id) throw new Error('ComfyUI 未返回运行标识');
        store.updateRun(runId, { prompt_id: response.prompt_id, phase: '等待生成' });
        run = store.run(runId);
      }
      if (execution?.clientId) watchProgress(runId, execution.clientId, state);
      let missing = 0;
      while (!ended(store.run(runId))) {
        let result;
        try { result = recoveredResult || await readComfyResult(run.promptId); recoveredResult = null; }
        catch (error) {
          if (/fetch failed|timeout|ECONNREFUSED/i.test(error.message)) {
            store.updateRun(runId, { phase: '连接中断 · 正在恢复连接' });
            await sleep(5000); continue;
          }
          throw error;
        }
        if (result.state === 'succeeded') {
          store.updateRun(runId, { phase: '回收生成结果' });
          const buffers = [];
          for (const image of result.images) buffers.push(await downloadComfy(image));
          await saveOutputs(run, buffers, { provider: 'comfy', promptId: run.promptId, outputFiles: result.images });
          // Only this app's proven, registered outputs are removed from the temporary Comfy output directory.
          const outputRoot = resolve(process.env.REFERENCE_COMFY_OUTPUT || '/home/sean/projects/ComfyUI/output');
          const expected = resolve(outputRoot, 'sean_reference_workspace', runId) + sep;
          for (const image of result.images) {
            const file = resolve(outputRoot, image.subfolder || '', image.filename);
            if (file.startsWith(expected) && existsSync(file)) {
              try { unlinkSync(file); } catch (error) { console.error('Reference output cleanup:', error.message); }
            }
          }
          break;
        }
        if (result.state === 'unknown') {
          missing++;
          if (missing >= 20) throw new Error('队列与历史中均找不到本次运行，可能已被外部删除或服务重启');
          store.updateRun(runId, { phase: '等待执行状态' });
        } else {
          missing = 0;
          store.updateRun(runId, { status: result.state, phase: result.state === 'queued' ? '在 ComfyUI 队列中等待' : '正在生成' });
        }
        await sleep(2000);
      }
    } catch (error) {
      if (!ended(store.run(runId))) store.updateRun(runId, { status: 'failed', phase: '生成失败', error: error.message.slice(0, 1000), completed_at: now() });
    } finally {
      clearInterval(state.heartbeat);
      clearInterval(state.sampler);
      state.ws?.close();
      if (state.leaseId) {
        try {
          await sample();
          const run = store.run(runId);
          await resource('observe', '--resource', 'gpu:0', '--job', `reference:${runId}`, '--metrics', JSON.stringify({
            elapsedMs: Date.now() - Date.parse(run.createdAt), outputCount: run.outputs.filter(a => !a.deletedAt).length,
            succeeded: run.status === 'succeeded', sampledPeakVramMb: state.sampledPeakVramMb, sampleIntervalMs: 5000
          }));
        } catch (error) { console.error('Reference resource observation:', error.message); }
        try { await resource('lease', 'release', state.leaseId); }
        catch (error) { console.error('Reference GPU lease release:', error.message); }
      }
      active.delete(runId);
    }
  }
  return {
    restore(runId) {
      const run = store.run(runId), source = run.snapshot;
      const input = { modelId: source.model.id, styleId: source.style.id, prompt: source.prompt, purpose: source.purpose,
        references: source.references.map(asset => asset.id), parameters: source.parameters, sourceRunId: run.id };
      let compatible = true, reason = null;
      try {
        const { model, style } = validateRun(input);
        if (!isDeepStrictEqual(model, source.model) || !isDeepStrictEqual(style, source.style) || !sameTemplate(run, model))
          throw new Error('历史模型、风格或工作流版本已变化，请重新选择当前配置后检查输入');
      } catch (error) { compatible = false; reason = error.message; }
      return { input, workflow: recordedWorkflow(run), compatible, reason };
    },
    start(entityId, body, key) {
      const saved = store.createRun(entityId, snapshot(entityId, body), key);
      if (saved.created) void execute(saved.run.id);
      return saved.run;
    },
    retry(runId, key) {
      const run = store.run(runId);
      if (!['failed', 'cancelled'].includes(run.status)) throw new HttpError(409, '只有失败或取消的运行可以重试');
      // Validate against the current capability catalog; never silently reuse a changed template.
      const validated = snapshot(run.entityId, { modelId: run.snapshot.model.id, styleId: run.snapshot.style.id,
        prompt: run.snapshot.prompt, purpose: run.snapshot.purpose, references: run.snapshot.references.map(a => a.id), parameters: run.snapshot.parameters });
      if (JSON.stringify(validated.model) !== JSON.stringify(run.snapshot.model) || JSON.stringify(validated.style) !== JSON.stringify(run.snapshot.style))
        throw new HttpError(409, '模型或风格配置已变化，请检查输入后创建新运行');
      if (run.snapshot.template.hash && run.snapshot.template.hash !== validated.template.hash)
        throw new HttpError(409, '工作流模板已变化，请检查输入后创建新运行');
      const saved = store.createRun(run.entityId, run.snapshot, key);
      if (saved.created) void execute(saved.run.id);
      return saved.run;
    },
    async cancel(runId) {
      const run = store.run(runId);
      if (run.status !== 'queued' || !run.promptId) throw new HttpError(409, '当前运行无法从队列取消');
      const queue = await comfyRequest('/queue');
      if (!queue.queue_pending.some(item => item[1] === run.promptId)) throw new HttpError(409, '运行已经开始，不能使用共享实例的全局中断');
      await comfyRequest('/queue', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ delete: [run.promptId] }) });
      const after = await readComfyResult(run.promptId);
      if (after.state !== 'unknown' || ended(store.run(runId))) throw new HttpError(409, '运行状态已改变，请刷新后查看结果');
      store.updateRun(runId, { status: 'cancelled', phase: '已取消排队', completed_at: now() });
    },
    recover() { for (const row of store.db.prepare("SELECT id FROM runs WHERE status IN ('queued','running')").all()) void execute(row.id, true); }
  };
}
