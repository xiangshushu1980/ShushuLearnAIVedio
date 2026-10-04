// Owner: Sean — real natural-language continuation, variants and text consistency in a private temporary DB.
// Reuses app-owned Pi credentials; never imports run services or invokes ComfyUI/image generation.
import {mkdtempSync,mkdirSync,copyFileSync,existsSync,writeFileSync,rmSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {join,resolve} from 'node:path';
import assert from 'node:assert/strict';
import {createStore,id} from '../server/store.mjs';
import {createProjectWorkspace} from '../server/project-workspace.mjs';
import {createEntityAuthoring} from '../server/entity-authoring.mjs';
import {createEntityManagement} from '../server/entity-management.mjs';
import {createAgentWorkspace} from '../server/agent-workspace.mjs';
const appRoot=resolve(new URL('..',import.meta.url).pathname),root=mkdtempSync(join(tmpdir(),'sean-authoring-scenarios-')),agentRoot=join(root,'agent');
mkdirSync(agentRoot,{recursive:true,mode:0o700});
for(const name of ['auth.json','models.json','models-store.json','preferences.json']){const source=join(appRoot,'.data/agent',name);if(existsSync(source))copyFileSync(source,join(agentRoot,name));}
const store=createStore(root),projects=createProjectWorkspace(store),authoring=createEntityAuthoring(store,{projectService:projects}),management=createEntityManagement(store),agents=createAgentWorkspace(store,{projectService:projects,authoringService:authoring});
const output=resolve(appRoot,'../experiments/sean_reference_authoring_goal_20261004/real-authoring-scenarios-'+Date.now()+'.json');
const evidence={owner:'Sean',createdAt:new Date().toISOString(),scope:'real Pi text/tool verification; temporary DB; no image observation or generation',scenarios:[],credentials:'private app-owned copies; not exported'};
let liveRun;
const p=projects.saveProject(null,{name:'普通城市的夜班',brief:'既有角色与候车厅，仅验证接续和变体。',worldRules:'普通现实城市，无魔法；不允许电子设备，所有道具是机械或手工物品。伤势不改变人物身份与已有服装。',synopsis:'林岚在旧候车厅值守。',decisions:'没有已选主图或空间图，不允许声称观察过图片。相邻和通向不等于同轴或直线。',entityIds:[]});
function add(name,type,flags,description,appearance){const d=projects.createEntity(p.id,{profile:{name,flags,description,appearance,voiceDescription:''},expectedRevision:projects.project(p.id).revision});const e=d.entity;store.db.prepare('UPDATE entities SET context=? WHERE id=?').run(JSON.stringify({...e.context,type}),e.id);return e.id;}
const characterId=add('林岚','character',['人物'],'夜班女管理员，短黑发中有一缕白发。','灰色长外套，深蓝裤子，身份与服装保持一致。');
const sceneId=add('旧候车厅','scene',['场景'],'入口与长凳区相邻，长凳区通向站台门。','入口、长凳区、站台门。朝向、绝对尺寸和完整平面布局未确定。');
async function talk(label,text,existingSessionId=null){
 const s=existingSessionId?{id:existingSessionId}:await agents.createSession({projectId:p.id,entityId:null,purpose:'project-authoring',provider:evidence.provider,modelId:evidence.modelId});
 const r=await agents.start(s.id,{requestId:id(),text,referenceAssetIds:[]});liveRun=r.runId;
 console.log(JSON.stringify({owner:'Sean',scenario:label,runId:liveRun,status:'running'}));
 const deadline=Date.now()+300000;while(agents.run(liveRun).status==='running'&&Date.now()<deadline)await new Promise(resolve=>setTimeout(resolve,500));
 if(agents.run(liveRun).status==='running')await agents.cancel(liveRun);
 const state=agents.run(liveRun),chat=agents.session(s.id),record={label,sessionId:s.id,runId:liveRun,runStatus:state.status,error:state.error,messages:chat.messages,events:agents.events(liveRun,0),plans:authoring.list(p.id).filter(plan=>plan.sessionId===s.id),reviews:chat.projectProposals.filter(v=>v.runId===liveRun)};
 evidence.scenarios.push(record);persist();assert.equal(state.status,'succeeded');return record;
}
function persist(){evidence.generationRunCount=store.db.prepare('SELECT count(*) n FROM runs').get().n;writeFileSync(output,JSON.stringify(evidence,null,2));}
try{
 const models=await agents.models(),m=models.find(m=>m.provider==='deepseek'&&m.id==='deepseek-flash')||models[0];if(!m)throw new Error('No configured model');evidence.provider=m.provider;evidence.modelId=m.id;
 if(process.env.REFERENCE_VERIFY_RELATIONS_ONLY==='1'||process.env.REFERENCE_VERIFY_RELATION_REPAIR==='1'){
 const forbiddenId=add('电子腕表','object',['物品'],'电子显示和电池供电的腕表。','黑色电子屏幕。');
 const equipment=management.addRelation(characterId,{targetEntityId:forbiddenId,category:'setting',type:'携带',description:'林岚携带电子腕表；这条导入关系需要核对世界规则。'}).relations.find(r=>r.targetEntityId===forbiddenId);
 const story=projects.saveRelation(p.id,null,{sourceEntityId:characterId,targetEntityId:sceneId,type:'值守',description:'林岚在候车厅值守，属于本项目剧情，不固定当前站位。',expectedRevision:projects.project(p.id).revision}).relations[0];
 const before=projects.context(p.id);
 const review=await talk('exact-relation-sources',`检查本项目全部实体和关系，完整读取每个实体。世界规则禁止电子设备，请核对林岚携带物品的固定设定关系 ${equipment.relationId}。同时核对本项目值守剧情关系 ${story.relationId}，不要把剧情动作写成固定空间事实。具体关系问题请使用 relationIds 引用实际关系 ID，在 entityIds 中包含两端。明确矛盾、未提供信息、设计建议分开。未给场景朝向或声音并不代表错误。保存项目一致性报告，不修改、不生成、不声称看图。`);
 const report=review.reviews.find(r=>r.kind==='review');assert.ok(report);
 assert.ok(report.issues.some(i=>i.category==='conflict'&&i.relationIds?.includes(equipment.relationId)&&i.entityIds.includes(characterId)&&i.entityIds.includes(forbiddenId)));
 assert.ok(report.relationSources.some(r=>r.relationId===equipment.relationId&&r.scope==='entity-setting'));
 assert.equal(report.coverage.entityCoverage,'complete');assert.deepEqual(projects.context(p.id),before);
 review.expectedRelations={equipmentRelationId:equipment.relationId,storyRelationId:story.relationId};review.projectUnchanged=true;persist();
 if(process.env.REFERENCE_VERIFY_RELATION_REPAIR==='1'){
 const repair=await talk('review-to-world-rule-proposal','我决定保留当前电子腕表和两条关系，修改项目世界规则：普通现实城市，无魔法；允许现实存在的机械、手工和电子设备；伤势不改变人物身份与已有服装。请只提出 worldRules 修改建议，使用项目修改提案工具保存，不应用；不要改任何实体、关系、剧情作用或其他项目字段。',review.sessionId);
 const update=repair.reviews.find(v=>v.kind==='update');assert.ok(update);assert.deepEqual(Object.keys(update.changes),['worldRules']);assert.deepEqual(projects.context(p.id),before);
 assert.equal(agents.session(review.sessionId).projectProposals.find(v=>v.id===report.id).stale,false);
 repair.acceptance=agents.applyProjectProposal(update.id,{expectedContentHash:update.contentHash});
 const after=projects.context(p.id);assert.deepEqual(after.entities,before.entities);assert.deepEqual(after.storyRelations,before.storyRelations);assert.notEqual(after.project.worldRules,before.project.worldRules);
 assert.equal(agents.session(review.sessionId).projectProposals.find(v=>v.id===report.id).stale,true);persist();
 const recheck=await talk('recheck-after-accepted-rules','刚才的项目规则修订已在网页接受。请重新读取当前项目、全部实体与两条关系，按新规则保存一份新的项目一致性检查报告。不要继续把电子设备允许这一点判为冲突；其他未给信息仍是待补充。不修改，不生成，不声称观察图片。',review.sessionId);
 const latest=recheck.reviews.find(v=>v.kind==='review');assert.ok(latest);assert.equal(latest.coverage.entityCoverage,'complete');assert.ok(!latest.issues.some(v=>v.category==='conflict'));assert.deepEqual(projects.context(p.id),after);recheck.projectUnchanged=true;persist();
 }

 }else{
 const before=projects.context(p.id),continuation=await talk('existing-character-and-scene',`给已有角色林岚（${characterId}）增加一张脸部＋正面／背面／侧面的 V3 Simple 多视图。给已有场景旧候车厅（${sceneId}）增加入口回看的角度和长凳细节两张图片，不新增场景实体。两者都等待各自已选主图，但目前还没选；保留原资料、服装和布局。不要再建同名实体，不自动生成；保存可审阅的工作流方案。没有给出朝向、尺度与完整平面布局，不要补成直线、同轴或南北方向。`);
 const candidates=continuation.plans.flatMap(p=>p.candidates);assert.ok(candidates.some(c=>c.existingEntityId===characterId&&c.images.some(im=>im.role==='three_view'&&im.modelId==='qwen-v3-simple-face-front-back-side'&&im.useMainAppearance)));assert.ok(candidates.some(c=>c.existingEntityId===sceneId&&c.images.length===2));assert.ok(candidates.every(c=>c.existingEntityId));
 continuation.applied=continuation.plans.map(plan=>authoring.apply(p.id,plan.id,{expectedContentHash:plan.contentHash,acknowledgeNewDesign:true}));assert.deepEqual(projects.context(p.id),before);continuation.projectUnchanged=true;persist();
 if(process.env.REFERENCE_VERIFY_CONTINUATION_ONLY!=='1'){
 const variants=await talk('new-variant-and-equipment',`基于已有林岚（${characterId}）创建独立实验变体“林岚·腕伤”，只改变右手腕增加白色绷带，脸、白发、服装保持原样。白色绷带也作为一个独立物品实体，创建人物使用它的设定关系。变体与绷带各安排一张概念图。变体需要基础林岚主形象作为身份参考，但目前还没有主图，应等待。不要修改基础林岚，不做额外新服装、伤痕、武器，也不把当前站位或镜头动作写进实体。声音信息没有提供，保留待补充。请保存可审阅方案，不生成图片。`);
 const design=variants.plans.flatMap(p=>p.candidates),v=design.find(c=>c.kind==='character'&&c.baseEntityId===characterId);assert.ok(v);assert.ok(v.images.every(im=>im.useBaseAppearance));assert.ok(design.some(c=>c.kind==='object'));assert.ok(variants.plans.some(p=>p.relations.some(r=>r.sourceKey===v.key&&r.category==='setting')));variants.applied=variants.plans.map(plan=>authoring.apply(p.id,plan.id,{expectedContentHash:plan.contentHash,acknowledgeNewDesign:true}));persist();
 const forbiddenId=add('电子腕表','object',['物品'],'电子显示和电池供电的腕表。','黑色电子屏幕。');management.addRelation(characterId,{targetEntityId:forbiddenId,category:'setting',type:'携带',description:'导入资料中的携带关系，尚需检查世界规则。'});
 const review=await talk('world-rules-and-missing-evidence',`检查这个项目所有已有实体、变体和关系是否与世界规则一致。特别核对林岚携带的物品，不要只读摘要。区分明确矛盾、缺少资料和设计建议。场景朝向／尺寸／完整平面布局与人物声音尚未提供，不能当作已经确定的错误，也不能猜方向。没有选图，不要声称图像一致。保存项目一致性检查报告，不修改资料。`);
 const report=review.reviews.find(r=>r.kind==='review');assert.ok(report);assert.ok(report.issues.some(i=>i.category==='conflict'&&i.entityIds.includes(forbiddenId)));assert.ok(report.issues.some(i=>i.category==='missing'));review.basicChecksPassed=true;
 }
 }
 evidence.steps=authoring.steps(p.id);evidence.structuralChecksPassed=true;persist();assert.equal(evidence.generationRunCount,0);
 console.log(JSON.stringify({owner:'Sean',status:'verified',scenarioCount:evidence.scenarios.length,stepCount:evidence.steps.length,generationRunCount:0,evidence:output}));
}catch(error){evidence.structuralChecksPassed=false;evidence.failure=error.code==='ERR_ASSERTION'?'Scenario assertion failed; inspect saved sanitized evidence.':typeof error.status==='number'?error.message:'Real-provider verification failed; inspect saved sanitized evidence.';persist();console.error(JSON.stringify({owner:'Sean',status:'verification-failed',reason:evidence.failure,evidence:output}));process.exitCode=1;}finally{await agents.close();store.db.close();rmSync(root,{recursive:true,force:true});}
