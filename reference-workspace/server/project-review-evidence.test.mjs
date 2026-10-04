// Owner: Sean — entity findings require full reading, with durable complete/partial text coverage.
import test from 'node:test';
import assert from 'node:assert/strict';
import {mkdtempSync,rmSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import {createStore,id} from './store.mjs';
import {createProjectWorkspace} from './project-workspace.mjs';
import {createAgentWorkspace} from './agent-workspace.mjs';
async function fixture(t,{selected=false}={}){const root=mkdtempSync(join(tmpdir(),'sean-project-review-')),store=createStore(root),projects=createProjectWorkspace(store),p=projects.saveProject(null,{name:'Review',brief:'Test',decisions:'',entityIds:[]});const first=projects.createEntity(p.id,{profile:{name:'Character'},expectedRevision:p.revision}).entity.id,second=projects.createEntity(p.id,{profile:{name:'Scene',flags:['场景']},expectedRevision:projects.project(p.id).revision}).entity.id;let reading=[],issues=[],result;const runtime={models:async()=>[{provider:'fixture',id:'fixture'}],open:async({tools})=>({entries:()=>[],session:{subscribe:()=>()=>{},messages:[],dispose(){},async prompt(){for(const entityId of reading)await tools.find(t=>t.name==='get_project_entity').execute('read',{entityId});result=JSON.parse((await tools.find(t=>t.name==='propose_project_review').execute('review',{summary:'Only actual reading',issues})).content[0].text);}}})};const agents=createAgentWorkspace(store,{runtime,projectService:projects});t.after(async()=>{await agents.close();store.db.close();rmSync(root,{recursive:true,force:true});});const session=await agents.createSession({projectId:p.id,entityId:selected?first:null,purpose:'project-authoring',provider:'fixture',modelId:'fixture'});async function submit(ids,findings){reading=ids;issues=findings;const run=await agents.start(session.id,{requestId:id(),text:'Check',referenceAssetIds:[]});for(let n=0;n<100&&agents.run(run.runId).status==='running';n++)await new Promise(r=>setTimeout(r,5));assert.equal(agents.run(run.runId).status,'succeeded');return {result,reports:agents.session(session.id).projectProposals};}return {store,agents,projects,p,first,second,submit};}
const issue=entityIds=>({entityIds,category:'missing',description:'Voice not specified',suggestion:'Ask user when needed'});
test('a text issue cannot cite an unread entity or confuse previous-turn reading with current evidence',async t=>{const f=await fixture(t);let r=await f.submit([],[issue([f.first])]);assert.equal(r.result.status,400);assert.equal(r.reports.length,0);r=await f.submit([f.first],[issue([f.first,f.second])]);assert.equal(r.result.status,400);assert.equal(r.reports.length,0);r=await f.submit([f.first],[issue([f.first])]);assert.equal(r.reports.length,1);r=await f.submit([],[issue([f.first])]);assert.equal(r.result.status,400);assert.equal(r.reports.length,1);});
test('partial and complete coverage record exact unread IDs without asserting image verification',async t=>{const f=await fixture(t);let r=await f.submit([f.first],[issue([f.first])]);const partial=r.reports[0];assert.equal(partial.coverage.entityCoverage,'partial');assert.deepEqual(partial.coverage.unreviewedEntityIds,[f.second]);assert.deepEqual(partial.coverage.viewedImageAssetIds,[]);r=await f.submit([f.first,f.second],[issue([f.first])]);const complete=r.reports[1];assert.equal(complete.coverage.entityCoverage,'complete');assert.deepEqual(complete.coverage.unreviewedEntityIds,[]);assert.equal(complete.coverage.reviewedEntityIds.length,2);assert.equal(f.store.db.prepare('SELECT count(*) n FROM runs').get().n,0);});
test('project-wide missing fields may be reported without attributing findings to unread entities',async t=>{const f=await fixture(t),r=await f.submit([],[{...issue([]),description:'World rules missing'}]);assert.equal(r.reports.length,1);assert.equal(r.reports[0].coverage.entityCoverage,'partial');assert.deepEqual(r.reports[0].coverage.unreviewedEntityIds.sort(),[f.first,f.second].sort());});

test('selecting an entity does not count as having read its full context',async t=>{const f=await fixture(t,{selected:true}),r=await f.submit([],[issue([f.first])]);assert.equal(r.result.status,400);assert.equal(r.reports.length,0);});

test('relation findings require two fully read endpoints and persist the actual project story source',async t=>{
 const f=await fixture(t),saved=f.projects.saveRelation(f.p.id,null,{sourceEntityId:f.first,targetEntityId:f.second,type:'进入',description:'Character enters scene',expectedRevision:f.projects.project(f.p.id).revision}),r=saved.relations[0];
 const finding={...issue([f.first,f.second]),relationIds:[r.relationId]};
 let turn=await f.submit([f.first],[finding]);assert.equal(turn.result.status,400);
 turn=await f.submit([f.first,f.second],[{...finding,entityIds:[f.first]}]);assert.equal(turn.result.status,400);
 turn=await f.submit([f.first,f.second],[finding]);assert.equal(turn.reports.length,1);
 const report=turn.reports[0],source=report.relationSources[0];assert.equal(source.scope,'project-story');assert.equal(source.description,r.description);assert.equal(source.relationId,r.relationId);assert.equal(source.contentHash.length,64);
 f.projects.saveRelation(f.p.id,r.relationId,{sourceEntityId:f.first,targetEntityId:f.second,type:'离开',description:'Revised plot',expectedRevision:f.projects.project(f.p.id).revision});
 const historical=f.agents.session(f.agents.sessions(f.p.id,null,'project-authoring')[0].id).projectProposals[0];assert.equal(historical.stale,true);assert.equal(historical.relationSources[0].description,'Character enters scene');
});

test('unknown, duplicate, foreign and out-of-project setting relation references are rejected',async t=>{
 const f=await fixture(t),{createEntityManagement}=await import('./entity-management.mjs'),management=createEntityManagement(f.store);
 const details=management.addRelation(f.first,{targetEntityId:f.second,category:'setting',type:'关联',description:'Stable fixture link'}),r=details.relations[0];
 let turn=await f.submit([f.first,f.second],[{...issue([f.first,f.second]),relationIds:[r.relationId]}]);assert.equal(turn.reports[0].relationSources[0].scope,'entity-setting');
 for(const ids of [[id()],[r.relationId,r.relationId]]){turn=await f.submit([f.first,f.second],[{...issue([f.first,f.second]),relationIds:ids}]);assert.ok([400,404].includes(turn.result.status));}
 const external=management.create({name:'Outside'}).entity.id,outside=management.addRelation(f.first,{targetEntityId:external,category:'setting',type:'外部',description:''}).relations.find(r=>r.targetEntityId===external);
 turn=await f.submit([f.first,f.second],[{...issue([f.first,f.second]),relationIds:[outside.relationId]}]);assert.equal(turn.result.status,404);
 const legacy=management.addRelation(f.first,{targetEntityId:f.second,category:'story',type:'历史剧情',description:'Not assigned to this project'}).relations.find(r=>r.category==='story');
 turn=await f.submit([f.first,f.second],[{...issue([f.first,f.second]),relationIds:[legacy.relationId]}]);assert.equal(turn.reports.at(-1).relationSources[0].scope,'legacy-unassigned-story');
 assert.equal(f.store.db.prepare('SELECT count(*) n FROM runs').get().n,0);
});
