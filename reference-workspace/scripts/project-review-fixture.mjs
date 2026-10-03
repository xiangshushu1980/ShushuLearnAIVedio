// Owner: Sean — isolated partial text-review UI fixture, no model/credential/generation calls.
import {createAgentWorkspace,agentWorkspaceRouter} from '../server/agent-workspace.mjs';
import {id} from '../server/store.mjs';
export async function installProjectReviewFixture(store,projects,authoring){
 const project=projects.projects()[0],entityId=project.entityIds[0];
 const runtime={models:async()=>[{provider:'fixture',id:'fixture',name:'模拟助手（不调用模型）'}],open:async({tools})=>({entries:()=>[],session:{subscribe:()=>()=>{},messages:[],dispose(){},async prompt(){await tools.find(t=>t.name==='get_project_entity').execute('read',{entityId});await tools.find(t=>t.name==='propose_project_review').execute('report',{summary:'只核对候车厅文字；其他实体和图片未检查。',issues:[{entityIds:[entityId],category:'missing',description:'候车厅绝对方向与尺度尚未登记，不能从相邻与通向推断。',suggestion:'补充可核对的空间资料；保留未知，不判定为错误。'}]});}}})};
 const agents=createAgentWorkspace(store,{runtime,projectService:projects,authoringService:authoring}),session=await agents.createSession({projectId:project.id,entityId:null,purpose:'project-authoring',provider:'fixture',modelId:'fixture'}),run=await agents.start(session.id,{requestId:id(),text:'部分文字审阅 UI 模拟',referenceAssetIds:[]});
 for(let n=0;n<100&&agents.run(run.runId).status==='running';n++)await new Promise(r=>setTimeout(r,5));
 if(agents.run(run.runId).status!=='succeeded')throw new Error('Fixture review failed');return {agents,router:agentWorkspaceRouter(agents),sessionId:session.id};
}
