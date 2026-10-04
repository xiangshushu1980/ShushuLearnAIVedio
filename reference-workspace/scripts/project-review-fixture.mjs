// Owner: Sean — isolated partial text-review UI fixture, no model/credential/generation calls.
import {createAgentWorkspace,agentWorkspaceRouter} from '../server/agent-workspace.mjs';
import {id} from '../server/store.mjs';
export async function installProjectReviewFixture(store,projects,authoring){
 const project=projects.projects()[0],entityId=project.entityIds[0];
 const relationMode=process.env.REFERENCE_RELATION_REVIEW_FIXTURE==='1';
 const targetId=project.entityIds.find(e=>e!==entityId);
 const relation=relationMode?projects.saveRelation(project.id,null,{sourceEntityId:entityId,targetEntityId:targetId,type:'进入',description:'模拟剧情关系，用于检验来源显示，不是真实剧情。',expectedRevision:projects.project(project.id).revision}).relations[0]:null;
 const runtime={models:async()=>[{provider:'fixture',id:'fixture',name:'模拟助手（不调用模型）'}],open:async({tools})=>({entries:()=>[],session:{subscribe:()=>()=>{},messages:[],dispose(){},async prompt(){await tools.find(t=>t.name==='get_project_entity').execute('read',{entityId});if(relationMode){await tools.find(t=>t.name==='get_project_entity').execute('read-target',{entityId:targetId});await tools.find(t=>t.name==='propose_project_review').execute('relation-report',{summary:'模拟关系检验：已读取两个端点。',issues:[{entityIds:[entityId,targetId],relationIds:[relation.relationId],category:'suggestion',description:'核对进入场景的剧情用途。',suggestion:'人工查看关系与项目设定。'}]});return;}await tools.find(t=>t.name==='propose_project_review').execute('report',{summary:'只核对候车厅文字；其他实体和图片未检查。',issues:[{entityIds:[entityId],category:'missing',description:'候车厅绝对方向与尺度尚未登记，不能从相邻与通向推断。',suggestion:'补充可核对的空间资料；保留未知，不判定为错误。'}]});}}})};
 const agents=createAgentWorkspace(store,{runtime,projectService:projects,authoringService:authoring}),session=await agents.createSession({projectId:project.id,entityId:null,purpose:'project-authoring',provider:'fixture',modelId:'fixture'}),run=await agents.start(session.id,{requestId:id(),text:'部分文字审阅 UI 模拟',referenceAssetIds:[]});
 for(let n=0;n<100&&agents.run(run.runId).status==='running';n++)await new Promise(r=>setTimeout(r,5));
 if(agents.run(run.runId).status!=='succeeded')throw new Error('Fixture review failed');return {agents,router:agentWorkspaceRouter(agents),sessionId:session.id};
}
