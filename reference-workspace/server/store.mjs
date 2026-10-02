// Owner: Sean — durable business data, independent of ComfyUI output paths.
import { DatabaseSync } from 'node:sqlite';
import { randomUUID, createHash } from 'node:crypto';
import { mkdirSync, writeFileSync, unlinkSync, existsSync, readFileSync } from 'node:fs';
import { join, resolve } from 'node:path';
import sharp from 'sharp';

export const now = () => new Date().toISOString();
export const id = () => randomUUID();
export class HttpError extends Error {
  constructor(status, message, details) { super(message); this.status = status; this.details = details; }
}

export function createStore(dataDir) {
  const root = resolve(dataDir);
  const media = join(root, 'media');
  mkdirSync(media, { recursive: true });
  const db = new DatabaseSync(join(root, 'workspace.sqlite'));
  db.exec(`PRAGMA journal_mode=WAL; PRAGMA foreign_keys=ON;
    CREATE TABLE IF NOT EXISTS entities (id TEXT PRIMARY KEY, name TEXT NOT NULL, context TEXT NOT NULL DEFAULT '{}', created_at TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS assets (id TEXT PRIMARY KEY, entity_id TEXT NOT NULL REFERENCES entities(id), kind TEXT NOT NULL,
      name TEXT NOT NULL, file TEXT NOT NULL, mime TEXT NOT NULL, hash TEXT NOT NULL, width INTEGER NOT NULL, height INTEGER NOT NULL,
      locked INTEGER NOT NULL DEFAULT 0, protected INTEGER NOT NULL DEFAULT 0, ever_confirmed INTEGER NOT NULL DEFAULT 0,
      description TEXT NOT NULL DEFAULT '', description_source TEXT NOT NULL DEFAULT 'empty', metadata TEXT NOT NULL,
      run_id TEXT, created_at TEXT NOT NULL, deleted_at TEXT);
    CREATE TABLE IF NOT EXISTS runs (id TEXT PRIMARY KEY, entity_id TEXT NOT NULL REFERENCES entities(id), status TEXT NOT NULL,
      snapshot TEXT NOT NULL, progress REAL, phase TEXT NOT NULL, prompt_id TEXT, execution TEXT,
      error TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, completed_at TEXT);
    CREATE TABLE IF NOT EXISTS run_inputs (run_id TEXT NOT NULL REFERENCES runs(id), asset_id TEXT NOT NULL REFERENCES assets(id), position INTEGER NOT NULL,
      PRIMARY KEY(run_id, position));
    CREATE TABLE IF NOT EXISTS drafts (entity_id TEXT PRIMARY KEY REFERENCES entities(id), value TEXT NOT NULL, updated_at TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS request_keys (key TEXT PRIMARY KEY, run_id TEXT NOT NULL REFERENCES runs(id), fingerprint TEXT NOT NULL);
    CREATE INDEX IF NOT EXISTS assets_entity ON assets(entity_id, created_at);
    CREATE INDEX IF NOT EXISTS runs_entity ON runs(entity_id, created_at);
    CREATE INDEX IF NOT EXISTS input_asset ON run_inputs(asset_id);`);
  const transaction = (fn) => {
    db.exec('BEGIN IMMEDIATE');
    try { const value = fn(); db.exec('COMMIT'); return value; }
    catch (error) { db.exec('ROLLBACK'); throw error; }
  };
  const entity = (entityId) => {
    const row = db.prepare('SELECT * FROM entities WHERE id=?').get(entityId);
    if (!row) throw new HttpError(404, '找不到该实体');
    return { id: row.id, name: row.name, context: JSON.parse(row.context), createdAt: row.created_at };
  };
  const assetView = (row) => row && ({ id: row.id, entityId: row.entity_id, kind: row.kind, name: row.name,
    mime: row.mime, hash: row.hash, width: row.width, height: row.height, locked: !!row.locked, protected: !!row.protected,
    everConfirmed: !!row.ever_confirmed, description: row.description, descriptionSource: row.description_source,
    metadata: JSON.parse(row.metadata), runId: row.run_id, createdAt: row.created_at, deletedAt: row.deleted_at,
    url: row.deleted_at ? null : `/api/assets/${row.id}/content` });
  const asset = (assetId, includeDeleted = false) => {
    const row = db.prepare('SELECT * FROM assets WHERE id=?').get(assetId);
    if (!row || (row.deleted_at && !includeDeleted)) throw new HttpError(404, '来源图已删除或不存在');
    return assetView(row);
  };
  const runView = (row) => row && ({ id: row.id, entityId: row.entity_id, status: row.status, snapshot: JSON.parse(row.snapshot),
    progress: row.progress, phase: row.phase, promptId: row.prompt_id, error: row.error, createdAt: row.created_at,
    updatedAt: row.updated_at, completedAt: row.completed_at,
    references: db.prepare('SELECT asset_id, position FROM run_inputs WHERE run_id=? ORDER BY position').all(row.id)
      .map(({ asset_id, position }) => ({ ...asset(asset_id, true), position })),
    outputs: db.prepare("SELECT * FROM assets WHERE run_id=? ORDER BY created_at, id").all(row.id).map(assetView) });
  const run = (runId) => {
    const row = db.prepare('SELECT * FROM runs WHERE id=?').get(runId);
    if (!row) throw new HttpError(404, '找不到该次运行');
    return runView(row);
  };
  async function stageImage(buffer, name, entityId, kind, runId, metadata = {}) {
    entity(entityId);
    if (buffer.length > 25 * 1024 * 1024) throw new HttpError(413, '单张图片不得超过 25 MB');
    let info;
    try { info = await sharp(buffer, { limitInputPixels: 40_000_000, animated: false }).metadata(); }
    catch { throw new HttpError(400, `${name} 不是可用图片`); }
    const formats = { png: ['png', 'image/png'], jpeg: ['jpg', 'image/jpeg'], webp: ['webp', 'image/webp'] };
    const format = formats[info.format];
    if (!format || (info.pages || 1) !== 1) throw new HttpError(400, '请选择静态 PNG、JPEG 或 WebP 图片');
    const assetId = id();
    const file = `${assetId}.${format[0]}`;
    writeFileSync(join(media, file), buffer, { flag: 'wx' });
    return { assetId, file, entityId, kind, name: name.slice(0, 200), mime: format[1],
      hash: createHash('sha256').update(buffer).digest('hex'), width: info.width, height: info.height,
      runId: runId || null, metadata: { ...metadata, owner: 'Sean' }, createdAt: now() };
  }
  const discardStage = (stage) => { if (existsSync(join(media, stage.file))) unlinkSync(join(media, stage.file)); };
  function registerStages(stages) {
    const insert = db.prepare(`INSERT INTO assets (id,entity_id,kind,name,file,mime,hash,width,height,locked,metadata,run_id,created_at)
      VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)`);
    for (const s of stages) insert.run(s.assetId, s.entityId, s.kind, s.name, s.file, s.mime, s.hash, s.width, s.height,
      s.kind === 'concept' ? 1 : 0, JSON.stringify(s.metadata), s.runId, s.createdAt);
    return stages.map(s => asset(s.assetId));
  }
  function createRun(entityId, snapshot, key) {
    return transaction(() => {
      entity(entityId);
      const fingerprint = createHash('sha256').update(JSON.stringify({ entityId, snapshot })).digest('hex');
      const existing = db.prepare('SELECT * FROM request_keys WHERE key=?').get(key);
      if (existing) {
        if (existing.fingerprint !== fingerprint) throw new HttpError(409, '重复提交标识与原输入不一致');
        return { run: run(existing.run_id), created: false };
      }
      const runId = id(), timestamp = now();
      db.prepare(`INSERT INTO runs (id,entity_id,status,snapshot,progress,phase,created_at,updated_at)
        VALUES (?,?,'queued',?,NULL,'等待提交',?,?)`).run(runId, entityId, JSON.stringify(snapshot), timestamp, timestamp);
      snapshot.references.forEach((ref, position) => {
        const a = asset(ref.id);
        if (a.entityId !== entityId) throw new HttpError(400, '引用图片不属于当前实体');
        db.prepare('INSERT INTO run_inputs VALUES (?,?,?)').run(runId, ref.id, position);
      });
      db.prepare('INSERT INTO request_keys VALUES (?,?,?)').run(key, runId, fingerprint);
      return { run: run(runId), created: true };
    });
  }
  function updateRun(runId, values) {
    const allowed = new Set(['status', 'progress', 'phase', 'prompt_id', 'execution', 'error', 'completed_at']);
    const entries = Object.entries(values).filter(([k]) => allowed.has(k));
    if (entries.length) db.prepare(`UPDATE runs SET ${entries.map(([k]) => `${k}=?`).join(',')},updated_at=? WHERE id=?`)
      .run(...entries.map(([,v]) => v), now(), runId);
  }
  function deleteAsset(assetId, confirmUsed = false) {
    const result = transaction(() => {
      const a = asset(assetId);
      if (a.protected) throw new HttpError(409, '当前主形象来源受保护');
      if (a.locked) throw new HttpError(409, '请先明确解锁图片');
      const usages = db.prepare(`SELECT runs.id,runs.status FROM run_inputs JOIN runs ON runs.id=run_inputs.run_id WHERE asset_id=?`).all(assetId);
      if (usages.some(r => ['queued', 'running'].includes(r.status))) throw new HttpError(409, '图片仍被未结束运行引用，请等待运行结束');
      if (usages.length && !confirmUsed) throw new HttpError(409, '图片被历史运行引用，删除后保留来源标识', { requiresConfirmation: true, runs: usages.map(r => r.id) });
      db.prepare('UPDATE assets SET deleted_at=? WHERE id=?').run(now(), assetId);
      return db.prepare('SELECT file FROM assets WHERE id=?').get(assetId).file;
    });
    // A tombstone is committed before touching bytes; history never loses the asset identity.
    if (existsSync(join(media, result))) unlinkSync(join(media, result));
  }
  return { db, root, media, transaction, entity, asset, run, runView, assetView, stageImage, discardStage, registerStages,
    createRun, updateRun, deleteAsset,
    assetPath: (assetId) => { asset(assetId); return join(media, db.prepare('SELECT file FROM assets WHERE id=?').get(assetId).file); },
    assetBytes: (assetId) => readFileSync(join(media, db.prepare('SELECT file FROM assets WHERE id=?').get(assetId).file)) };
}
