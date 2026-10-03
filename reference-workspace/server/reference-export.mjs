// Owner: Sean — versioned, read-only Reference exports; no generation or editable-data writes.
import { Router } from 'express';
import { z } from 'zod';
import { createHash, randomUUID } from 'node:crypto';
import { existsSync, realpathSync, statSync, readFileSync } from 'node:fs';
import { relative, isAbsolute, sep } from 'node:path';
import { HttpError } from './store.mjs';
import { canonicalJSON,contentHash } from './content-hash.mjs';
import { createProjectWorkspace } from './project-workspace.mjs';
import { sceneSpatialView,isSceneEntity } from './scene-spatial.mjs';

export const assetRoles = ['setting', 'concept', 'main_appearance', 'three_view', 'voice', 'voice_emotion', 'voice_source', 'sound_effect'];
export const manifestRequestSchema = z.object({
  projectId: z.string().uuid().optional(),
  entityIds: z.array(z.string().uuid()).min(1).max(100),
  includeRelations: z.enum(['none', 'direct']).default('none'),
  assetRoles: z.array(z.enum(assetRoles)).min(1).max(assetRoles.length).default(['main_appearance', 'three_view', 'voice', 'sound_effect']),
  includeUnconfirmed: z.boolean().default(false),
  assetIds: z.array(z.string().uuid()).max(500).optional()
}).strict().superRefine((value, ctx) => {
  for (const key of ['entityIds', 'assetRoles', 'assetIds']) if (value[key] && new Set(value[key]).size !== value[key].length)
    ctx.addIssue({ code: 'custom', path: [key], message: '不允许重复值' });
});
export { canonicalJSON,contentHash } from './content-hash.mjs';
const fileHash = bytes => createHash('sha256').update(bytes).digest('hex');
// Only documented text is exposed; arbitrary context, metadata, execution and credentials stay private.
const text = value => typeof value === 'string' ? value
  .replace(/\b(?:sk|rk)-[A-Za-z0-9_-]{16,}\b/g, '[redacted]')
  .replace(/\b(api[_ -]?key|authorization|access[_ -]?token|password)\s*[:=]\s*[^\s,;]+/gi, '$1=[redacted]')
  .replace(/Bearer\s+[A-Za-z0-9._-]+/gi, 'Bearer [redacted]')
  .replace(/(?<![\w:/])(?:[A-Za-z]:[\\/]|\/)(?:[^\s<>"'\\/]+[\\/])+[^\s<>"']*/g, '[local-path]') : null;
const capabilities = {
  owner: 'Sean', entityManagement: false,
  entityText: { storage: 'optional explicit string fields in entities.context', fields: ['type', 'description', 'appearance', 'voiceDescription'], formalSchema: false },
  relations: { supported: false, directScope: 'both endpoints must be explicitly selected', reason: '当前 Reference 数据层没有关系表；不解析任意 context.relations' },
  soundEffects: { supported: false, reason: '当前没有音效素材模型或登记入口' },
  confirmation: { supported: true, source: 'appearance_versions / view_confirmations / voice_versions', lockedIsConfirmation: false,
    supportedRoles: ['main_appearance', 'three_view', 'voice'], unsupportedRoles: ['setting', 'concept', 'voice_emotion', 'voice_source', 'sound_effect'] },
  reviewStatus: { supported: false }, promptVersions: { supported: false, source: 'immutable run snapshot; use contentHash and sourceRunId' },
  assetContent: { range: true, stableIds: true, snapshotRetainsBytes: false, deletedContentReturns: 404 }
};
function validId(value, field) {
  if (!z.string().uuid().safeParse(value).success) throw new HttpError(400, '无效请求', { fieldErrors: { [field]: ['须为 UUID'] } });
}
function parseRequest(body) {
  const result = manifestRequestSchema.safeParse(body);
  if (!result.success) {
    const fieldErrors = {};
    for (const issue of result.error.issues) (fieldErrors[issue.path.join('.') || 'body'] ||= []).push(issue.message);
    throw new HttpError(400, '无效导出请求', { fieldErrors });
  }
  return result.data;
}
export function createReferenceExport(store) {
  store.db.exec(`CREATE TABLE IF NOT EXISTS reference_manifests (id TEXT PRIMARY KEY, payload TEXT NOT NULL, created_at TEXT NOT NULL);
    CREATE TRIGGER IF NOT EXISTS reference_manifests_no_update BEFORE UPDATE ON reference_manifests BEGIN SELECT RAISE(ABORT, 'immutable manifest'); END;
    CREATE TRIGGER IF NOT EXISTS reference_manifests_no_delete BEFORE DELETE ON reference_manifests BEGIN SELECT RAISE(ABORT, 'immutable manifest'); END;`);
  const hasTable = name => !!store.db.prepare("SELECT name FROM sqlite_master WHERE type='table' AND name=?").get(name);
  const projectService=hasTable('agent_projects')?createProjectWorkspace(store):null;
  function exportCapabilities() {
    const managed = hasTable('entity_relations');
    return { ...capabilities, projectContext:{supported:!!projectService,selection:'optional projectId',legacyStoryRelations:'unassigned; exported only without projectId',scope:'project settings plus explicitly selected entities; no graph expansion'}, sceneSpatial: {supported:hasTable('scene_spatial_versions'),schemaVersion:1,fixedFactsRequireConfirmation:true,stableIds:'entityId#id',dynamicState:'shooting script',automaticImageUnderstanding:false}, entityManagement: managed, flags: { supported: managed },
      entityText: { ...capabilities.entityText, formalSchema: managed, validatedFields: managed ? ['description','appearance','voiceDescription'] : [], typeEditing: false },
      derivation: { supported: hasTable('entity_derivations'), independentEntities: true, changeNotifications: false },
      relations: managed ? { supported: true, categories: ['setting','story'], directScope: 'both endpoints must be explicitly selected' } : capabilities.relations };
  }
  function exportedRelations(ids,projectId) {
    if (!hasTable('entity_relations')) return [];
    const placeholders=ids.map(()=>'?').join(',');
    const global=store.db.prepare(`SELECT * FROM entity_relations WHERE status='active' AND source_entity_id IN (${placeholders}) AND target_entity_id IN (${placeholders}) ORDER BY id`).all(...ids,...ids).map(row=>{
      const value={relationId:row.id,sourceEntityId:row.source_entity_id,targetEntityId:row.target_entity_id,category:row.category,type:text(row.type),description:text(row.description),status:row.status,targetRevision:row.target_revision,createdAt:row.created_at,updatedAt:row.updated_at};
      return {...value,contentHash:contentHash(value),sourceRevision:contentHash(value)};
    }).filter(r=>!projectId||r.category==='setting');
    const story=projectId?projectService.relations(projectId).filter(r=>ids.includes(r.sourceEntityId)&&ids.includes(r.targetEntityId)).map(r=>{const value={relationId:r.relationId,projectId,sourceEntityId:r.sourceEntityId,targetEntityId:r.targetEntityId,category:'story',type:text(r.type),description:text(r.description),status:r.status,createdAt:r.createdAt,updatedAt:r.updatedAt};return {...value,contentHash:contentHash(value),sourceRevision:r.sourceRevision};}):[];
    return [...global,...story].sort((a,b)=>a.relationId.localeCompare(b.relationId));
  }
  function file(assetId) {
    const asset = store.asset(assetId), path = store.assetPath(assetId);
    if (!existsSync(path)) throw new HttpError(404, '素材内容已删除或不存在');
    const actual = realpathSync(path), root = realpathSync(store.media), rel = relative(root, actual);
    if (!rel || rel === '..' || rel.startsWith(`..${sep}`) || isAbsolute(rel) || !statSync(actual).isFile())
      throw new HttpError(404, '素材内容不可用');
    return { asset, path: actual, size: statSync(actual).size };
  }
  function collect(entityId) {
    const entity = store.entity(entityId), visual = store.visualState(entityId), voices = store.voiceState(entityId);
    const records = new Map();
    function add(assetId, kind, record, isCurrent) {
      const asset = store.asset(assetId, true);
      if (asset.entityId !== entityId) throw new HttpError(409, '确认素材的实体归属不一致');
      const item = records.get(assetId) || { status: 'confirmed', isCurrent: false, records: [] };
      item.isCurrent ||= isCurrent;
      item.records.push({ kind, confirmationId: record.id, version: record.version, createdAt: record.createdAt }); records.set(assetId, item);
    }
    for (const a of visual.appearanceHistory) add(a.assetId, 'appearance', a, a.id === visual.appearance?.id);
    for (const v of visual.viewHistory) add(v.assetId, 'view', v, v.assetId === visual.view?.id && v.appearanceId === visual.appearance?.id);
    for (const v of voices.history) add(v.assetId, 'voice', v, v.id === voices.current?.id);
    const assets = store.db.prepare('SELECT * FROM assets WHERE entity_id=? AND deleted_at IS NULL ORDER BY id').all(entityId).map(store.assetView).map(a => {
      const confirmation = records.get(a.id);
      const role = a.kind === 'concept' && confirmation?.records.some(r => r.kind === 'appearance') ? 'main_appearance'
        : ({ setting: 'setting', concept: 'concept', multiview: 'three_view', voice: a.metadata.voiceRole === 'emotion' ? 'voice_emotion' : 'voice', 'voice-source': 'voice_source' })[a.kind];
      let size = null;
      try { size = file(a.id).size; } catch (error) { if (error.status !== 404) throw error; }
      const exported = { assetId: a.id, entityId, name: text(a.name), role: role || null, mediaType: a.mediaType, mime: a.mime, fileSize: size,
        contentHash: a.hash, contentUrl: `/api/reference/v1/assets/${a.id}/content`,
        createdAt: a.createdAt, description: text(a.description) || null, layout: typeof a.metadata.layout === 'string' ? text(a.metadata.layout) : null,
        width: a.width || null, height: a.height || null, durationSec: a.durationSec,
        confirmation: confirmation || (['three_view', 'voice'].includes(role) ? { status: 'unconfirmed', isCurrent: false, records: [] } : null),
        reviewStatus: null, sourceRunId: a.runId || a.metadata.inheritance?.sourceRunId || null,
        inheritance: a.metadata.inheritance ? Object.fromEntries(['sourceEntityId','sourceAssetId','sourceHash','sourceRevision','sourceVoiceId','sourceRunId','sourceRunEntityId'].filter(k=>a.metadata.inheritance[k]).map(k=>[k,a.metadata.inheritance[k]])) : null, available: size !== null };
      return { ...exported, sourceRevision: contentHash(exported) };
    });
    const prompts = [];
    for (const runId of [...new Set(assets.map(a => a.sourceRunId).filter(Boolean))].sort()) {
      const run = store.run(runId);
      if (run.entityId !== entityId) {
        for (const a of assets.filter(a=>a.sourceRunId===runId)) {
          const origin=a.inheritance?.sourceVoiceId && store.db.prepare('SELECT * FROM voice_versions WHERE id=?').get(a.inheritance.sourceVoiceId);
          if (!origin || origin.entity_id!==a.inheritance.sourceEntityId || origin.asset_id!==a.inheritance.sourceAssetId || origin.source_run_id!==runId)
            throw new HttpError(409, '提示词来源的实体归属不一致');
        }
      }
      const s = run.snapshot;
      const p = { promptId: `run:${runId}`, sourceRunId: runId, sourceEntityId: run.entityId, stage: s.stage || 'concept', version: null,
        text: text(s.prompt) || '', effectiveText: text(s.effectivePrompt || s.prompt) || '', purpose: text(s.purpose) || null,
        workflow: s.template ? { id: text(s.template.id), version: s.template.version ?? null, contentHash: s.template.hash ?? null } : null,
        samples: (s.samples || []).map(sample => ({ text: text(sample.text), direction: text(sample.instruction || sample.direction) })),
        createdAt: run.createdAt, assetIds: assets.filter(a => a.sourceRunId === runId).map(a => a.assetId) };
      p.contentHash = contentHash(p); p.sourceRevision = p.contentHash; prompts.push(p);
    }
    const voiceRun = voices.current ? store.run(voices.current.sourceRunId).snapshot : null;
    const fields = { type: text(entity.context.type), description: text(entity.context.description), appearance: text(entity.context.appearance),
      voiceDescription: text(entity.context.voiceDescription) || text(voiceRun?.prompt) || null };
    const fieldSources = Object.fromEntries(Object.entries(fields).map(([key, value]) => [key, value === null ? null : {
      source: key === 'voiceDescription' && !entity.context.voiceDescription ? 'current voice source run' : `entities.context.${key}`, contentHash: contentHash(value) }]));
    const derivation=hasTable('entity_derivations')?store.db.prepare('SELECT * FROM entity_derivations WHERE entity_id=?').get(entityId):null;
    const relationRevisions=hasTable('entity_relations')?store.db.prepare("SELECT * FROM entity_relations WHERE (source_entity_id=? OR target_entity_id=?) AND status='active' ORDER BY id").all(entityId,entityId).map(contentHash):[];
    const spatial=sceneSpatialView(store,entityId,{includeUnconfirmed:false,sanitize:text});
    const result = { sceneSpatial:spatial, flags: Array.isArray(entity.context.flags)?entity.context.flags.filter(f=>typeof f==='string').map(text):[],
      derivedFrom:derivation?{entityId:derivation.base_entity_id,sourceRevision:derivation.base_revision,description:text(derivation.description),createdAt:derivation.created_at}:null, relationRevisions, entityId: entity.id, name: text(entity.name), ...fields, createdAt: entity.createdAt, fieldSources,
      currentAppearance: visual.appearance ? { confirmationId: visual.appearance.id, version: visual.appearance.version, assetId: visual.appearance.assetId, contentHash: visual.appearance.assetHash } : null,
      currentVoice: voices.current ? { confirmationId: voices.current.id, version: voices.current.version, assetId: voices.current.assetId, contentHash: voices.current.assetHash } : null,
      missingFields: [...Object.entries(fields).filter(([, v]) => v === null).map(([k]) => k),...(isSceneEntity(entity)&&spatial.status==='missing'?['sceneSpatial']:[])], assets, prompts };
    result.contentHash = contentHash(result); result.sourceRevision = result.contentHash;
    return result;
  }
  function list() {
    return store.transaction(() => ({ format: 'reference-entity-list', schemaVersion: 1, owner: 'Sean', capabilities: exportCapabilities(),
      entities: store.db.prepare('SELECT id FROM entities ORDER BY created_at,id').all().map(({ id }) => {
        const e = collect(id);
        return { entityId: e.entityId, name: e.name, flags:e.flags, derivedFrom:e.derivedFrom, type: e.type, description: e.description?.slice(0, 240) ?? null,
          contentHash: e.contentHash, sourceRevision: e.sourceRevision, missingFields: e.missingFields };
      }) }));
  }
  function create(body) {
    const selection = parseRequest(body);
    return store.transaction(() => {
      let projectContext;
      if(selection.projectId){
        if(!projectService)throw new HttpError(404,'项目不存在');
        const p=projectService.project(selection.projectId);for(const e of selection.entityIds)projectService.member(p.id,e);
        const fields=Object.fromEntries(['name','brief','synopsis','worldRules','visualStyle','decisions'].map(k=>[k,text(p[k])]));
        projectContext={owner:'Sean',projectId:p.id,...fields,revision:p.revision,updatedAt:p.updatedAt,missingFields:['brief','synopsis','worldRules','visualStyle'].filter(k=>!p[k].trim())};
        projectContext.sourceRevision=contentHash(projectContext);
      }
      const all = selection.entityIds.map(collect), selectedAssets = selection.assetIds && new Set(selection.assetIds);
      if (selectedAssets) for (const assetId of selectedAssets) {
        const a = store.asset(assetId);
        if (!selection.entityIds.includes(a.entityId)) throw new HttpError(400, '无效素材选择', { fieldErrors: { assetIds: ['素材必须属于已选实体'] } });
      }
      const omissions = [];
      const entities = all.map(e => {
        const assets = e.assets.filter(a => {
          if (selectedAssets && !selectedAssets.has(a.assetId)) return false;
          let reason = !selection.assetRoles.includes(a.role) ? 'role_not_requested' : !a.available ? 'content_missing'
            : !selection.includeUnconfirmed && a.confirmation?.status !== 'confirmed' ? 'not_confirmed' : null;
          if (reason) { if (reason !== 'role_not_requested') omissions.push({ entityId: e.entityId, assetId: a.assetId, reason }); return false; }
          const { path, asset } = file(a.assetId);
          if (fileHash(readFileSync(path)) !== asset.hash) throw new HttpError(409, '素材内容与登记哈希不一致，请恢复原始素材');
          return true;
        });
        const projectRole=selection.projectId?projectService.role(selection.projectId,e.entityId):null;
        const scoped=projectRole?{projectRole:{projectId:selection.projectId,role:text(projectRole.role),plotNotes:text(projectRole.plotNotes),revision:projectRole.revision,sourceRevision:projectRole.sourceRevision,updatedAt:projectRole.updatedAt},sourceRevision:contentHash({entityRevision:e.sourceRevision,projectRoleRevision:projectRole.sourceRevision})}:{};
        return { ...e,...scoped, ...(projectRole?{contentHash:scoped.sourceRevision}:{}), sceneSpatial:sceneSpatialView(store,e.entityId,{includeUnconfirmed:selection.includeUnconfirmed,sanitize:text}), assets, prompts: e.prompts.filter(p => assets.some(a => a.sourceRunId === p.sourceRunId))
          .map(p => {
            const { contentHash: oldHash, sourceRevision, ...fields } = p;
            const value = { ...fields, assetIds: p.assetIds.filter(id => assets.some(a => a.assetId === id)) };
            return { ...value, contentHash: contentHash(value), sourceRevision };
          }) };
      });
      const caps=exportCapabilities();
      const payload = { format: 'reference-manifest', schemaVersion: 1, owner: 'Sean', capabilities:caps, selection, ...(projectContext?{projectContext}:{}), entities, relations: selection.includeRelations==='direct'?exportedRelations(selection.entityIds,selection.projectId):[],
        omissions, missingCapabilities: [...(!caps.relations.supported?['relations']:[]),'sound_effect', 'review_status', 'prompt_version'] };
      const snapshot = { ...payload, manifestId: randomUUID(), createdAt: new Date().toISOString(), contentHash: contentHash(payload) };
      const bytes = canonicalJSON(snapshot);
      store.db.prepare('INSERT INTO reference_manifests VALUES (?,?,?)').run(snapshot.manifestId, bytes, snapshot.createdAt);
      return JSON.parse(bytes);
    });
  }
  function get(manifestId) {
    validId(manifestId, 'manifestId');
    const row = store.db.prepare('SELECT payload FROM reference_manifests WHERE id=?').get(manifestId);
    if (!row) throw new HttpError(404, '导出快照不存在');
    return JSON.parse(row.payload);
  }
  return { list, create, get, file };
}
export function referenceExportRouter(store) {
  const router = Router(), service = createReferenceExport(store);
  router.use((req, _res, next) => {
    if (Object.keys(req.query).length) return next(new HttpError(400, '不支持查询参数', { fieldErrors: { query: ['此接口不接受路径或其他查询参数'] } }));
    next();
  });
  router.get('/entities', (_req, res) => res.json(service.list()));
  router.post('/manifests', (req, res) => res.status(201).json(service.create(req.body)));
  router.get('/manifests/:manifestId', (req, res) => {
    const value = service.get(req.params.manifestId);
    res.set('ETag', `"${value.contentHash}"`).set('Cache-Control', 'private, no-cache').json(value);
  });
  router.get('/assets/:assetId/content', (req, res) => {
    validId(req.params.assetId, 'assetId');
    const { asset, path } = service.file(req.params.assetId);
    if (fileHash(readFileSync(path)) !== asset.hash) throw new HttpError(409, '素材内容与登记哈希不一致');
    res.set('Content-Type', asset.mime).set('ETag', `"${asset.hash}"`).set('Cache-Control', 'private, no-cache');
    res.sendFile(path, { dotfiles: 'allow' });
  });
  return router;
}
