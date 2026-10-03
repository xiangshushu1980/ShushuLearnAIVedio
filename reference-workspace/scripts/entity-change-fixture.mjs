// Owner: Sean — real entity-change API/UI with an isolated mock Agent; no provider or generation calls.
export async function installEntityChangeFixture(store,projects,authoring){
  const {createAgentWorkspace,agentWorkspaceRouter}=await import('../server/agent-workspace.mjs');
  const {id}=await import('../server/store.mjs');
  const project=projects.projects()[0],entityId=authoring.steps(project.id)[0].entityId;let proposalId;
  const runtime={models:async()=>[{provider:'fixture',id:'fixture',name:'模拟助手（不调用模型）'}],open:async({tools})=>({entries:()=>[],session:{subscribe:()=>()=>{},messages:[],dispose(){},async prompt(){
    await tools.find(t=>t.name==='get_project_entity').execute(id(),{entityId});
    const result=JSON.parse((await tools.find(t=>t.name==='propose_entity_update').execute(id(),{entityId,summary:'模拟人物/场景文字修改，仅验证接口与预览',changes:{description:'用户指定的新说明（模拟）；保留原外观和其他资料。'}})).content[0].text);if(result.error)throw new Error(result.error);proposalId=result.proposalId;
  }}})};
  const agents=createAgentWorkspace(store,{runtime,projectService:projects,authoringService:authoring}),session=await agents.createSession({projectId:project.id,entityId:null,purpose:'project-authoring',provider:'fixture',modelId:'fixture'}),run=await agents.start(session.id,{requestId:id(),text:'请整理模拟文字修改提案，不自动应用',referenceAssetIds:[]});
  for(let n=0;n<200&&agents.run(run.runId).status==='running';n++)await new Promise(r=>setTimeout(r,5));
  if(!proposalId||agents.run(run.runId).status!=='succeeded')throw new Error('Fixture entity proposal failed');
  return {agents,router:agentWorkspaceRouter(agents),sessionId:session.id,proposalId,changeEntityId:entityId};
}
