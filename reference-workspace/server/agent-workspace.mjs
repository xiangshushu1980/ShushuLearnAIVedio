// Owner: Sean — shared creative projects, durable conversations/events and reviewable spatial proposals.
import { Router } from 'express';
import { z } from 'zod';
import sharp from 'sharp';
import { createHash } from 'node:crypto';
import { id, now, HttpError } from './store.mjs';
import { canonicalJSON, contentHash } from './content-hash.mjs';
import { createEntityManagement } from './entity-management.mjs';
import { isSceneEntity } from './scene-spatial.mjs';
import { spatialDocumentSchema, spatialDocumentShape } from './spatial-schema.mjs';
import { sceneProfile, agentProfiles } from './agent-profiles.mjs';
import { createPiRuntime } from './pi-agent-runtime.mjs';

const parse = (schema, body) => {
  const r = schema.safeParse(body);
  if (!r.success) {
    const fieldErrors = {};
    for (const issue of r.error.issues) (fieldErrors[issue.path.join('.') || 'body'] ||= []).push(issue.message);
    throw new HttpError(400, '助手输入格式不正确', { fieldErrors });
  }
  return r.data;
};
const uuid = z.string().uuid();
const projectFields = z.object({ name: z.string().trim().min(1).max(100), brief: z.string().max(12000),
  decisions: z.string().max(12000), entityIds: z.array(uuid).max(100).refine(v => new Set(v).size === v.length, '实体不能重复') }).strict();
const sourceSchema = z.object({ target: z.string().max(100), kind: z.enum(['image', 'user', 'existing']),
  refs: z.array(z.string().max(100)).min(1).max(16), explanation: z.string().trim().min(1).max(2000) }).strict();
const proposalSchema = z.object({ document: spatialDocumentSchema, summary: z.string().trim().min(1).max(4000),
  questions: z.array(z.string().trim().min(1).max(2000)).max(3), sources: z.array(sourceSchema).max(500) }).strict();
const jsonTool = value => ({ content: [{ type: 'text', text: canonicalJSON(value) }], details: {} });
const terminal = status => status !== 'running';
const labels = { get_scene_context: '读取工程和场景资料', view_reference_image: '查看参考图',
  load_authoring_skill: '读取空间设定方法', propose_scene_spatial: '整理空间提案' };

