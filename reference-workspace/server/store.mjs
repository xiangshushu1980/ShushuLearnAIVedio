// Owner: Sean — durable business data, independent of ComfyUI output paths.
import { DatabaseSync } from 'node:sqlite';
import { randomUUID, createHash } from 'node:crypto';
import { mkdirSync, writeFileSync, unlinkSync, existsSync, readFileSync } from 'node:fs';
import { join, resolve } from 'node:path';
import sharp from 'sharp';
import { execFile } from 'node:child_process';
import { promisify } from 'node:util';

const executeFile = promisify(execFile);

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
  db.exec(`CREATE TABLE IF NOT EXISTS appearance_versions (
    id TEXT PRIMARY KEY, entity_id TEXT NOT NULL REFERENCES entities(id), asset_id TEXT NOT NULL REFERENCES assets(id),
    source_run_id TEXT, asset_hash TEXT NOT NULL, version INTEGER NOT NULL, created_at TEXT NOT NULL,
    UNIQUE(entity_id,version));
    CREATE TABLE IF NOT EXISTS entity_visual_state (
      entity_id TEXT PRIMARY KEY REFERENCES entities(id), appearance_id TEXT REFERENCES appearance_versions(id),
      view_asset_id TEXT REFERENCES assets(id), updated_at TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS multiview_drafts (
      entity_id TEXT PRIMARY KEY REFERENCES entities(id), value TEXT NOT NULL, updated_at TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS view_confirmations (
      id TEXT PRIMARY KEY, entity_id TEXT NOT NULL REFERENCES entities(id), appearance_id TEXT NOT NULL REFERENCES appearance_versions(id),
      asset_id TEXT NOT NULL REFERENCES assets(id), version INTEGER NOT NULL, created_at TEXT NOT NULL,
      UNIQUE(entity_id,version));
    CREATE TABLE IF NOT EXISTS voice_drafts (
      entity_id TEXT PRIMARY KEY REFERENCES entities(id), value TEXT NOT NULL, updated_at TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS voice_versions (
      id TEXT PRIMARY KEY, entity_id TEXT NOT NULL REFERENCES entities(id), asset_id TEXT NOT NULL REFERENCES assets(id),
      source_run_id TEXT NOT NULL, asset_hash TEXT NOT NULL, version INTEGER NOT NULL, created_at TEXT NOT NULL,
      UNIQUE(entity_id,version));
    CREATE TABLE IF NOT EXISTS entity_voice_state (
      entity_id TEXT PRIMARY KEY REFERENCES entities(id), voice_id TEXT NOT NULL REFERENCES voice_versions(id), updated_at TEXT NOT NULL);`);
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
    metadata: JSON.parse(row.metadata), mediaType: row.mime.startsWith('audio/') ? 'audio' : 'image',
    durationSec: JSON.parse(row.metadata).durationSec ?? null, runId: row.run_id, createdAt: row.created_at, deletedAt: row.deleted_at,
    url: row.deleted_at ? null : `/api/assets/${row.id}/content` });
  const asset = (assetId, includeDeleted = false) => {
    const row = db.prepare('SELECT * FROM assets WHERE id=?').get(assetId);
    if (!row || (row.deleted_at && !includeDeleted)) throw new HttpError(404, '来源素材已删除或不存在');
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
  async function stageAudio(buffer, name, entityId, kind, runId, metadata = {}) {
    entity(entityId);
    if (buffer.length > 25 * 1024 * 1024) throw new HttpError(413, '音频不得超过 25 MB');
    const wave = buffer.toString('ascii', 0, 4) === 'RIFF' && buffer.toString('ascii', 8, 12) === 'WAVE';
    const flac = buffer.toString('ascii', 0, 4) === 'fLaC';
    const mp3 = buffer.toString('ascii', 0, 3) === 'ID3' || (buffer[0] === 255 && (buffer[1] & 224) === 224);
    if (!wave && !flac && !mp3) throw new HttpError(400, '请选择 WAV、FLAC 或 MP3 音频');
    const assetId = id(), file = `${assetId}.wav`, input = join(media, `${assetId}.upload`), output = join(media, file);
    writeFileSync(input, buffer, { flag: 'wx' });
    try {
      const probe = await executeFile('ffprobe', ['-v', 'error', '-protocol_whitelist', 'file,pipe', '-show_entries', 'format=duration', '-of', 'json', input], { timeout: 30_000 });
      const duration = Number(JSON.parse(probe.stdout).format?.duration);
      const maxDuration = kind === 'voice-source' ? 30 : 60;
      if (!Number.isFinite(duration) || duration <= 0 || duration > maxDuration)
        throw new HttpError(400, `音频须为 0–${maxDuration} 秒的有效片段`);
      await executeFile('ffmpeg', ['-v', 'error', '-nostdin', '-protocol_whitelist', 'file,pipe', '-i', input,
        '-vn', '-ac', '1', '-ar', '24000', '-c:a', 'pcm_s16le', '-t', String(maxDuration + 1), output], { timeout: 30_000 });
      const bytes = readFileSync(output);
      return { assetId, file, entityId, kind, name: name.slice(0, 200), mime: 'audio/wav',
        hash: createHash('sha256').update(bytes).digest('hex'), width: 0, height: 0, runId: runId || null,
        metadata: { ...metadata, owner: 'Sean', durationSec: duration, sampleRate: 24000, channels: 1,
          originalHash: createHash('sha256').update(buffer).digest('hex') }, createdAt: now() };
    } catch (error) {
      if (existsSync(output)) unlinkSync(output);
      if (error instanceof HttpError) throw error;
      throw new HttpError(400, '音频无法解码，请提供有效的 WAV、FLAC 或 MP3');
    } finally { if (existsSync(input)) unlinkSync(input); }
  }
  function registerStages(stages) {
    const insert = db.prepare(`INSERT INTO assets (id,entity_id,kind,name,file,mime,hash,width,height,locked,metadata,run_id,created_at)
      VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)`);
    for (const s of stages) insert.run(s.assetId, s.entityId, s.kind, s.name, s.file, s.mime, s.hash, s.width, s.height,
      ['concept', 'multiview', 'voice'].includes(s.kind) ? 1 : 0, JSON.stringify(s.metadata), s.runId, s.createdAt);
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
      if(db.prepare("SELECT name FROM sqlite_master WHERE type='table' AND name='scene_image_versions'").get()){
        const set=db.prepare('SELECT v.document,v.confirmation FROM entity_scene_image_state s JOIN scene_image_versions v ON v.id=s.version_id WHERE s.entity_id=?').get(a.entityId);
        if(set?.confirmation&&JSON.parse(set.document).images.some(i=>i.assetId===assetId))throw new HttpError(409,'素材属于当前已确认场景图片组，请先调整并保存图片组');
      }
      if (a.protected) throw new HttpError(409, '当前定稿来源受保护');
      if (a.locked) throw new HttpError(409, '请先明确解锁素材');
      const usages = db.prepare(`SELECT runs.id,runs.status FROM run_inputs JOIN runs ON runs.id=run_inputs.run_id WHERE asset_id=?`).all(assetId);
      if (usages.some(r => ['queued', 'running'].includes(r.status))) throw new HttpError(409, '素材仍被未结束运行引用，请等待运行结束');
      if (usages.length && !confirmUsed) throw new HttpError(409, '素材被历史运行引用，删除后保留来源标识', { requiresConfirmation: true, runs: usages.map(r => r.id) });
      db.prepare('UPDATE assets SET deleted_at=? WHERE id=?').run(now(), assetId);
      return db.prepare('SELECT file FROM assets WHERE id=?').get(assetId).file;
    });
    // A tombstone is committed before touching bytes; history never loses the asset identity.
    if (existsSync(join(media, result))) unlinkSync(join(media, result));
  }
  function appearanceView(row) {
    return row && { id: row.id, entityId: row.entity_id, assetId: row.asset_id, sourceRunId: row.source_run_id,
      assetHash: row.asset_hash, version: row.version, createdAt: row.created_at, asset: asset(row.asset_id, true) };
  }
  function visualState(entityId) {
    entity(entityId);
    const state = db.prepare('SELECT * FROM entity_visual_state WHERE entity_id=?').get(entityId);
    const versions = db.prepare('SELECT * FROM appearance_versions WHERE entity_id=? ORDER BY version DESC').all(entityId).map(appearanceView);
    const confirmations = db.prepare('SELECT * FROM view_confirmations WHERE entity_id=? ORDER BY version DESC').all(entityId)
      .map(row => ({ id: row.id, assetId: row.asset_id, appearanceId: row.appearance_id, version: row.version, createdAt: row.created_at }));
    return { appearance: versions.find(v => v.id === state?.appearance_id) || null, appearanceHistory: versions, viewHistory: confirmations,
      view: state?.view_asset_id ? asset(state.view_asset_id, true) : null, updatedAt: state?.updated_at || null };
  }
  function confirmAppearance(entityId, assetId, expectedAppearanceId) {
    return transaction(() => {
      const current = visualState(entityId), candidate = asset(assetId);
      if ((current.appearance?.id || null) !== expectedAppearanceId) throw new HttpError(409, '主形象已在其他页面改变，请刷新后选择');
      if (candidate.entityId !== entityId || candidate.kind !== 'concept') throw new HttpError(400, '请从当前实体的概念图结果中选择');
      if (candidate.runId && run(candidate.runId).status !== 'succeeded') throw new HttpError(409, '请选择已完成生成的概念图');
      if (current.appearance?.assetId === assetId) return current;
      const versionId = id(), timestamp = now();
      for (const old of [current.appearance?.asset, current.view].filter(Boolean))
        db.prepare('UPDATE assets SET protected=0,locked=1 WHERE id=?').run(old.id);
      db.prepare('INSERT INTO appearance_versions VALUES (?,?,?,?,?,?,?)').run(versionId, entityId, assetId, candidate.runId,
        candidate.hash, (current.appearanceHistory[0]?.version || 0) + 1, timestamp);
      db.prepare('UPDATE assets SET protected=1,locked=1,ever_confirmed=1 WHERE id=?').run(assetId);
      db.prepare(`INSERT INTO entity_visual_state VALUES (?,?,NULL,?) ON CONFLICT(entity_id)
        DO UPDATE SET appearance_id=excluded.appearance_id,view_asset_id=NULL,updated_at=excluded.updated_at`).run(entityId, versionId, timestamp);
      return visualState(entityId);
    });
  }
  function confirmView(entityId, assetId, expectedAppearanceId) {
    return transaction(() => {
      const current = visualState(entityId), candidate = asset(assetId);
      if (!current.appearance || current.appearance.id !== expectedAppearanceId) throw new HttpError(409, '主形象已改变，请刷新后核对视图来源');
      if (candidate.entityId !== entityId || candidate.kind !== 'multiview' || !candidate.runId) throw new HttpError(400, '请选择当前实体的多视图结果');
      const source = run(candidate.runId);
      if (source.status !== 'succeeded' || source.snapshot.appearance?.id !== current.appearance.id)
        throw new HttpError(409, '这张视图来自其他主形象版本，请为当前主形象重新生成或选择对应结果');
      if (current.view?.id === assetId) return current;
      if (current.view && current.view.id !== assetId) db.prepare('UPDATE assets SET protected=0,locked=1 WHERE id=?').run(current.view.id);
      db.prepare('UPDATE assets SET protected=1,locked=1,ever_confirmed=1 WHERE id=?').run(assetId);
      db.prepare('INSERT INTO view_confirmations VALUES (?,?,?,?,?,?)').run(id(), entityId, current.appearance.id, assetId,
        (current.viewHistory[0]?.version || 0) + 1, now());
      db.prepare('UPDATE entity_visual_state SET view_asset_id=?,updated_at=? WHERE entity_id=?').run(assetId, now(), entityId);
      return visualState(entityId);
    });
  }
  function voiceState(entityId) {
    entity(entityId);
    const state = db.prepare('SELECT * FROM entity_voice_state WHERE entity_id=?').get(entityId);
    const history = db.prepare('SELECT * FROM voice_versions WHERE entity_id=? ORDER BY version DESC').all(entityId)
      .map(row => ({ id: row.id, assetId: row.asset_id, sourceRunId: row.source_run_id, assetHash: row.asset_hash,
        version: row.version, createdAt: row.created_at, asset: asset(row.asset_id, true) }));
    return { current: history.find(version => version.id === state?.voice_id) || null, history, updatedAt: state?.updated_at || null };
  }
  function confirmVoice(entityId, assetId, expectedVoiceId) {
    return transaction(() => {
      const state = voiceState(entityId), candidate = asset(assetId);
      if ((state.current?.id || null) !== expectedVoiceId) throw new HttpError(409, '当前声音已在其他页面改变，请刷新后选择');
      if (candidate.entityId !== entityId || candidate.kind !== 'voice' || !candidate.runId || run(candidate.runId).status !== 'succeeded')
        throw new HttpError(400, '请选择当前实体已完成生成的声音候选');
      if (candidate.metadata.voiceRole === 'emotion') throw new HttpError(400, '情绪样音展示基础音色，不能替换人物基础声音');
      if (state.current?.assetId === candidate.id) return state;
      if (state.current) db.prepare('UPDATE assets SET protected=0,locked=1 WHERE id=?').run(state.current.assetId);
      const versionId = id(), timestamp = now();
      db.prepare('INSERT INTO voice_versions VALUES (?,?,?,?,?,?,?)').run(versionId, entityId, candidate.id,
        candidate.runId, candidate.hash, (state.history[0]?.version || 0) + 1, timestamp);
      db.prepare('UPDATE assets SET protected=1,locked=1,ever_confirmed=1 WHERE id=?').run(candidate.id);
      db.prepare(`INSERT INTO entity_voice_state VALUES (?,?,?) ON CONFLICT(entity_id)
        DO UPDATE SET voice_id=excluded.voice_id,updated_at=excluded.updated_at`).run(entityId, versionId, timestamp);
      return voiceState(entityId);
    });
  }
  return { db, root, media, transaction, entity, asset, run, runView, assetView, stageImage, stageAudio, discardStage, registerStages,
    createRun, updateRun, deleteAsset, visualState, confirmAppearance, confirmView,
    voiceState, confirmVoice,
    assetPath: (assetId) => { asset(assetId); return join(media, db.prepare('SELECT file FROM assets WHERE id=?').get(assetId).file); },
    assetBytes: (assetId) => readFileSync(join(media, db.prepare('SELECT file FROM assets WHERE id=?').get(assetId).file)) };
}
