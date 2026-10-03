// Owner: Sean — execution adapters never own entity or history lifecycle.
import { readFileSync } from 'node:fs';
import { buildComfyWorkflow } from './catalog.mjs';

export const comfyUrl = (process.env.REFERENCE_COMFY_URL || 'http://127.0.0.1:8188').replace(/\/$/, '');
export async function comfyRequest(path, options = {}) {
  const response = await fetch(`${comfyUrl}${path}`, { ...options, signal: AbortSignal.timeout(30_000) });
  if (!response.ok) throw new Error(`ComfyUI ${response.status}: ${(await response.text()).slice(0, 500)}`);
  return response.json();
}
export async function prepareComfy(store, run) {
  const names = [];
  for (const reference of run.snapshot.references) {
    const form = new FormData();
    const a = store.asset(reference.id);
    form.set('image', new Blob([readFileSync(store.assetPath(a.id))], { type: a.mime }), `${a.id}.${a.mime === 'audio/wav' ? 'wav' : a.mime.split('/')[1]}`);
    form.set('subfolder', 'sean_reference_workspace');
    form.set('overwrite', 'false');
    const upload = await comfyRequest('/upload/image', { method: 'POST', body: form });
    names.push(upload.subfolder ? `${upload.subfolder}/${upload.name}` : upload.name);
  }
  return { workflow: buildComfyWorkflow(run.snapshot, names, run.id), clientId: `sean-reference-${run.id}` };
}
export async function submitComfy(execution) {
  return comfyRequest('/prompt', { method: 'POST', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ prompt: execution.workflow, client_id: execution.clientId, extra_data: { extra_pnginfo: { owner: 'Sean' } } }) });
}
export async function readComfyResult(promptId, mediaType = 'image') {
  const history = await comfyRequest(`/history/${encodeURIComponent(promptId)}`);
  const entry = history[promptId];
  if (entry) {
    const failure = entry.status?.messages?.find(([kind]) => ['execution_error', 'execution_interrupted'].includes(kind));
    if (failure || entry.status?.status_str === 'error') throw new Error(failure?.[1]?.exception_message || 'ComfyUI 运行失败或被中断');
    if (entry.status?.completed) {
      const images = Object.entries(entry.outputs || {}).flatMap(([nodeId, output]) =>
        (mediaType === 'audio' ? output.audio || [] : output.images || []).map(file => ({ ...file, nodeId }))).filter(i => i.type === 'output');
      if (!images.length) throw new Error(`运行已结束，但没有可回收的${mediaType === 'audio' ? '音频' : '图片'}`);
      return { state: 'succeeded', images };
    }
  }
  const queue = await comfyRequest('/queue');
  if (queue.queue_running.some(item => item[1] === promptId)) return { state: 'running' };
  if (queue.queue_pending.some(item => item[1] === promptId)) return { state: 'queued' };
  return { state: 'unknown' };
}
export async function downloadComfy(image) {
  const query = new URLSearchParams({ filename: image.filename, subfolder: image.subfolder || '', type: 'output' });
  const response = await fetch(`${comfyUrl}/view?${query}`, { signal: AbortSignal.timeout(30_000) });
  if (!response.ok) throw new Error(`无法回收生成素材 (${response.status})`);
  return readLimited(response, 25 * 1024 * 1024);
}
export async function readLimited(response, limit) {
  if (Number(response.headers.get('content-length')) > limit) throw new Error('素材超过大小上限');
  const chunks = []; let length = 0;
  for await (const chunk of response.body) {
    length += chunk.length;
    if (length > limit) throw new Error('素材超过大小上限');
    chunks.push(chunk);
  }
  return Buffer.concat(chunks);
}
