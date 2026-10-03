// Owner: Sean — isolated real Pi authoring verification; no generation tools or ComfyUI requests.
import { mkdtempSync,mkdirSync,copyFileSync,existsSync,writeFileSync,rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join,resolve } from 'node:path';
import { randomUUID } from 'node:crypto';
import { createStore } from '../server/store.mjs';
import { createProjectWorkspace } from '../server/project-workspace.mjs';
import { createEntityAuthoring } from '../server/entity-authoring.mjs';
import { createAgentWorkspace } from '../server/agent-workspace.mjs';
const appRoot=resolve(new URL('..',import.meta.url).pathname),dataRoot=mkdtempSync(join(tmpdir(),'sean-authoring-conversation-')),agentRoot=join(dataRoot,'agent');
mkdirSync(agentRoot,{recursive:true,mode:0o700});
for(const file of ['auth.json','models.json','models-store.json','preferences.json']){const source=join(appRoot,'.data','agent',file);if(existsSync(source))copyFileSync(source,join(agentRoot,file));}
const store=createStore(dataRoot),projects=createProjectWorkspace(store),authoring=createEntityAuthoring(store,{projectService:projects}),agents=createAgentWorkspace(store,{projectService:projects,authoringService:authoring});
const evidence=resolve(appRoot,'../experiments/sean_reference_authoring_goal_20261004');const evidenceName=process.env.REFERENCE_VERIFY_EVIDENCE_NAME||'conversation-evidence.json';mkdirSync(evidence,{recursive:true});
const project=projects.saveProject(null,{name:'隔离测试：夜班管理员与候车厅',brief:'仅用于验证 Reference 自然语言实体创作。以下内容是人为定义的新设计，不是现实观察事实。',synopsis:'管理员在废弃候车厅值守，实验比较日常状态与受伤状态。',worldRules:'同一角色不同状态保持身份与服装；候车厅固定布局不随镜头改变。没有提供的地理朝向、绝对尺度和完整平面布局均待补充。',visualStyle:'统一写实概念设定风格；后续视角保持同一实体外观与空间结构。',decisions:'只生成可审阅设定与图片步骤，不实际生成图片，不自动确认。',entityIds:[]});
let runId,sessionId;
try{
  const models=await agents.models(),model=models.find(m=>m.provider==='deepseek'&&m.id==='deepseek-flash')||models[0];if(!model)throw new Error('No configured model');
  const session=await agents.createSession({projectId:project.id,entityId:null,purpose:'project-authoring',provider:model.provider,modelId:model.id});sessionId=session.id;
  const result=await agents.start(session.id,{requestId:randomUUID(),referenceAssetIds:[],text:'这是隔离能力验证，请直接完成一个可审阅方案，不提交生成。新设计要求：人物“林岚”是一名夜班女管理员，短黑发中有一缕白发，灰色长外套、深蓝裤子。基础日常状态与实验变体“林岚·受伤”是独立实体，后者只改变右手腕绷带，身份和服装保持不变；声音没给出则待补充。场景“旧候车厅”由入口、长凳区、站台门三个稳定区域构成；新设计明确入口与长凳区相邻，长凳区通向站台门，地理朝向和绝对尺寸未知。人物在此值守，给出项目剧情关系。人物各安排一张概念图；场景安排总览、从站台门回看入口的角度、长凳细节三张一致图片，后两张等待先选定场景主图。无参考图的第一张可以使用当前 Qwen 文本生成能力，后两张 useMainAppearance。请读取 entity-workflow 方法和 catalog，把所有 profile、projectRole、变体 changes、图片 prompt/invariants/unknowns 填齐，调用 propose_entity_workflow 持久化。其他缺失列未知，不追加门窗、钟表、武器等设计。'});runId=result.runId;
  console.log(JSON.stringify({owner:'Sean',runId,status:'running',provider:model.provider,modelId:model.id}));
  const deadline=Date.now()+340000;while(agents.run(runId).status==='running'&&Date.now()<deadline)await new Promise(r=>setTimeout(r,500));if(agents.run(runId).status==='running')await agents.cancel(runId);
  const state=agents.run(runId),saved=authoring.list(project.id),chat=agents.session(session.id),events=agents.events(runId,0);let applied=null;
  if(state.status==='succeeded'&&saved.length){const selected=saved[0];applied=authoring.apply(project.id,selected.id,{expectedContentHash:selected.contentHash,acknowledgeNewDesign:true});for(const step of authoring.steps(project.id).filter(s=>!s.issue))authoring.preview(project.id,step.id);}
  const report={owner:'Sean',createdAt:new Date().toISOString(),purpose:'isolated real-provider natural-language entity authoring; no image generation',provider:model.provider,modelId:model.id,runStatus:state.status,error:state.error,plans:saved,messages:chat.messages,events,applied,steps:authoring.steps(project.id),generationRunCount:store.db.prepare('SELECT count(*) AS n FROM runs').get().n,dataLocation:'private temporary directory; auth copies not exported'};
  writeFileSync(join(evidence,evidenceName),JSON.stringify(report,null,2));
  console.log(JSON.stringify({owner:'Sean',status:state.status,planCount:saved.length,candidateCount:saved[0]?.candidates.length||0,stepCount:report.steps.length,applied:!!applied,generationRunCount:report.generationRunCount,evidence:`experiments/sean_reference_authoring_goal_20261004/${evidenceName}`}));
}catch(error){console.error(JSON.stringify({owner:'Sean',status:'verification_failed',reason:typeof error.status==='number'?error.message:'Isolated authoring verification failed; inspect sanitized app evidence.'}));process.exitCode=1;}finally{await agents.close();store.db.close();rmSync(dataRoot,{recursive:true,force:true});}
