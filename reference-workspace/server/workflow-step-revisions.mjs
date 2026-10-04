// Owner: Sean — immutable image-step proposals and explicit, concurrent-safe user adoption.
import {createHash} from 'node:crypto';
import {z} from 'zod';
import {id,now,HttpError} from './store.mjs';
import {canonicalJSON,contentHash} from './content-hash.mjs';
import {projectInput} from './project-workspace.mjs';
import {imageFeedbackSchema,correctionEvidence} from './image-feedback.mjs';

export function createWorkflowStepRevisions(store,{projectService,management,basis,validate,imageSchema}){
  const db=store.db;
  const revisionSchema=z.object({expectedStepHash:z.string().length(64),expectedActiveStepId:z.string().uuid(),expectedContextHash:z.string().length(64),reason:z.string().trim().min(1).max(4000),image:imageSchema,feedback:imageFeedbackSchema.optional()}).strict();
  db.exec(`CREATE TABLE IF NOT EXISTS entity_workflow_step_revisions(step_id TEXT PRIMARY KEY REFERENCES entity_workflow_steps(id),parent_step_id TEXT NOT NULL REFERENCES entity_workflow_steps(id),root_step_id TEXT NOT NULL REFERENCES entity_workflow_steps(id),version INTEGER NOT NULL,reason TEXT NOT NULL,session_id TEXT,run_id TEXT,basis TEXT NOT NULL,UNIQUE(root_step_id,version));
    CREATE TABLE IF NOT EXISTS entity_workflow_step_heads(root_step_id TEXT PRIMARY KEY REFERENCES entity_workflow_steps(id),step_id TEXT NOT NULL REFERENCES entity_workflow_steps(id));
    CREATE TABLE IF NOT EXISTS entity_workflow_step_selections(id TEXT PRIMARY KEY,root_step_id TEXT NOT NULL REFERENCES entity_workflow_steps(id),from_step_id TEXT NOT NULL,to_step_id TEXT NOT NULL,created_at TEXT NOT NULL);
    CREATE TRIGGER IF NOT EXISTS workflow_revisions_immutable BEFORE UPDATE ON entity_workflow_step_revisions BEGIN SELECT RAISE(ABORT,'immutable step revision'); END;
    CREATE TRIGGER IF NOT EXISTS workflow_revisions_no_delete BEFORE DELETE ON entity_workflow_step_revisions BEGIN SELECT RAISE(ABORT,'immutable step revision'); END;`);
  function row(projectId,stepId){projectService.project(projectId);const r=db.prepare('SELECT * FROM entity_workflow_steps WHERE id=? AND project_id=?').get(stepId,projectId);if(!r)throw new HttpError(404,'图片步骤不存在');projectService.member(projectId,r.entity_id);return r;}
  function metadata(stepId){const rev=db.prepare('SELECT * FROM entity_workflow_step_revisions WHERE step_id=?').get(stepId);const root=rev?.root_step_id||stepId,head=db.prepare('SELECT step_id FROM entity_workflow_step_heads WHERE root_step_id=?').get(root)?.step_id||root;const adopted=stepId===root||!!db.prepare('SELECT id FROM entity_workflow_step_selections WHERE to_step_id=? LIMIT 1').get(stepId);return {rootStepId:root,parentStepId:rev?.parent_step_id||null,version:rev?.version||1,reason:rev?.reason||'',sessionId:rev?.session_id||null,runId:rev?.run_id||null,activeStepId:head,isCurrent:head===stepId,revisionStatus:head===stepId?'current':adopted?'history':'proposal',revisionBasis:rev?JSON.parse(rev.basis):null};}
  function hashes(images){return Object.fromEntries(images.map(assetId=>{const a=store.asset(assetId),hash=createHash('sha256').update(store.assetBytes(assetId)).digest('hex');if(hash!==a.hash)throw new HttpError(409,'参考图内容变化，请重新选择');return [assetId,hash];}));}
  function make(projectId,stepId,raw,{sessionId=null,runId=null}={}){const input=projectInput(revisionSchema,raw);return store.transaction(()=>{
    const old=row(projectId,stepId),oldBody=JSON.parse(old.body),meta=metadata(stepId),current=basis(projectId);
    if(old.content_hash!==input.expectedStepHash||meta.activeStepId!==input.expectedActiveStepId)throw new HttpError(409,'步骤或当前选用版本已变化，请重新载入');
    if(current.contextHash!==input.expectedContextHash)throw new HttpError(409,'项目依据已变化，请重新讨论');
    if(input.image.key!==oldBody.key)throw new HttpError(400,'修订不能改变逻辑步骤 key',{fieldErrors:{'image.key':['请保留原步骤 key']}});
    const d=management.detail(old.entity_id),derived=db.prepare('SELECT * FROM entity_derivations WHERE entity_id=?').get(old.entity_id);
    const candidate={key:oldBody.candidateKey,kind:oldBody.candidateKind,profile:d.profile,baseEntityId:derived?.base_entity_id||null,variationOf:null,changes:derived?.description||'',projectRole:{role:'',plotNotes:''},unknowns:[],images:[input.image]};
    if(oldBody.sceneIntent&&!input.image.sceneIntent)throw new HttpError(400,'此步骤需保留资料编译模式，请调整取景目标而非取消来源');
    const checked=validate(projectId,{title:'图片步骤修订',summary:input.reason,candidates:[candidate],relations:[],questions:[]},{compilationEntityId:old.entity_id}).candidates[0].images[0];
    const feedback=input.feedback?correctionEvidence(store,projectService,projectId,old,meta,input.feedback,runId):null;
    const captured={...current,imageHashes:hashes(checked.referenceAssetIds),...(feedback?{feedback}:{})},stepIdNew=id(),version=(db.prepare('SELECT max(version) AS n FROM entity_workflow_step_revisions WHERE root_step_id=?').get(meta.rootStepId).n||1)+1;
    const body={...checked,candidateKey:oldBody.candidateKey,candidateKind:oldBody.candidateKind,entityRevision:d.revision};
    db.prepare('INSERT INTO entity_workflow_steps VALUES (?,?,?,?,?,?,?)').run(stepIdNew,old.plan_id,projectId,old.entity_id,canonicalJSON(body),contentHash(body),now());
    db.prepare('INSERT INTO entity_workflow_step_revisions VALUES (?,?,?,?,?,?,?,?)').run(stepIdNew,stepId,meta.rootStepId,version,input.reason,sessionId,runId,canonicalJSON(captured));
    return {owner:'Sean',stepId:stepIdNew,rootStepId:meta.rootStepId,version,savedAs:'proposal-only',generationSubmitted:false};
  });}
  function adopt(projectId,stepId,raw){const input=projectInput(z.object({expectedStepHash:z.string().length(64),expectedActiveStepId:z.string().uuid(),acknowledgeReview:z.literal(true)}).strict(),raw);return store.transaction(()=>{
    const r=row(projectId,stepId),body=JSON.parse(r.body),meta=metadata(stepId);
    if(r.content_hash!==input.expectedStepHash)throw new HttpError(409,'步骤版本不匹配');
    if(meta.activeStepId===stepId)return {stepId,alreadyAdopted:true};
    if(meta.activeStepId!==input.expectedActiveStepId)throw new HttpError(409,'当前选用版本已变化，请比较后重新选择');
    if(body.entityRevision!==management.detail(r.entity_id).revision)throw new HttpError(409,'实体资料已变化，请以当前资料保存新的修订');
    if(meta.runId&&db.prepare('SELECT status FROM agent_runs WHERE id=?').get(meta.runId)?.status!=='succeeded')throw new HttpError(409,'等待助手对话完整结束后采用');
    if(meta.revisionBasis&&meta.revisionStatus==='proposal'&&meta.revisionBasis.contextHash!==basis(projectId).contextHash)throw new HttpError(409,'项目依据已变化，请重新讨论修订');
    const captured=meta.revisionBasis||JSON.parse(db.prepare('SELECT basis FROM entity_authoring_plans WHERE id=?').get(r.plan_id).basis);
    if(meta.revisionStatus==='proposal'&&captured.feedback)correctionEvidence(store,projectService,projectId,r,meta,{reviewId:captured.feedback.reviewId,expectedReviewHash:captured.feedback.reviewHash,assetIds:captured.feedback.assets.map(a=>a.assetId)});
    for(const [a,hash] of Object.entries(captured.imageHashes)){projectService.member(projectId,store.asset(a).entityId);if(createHash('sha256').update(store.assetBytes(a)).digest('hex')!==hash)throw new HttpError(409,'参考图内容已变化');}
    db.prepare('INSERT INTO entity_workflow_step_heads VALUES (?,?) ON CONFLICT(root_step_id) DO UPDATE SET step_id=excluded.step_id').run(meta.rootStepId,stepId);
    db.prepare('INSERT INTO entity_workflow_step_selections VALUES (?,?,?,?,?)').run(id(),meta.rootStepId,meta.activeStepId,stepId,now());
    return {owner:'Sean',stepId,rootStepId:meta.rootStepId,generationSubmitted:false};
  });}
  return {metadata,make,adopt,revisionSchema};
}
