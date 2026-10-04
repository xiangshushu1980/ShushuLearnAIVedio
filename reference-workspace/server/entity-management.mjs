// Owner: Sean — entity profiles, flags, relationships and independent derivation snapshots.
import { Router } from 'express';
import { z } from 'zod';
import { writeFileSync, unlinkSync, existsSync } from 'node:fs';
import { join } from 'node:path';
import { createHash } from 'node:crypto';
import { id, now, HttpError } from './store.mjs';
import { createSceneImages, sceneImageSetView } from './scene-images.mjs';
import { catalog } from './catalog.mjs';
import { contentHash } from './content-hash.mjs';
import { createSceneSpatial, sceneSpatialView } from './scene-spatial.mjs';

const flags = z.array(z.string().trim().min(1).max(40).refine(v=>!v.includes(','),'flag不能包含逗号')).max(30).refine(a => new Set(a).size === a.length, 'flag不能重复');
const profile = z.object({ name: z.string().trim().min(1).max(100), flags: flags.default([]), description: z.string().max(8000).default(''),
  appearance: z.string().max(8000).default(''), voiceDescription: z.string().max(4000).default('') }).strict();
const relationInput = z.object({ targetEntityId: z.string().uuid(), category: z.enum(['setting', 'story']), type: z.string().trim().min(1).max(60), description: z.string().max(4000).default('') }).strict();
function parse(schema, body) {
  const r = schema.safeParse(body);
  if (!r.success) throw new HttpError(400, '输入格式不正确', { fieldErrors: r.error.flatten().fieldErrors });
  return r.data;
}
export function createEntityManagement(store) {
  const spatial=createSceneSpatial(store),sceneImages=createSceneImages(store);
  store.db.exec(`CREATE TABLE IF NOT EXISTS entity_relations (
    id TEXT PRIMARY KEY, source_entity_id TEXT NOT NULL REFERENCES entities(id), target_entity_id TEXT NOT NULL REFERENCES entities(id),
    category TEXT NOT NULL CHECK(category IN ('setting','story')), type TEXT NOT NULL, description TEXT NOT NULL DEFAULT '',
    status TEXT NOT NULL CHECK(status IN ('active','removed')), target_revision TEXT NOT NULL, created_at TEXT NOT NULL, updated_at TEXT NOT NULL);
    CREATE INDEX IF NOT EXISTS relation_source ON entity_relations(source_entity_id,status);
    CREATE INDEX IF NOT EXISTS relation_target ON entity_relations(target_entity_id,status);
    CREATE TABLE IF NOT EXISTS entity_derivations (
    entity_id TEXT PRIMARY KEY REFERENCES entities(id), base_entity_id TEXT NOT NULL REFERENCES entities(id), base_revision TEXT NOT NULL,
    options TEXT NOT NULL, description TEXT NOT NULL, created_at TEXT NOT NULL);`);
  function revision(entityId) {
    const e = store.entity(entityId), v = store.visualState(entityId), a = store.voiceState(entityId);
    return contentHash({ id: e.id, name: e.name, context: e.context, appearance: v.appearance?.assetHash || null,
      view: v.view?.hash || null, voice: a.current?.assetHash || null,
      spatial: sceneSpatialView(store,entityId,{includeUnconfirmed:false}).sourceRevision,
      sceneImages: sceneImageSetView(store,entityId).sourceRevision,
      relations: store.db.prepare("SELECT * FROM entity_relations WHERE source_entity_id=? AND status='active' ORDER BY id").all(entityId) });
  }
  const relationView = row => ({ relationId: row.id, sourceEntityId: row.source_entity_id, targetEntityId: row.target_entity_id,
    category: row.category, type: row.type, description: row.description, status: row.status, targetRevision: row.target_revision,
    createdAt: row.created_at, updatedAt: row.updated_at, sourceName: store.entity(row.source_entity_id).name, targetName: store.entity(row.target_entity_id).name });
  function relations(entityId) {
    store.entity(entityId);
    return store.db.prepare("SELECT * FROM entity_relations WHERE (source_entity_id=? OR target_entity_id=?) AND status='active' ORDER BY created_at,id").all(entityId, entityId).map(relationView);
  }
  function detail(entityId) {
    const e = store.entity(entityId), visualState = store.visualState(entityId), voiceState = store.voiceState(entityId);
    const derivation = store.db.prepare('SELECT * FROM entity_derivations WHERE entity_id=?').get(entityId);
    return { entity: e, profile: { name: e.name, flags: Array.isArray(e.context.flags) ? e.context.flags.filter(f=>typeof f==='string') : [], description: typeof e.context.description==='string'?e.context.description:'',
      appearance: typeof e.context.appearance==='string'?e.context.appearance:'', voiceDescription: typeof e.context.voiceDescription==='string'&&e.context.voiceDescription ? e.context.voiceDescription : (voiceState.current ? store.run(voiceState.current.sourceRunId).snapshot.prompt || '' : '') },
      revision: revision(entityId), visualState, voiceState, sceneSpatial: sceneSpatialView(store,entityId), sceneImages:sceneImageSetView(store,entityId,{includeUnconfirmed:true}), relations: relations(entityId),
      derivedFrom: derivation ? { entityId: derivation.base_entity_id, name: store.entity(derivation.base_entity_id).name, sourceRevision: derivation.base_revision,
        description: derivation.description, options: JSON.parse(derivation.options), createdAt: derivation.created_at } : null,
      descendants: store.db.prepare('SELECT entity_id FROM entity_derivations WHERE base_entity_id=? ORDER BY created_at').all(entityId).map(r => ({ entityId: r.entity_id, name: store.entity(r.entity_id).name })) };
  }
  function list(query = {}) {
    const q = typeof query.q === 'string' ? query.q.toLocaleLowerCase() : '';
    const selected = typeof query.flags === 'string' ? query.flags.split(',').filter(Boolean) : [];
    const entries = store.db.prepare('SELECT id FROM entities ORDER BY created_at DESC,id').all().map(({ id }) => {
      const e = store.entity(id), v = store.visualState(id), a = store.voiceState(id), origin = store.db.prepare('SELECT base_entity_id FROM entity_derivations WHERE entity_id=?').get(id);
      return { id, name: e.name, flags: Array.isArray(e.context.flags) ? e.context.flags.filter(f=>typeof f==='string') : [], description: typeof e.context.description==='string'?e.context.description:'',
        thumbnail: v.appearance?.asset.url || null, hasView: !!v.view, hasVoice: !!a.current, baseEntityId: origin?.base_entity_id || null, createdAt: e.createdAt };
    });
    const allFlags = [...new Set(entries.flatMap(e => e.flags).concat(['人物','物品','技能','场景']))].sort().map(flag => ({ flag, count: entries.filter(e => e.flags.includes(flag)).length }));
    return { flags: allFlags, entities: entries.filter(e => (!q || (e.name+' '+e.description+' '+e.flags.join(' ')).toLocaleLowerCase().includes(q))
      && (!selected.length || (query.match === 'any' ? selected.some(f => e.flags.includes(f)) : selected.every(f => e.flags.includes(f))))) };
  }
  function create(body, { inTransaction = false } = {}) {
    const input = parse(profile, body), entityId = id();
    const write = () => store.db.prepare('INSERT INTO entities VALUES (?,?,?,?)').run(entityId, input.name, JSON.stringify({ owner: 'Sean', ...Object.fromEntries(Object.entries(input).filter(([k]) => k !== 'name')) }), now());
    if (inTransaction) write(); else store.transaction(write);
    return detail(entityId);
  }
  function update(entityId, body, {inTransaction=false,partial=false}={}) {
    const patch=z.object({name:profile.shape.name.optional(),description:z.string().max(8000).optional(),appearance:z.string().max(8000).optional(),voiceDescription:z.string().max(4000).optional(),expectedRevision:z.string()}).strict();
    const { expectedRevision, ...input } = parse(partial?patch:profile.extend({ expectedRevision: z.string() }).strict(), body);
    const write=() => {
      const e = store.entity(entityId);
      if (revision(entityId) !== expectedRevision) throw new HttpError(409, '实体资料已变化，请重新载入后编辑');
      const { name, ...fields } = input;
      store.db.prepare('UPDATE entities SET name=?,context=? WHERE id=?').run(name===undefined?e.name:name, JSON.stringify({ ...e.context, ...fields }), entityId);
    };
    if(inTransaction)write();else store.transaction(write);
    return detail(entityId);
  }
  function addRelation(entityId, body) {
    const input = parse(relationInput, body);store.entity(entityId);store.entity(input.targetEntityId);
    if (entityId === input.targetEntityId) throw new HttpError(400, '不能建立自身关系');
    if (input.type === '派生自') throw new HttpError(400, '派生关系由创建派生实体建立');
    const relationId = id(), timestamp = now();
    store.transaction(() => {
      if (store.db.prepare("SELECT id FROM entity_relations WHERE source_entity_id=? AND target_entity_id=? AND category=? AND type=? AND status='active'").get(entityId,input.targetEntityId,input.category,input.type)) throw new HttpError(409,'相同关系已存在');
      store.db.prepare('INSERT INTO entity_relations VALUES (?,?,?,?,?,?,?,?,?,?)').run(relationId,entityId,input.targetEntityId,input.category,input.type,input.description,'active',revision(input.targetEntityId),timestamp,timestamp);
    });
    return detail(entityId);
  }
  function changeRelation(entityId, relationId, body, removing = false, {inTransaction=false}={}) {
    const row = store.db.prepare("SELECT * FROM entity_relations WHERE id=? AND source_entity_id=? AND status='active'").get(relationId,entityId);
    if (!row) throw new HttpError(404, '关系不存在或请从来源实体编辑');
    if (row.type === '派生自') throw new HttpError(400, '派生来源不可修改或解除');
    const timestamp = new Date(Math.max(Date.now(), Date.parse(row.updated_at)+1)).toISOString();
    const value = parse(removing ? z.object({ expectedUpdatedAt: z.string() }).strict() : relationInput.extend({ expectedUpdatedAt: z.string() }).strict(), body);
    const write=() => {
      if (store.db.prepare('SELECT updated_at FROM entity_relations WHERE id=?').get(relationId)?.updated_at !== value.expectedUpdatedAt) throw new HttpError(409,'关系已改变，请刷新');
      if (removing) store.db.prepare("UPDATE entity_relations SET status='removed',updated_at=? WHERE id=?").run(timestamp,relationId);
      else {
        store.entity(value.targetEntityId);
        if (value.targetEntityId === entityId || value.type === '派生自') throw new HttpError(400,'无效关系');
        if (store.db.prepare("SELECT id FROM entity_relations WHERE source_entity_id=? AND target_entity_id=? AND category=? AND type=? AND status='active' AND id<>?").get(entityId,value.targetEntityId,value.category,value.type,relationId)) throw new HttpError(409,'相同关系已存在');
        store.db.prepare('UPDATE entity_relations SET target_entity_id=?,category=?,type=?,description=?,target_revision=?,updated_at=? WHERE id=?').run(value.targetEntityId,value.category,value.type,value.description,revision(value.targetEntityId),timestamp,relationId);
      }
    };if(inTransaction)write();else store.transaction(write);return detail(entityId);
  }
  function derive(baseId, body, { onCreated = () => {} } = {}) {
    const input = parse(profile.extend({ copyProfile: z.boolean().default(true), copyReference: z.boolean().default(true), reuseVoice: z.boolean().default(false),
      copySettingRelations: z.boolean().default(true), changes: z.string().max(8000).default(''), expectedBaseRevision: z.string() }).strict(), body);
    const base = detail(baseId), entityId = id(), timestamp = now(), stages = [];
    if (base.revision !== input.expectedBaseRevision) throw new HttpError(409,'基础实体已变化，请刷新后派生');
    if (input.reuseVoice && !base.voiceState.current) throw new HttpError(400,'基础实体没有已选声音，请关闭沿用声音');
    function copy(asset, kind, inheritance) {
      const bytes = store.assetBytes(asset.id);
      if (createHash('sha256').update(bytes).digest('hex') !== asset.hash) throw new HttpError(409,'来源素材内容已变化');
      const assetId = id(), ext = { 'image/png':'png','image/jpeg':'jpg','image/webp':'webp','audio/wav':'wav' }[asset.mime];
      if (!ext) throw new HttpError(400,'来源素材格式不支持复制');
      const file = `${assetId}.${ext}`;
      writeFileSync(join(store.media,file),bytes,{flag:'wx'});
      const stage = { assetId,file,entityId,kind,name:asset.name,mime:asset.mime,hash:asset.hash,width:asset.width,height:asset.height,runId:null,createdAt:timestamp,
        metadata:{owner:'Sean',source:'entity-inheritance',inheritance,...(kind==='voice'?{voiceRole:'base',sampleText:asset.metadata.sampleText||'',sampleLabel:'沿用基础声音',durationSec:asset.durationSec,sampleRate:24000,channels:1}:{})} };
      stages.push(stage);return stage;
    }
    try {
      store.transaction(() => {
        const fields = input.copyProfile ? { description:base.profile.description,appearance:base.profile.appearance,voiceDescription:base.profile.voiceDescription } : {};
        const context={...fields,owner:'Sean',flags:input.flags,description:input.description || (input.copyProfile?base.profile.description:''),
          appearance:input.appearance || (input.copyProfile?base.profile.appearance:''),voiceDescription:input.voiceDescription || (input.reuseVoice?base.profile.voiceDescription:'')};
        store.db.prepare('INSERT INTO entities VALUES (?,?,?,?)').run(entityId,input.name,JSON.stringify(context),timestamp);
        const options={copyProfile:input.copyProfile,copyReference:input.copyReference,reuseVoice:input.reuseVoice,copySettingRelations:input.copySettingRelations};
        store.db.prepare('INSERT INTO entity_derivations VALUES (?,?,?,?,?,?)').run(entityId,baseId,base.revision,JSON.stringify(options),input.changes,timestamp);
        store.db.prepare('INSERT INTO entity_relations VALUES (?,?,?,?,?,?,?,?,?,?)').run(id(),entityId,baseId,'setting','派生自',input.changes,'active',base.revision,timestamp,timestamp);
        let referenceStage;
        if(input.copyReference&&base.visualState.appearance) referenceStage=copy(base.visualState.appearance.asset,'setting',{sourceEntityId:baseId,sourceAssetId:base.visualState.appearance.assetId,sourceHash:base.visualState.appearance.assetHash,sourceRevision:base.revision});
        let voiceStage;
        if(input.reuseVoice) {
          const v=base.voiceState.current, originalRun=store.run(v.sourceRunId);
          voiceStage=copy(v.asset,'voice',{sourceEntityId:baseId,sourceAssetId:v.assetId,sourceHash:v.assetHash,sourceRevision:base.revision,sourceVoiceId:v.id,sourceRunId:v.sourceRunId,sourceRunEntityId:originalRun.entityId});
        }
        store.registerStages(stages);
        const model=catalog.models.find(m=>m.id==='qwen-image-2.1');
        if(model) {
          const draft={modelId:model.id,styleId:'original',purpose:'派生实体形象创作',prompt:input.changes?(referenceStage?'以 Image 1 作为角色身份参考，按以下变化要求创作新的形象。\n':'')+input.changes:'',references:referenceStage?[referenceStage.assetId]:[],parameters:Object.fromEntries(Object.entries(model.fields).map(([key,value])=>[key,value.default]))};
          store.db.prepare('INSERT INTO drafts VALUES (?,?,?)').run(entityId,JSON.stringify(draft),timestamp);
        }
        if(input.copyProfile) spatial.cloneDraft(baseId,entityId,new Map(referenceStage?[[base.visualState.appearance.assetId,referenceStage.assetId]]:[]));
        if(voiceStage) {
          const voiceId=id();store.db.prepare('INSERT INTO voice_versions VALUES (?,?,?,?,?,?,?)').run(voiceId,entityId,voiceStage.assetId,base.voiceState.current.sourceRunId,voiceStage.hash,1,timestamp);
          store.db.prepare('INSERT INTO entity_voice_state VALUES (?,?,?)').run(entityId,voiceId,timestamp);
          store.db.prepare('UPDATE assets SET protected=1,locked=1,ever_confirmed=1 WHERE id=?').run(voiceStage.assetId);
        }
        if(input.copySettingRelations) for(const r of base.relations.filter(r=>r.sourceEntityId===baseId&&r.category==='setting'&&r.type!=='派生自')) {
          store.db.prepare('INSERT INTO entity_relations VALUES (?,?,?,?,?,?,?,?,?,?)').run(id(),entityId,r.targetEntityId,r.category,r.type,r.description,'active',revision(r.targetEntityId),timestamp,timestamp);
        }
        onCreated(entityId);
      });
    } catch(error) { for(const stage of stages) if(existsSync(join(store.media,stage.file))) unlinkSync(join(store.media,stage.file));throw error; }
    return detail(entityId);
  }
  function importReference(entityId, body) {
    const input=parse(z.object({sourceEntityId:z.string().uuid(),assetId:z.string().uuid(),category:z.enum(['setting','story']).default('setting'),relationType:z.string().trim().min(1).max(60).nullable().default(null),description:z.string().max(4000).default('')}).strict(),body);
    store.entity(entityId);store.entity(input.sourceEntityId);
    if(entityId===input.sourceEntityId)throw new HttpError(400,'请在本实体素材中选择');
    const asset=store.asset(input.assetId);
    if(asset.entityId!==input.sourceEntityId||asset.mediaType!=='image')throw new HttpError(400,'请选择来源实体的图片');
    if(input.relationType==='派生自')throw new HttpError(400,'请使用创建派生实体');
    const bytes=store.assetBytes(asset.id), hash=createHash('sha256').update(bytes).digest('hex');if(hash!==asset.hash)throw new HttpError(409,'来源图片已变化');
    const assetId=id(), ext={'image/png':'png','image/jpeg':'jpg','image/webp':'webp'}[asset.mime];if(!ext)throw new HttpError(400,'图片格式不可用');
    const file=`${assetId}.${ext}`, timestamp=now(), sourceRevision=revision(input.sourceEntityId);
    writeFileSync(join(store.media,file),bytes,{flag:'wx'});
    try {
      const imported=store.transaction(()=>{
        const [result]=store.registerStages([{assetId,file,entityId,kind:'setting',name:asset.name,mime:asset.mime,hash,width:asset.width,height:asset.height,runId:null,createdAt:timestamp,
          metadata:{owner:'Sean',source:'entity-reference',inheritance:{sourceEntityId:input.sourceEntityId,sourceAssetId:asset.id,sourceHash:asset.hash,sourceRevision}}}]);
        if(input.relationType&&!store.db.prepare("SELECT id FROM entity_relations WHERE source_entity_id=? AND target_entity_id=? AND category=? AND type=? AND status='active'").get(entityId,input.sourceEntityId,input.category,input.relationType))
          store.db.prepare('INSERT INTO entity_relations VALUES (?,?,?,?,?,?,?,?,?,?)').run(id(),entityId,input.sourceEntityId,input.category,input.relationType,input.description,'active',sourceRevision,timestamp,timestamp);
        return result;
      });return imported;
    } catch(error) {if(existsSync(join(store.media,file)))unlinkSync(join(store.media,file));throw error;}
  }
  return {list,detail,create,update,addRelation,changeRelation,derive,importReference,spatial,sceneImages};
}
export function entityManagementRouter(store) {
  const service=createEntityManagement(store),r=Router();
  r.param('id',(req,_res,next,value)=>{if(!z.string().uuid().safeParse(value).success)return next(new HttpError(400,'无效实体ID',{fieldErrors:{id:['须为UUID']}}));next();});
  r.param('relationId',(req,_res,next,value)=>{if(!z.string().uuid().safeParse(value).success)return next(new HttpError(400,'无效关系ID',{fieldErrors:{relationId:['须为UUID']}}));next();});
  r.get('/entities',(req,res)=>res.json(service.list(req.query)));
  r.post('/entities',(req,res)=>res.status(201).json(service.create(req.body)));
  r.get('/entities/:id/scene-images',(req,res)=>res.json(service.sceneImages.get(req.params.id)));
  r.put('/entities/:id/scene-images',(req,res)=>res.json(service.sceneImages.save(req.params.id,req.body)));
  r.post('/entities/:id/scene-images/confirm',(req,res)=>res.json(service.sceneImages.confirm(req.params.id,req.body)));
  r.get('/entities/:id/spatial',(req,res)=>res.json(service.spatial.get(req.params.id)));
  r.put('/entities/:id/spatial',(req,res)=>res.json(service.spatial.save(req.params.id,req.body)));
  r.post('/entities/:id/spatial/confirm',(req,res)=>res.json(service.spatial.confirm(req.params.id,req.body)));
  r.get('/entities/:id',(req,res)=>res.json(service.detail(req.params.id)));
  r.patch('/entities/:id',(req,res)=>res.json(service.update(req.params.id,req.body)));
  r.post('/entities/:id/derive',(req,res)=>res.status(201).json(service.derive(req.params.id,req.body)));
  r.post('/entities/:id/relations',(req,res)=>res.status(201).json(service.addRelation(req.params.id,req.body)));
  r.patch('/entities/:id/relations/:relationId',(req,res)=>res.json(service.changeRelation(req.params.id,req.params.relationId,req.body)));
  r.delete('/entities/:id/relations/:relationId',(req,res)=>res.json(service.changeRelation(req.params.id,req.params.relationId,req.body,true)));
  r.post('/entities/:id/references',(req,res)=>res.status(201).json(service.importReference(req.params.id,req.body)));
  return r;
}