export function createAgentWorkspace(store, { runtime = createPiRuntime(store.root) } = {}) {
  const management = createEntityManagement(store), db = store.db;
  const active = new Map();
  db.exec(`CREATE TABLE IF NOT EXISTS agent_projects(id TEXT PRIMARY KEY,body TEXT NOT NULL,revision INTEGER NOT NULL,created_at TEXT NOT NULL,updated_at TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS agent_sessions(id TEXT PRIMARY KEY,project_id TEXT NOT NULL REFERENCES agent_projects(id),entity_id TEXT NOT NULL REFERENCES entities(id),purpose TEXT NOT NULL,provider TEXT NOT NULL,model_id TEXT NOT NULL,entries TEXT NOT NULL DEFAULT '[]',created_at TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS agent_messages(id TEXT PRIMARY KEY,session_id TEXT NOT NULL REFERENCES agent_sessions(id),run_id TEXT,role TEXT NOT NULL,text TEXT NOT NULL,created_at TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS agent_runs(id TEXT PRIMARY KEY,session_id TEXT NOT NULL REFERENCES agent_sessions(id),request_id TEXT NOT NULL UNIQUE,status TEXT NOT NULL,basis TEXT NOT NULL,assistant_message_id TEXT NOT NULL,error TEXT,created_at TEXT NOT NULL,completed_at TEXT);
    CREATE TABLE IF NOT EXISTS agent_run_contexts(run_id TEXT PRIMARY KEY REFERENCES agent_runs(id),body TEXT NOT NULL);
    CREATE UNIQUE INDEX IF NOT EXISTS agent_one_run ON agent_runs(session_id) WHERE status='running';
    CREATE TABLE IF NOT EXISTS agent_events(seq INTEGER PRIMARY KEY AUTOINCREMENT,run_id TEXT NOT NULL REFERENCES agent_runs(id),type TEXT NOT NULL,body TEXT NOT NULL,created_at TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS agent_proposals(id TEXT PRIMARY KEY,run_id TEXT NOT NULL REFERENCES agent_runs(id),session_id TEXT NOT NULL REFERENCES agent_sessions(id),body TEXT NOT NULL,content_hash TEXT NOT NULL,applied_version_id TEXT,created_at TEXT NOT NULL);
    CREATE TRIGGER IF NOT EXISTS agent_proposal_body_immutable BEFORE UPDATE OF body,content_hash ON agent_proposals BEGIN SELECT RAISE(ABORT,'immutable agent proposal');END;`);
  const emit = (runId, type, body) => db.prepare('INSERT INTO agent_events(run_id,type,body,created_at) VALUES (?,?,?,?)').run(runId,type,canonicalJSON(body),now());
  function project(projectId) {
    const row = db.prepare('SELECT * FROM agent_projects WHERE id=?').get(projectId);
    if (!row) throw new HttpError(404, '工程不存在');
    return { owner: 'Sean', id: row.id, ...JSON.parse(row.body), revision: row.revision, createdAt: row.created_at, updatedAt: row.updated_at };
  }
  function projects() { return db.prepare('SELECT id FROM agent_projects ORDER BY created_at,id').all().map(r => project(r.id)); }
  function saveProject(projectId, body) {
    const input = parse(projectId ? projectFields.extend({ expectedRevision: z.number().int().positive() }).strict() : projectFields, body);
    return store.transaction(() => {
      for (const entityId of input.entityIds) store.entity(entityId);
      const stamp = now(), projectKey = projectId || id();
      const { expectedRevision, ...fields } = input;
      if (projectId) {
        const old = project(projectId);
        if (old.revision !== expectedRevision) throw new HttpError(409, '工程资料已变化，请重新载入');
        db.prepare('UPDATE agent_projects SET body=?,revision=revision+1,updated_at=? WHERE id=?').run(canonicalJSON(fields),stamp,projectId);
      } else db.prepare('INSERT INTO agent_projects VALUES (?,?,?,?,?)').run(projectKey,canonicalJSON(fields),1,stamp,stamp);
      return project(projectKey);
    });
  }
  function context(projectId) {
    const p = project(projectId);
    return { owner: 'Sean', schemaVersion: 1, project: p, entities: p.entityIds.map(entityId => {
      const d = management.detail(entityId);
      return { entityId, ...d.profile, sourceRevision: d.revision, sceneSpatial: d.sceneSpatial,
        relations: d.relations.filter(r => p.entityIds.includes(r.sourceEntityId) && p.entityIds.includes(r.targetEntityId)) };
    }) };
  }
  function sessionRow(sessionId) {
    const row = db.prepare('SELECT * FROM agent_sessions WHERE id=?').get(sessionId);
    if (!row) throw new HttpError(404, '助手会话不存在');
    return row;
  }
  function member(s) {
    const p = project(s.project_id);
    if (!p.entityIds.includes(s.entity_id)) throw new HttpError(409, '场景已移出工程，请重新选择工程');
    return p;
  }
  function session(sessionId) {
    const s = sessionRow(sessionId);
    const latestBases = new Map();
    const rows = db.prepare('SELECT * FROM agent_proposals WHERE session_id=? ORDER BY created_at,rowid').all(sessionId);
    for (const row of rows) {
      const b = runRow(row.run_id).basis, key=canonicalJSON(b.referenceAssetIds);
      if (!latestBases.has(key)) {try {latestBases.set(key,contentHash(basis(s,b.referenceAssetIds)));}catch {latestBases.set(key,null);}}
    }
    return { owner: 'Sean', id: s.id, projectId: s.project_id, entityId: s.entity_id, purpose: s.purpose,
      provider: s.provider, modelId: s.model_id, createdAt: s.created_at,
      messages: db.prepare('SELECT id,role,text,created_at AS createdAt,run_id AS runId FROM agent_messages WHERE session_id=? ORDER BY created_at,rowid').all(sessionId),
      runs: db.prepare('SELECT id,status,error,created_at AS createdAt FROM agent_runs WHERE session_id=? ORDER BY created_at,rowid').all(sessionId),
      proposals: rows.map(row => ({id:row.id,runId:row.run_id,...JSON.parse(row.body),contentHash:row.content_hash,
        appliedVersionId:row.applied_version_id,createdAt:row.created_at,
        stale:!row.applied_version_id&&latestBases.get(canonicalJSON(runRow(row.run_id).basis.referenceAssetIds))!==contentHash(runRow(row.run_id).basis)})) };
  }
  function sessions(projectId, entityId) {
    project(projectId); store.entity(entityId);
    return db.prepare('SELECT id,provider,model_id AS modelId,created_at AS createdAt FROM agent_sessions WHERE project_id=? AND entity_id=? ORDER BY created_at DESC,rowid DESC').all(projectId,entityId);
  }
  async function createSession(body) {
    const input = parse(z.object({ projectId: uuid, entityId: uuid, purpose: z.literal('scene-spatial'),
      provider: z.string().min(1).max(100), modelId: z.string().min(1).max(150) }).strict(), body);
    const p = project(input.projectId), e = store.entity(input.entityId);
    if(!isSceneEntity(e)&&management.spatial.get(e.id).summary.version===0)
      throw new HttpError(400,'当前用途只支持场景实体',{fieldErrors:{entityId:['请为实体添加场景 flag']}});
    if (!p.entityIds.includes(e.id)) throw new HttpError(400, '请先把场景加入工程', { fieldErrors: { entityId: ['实体不属于当前工程'] } });
    if (!(await runtime.models()).some(m => m.provider === input.provider && m.id === input.modelId))
      throw new HttpError(400, '模型未配置或不支持图片输入', { fieldErrors: { modelId: ['请选择模型列表中的已配置模型'] } });
    const sessionId = id();
    db.prepare('INSERT INTO agent_sessions VALUES (?,?,?,?,?,?,?,?)').run(sessionId,p.id,e.id,input.purpose,input.provider,input.modelId,'[]',now());
    return session(sessionId);
  }
  function runRow(runId) {
    const row = db.prepare('SELECT * FROM agent_runs WHERE id=?').get(runId);
    if (!row) throw new HttpError(404, '对话运行不存在');
    return { ...row, basis: JSON.parse(row.basis) };
  }
  function basis(s, refs) {
    member(s);
    const c = context(s.project_id), spatial = management.spatial.get(s.entity_id);
    const images = refs.map(assetId => {
      const a = store.asset(assetId);
      if (a.entityId !== s.entity_id || a.mediaType !== 'image') throw new HttpError(400, '参考图须属于当前场景', { fieldErrors: { referenceAssetIds: ['请选择当前实体图片'] } });
      const actual = createHash('sha256').update(store.assetBytes(a.id)).digest('hex');
      if (actual !== a.hash) throw new HttpError(409, '参考图内容与登记资料不同，请重新导入');
      return { assetId, contentHash: a.hash };
    });
    return { contextHash: contentHash(c), spatialVersionId: spatial.expectedVersionId, evidenceStateHash: spatial.evidenceStateHash,
      referenceAssetIds: refs, images, profileVersion: sceneProfile.version, skillVersion: sceneProfile.skillVersion };
  }
  function sceneContext(s) {
    const c=context(s.project_id), current=c.entities.find(e=>e.entityId===s.entity_id);
    return {owner:'Sean',schemaVersion:1,project:c.project,entityId:s.entity_id,currentEntity:current,
      otherEntities:c.entities.filter(e=>e.entityId!==s.entity_id).map(e=>({entityId:e.entityId,name:e.name,flags:e.flags,
        description:e.description.slice(0,500),appearance:e.appearance.slice(0,300),sourceRevision:e.sourceRevision})),
      spatial:management.spatial.get(s.entity_id)};
  }
  function sourceTargets(doc) {
    return new Map([['frame',doc.frame],...['elements','links','routes'].flatMap(key => doc[key].map(item => [key+'/'+item.id,item]))]);
  }
  function createProposal(s, run, raw, seenImages) {
    const input = parse(proposalSchema, raw);
    if (canonicalJSON(input.document.referenceAssetIds) !== canonicalJSON(run.basis.referenceAssetIds))
      throw new HttpError(400, '提案必须使用用户本轮选择的参考图');
    const before = management.spatial.get(s.entity_id).document;
    // The run's captured source revision must still be current before proposing or applying.
    if (contentHash(basis(s, run.basis.referenceAssetIds)) !== contentHash(run.basis)) throw new HttpError(409, '资料已变化，请重新讨论当前版本');
    const prior = db.prepare('SELECT body FROM agent_proposals WHERE session_id=? ORDER BY rowid DESC LIMIT 1').get(s.id);
    const existingIds = new Set(['elements','links','routes'].flatMap(k => before[k].concat(prior ? JSON.parse(prior.body).document[k] : []).map(v => v.id)));
    const targets = sourceTargets(input.document), originals = sourceTargets(before);
    const userIds = new Set(db.prepare("SELECT id FROM agent_messages WHERE session_id=? AND role='user'").all(s.id).map(m=>m.id));
    for (const source of input.sources) {
      if (!targets.has(source.target)) throw new HttpError(400, '来源指向未知条目');
      const allowed = source.kind === 'image' ? seenImages : source.kind === 'user' ? userIds : new Set([...originals].filter(([,v])=>v.status==='known').map(([k])=>k));
      if (source.refs.some(ref=>!allowed.has(ref))) throw new HttpError(400, '来源须引用已读图片、用户消息或已有明确事实');
    }
    for (const [target,item] of targets) if (item.status === 'known' && !input.sources.some(src=>src.target === target))
      throw new HttpError(400, `已知条目 ${target} 缺少来源，请提供依据或标记待补充`);
    const remap = new Map();
    for (const key of ['elements','links','routes']) for (const item of input.document[key]) {
      if (!existingIds.has(item.id)) remap.set(item.id,`${key === 'elements' ? 'place' : key === 'links' ? 'rel' : 'route'}_${id().replaceAll('-','').slice(0,16)}`);
    }
    for (const key of ['elements','links','routes']) for (const item of input.document[key]) {
      item.id = remap.get(item.id) || item.id;
      if (key === 'links') { item.from = remap.get(item.from)||item.from; item.to = remap.get(item.to)||item.to; }
      if (key === 'routes') item.via = item.via.map(v=>remap.get(v)||v);
    }
    input.sources = input.sources.map(src => { const [key,anchor] = src.target.split('/'); return { ...src, target: anchor ? key+'/'+(remap.get(anchor)||anchor) : key }; });
    input.document=parse(spatialDocumentSchema,input.document);
    const changes = [];
    if (canonicalJSON(before.frame) !== canonicalJSON(input.document.frame)) changes.push('调整方向基准');
    if(canonicalJSON(before.unknowns)!==canonicalJSON(input.document.unknowns))changes.push('更新待补充事项');
    if(canonicalJSON(before.referenceAssetIds)!==canonicalJSON(input.document.referenceAssetIds))changes.push('更新核对参考图');
    for (const key of ['elements','links','routes']) {
      const old = new Map(before[key].map(item=>[item.id,item]));
      for (const item of input.document[key]) changes.push(!old.has(item.id)?`新增：${item.label||item.id}`:canonicalJSON(old.get(item.id))!==canonicalJSON(item)?`修改：${item.label||item.id}`:'');
      for (const item of before[key]) if (!input.document[key].some(v=>v.id===item.id)) changes.push(`移除：${item.label||item.id}`);
    }
    const body = { owner:'Sean', ...input, changes: changes.filter(Boolean), basis: run.basis };
    const proposalId = id();
    db.prepare('INSERT INTO agent_proposals VALUES (?,?,?,?,?,?,?)').run(proposalId,run.id,s.id,canonicalJSON(body),contentHash(body),null,now());
    emit(run.id,'proposal',{proposalId});
    return { proposalId, document: input.document, changes: body.changes, savedAs: 'proposal-only', confirmation: 'requires-user' };
  }
  async function execute(runId) {
    const run = runRow(runId), s = sessionRow(run.session_id), state = active.get(runId);
    let opened, unsubscribe, timer;
    const seenImages = new Set();
    const imageCache = new Map();
    let calls = 0;
    const tool = (name,description,parameters,fn) => ({ name, label: labels[name], description, parameters,
      execute: async (_callId, args) => {
        if (state.cancelled) throw new Error('对话已取消');
        if (++calls > 24) { state.cancelled = true; void opened?.session.abort(); throw new Error('本轮工具调用达到上限，请继续讨论'); }
        try {return await fn(args);} catch(error) {
          if(error instanceof HttpError)return jsonTool({error:error.message,status:error.status,details:error.details||null,instruction:'请依据错误修订提案或询问用户，不能假称操作成功。'});
          return jsonTool({error:'工具未能读取或保存当前资料，请核对参考图后继续。',instruction:'不要声称此工具已成功执行。'});
        }
      } });
    const tools = [
      tool('get_scene_context','读取当前工程共用设定、实体关系、空间文档及可引用用户消息。',{type:'object',properties:{},additionalProperties:false},()=>{
        if(contentHash(basis(s,run.basis.referenceAssetIds))!==contentHash(run.basis))throw new HttpError(409,'资料已在本轮期间变化，请停止本轮并继续讨论最新版本');
        const previous = db.prepare('SELECT body FROM agent_proposals WHERE session_id=? ORDER BY rowid DESC LIMIT 1').get(s.id);
        const captured=JSON.parse(db.prepare('SELECT body FROM agent_run_contexts WHERE run_id=?').get(runId).body);
        return jsonTool({ ...captured,
          selectedImages:run.basis.images, previousProposal:previous?JSON.parse(previous.body):null,
          userMessages:db.prepare("SELECT id,text FROM agent_messages WHERE session_id=? AND role='user' ORDER BY rowid DESC LIMIT 30").all(s.id),
          basis:run.basis });
      }),
      tool('view_reference_image','查看用户本轮选定的一张场景图片；只接受稳定素材 ID。',z.toJSONSchema(z.object({assetId:uuid}).strict()),async raw=>{
        const {assetId}=parse(z.object({assetId:uuid}).strict(),raw);
        if (!run.basis.referenceAssetIds.includes(assetId)) throw new HttpError(400,'图片不在用户本轮选图中');
        if(contentHash(basis(s,run.basis.referenceAssetIds))!==contentHash(run.basis))throw new HttpError(409,'本轮依据已变化，请继续讨论最新版本后重新看图');
        if(imageCache.has(assetId))return jsonTool({assetId,alreadyViewed:true,notice:'本轮之前的图片工具结果已包含此图，不重复追加图片。'});
        const a=store.asset(assetId), bytes=await sharp(store.assetBytes(assetId)).resize({width:1600,height:1600,fit:'inside',withoutEnlargement:true}).png().toBuffer();
        seenImages.add(assetId);
        imageCache.set(assetId,true);
        return {content:[{type:'text',text:`assetId=${assetId}；名称=${a.name}；来源哈希=${a.hash}；缩放仅供观察，不证明绝对尺度。`},
          {type:'image',source:{type:'base64',mediaType:'image/png',data:bytes.toString('base64')}}],details:{}};
      }),
      tool('load_authoring_skill','读取场景固定空间设定方法。',z.toJSONSchema(z.object({skillId:z.literal('fixed-space')}).strict()),raw=>{
        parse(z.object({skillId:z.literal('fixed-space')}).strict(),raw);return jsonTool(sceneProfile.skills[0]);
      }),
      tool('propose_scene_spatial','提出有来源的完整空间候选草稿，不保存或确认实体事实。',{
        type:'object',properties:{document:z.toJSONSchema(spatialDocumentShape),summary:{type:'string'},questions:{type:'array',items:{type:'string'},maxItems:3},
          sources:z.toJSONSchema(z.array(sourceSchema))},required:['document','summary','questions','sources'],additionalProperties:false
      },raw=>jsonTool(createProposal(s,run,raw,seenImages)))
    ];
    try {
      if (state.cancelled) return;
      timer = setTimeout(()=>{state.cancelled=true;state.reason='本轮达到 5 分钟上限，已停止，可继续讨论';void opened?.session.abort();},300000);
      opened = await runtime.open({sessionId:s.id,entries:JSON.parse(s.entries),provider:s.provider,modelId:s.model_id,prompt:sceneProfile.prompt,tools});
      state.session = opened.session;
      if (state.cancelled) return;
      let output='';
      unsubscribe = opened.session.subscribe(event=>{
        if(event.type==='message_start'&&event.message?.role==='assistant'&&output)output+='\n\n';
        else if (event.type==='message_update' && event.assistantMessageEvent?.type==='text_delta') {
          const delta=event.assistantMessageEvent.delta;
          if (output.length+delta.length>64000) {state.cancelled=true;void opened.session.abort();return;}
          output+=delta; db.prepare('UPDATE agent_messages SET text=? WHERE id=?').run(output,run.assistant_message_id);emit(runId,'text',{delta});
        } else if (event.type==='tool_execution_start') emit(runId,'tool',{label:labels[event.toolName]||'整理资料'});
        else if(event.type==='turn_end') queueMicrotask(()=>{
          if(active.get(runId)===state)db.prepare('UPDATE agent_sessions SET entries=? WHERE id=?').run(canonicalJSON(opened.entries()),s.id);
        });
      });
      const message=db.prepare("SELECT id,text FROM agent_messages WHERE run_id=? AND role='user'").get(runId);
      await opened.session.prompt(`本轮用户消息 ID：${message.id}\n本轮选定参考图 ID：${run.basis.referenceAssetIds.join(', ')}\n最新资料依据：${canonicalJSON(run.basis)}\n用户：${message.text}`,{expandPromptTemplates:false});
      const last=opened.session.messages.filter(m=>m.role==='assistant').at(-1);
      if (last?.stopReason==='error' && !state.cancelled) throw new Error('模型请求失败');
      emit(runId,'usage',{usage:last?.usage||null});
      const status=state.cancelled?'cancelled':'succeeded';
      db.prepare('UPDATE agent_runs SET status=?,error=?,completed_at=? WHERE id=?').run(status,state.reason||null,now(),runId);
    } catch (_error) {
      // Provider errors may contain keys or internal paths. Keep public events and logs free of raw provider errors.
      db.prepare('UPDATE agent_runs SET status=?,error=?,completed_at=? WHERE id=?').run(state.cancelled?'cancelled':'failed',
        state.reason||'助手请求未完成，请检查模型配置后继续；已保存的讨论和提案仍保留。',now(),runId);
    } finally {
      clearTimeout(timer);unsubscribe?.();
      if (opened) {
        db.prepare('UPDATE agent_sessions SET entries=? WHERE id=?').run(canonicalJSON(opened.entries()),s.id);
        opened.session.dispose();
      }
      if (!terminal(runRow(runId).status)) db.prepare("UPDATE agent_runs SET status='cancelled',completed_at=? WHERE id=?").run(now(),runId);
      active.delete(runId);emit(runId,'done',{status:runRow(runId).status});
    }
  }
  async function start(sessionId, body) {
    const input=parse(z.object({requestId:uuid,text:z.string().trim().min(1).max(12000),referenceAssetIds:z.array(uuid).min(1).max(8)
      .refine(v=>new Set(v).size===v.length,'参考图不能重复')}).strict(),body);
    const s=sessionRow(sessionId);member(s);
    const old=db.prepare('SELECT * FROM agent_runs WHERE request_id=?').get(input.requestId);
    if (old) {
      const m=db.prepare("SELECT text FROM agent_messages WHERE run_id=? AND role='user'").get(old.id);
      if (old.session_id!==sessionId||m?.text!==input.text||canonicalJSON(JSON.parse(old.basis).referenceAssetIds)!==canonicalJSON(input.referenceAssetIds)) throw new HttpError(409,'重复请求标识用于不同内容');
      return {runId:old.id,status:old.status};
    }
    if (db.prepare("SELECT id FROM agent_runs WHERE session_id=? AND status='running'").get(sessionId)) throw new HttpError(409,'请等待当前回复或先取消');
    if (active.size>=2) throw new HttpError(409,'助手正在处理其他对话，请稍后再试');
    if (!(await runtime.models()).some(m=>m.provider===s.provider&&m.id===s.model_id)) throw new HttpError(400,'此会话模型当前不可用，请检查配置或新建对话');
    // Recheck after asynchronous model discovery to prevent concurrent submissions.
    const runId=id(), assistantId=id(), stamp=now();
    store.transaction(()=>{
      if (active.size>=2) throw new HttpError(409,'助手正在处理其他对话，请稍后再试');
      if (db.prepare("SELECT id FROM agent_runs WHERE session_id=? AND status='running'").get(sessionId)) throw new HttpError(409,'当前会话已有回复正在运行');
      db.prepare('INSERT INTO agent_runs VALUES (?,?,?,?,?,?,?,?,?)').run(runId,sessionId,input.requestId,'running',canonicalJSON(basis(s,input.referenceAssetIds)),assistantId,null,stamp,null);
      db.prepare('INSERT INTO agent_run_contexts VALUES (?,?)').run(runId,canonicalJSON(sceneContext(s)));
      db.prepare('INSERT INTO agent_messages VALUES (?,?,?,?,?,?)').run(id(),sessionId,runId,'user',input.text,stamp);
      db.prepare('INSERT INTO agent_messages VALUES (?,?,?,?,?,?)').run(assistantId,sessionId,runId,'assistant','',stamp);
    });
    active.set(runId,{cancelled:false});queueMicrotask(()=>void execute(runId));
    return {runId,status:'running'};
  }
  async function cancel(runId) {
    const run=runRow(runId), state=active.get(runId);
    if (state) { state.cancelled=true; await state.session?.abort(); }
    return {runId,status:runRow(run.id).status};
  }
  function applyProposal(proposalId, body) {
    const input=parse(z.object({expectedContentHash:z.string().length(64)}).strict(),body);
    const row=db.prepare('SELECT * FROM agent_proposals WHERE id=?').get(proposalId);
    if (!row) throw new HttpError(404,'空间提案不存在');
    const s=sessionRow(row.session_id), run=runRow(row.run_id), proposal=JSON.parse(row.body);
    if (row.content_hash!==input.expectedContentHash) throw new HttpError(409,'提案内容不匹配');
    if (row.applied_version_id) return {versionId:row.applied_version_id,alreadyApplied:true};
    if (run.status!=='succeeded') throw new HttpError(409,'只能应用完整结束的对话提案，请继续讨论后重新提出');
    // Single transaction covers the source check, draft write and provenance pointer.
    const result=store.transaction(()=>{
      if (contentHash(basis(s,run.basis.referenceAssetIds))!==contentHash(run.basis)) throw new HttpError(409,'工程、场景或参考图已经变化，请继续讨论后生成新提案');
      const doc=parse(spatialDocumentSchema,proposal.document), current=management.spatial.get(s.entity_id);
      const versionId=id(), version=current.summary.version+1;
      db.prepare('INSERT INTO scene_spatial_versions VALUES (?,?,?,?,?,?,?)').run(versionId,s.entity_id,version,canonicalJSON(doc),contentHash(doc),null,now());
      db.prepare('INSERT INTO entity_spatial_state VALUES (?,?) ON CONFLICT(entity_id) DO UPDATE SET version_id=excluded.version_id').run(s.entity_id,versionId);
      db.prepare('UPDATE agent_proposals SET applied_version_id=? WHERE id=?').run(versionId,proposalId);
      return {versionId,alreadyApplied:false};
    });
    return result;
  }
  function events(runId, after) { runRow(runId);return db.prepare('SELECT seq,type,body FROM agent_events WHERE run_id=? AND seq>? ORDER BY seq LIMIT 300').all(runId,after).map(r=>({...r,body:JSON.parse(r.body)})); }
  return { projects,project,saveProject,context,sessions,session,createSession,start,cancel,applyProposal,events,run:runRow,
    models:runtime.models,profiles:agentProfiles.map(({prompt,skills,...p})=>({...p,skills:skills.map(({text,...skill})=>skill)})),
    recover() {db.prepare("UPDATE agent_runs SET status='interrupted',error='服务停止时对话未结束，请继续讨论',completed_at=? WHERE status='running'").run(now());},
    async close() { await Promise.allSettled([...active.keys()].map(cancel)); } };
}

