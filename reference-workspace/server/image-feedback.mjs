// Owner: Sean — immutable review evidence linked to image workflow corrections.
import {createHash} from 'node:crypto';
import {z} from 'zod';
import {HttpError} from './store.mjs';
import {contentHash} from './content-hash.mjs';

const uuid=z.string().uuid();
export const imageReviewSchema=z.object({
  summary:z.string().trim().min(1).max(4000),
  reviewedAssetIds:z.array(uuid).min(1).max(8),
  conclusion:z.enum(['consistent','conflicts','inconclusive']),
  issues:z.array(z.object({entityIds:z.array(uuid).max(100),assetIds:z.array(uuid).max(8).optional(),category:z.enum(['conflict','missing','suggestion']),description:z.string().trim().min(1).max(4000),suggestion:z.string().max(4000)}).strict()).max(30)
}).strict();
export const imageFeedbackSchema=z.object({reviewId:uuid,expectedReviewHash:z.string().length(64),assetIds:z.array(uuid).min(1).max(8).refine(a=>new Set(a).size===a.length,'图片不能重复')}).strict();

export function imageReviewSources(store,authoring,projectId,assetIds,readSteps=new Map()){
  return assetIds.map(assetId=>{
    const asset=store.asset(assetId),source={assetId,entityId:asset.entityId,contentHash:asset.hash,runId:asset.runId||null,workflow:null};
    if(!asset.runId)return source;
    const run=store.run(asset.runId),origin=run.snapshot.authoring;
    if(run.entityId!==asset.entityId||!origin?.stepId)return source;
    try{
      const step=authoring.getStep(projectId,origin.stepId);
      if(step.entityId!==asset.entityId||step.contentHash!==origin.sourceRevision)return source;
      source.workflow={stepId:step.id,rootStepId:step.rootStepId,version:step.version,stepHash:step.contentHash,label:step.label,role:step.role,batchId:origin.batchId||null,fullStepRead:readSteps.get(step.id)?.hash===step.contentHash};
    }catch{/* An imported image or unavailable source cannot become a correction target. */}
    return source;
  });
}

// Read coverage is evidence of context access, not proof of visual correctness.
export function imageComparisonCoverage(sources,reviewedEntities){
  const entityIds=[...new Set(sources.map(a=>a.entityId))].sort();
  const steps=[...new Map(sources.filter(a=>a.workflow).map(a=>[a.workflow.stepId,a.workflow])).values()];
  const missingEntityIds=entityIds.filter(e=>!reviewedEntities.has(e));
  const unreadStepIds=steps.filter(s=>!s.fullStepRead).map(s=>s.stepId).sort();
  return {entityIds,missingEntityIds,stepIds:steps.map(s=>s.stepId).sort(),unreadStepIds,
    untrackedAssetIds:sources.filter(a=>!a.workflow).map(a=>a.assetId).sort(),
    status:missingEntityIds.length||unreadStepIds.length?'incomplete':'complete',
    scope:'reviewed images versus their fully read registered entity data and available generation steps; not an approval or proof of image quality'};
}

export function getImageReview(store,projects,projectId,reviewId){
  projects.project(projectId);
  const exists=store.db.prepare("SELECT name FROM sqlite_master WHERE type='table' AND name='agent_project_proposals'").get();
  const row=exists&&store.db.prepare("SELECT p.*,s.project_id,r.status AS run_status FROM agent_project_proposals p JOIN agent_sessions s ON s.id=p.session_id JOIN agent_runs r ON r.id=p.run_id WHERE p.id=? AND s.project_id=? AND p.kind='image-review'").get(reviewId,projectId);
  if(!row)throw new HttpError(404,'图片检验报告不存在');
  const body=JSON.parse(row.body);let stale=true;
  try{stale=body.basis.contextHash!==contentHash(projects.context(projectId))||body.basis.images.some(a=>createHash('sha256').update(store.assetBytes(a.assetId)).digest('hex')!==a.contentHash);}catch{}
  return {owner:'Sean',id:row.id,projectId,runId:row.run_id,runStatus:row.run_status,contentHash:row.content_hash,createdAt:row.created_at,...body,stale};
}

export function correctionEvidence(store,projects,projectId,step,meta,feedback,requesterRunId=null){
  const report=getImageReview(store,projects,projectId,feedback.reviewId);
  if(report.contentHash!==feedback.expectedReviewHash)throw new HttpError(409,'检验报告版本不匹配');
  if(report.stale)throw new HttpError(409,'报告依据已变化，请基于最新资料重新检验');
  if(report.runStatus!=='succeeded'&&!(report.runStatus==='running'&&report.runId===requesterRunId))throw new HttpError(409,'检验对话未完整结束，请重新检验');
  const assets=feedback.assetIds.map(assetId=>{
    const source=report.workflowSources?.find(a=>a.assetId===assetId);
    if(!report.reviewedAssetIds.includes(assetId)||!source?.workflow||source.entityId!==step.entity_id||source.workflow.rootStepId!==meta.rootStepId)throw new HttpError(400,'修订依据必须是报告已检查的同一逻辑步骤图片',{fieldErrors:{'feedback.assetIds':['请选择该步骤的已检查结果']}});
    const a=store.asset(assetId);projects.member(projectId,a.entityId);
    if(a.hash!==source.contentHash||createHash('sha256').update(store.assetBytes(assetId)).digest('hex')!==source.contentHash)throw new HttpError(409,'检验图片内容变化，请重新检验');
    return source;
  });
  return {reviewId:report.id,reviewHash:report.contentHash,conclusion:report.conclusion,summary:report.summary,assets};
}
