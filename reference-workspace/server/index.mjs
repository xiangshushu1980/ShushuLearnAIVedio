// Owner: Sean — standalone loopback API and React application host.
import express from 'express';
import multer from 'multer';
import { z } from 'zod';
import { resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { existsSync } from 'node:fs';
import { createStore, HttpError, id, now } from './store.mjs';
import { catalog } from './catalog.mjs';
import { createRunService } from './runs.mjs';
import { comfyRequest } from './adapters.mjs';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const port = Number(process.env.REFERENCE_PORT || 4188);
const store = createStore(process.env.REFERENCE_DATA_DIR || resolve(root, '.data'));
const runs = createRunService(store);
if (!store.db.prepare('SELECT id FROM entities LIMIT 1').get()) {
  store.db.prepare('INSERT INTO entities VALUES (?,?,?,?)').run(id(), '参考实体', '{}', now());
}
const app = express();
app.disable('x-powered-by');
// The first release is a local application. Mutation requests must originate from its own UI.
app.use((req, res, next) => {
  if (!/^(127\.0\.0\.1|localhost)(:\d+)?$/.test(req.headers.host || '')) return next(new HttpError(403, '仅支持本机访问'));
  if (!['GET', 'HEAD', 'OPTIONS'].includes(req.method) && req.headers.origin) {
    try {
      if (new URL(req.headers.origin).host !== req.headers.host) return next(new HttpError(403, '请求来源与工作台不一致'));
    } catch { return next(new HttpError(403, '请求来源无效')); }
  }
  res.set('X-Content-Type-Options', 'nosniff');
  next();
});
app.use(express.json({ limit: '256kb' }));
const check = (schema, input) => {
  const parsed = schema.safeParse(input);
  if (!parsed.success) throw new HttpError(400, '输入格式不正确', parsed.error.flatten());
  return parsed.data;
};
const key = req => {
  const value = req.get('Idempotency-Key');
  if (!value || value.length > 120) throw new HttpError(400, '缺少有效的重复提交标识');
  return value;
};
app.get('/api/health', (_req, res) => res.json({ ok: true, owner: 'Sean', version: 1 }));
app.get('/api/catalog', (_req, res) => res.json(catalog));
app.get('/api/entities', (_req, res) => res.json(store.db.prepare('SELECT id,name,created_at AS createdAt FROM entities ORDER BY created_at').all()));
// Integration endpoint for a future management view; creation panels do not edit entity context.
app.post('/api/entities', (req, res) => {
  const input = check(z.object({ name: z.string().trim().min(1).max(100), context: z.record(z.string(), z.unknown()).default({}) }).strict(), req.body);
  const entityId = id();
  store.db.prepare('INSERT INTO entities VALUES (?,?,?,?)').run(entityId, input.name, JSON.stringify(input.context), now());
  res.status(201).json(store.entity(entityId));
});
app.get('/api/entities/:entityId', (req, res) => res.json(store.entity(req.params.entityId)));
app.get('/api/entities/:entityId/workspace', (req, res) => {
  const entity = store.entity(req.params.entityId);
  const assets = store.db.prepare('SELECT * FROM assets WHERE entity_id=? AND deleted_at IS NULL ORDER BY created_at DESC,id').all(entity.id).map(store.assetView);
  const history = store.db.prepare('SELECT * FROM runs WHERE entity_id=? ORDER BY created_at DESC,id').all(entity.id).map(store.runView);
  const draft = store.db.prepare('SELECT value,updated_at FROM drafts WHERE entity_id=?').get(entity.id);
  res.json({ entity, assets, runs: history, draft: draft ? { value: JSON.parse(draft.value), updatedAt: draft.updated_at } : null });
});
app.put('/api/entities/:entityId/draft', (req, res) => {
  const entityId = store.entity(req.params.entityId).id;
  const body = check(z.object({ expectedUpdatedAt: z.string().nullable(), value: z.object({
    modelId: z.string().max(100), styleId: z.string().max(100), prompt: z.string().max(16000), purpose: z.string().max(2000),
    references: z.array(z.string().uuid()).max(16), parameters: z.record(z.string(), z.union([z.string(), z.number()]))
  }).strict() }).strict(), req.body);
  if (!catalog.models.some(m => m.id === body.value.modelId) || !catalog.styles.some(s => s.id === body.value.styleId))
    throw new HttpError(400, '草稿的模型或风格不可用');
  const updatedAt = store.transaction(() => {
    const current = store.db.prepare('SELECT updated_at FROM drafts WHERE entity_id=?').get(entityId);
    if ((current?.updated_at || null) !== body.expectedUpdatedAt) throw new HttpError(409, '草稿已在另一页面更新，请重新载入后比较');
    const timestamp = new Date(Math.max(Date.now(), current ? Date.parse(current.updated_at) + 1 : 0)).toISOString();
    store.db.prepare('INSERT INTO drafts VALUES (?,?,?) ON CONFLICT(entity_id) DO UPDATE SET value=excluded.value,updated_at=excluded.updated_at')
      .run(entityId, JSON.stringify(body.value), timestamp);
    return timestamp;
  });
  res.json({ updatedAt });
});
const upload = multer({ storage: multer.memoryStorage(), limits: { files: 16, fileSize: 25 * 1024 * 1024, fields: 0 } });
app.post('/api/entities/:entityId/settings', upload.array('images', 16), async (req, res) => {
  const entityId = store.entity(req.params.entityId).id;
  if (!req.files?.length) throw new HttpError(400, '请选择图片');
  const stages = [];
  try {
    for (const file of req.files) stages.push(await store.stageImage(file.buffer, Buffer.from(file.originalname, 'latin1').toString('utf8'), entityId, 'setting', null,
      { source: 'directory-import', importedAt: now(), originalFilename: file.originalname }));
    const assets = store.transaction(() => store.registerStages(stages));
    res.status(201).json({ assets });
  } catch (error) { stages.forEach(store.discardStage); throw error; }
});
app.get('/api/assets/:assetId/content', (req, res) => {
  const asset = store.asset(req.params.assetId);
  res.set('Content-Type', asset.mime).set('Cache-Control', 'private, no-cache');
  res.sendFile(store.assetPath(asset.id), { dotfiles: 'allow' });
});
app.patch('/api/assets/:assetId/lock', (req, res) => {
  const asset = store.asset(req.params.assetId);
  const { locked } = check(z.object({ locked: z.boolean() }).strict(), req.body);
  if (asset.protected && !locked) throw new HttpError(409, '当前主形象来源受保护');
  if (asset.kind !== 'concept') throw new HttpError(400, '只有概念图历史使用锁定操作');
  store.db.prepare('UPDATE assets SET locked=? WHERE id=?').run(locked ? 1 : 0, asset.id);
  res.json(store.asset(asset.id));
});
app.delete('/api/assets/:assetId', (req, res) => {
  const { confirmUsed } = check(z.object({ confirmUsed: z.boolean().default(false) }).strict(), req.body || {});
  store.deleteAsset(req.params.assetId, confirmUsed);
  res.status(204).end();
});
app.post('/api/entities/:entityId/runs', (req, res) => res.status(201).json(runs.start(req.params.entityId, req.body, key(req))));
app.get('/api/runs/:runId', (req, res) => res.json(store.run(req.params.runId)));
app.get('/api/runs/:runId/workflow', (req, res) => {
  store.run(req.params.runId);
  const row = store.db.prepare('SELECT execution FROM runs WHERE id=?').get(req.params.runId);
  if (!row.execution) throw new HttpError(409, '尚未构建本次运行工作流');
  res.json(JSON.parse(row.execution).workflow);
});
app.post('/api/runs/:runId/retry', (req, res) => res.status(201).json(runs.retry(req.params.runId, key(req))));
app.post('/api/runs/:runId/cancel', async (req, res) => { await runs.cancel(req.params.runId); res.json(store.run(req.params.runId)); });
app.get('/api/execution-status', async (_req, res) => {
  try {
    const queue = await comfyRequest('/queue');
    res.json({ connected: true, running: queue.queue_running.length, queued: queue.queue_pending.length });
  } catch { res.json({ connected: false }); }
});
app.use('/api', (_req, _res, next) => next(new HttpError(404, '接口不存在')));
if (process.argv.includes('--dev')) {
  const { createServer } = await import('vite');
  const vite = await createServer({ root, server: { middlewareMode: true }, appType: 'spa' });
  app.use(vite.middlewares);
} else {
  if (!existsSync(resolve(root, 'dist/index.html'))) throw new Error('请先运行 npm run build，或使用 npm run dev');
  app.use(express.static(resolve(root, 'dist')));
  app.get('/{*path}', (_req, res) => res.sendFile(resolve(root, 'dist/index.html')));
}
app.use((error, _req, res, _next) => {
  const status = error instanceof multer.MulterError ? 400 : error.status || 500;
  if (status === 500) console.error(error);
  res.status(status).json({ error: status === 500 ? '服务操作失败，请查看服务日志' : error.message, details: error.details });
});
const server = app.listen(port, '127.0.0.1', () => {
  console.log(`Owner: Sean — Reference 工作台 http://127.0.0.1:${port}`);
  runs.recover();
});
server.on('error', error => { console.error(error.message); process.exit(1); });
process.on('SIGTERM', () => { server.close(); process.exit(0); });
process.on('SIGINT', () => { server.close(); process.exit(0); });
