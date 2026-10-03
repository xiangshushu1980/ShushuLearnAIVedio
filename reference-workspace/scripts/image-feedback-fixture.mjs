// Owner: Sean — optional browser fixture using real APIs with a mock Agent; no model calls.
export async function installImageFeedbackFixture(store,projects,authoring,fakeRuns){
  const {createAgentWorkspace,agentWorkspaceRouter}=await import('../server/agent-workspace.mjs');
  const {id}=await import('../server/store.mjs');
  const project=projects.projects()[0],step=authoring.steps(project.id).find(s=>s.key==='overview');
  const prepared=authoring.prepareRun(project.id,step.id,step.contentHash),run=fakeRuns.startPrepared(step.entityId,prepared.input,id(),{stepId:step.id,stepHash:step.contentHash});
  for(let n=0;n<200&&store.run(run.id).status!=='succeeded';n++)await new Promise(r=>setTimeout(r,5));
  const asset=store.run(run.id).outputs[0];if(!asset)throw new Error('Fixture output missing');
  let reportId=null,reportHash=null;
  const runtime={models:async()=>[{provider:'fixture',id:'fixture',name:'模拟助手（不调用模型）'}],open:async({tools})=>({entries:()=>[],session:{subscribe:()=>()=>{},messages:[],dispose(){},async prompt(){
    const call=async(name,input)=>JSON.parse((await tools.find(t=>t.name===name).execute(id(),input)).content[0].text);
    await call('get_project_entity',{entityId:step.entityId});await call('get_entity_workflow_step',{stepId:step.id});
    if(!reportId){await tools.find(t=>t.name==='view_reference_image').execute(id(),{assetId:asset.id});const result=await call('propose_image_consistency_review',{summary:'模拟报告：用于验证修订入口，不是图像质量结论。',reviewedAssetIds:[asset.id],conclusion:'conflicts',issues:[{entityIds:[step.entityId],assetIds:[asset.id],category:'conflict',description:'模拟入口位置不一致',suggestion:'提示词明确保留原入口位置'}]});if(result.error)throw new Error(result.error);reportId=result.proposalId;reportHash=authoring.imageReview(project.id,reportId).contentHash;}
    else {await call('get_image_consistency_review',{reviewId:reportId});const {entityRevision,candidateKey,candidateKind,...image}=JSON.parse(store.db.prepare('SELECT body FROM entity_workflow_steps WHERE id=?').get(step.id).body);const result=await call('propose_image_step_revision',{stepId:step.id,expectedStepHash:step.contentHash,expectedActiveStepId:step.id,reason:'根据模拟报告保留入口位置',image:{...image,prompt:step.prompt+' Keep the established entrance position.'},feedback:{reviewId:reportId,expectedReviewHash:reportHash,assetIds:[asset.id]}});if(result.error)throw new Error(result.error);}
  }}})};
  const agents=createAgentWorkspace(store,{runtime,projectService:projects,authoringService:authoring}),session=await agents.createSession({projectId:project.id,entityId:null,purpose:'project-authoring',provider:'fixture',modelId:'fixture'}),seed=await agents.start(session.id,{requestId:id(),text:'模拟检验（不调用模型）',referenceAssetIds:[asset.id]});
  for(let n=0;n<200&&agents.run(seed.runId).status==='running';n++)await new Promise(r=>setTimeout(r,5));
  if(!reportId||agents.run(seed.runId).status!=='succeeded')throw new Error('Fixture review failed');
  return {agents,router:agentWorkspaceRouter(agents),reportId,sessionId:session.id,assetId:asset.id};
}
