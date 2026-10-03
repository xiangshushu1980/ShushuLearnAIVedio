// Owner: Sean — persistent spatial revisions and explicit image/text consistency confirmation.
import { existsSync,readFileSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { z } from 'zod';
import { id,now,HttpError } from './store.mjs';
import { contentHash,canonicalJSON } from './content-hash.mjs';
import { spatialDocumentSchema } from './spatial-schema.mjs';
const tableExists=store=>!!store.db.prepare("SELECT name FROM sqlite_master WHERE type='table' AND name='scene_spatial_versions'").get();
export const isSceneEntity=e=>(Array.isArray(e.context.flags)&&e.context.flags.includes('场景')) || ['scene','location','场景'].includes(e.context.type);
const empty=()=>({owner:'Sean',schemaVersion:1,scope:'fixed_scene_space',frame:{description:'',status:'pending'},elements:[],links:[],routes:[],unknowns:[],referenceAssetIds:[]});
function readRecord(store,entityId){store.entity(entityId);if(!tableExists(store))return null;const row=store.db.prepare('SELECT v.* FROM entity_spatial_state s JOIN scene_spatial_versions v ON v.id=s.version_id WHERE s.entity_id=?').get(entityId);return row?{...row,document:JSON.parse(row.document),confirmation:row.confirmation?JSON.parse(row.confirmation):null}:null;}
function evidenceState(store,entityId,doc){
  const entity=store.entity(entityId),visual=store.visualState(entityId);
  const images=doc.referenceAssetIds.map(assetId=>{try{const a=store.asset(assetId,true),available=!a.deletedAt&&existsSync(store.assetPath(assetId));return {assetId,contentHash:a.hash,available};}catch(e){if(e.status!==404)throw e;return {assetId,contentHash:'missing',available:false};}});
  return {images,textHash:contentHash({description:entity.context.description||'',appearance:entity.context.appearance||''}),appearanceId:visual.appearance?.id||null,appearanceAssetId:visual.appearance?.assetId||null,viewAssetId:visual.view?.id||null};
}
function notes(doc){const n=[...doc.unknowns];if(!doc.frame.description.trim()||doc.frame.status==='pending')n.push('方向基准待补充或确认；不可将镜头左/右直接当场景固定方向。');if(!doc.elements.length)n.push('主要区域、建筑结构与固定物体尚未登记。');for(const e of doc.elements){if(e.status==='pending')n.push(`[${e.id}] ${e.label} 待补充或确认。`);for(const [key,name] of [['position','位置/相对位置'],['orientation','朝向'],['scale','尺度']])if(!e[key].trim())n.push(`[${e.id}] ${name}未单独记录；只能使用已有说明，不得猜测。`);}for(const l of doc.links)if(l.status==='pending')n.push(`[${l.id}] 空间关系待确认。`);for(const r of doc.routes)if(r.status==='pending')n.push(`[${r.id}] 通路待确认。`);return [...new Set(n)];}
export function sceneSpatialView(store,entityId,{includeUnconfirmed=true,sanitize=v=>v}={}){
  const row=readRecord(store,entityId),doc=row?.document||empty(),basis=evidenceState(store,entityId,doc),issues=[];
  if(row?.confirmation){if(contentHash(basis)!==row.confirmation.evidenceStateHash)issues.push('参考图、当前主形象/视图或实体文字已变化，须重新核对。');if(basis.images.some(a=>!a.available))issues.push('核对参考图内容缺失。');for(const image of basis.images){if(!image.available)continue;const actual=createHash('sha256').update(readFileSync(store.assetPath(image.assetId))).digest('hex');if(actual!==image.contentHash)issues.push(`参考图 ${image.assetId} 与登记哈希不符。`);}}
  const status=!row?'missing':!row.confirmation?'draft':issues.length?'needs_review':'confirmed',usable=status==='confirmed';
  const clean=value=>JSON.parse(JSON.stringify(value,(_key,item)=>typeof item==='string'?sanitize(item):item));
  const elements=usable?doc.elements.filter(e=>e.status==='known'):[],links=usable?doc.links.filter(l=>l.status==='known'):[],routes=usable?doc.routes.filter(r=>r.status==='known'):[];
  const frame=usable&&doc.frame.status==='known'?doc.frame:null;
  const lines=usable?['固定场景空间事实（角色站位/移动/物品转移由拍摄本另行指定）',`方向基准：${frame.description}`,
    ...elements.map(e=>`[${e.id}] ${e.kind} ${e.label}：${e.description}${e.position?`；位置：${e.position}`:''}${e.orientation?`；朝向：${e.orientation}`:''}${e.scale?`；尺度：${e.scale}`:''}`),
    ...links.map(l=>`[${l.id}] ${l.from} → ${l.to}：${l.description}`),...routes.map(r=>`[${r.id}] ${r.label}：${r.via.join(' → ')}${r.description?'；'+r.description:''}`)]:[];
  const unknowns=notes(doc);if(unknowns.length&&usable)lines.push('待补充/不可推断：'+unknowns.join('；'));
  const view={schemaVersion:1,scope:'fixed_scene_space',status,version:row?.version||0,versionId:row?.id||null,contentHash:row?.content_hash||contentHash(doc),
    confirmedAt:row?.confirmation?.confirmedAt||null,frame,elements,links,routes,unknowns,issues,referenceImages:basis.images,promptContext:lines.join('\n'),
    draft:includeUnconfirmed?doc:null,usage:'空间标识以 entityId#id 引用；角色当前位置、朝向、移动时间线与可移动物品转移属于拍摄本。pending/draft/needs_review 内容不得作为已确认固定事实。'};
  const safe=clean(view);return {...safe,sourceRevision:contentHash(safe)};
}
function parse(schema,body){const r=schema.safeParse(body);if(!r.success){const errors={};for(const issue of r.error.issues){const path=issue.path.join('.')||'body';(errors[path]||=[]).push(issue.message);}throw new HttpError(400,'空间资料格式不正确',{fieldErrors:errors});}return r.data;}
export function createSceneSpatial(store){
  store.db.exec(`CREATE TABLE IF NOT EXISTS scene_spatial_versions(id TEXT PRIMARY KEY,entity_id TEXT NOT NULL REFERENCES entities(id),version INTEGER NOT NULL,document TEXT NOT NULL,content_hash TEXT NOT NULL,confirmation TEXT,created_at TEXT NOT NULL,UNIQUE(entity_id,version));
    CREATE TABLE IF NOT EXISTS entity_spatial_state(entity_id TEXT PRIMARY KEY REFERENCES entities(id),version_id TEXT NOT NULL REFERENCES scene_spatial_versions(id));
    CREATE TRIGGER IF NOT EXISTS spatial_versions_no_update BEFORE UPDATE ON scene_spatial_versions BEGIN SELECT RAISE(ABORT,'immutable spatial version');END;
    CREATE TRIGGER IF NOT EXISTS spatial_versions_no_delete BEFORE DELETE ON scene_spatial_versions BEGIN SELECT RAISE(ABORT,'immutable spatial version');END;`);
  function get(entityId){const row=readRecord(store,entityId),document=row?.document||empty(),basis=evidenceState(store,entityId,document);return {owner:'Sean',entityId,document,summary:sceneSpatialView(store,entityId),expectedVersionId:row?.id||null,evidenceStateHash:contentHash(basis)};}
  function write(entityId,document,confirmation=null){const current=readRecord(store,entityId),version=(current?.version||0)+1,versionId=id();store.db.prepare('INSERT INTO scene_spatial_versions VALUES (?,?,?,?,?,?,?)').run(versionId,entityId,version,canonicalJSON(document),contentHash(document),confirmation?canonicalJSON(confirmation):null,now());store.db.prepare('INSERT INTO entity_spatial_state VALUES (?,?) ON CONFLICT(entity_id) DO UPDATE SET version_id=excluded.version_id').run(entityId,versionId);}
  function checkExpected(entityId,expected){if((readRecord(store,entityId)?.id||null)!==expected)throw new HttpError(409,'空间资料已在其他页面修改，请重新载入');}
  function save(entityId,body){const input=parse(z.object({expectedVersionId:z.string().uuid().nullable(),document:spatialDocumentSchema}).strict(),body);store.transaction(()=>{checkExpected(entityId,input.expectedVersionId);for(const assetId of input.document.referenceAssetIds){const a=store.asset(assetId);if(a.entityId!==entityId||a.mediaType!=='image')throw new HttpError(400,'核对参考图须属于当前实体',{fieldErrors:{'document.referenceAssetIds':['请选择本实体图片']}});}write(entityId,input.document);});return get(entityId);}
  function confirm(entityId,body){const input=parse(z.object({expectedVersionId:z.string().uuid(),expectedContentHash:z.string(),expectedEvidenceStateHash:z.string(),acknowledgeConsistency:z.literal(true)}).strict(),body);store.transaction(()=>{checkExpected(entityId,input.expectedVersionId);const row=readRecord(store,entityId),doc=row.document,basis=evidenceState(store,entityId,doc);if(row.content_hash!==input.expectedContentHash||contentHash(basis)!==input.expectedEvidenceStateHash)throw new HttpError(409,'文字或参考资料已变化，请重新核对后确认');if(doc.frame.status!=='known'||!doc.frame.description.trim()||!doc.elements.some(e=>e.status==='known'))throw new HttpError(400,'至少确认方向基准和一个空间锚点，其他未知事实可保留待补充');if(basis.appearanceAssetId&&!doc.referenceAssetIds.includes(basis.appearanceAssetId))throw new HttpError(400,'请将当前主形象选为核对参考图，避免依据旧图确认新场景',{fieldErrors:{'document.referenceAssetIds':['必须包含当前主形象']}});if(!basis.images.length||basis.images.some(a=>!a.available))throw new HttpError(400,'请选择至少一张存在的参考图，并对照确认文字与图片一致');for(const ref of basis.images)if(createHash('sha256').update(store.assetBytes(ref.assetId)).digest('hex')!==ref.contentHash)throw new HttpError(409,'参考图内容发生变化');write(entityId,doc,{owner:'Sean',method:'user-explicit-consistency-check',confirmedAt:now(),evidenceStateHash:contentHash(basis)});});return get(entityId);}
  return {get,save,confirm,cloneDraft(baseId,newId,assetMapping=new Map()){const row=readRecord(store,baseId);if(!row)return;const doc=structuredClone(row.document);doc.referenceAssetIds=doc.referenceAssetIds.flatMap(assetId=>assetMapping.has(assetId)?[assetMapping.get(assetId)]:[]);doc.unknowns.push('派生场景空间布局需重新对照本实体参考图确认；锚点ID以新的entityId为范围。');write(newId,doc);}};
}
