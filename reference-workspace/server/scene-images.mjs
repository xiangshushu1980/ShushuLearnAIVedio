// Owner: Sean — versioned scene reference sets; human confirmation remains separate from Agent review.
import { z } from 'zod';
import { createHash } from 'node:crypto';
import { id, now, HttpError } from './store.mjs';
import { canonicalJSON, contentHash } from './content-hash.mjs';
import { isSceneEntity, sceneSpatialView } from './scene-spatial.mjs';

export const sceneImageRoles = ['scene_overview', 'scene_angle', 'scene_detail'];
export const sceneImageDocumentSchema = z.object({
  images: z.array(z.object({assetId:z.string().uuid(), role:z.enum(sceneImageRoles), label:z.string().trim().min(1).max(100),
    description:z.string().max(2000), anchorIds:z.array(z.string().min(1).max(100)).max(30)}).strict()).max(24),
  notes:z.string().max(4000)
}).strict().superRefine((v,c)=>{
  if(new Set(v.images.map(i=>i.assetId)).size!==v.images.length)c.addIssue({code:'custom',path:['images'],message:'同一图片只能登记一次'});
  if(v.images.length&&v.images.filter(i=>i.role==='scene_overview').length!==1)c.addIssue({code:'custom',path:['images'],message:'图片组须有且只有一张总览'});
  v.images.forEach((i,n)=>{if(new Set(i.anchorIds).size!==i.anchorIds.length)c.addIssue({code:'custom',path:['images',n,'anchorIds'],message:'锚点不能重复'});});
});
const empty=()=>({images:[],notes:''});
const hasTable=s=>!!s.db.prepare("SELECT name FROM sqlite_master WHERE type='table' AND name='scene_image_versions'").get();
function record(s,e){s.entity(e);if(!hasTable(s))return null;const r=s.db.prepare('SELECT v.* FROM entity_scene_image_state x JOIN scene_image_versions v ON v.id=x.version_id WHERE x.entity_id=?').get(e);return r?{...r,document:JSON.parse(r.document),confirmation:r.confirmation?JSON.parse(r.confirmation):null}:null;}
function evidence(s,e,doc){const entity=s.entity(e),spatial=sceneSpatialView(s,e,{includeUnconfirmed:false});return {
  textHash:contentHash({scene:isSceneEntity(entity),description:entity.context.description||'',appearance:entity.context.appearance||''}),
  appearanceId:s.visualState(e).appearance?.id||null, spatialRevision:spatial.sourceRevision,
  images:doc.images.map(i=>{try{const a=s.asset(i.assetId),actual=createHash('sha256').update(s.assetBytes(i.assetId)).digest('hex');return {assetId:a.id,hash:a.hash,available:a.entityId===e&&a.mediaType==='image'&&actual===a.hash};}catch{return {assetId:i.assetId,hash:'missing',available:false};}})
};}
export function sceneImageSetView(s,e,{includeUnconfirmed=false,sanitize=v=>v}={}){
  const r=record(s,e),doc=r?.document||empty(),basis=evidence(s,e,doc),issues=[];
  if(r?.confirmation&&r.confirmation.evidenceHash!==contentHash(basis))issues.push('场景文字、主图、空间设定或图片内容已变化，请重新核对图片组。');
  if(basis.images.some(i=>!i.available))issues.push('图片内容缺失、归属不符或哈希变化。');
  const status=!r?'missing':!r.confirmation?'draft':issues.length?'needs_review':'confirmed';
  const value={schemaVersion:1,status,versionId:r?.id||null,version:r?.version||0,contentHash:r?.content_hash||contentHash(doc),
    confirmedAt:r?.confirmation?.confirmedAt||null,images:status==='confirmed'||includeUnconfirmed?doc.images:[],
    notes:status==='confirmed'||includeUnconfirmed?doc.notes:'',issues,usage:'同一场景的人工选定参考图片组；图片角色和锚点指向不是新的空间事实，固定事实以 sceneSpatial 为准。'};
  const clean=JSON.parse(JSON.stringify(value,(_k,v)=>typeof v==='string'?sanitize(v):v));return {...clean,sourceRevision:contentHash(clean)};
}
function parse(schema,b){const r=schema.safeParse(b);if(!r.success){const fieldErrors={};for(const i of r.error.issues)(fieldErrors[i.path.join('.')||'body']||=[]).push(i.message);throw new HttpError(400,'场景图片组格式不正确',{fieldErrors});}return r.data;}
export function createSceneImages(s){
  s.db.exec(`CREATE TABLE IF NOT EXISTS scene_image_versions(id TEXT PRIMARY KEY,entity_id TEXT NOT NULL REFERENCES entities(id),version INTEGER NOT NULL,document TEXT NOT NULL,content_hash TEXT NOT NULL,confirmation TEXT,created_at TEXT NOT NULL,UNIQUE(entity_id,version));
    CREATE TABLE IF NOT EXISTS entity_scene_image_state(entity_id TEXT PRIMARY KEY REFERENCES entities(id),version_id TEXT NOT NULL REFERENCES scene_image_versions(id));
    CREATE TRIGGER IF NOT EXISTS scene_image_no_update BEFORE UPDATE ON scene_image_versions BEGIN SELECT RAISE(ABORT,'immutable scene image version'); END;
    CREATE TRIGGER IF NOT EXISTS scene_image_no_delete BEFORE DELETE ON scene_image_versions BEGIN SELECT RAISE(ABORT,'immutable scene image version'); END;`);
  const checkEntity=e=>{if(!isSceneEntity(s.entity(e)))throw new HttpError(400,'场景图片组只适用于场景实体');};
  function get(e){checkEntity(e);const r=record(s,e),document=r?.document||empty();return {owner:'Sean',entityId:e,document,expectedVersionId:r?.id||null,evidenceHash:contentHash(evidence(s,e,document)),summary:sceneImageSetView(s,e,{includeUnconfirmed:true}),
    candidates:s.db.prepare("SELECT * FROM assets WHERE entity_id=? AND deleted_at IS NULL AND kind IN ('setting','concept') ORDER BY created_at,id").all(e).map(s.assetView)};}
  function expected(e,v){if((record(s,e)?.id||null)!==v)throw new HttpError(409,'图片组已在另一页面更新，请刷新');}
  function validate(e,doc){const spatial=sceneSpatialView(s,e,{includeUnconfirmed:true}),anchors=new Set((spatial.draft?.elements||[]).map(x=>x.id));for(const i of doc.images){const a=s.asset(i.assetId);if(a.entityId!==e||a.mediaType!=='image'||!['concept','setting'].includes(a.kind))throw new HttpError(400,'请选择当前场景的概念图或设定图',{fieldErrors:{'document.images':['图片归属或类型不符']}});if(a.runId&&s.run(a.runId).status!=='succeeded')throw new HttpError(409,'生成未成功，不能纳入图片组');if(i.anchorIds.some(x=>!anchors.has(x)))throw new HttpError(400,'锚点不属于当前场景',{fieldErrors:{'document.images.anchorIds':['请使用当前空间设定锚点 ID']}});}if(evidence(s,e,doc).images.some(i=>!i.available))throw new HttpError(409,'图片内容缺失或哈希不符');}
  function write(e,doc,confirmation=null){const version=(record(s,e)?.version||0)+1,versionId=id();s.db.prepare('INSERT INTO scene_image_versions VALUES (?,?,?,?,?,?,?)').run(versionId,e,version,canonicalJSON(doc),contentHash(doc),confirmation?canonicalJSON(confirmation):null,now());s.db.prepare('INSERT INTO entity_scene_image_state VALUES (?,?) ON CONFLICT(entity_id) DO UPDATE SET version_id=excluded.version_id').run(e,versionId);}
  function save(e,b){checkEntity(e);const v=parse(z.object({expectedVersionId:z.string().uuid().nullable(),document:sceneImageDocumentSchema}).strict(),b);s.transaction(()=>{expected(e,v.expectedVersionId);validate(e,v.document);write(e,v.document);});return get(e);}
  function confirm(e,b){checkEntity(e);const v=parse(z.object({expectedVersionId:z.string().uuid(),expectedContentHash:z.string().length(64),expectedEvidenceHash:z.string().length(64),acknowledgeConsistency:z.literal(true)}).strict(),b);s.transaction(()=>{expected(e,v.expectedVersionId);const r=record(s,e);if(r.content_hash!==v.expectedContentHash||contentHash(evidence(s,e,r.document))!==v.expectedEvidenceHash)throw new HttpError(409,'资料已变化，请核对后重新确认');if(!r.document.images.length)throw new HttpError(400,'至少选择一张总览图');validate(e,r.document);const main=s.visualState(e).appearance;if(main&&!r.document.images.some(i=>i.assetId===main.assetId&&i.role==='scene_overview'))throw new HttpError(400,'当前场景主图须作为图片组总览',{fieldErrors:{'document.images':['请纳入当前主图并设为总览']}});write(e,r.document,{owner:'Sean',method:'user-explicit-consistency-check',confirmedAt:now(),evidenceHash:contentHash(evidence(s,e,r.document))});for(const i of r.document.images)s.db.prepare('UPDATE assets SET locked=1,ever_confirmed=1 WHERE id=?').run(i.assetId);});return get(e);}
  return {get,save,confirm};
}