export function agentWorkspaceRouter(service) {
  const r=Router();
  for (const param of ['projectId','sessionId','runId','proposalId']) r.param(param,(req,res,next,value)=>{
    try {parse(uuid,value);next();}catch(e){next(e);}
  });
  r.get('/capabilities',async (_req,res)=>{
    let models=[],configurationIssue=null;
    try {models=await service.models();} catch {configurationIssue='模型配置无法读取，请检查服务端 Agent 配置';}
    res.json({owner:'Sean',runtime:'pi-sdk',sdkVersion:'0.86.0',profiles:service.profiles,models,
      configurationIssue:configurationIssue||(!models.length?'尚无可用的看图模型：配置模型提供方凭据后即可使用。':null)});
  });
  r.get('/projects',(_req,res)=>res.json({projects:service.projects()}));
  r.post('/projects',(req,res)=>res.status(201).json(service.saveProject(null,req.body)));
  r.patch('/projects/:projectId',(req,res)=>res.json(service.saveProject(req.params.projectId,req.body)));
  r.get('/projects/:projectId/context',(req,res)=>res.json(service.context(req.params.projectId)));
  r.get('/projects/:projectId/sessions',(req,res)=>res.json({sessions:service.sessions(req.params.projectId,parse(uuid,req.query.entityId))}));
  r.post('/sessions',async (req,res)=>res.status(201).json(await service.createSession(req.body)));
  r.get('/sessions/:sessionId',(req,res)=>res.json(service.session(req.params.sessionId)));
  r.post('/sessions/:sessionId/messages',async (req,res)=>res.status(202).json(await service.start(req.params.sessionId,req.body)));
  r.post('/runs/:runId/cancel',async (req,res)=>res.json(await service.cancel(req.params.runId)));
  r.get('/runs/:runId/events',(req,res)=>{
    service.run(req.params.runId);
    let cursor=parse(z.coerce.number().int().nonnegative().max(Number.MAX_SAFE_INTEGER),req.get('Last-Event-ID')||req.query.after||0),closed=false;
    res.set({'Content-Type':'text/event-stream','Cache-Control':'no-cache','Connection':'keep-alive'});res.flushHeaders();
    function send() {
      if(closed)return;
      const batch=service.events(req.params.runId,cursor);
      for(const event of batch){res.write(`id: ${event.seq}\nevent: ${event.type}\ndata: ${JSON.stringify(event.body)}\n\n`);cursor=event.seq;}
      if(batch.length<300 && terminal(service.run(req.params.runId).status)) {res.end();return;}
      res.write(': keepalive\n\n');
    }
    const timer=setInterval(send,600);res.on('close',()=>{closed=true;clearInterval(timer);});send();
  });
  r.post('/proposals/:proposalId/apply',(req,res)=>res.json(service.applyProposal(req.params.proposalId,req.body)));
  return r;
}
