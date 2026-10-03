// Owner: Sean — minimal fixed scene space; dynamic actor/prop state belongs to the shooting script.
import { z } from 'zod';
const label = z.string().trim().min(1).max(150), prose=z.string().max(4000), stableId=z.string().regex(/^[A-Za-z][A-Za-z0-9_-]{0,47}$/);
const status=z.enum(['known','pending']);
export const spatialElementSchema=z.object({id:stableId,kind:z.enum(['area','structure','object']),label,description:prose.default(''),
  position:prose.default(''),orientation:prose.default(''),scale:prose.default(''),status:status.default('pending')}).strict();
const link=z.object({id:stableId,from:stableId,to:stableId,description:prose,status:status.default('pending')}).strict();
const route=z.object({id:stableId,label,via:z.array(stableId).min(2).max(40),description:prose.default(''),status:status.default('pending')}).strict();
export const spatialDocumentShape=z.object({owner:z.literal('Sean').default('Sean'),schemaVersion:z.literal(1).default(1),scope:z.literal('fixed_scene_space').default('fixed_scene_space'),
  frame:z.object({description:prose.default(''),status:status.default('pending')}).strict(),
  elements:z.array(spatialElementSchema).max(100).default([]),links:z.array(link).max(200).default([]),routes:z.array(route).max(50).default([]),
  unknowns:z.array(z.string().trim().min(1).max(2000)).max(100).default([]),referenceAssetIds:z.array(z.string().uuid()).max(32).default([])}).strict();
export const spatialDocumentSchema=spatialDocumentShape.superRefine((d,ctx)=>{
  const seen=new Set();for(const key of ['elements','links','routes'])d[key].forEach((item,i)=>{if(seen.has(item.id))ctx.addIssue({code:'custom',path:[key,i,'id'],message:'空间ID不能重复'});seen.add(item.id);});
  const elements=new Map(d.elements.map(e=>[e.id,e]));
  if(new Set(d.referenceAssetIds).size!==d.referenceAssetIds.length)ctx.addIssue({code:'custom',path:['referenceAssetIds'],message:'参考图不能重复'});
  if(d.frame.status==='known'&&!d.frame.description.trim())ctx.addIssue({code:'custom',path:['frame','description'],message:'已知方向基准须有说明'});
  d.elements.forEach((e,i)=>{if(e.status==='known'&&!e.description.trim()&&!e.position.trim())ctx.addIssue({code:'custom',path:['elements',i,'description'],message:'已知锚点须说明固定外观或空间位置'});});
  const check=(refs,known,path)=>refs.forEach((ref,i)=>{if(!elements.has(ref))ctx.addIssue({code:'custom',path:[...path,i],message:`未知空间锚点 ${ref}`});else if(known&&elements.get(ref).status!=='known')ctx.addIssue({code:'custom',path:[...path,i],message:'已知关系/通路不能依赖待补充锚点'});});
  d.links.forEach((l,i)=>{check([l.from,l.to],l.status==='known',['links',i]);if(l.from===l.to||!l.description.trim())ctx.addIssue({code:'custom',path:['links',i],message:'关系须连接不同锚点并填写固定空间关系'});});
  d.routes.forEach((r,i)=>check(r.via,r.status==='known',['routes',i,'via']));
});
const hash=z.string(), evidence=z.object({assetId:z.string().uuid(),contentHash:hash,available:z.boolean()}).strict();
export const spatialExportSchema=z.object({schemaVersion:z.literal(1),scope:z.literal('fixed_scene_space'),status:z.enum(['missing','draft','confirmed','needs_review']),
  version:z.number().int(),versionId:z.string().uuid().nullable(),contentHash:hash,sourceRevision:hash,confirmedAt:z.string().nullable(),
  frame:z.object({description:z.string(),status:z.literal('known')}).strict().nullable(),elements:z.array(spatialElementSchema),links:z.array(link),routes:z.array(route),
  unknowns:z.array(z.string()),issues:z.array(z.string()),referenceImages:z.array(evidence),promptContext:z.string(),
  draft:spatialDocumentShape.nullable(),usage:z.string()}).strict();
