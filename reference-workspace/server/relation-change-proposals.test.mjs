// Owner: Sean — isolated relation proposal lifecycle, scope, read evidence and atomic acceptance.
import test from 'node:test';import assert from 'node:assert/strict';import {mkdtempSync,rmSync} from 'node:fs';import {tmpdir} from 'node:os';import {join} from 'node:path';
import {createStore,id} from './store.mjs';import {createProjectWorkspace} from './project-workspace.mjs';import {createEntityManagement} from './entity-management.mjs';import {createAgentWorkspace} from './agent-workspace.mjs';
async function fixture(t){
 const root=mkdtempSync(join(tmpdir(),'sean-relation-change-')),store=createStore(root),projects=createProjectWorkspace(store),management=createEntityManagement(store),p=projects.saveProject(null,{name:'Relation changes',brief:'Fixture',decisions:'',entityIds:[]});
 const a=projects.createEntity(p.id,{profile:{name:'A'},expectedRevision:p.revision}).entity.id,b=projects.createEntity(p.id,{profile:{name:'B'},expectedRevision:projects.project(p.id).revision}).entity.id;
 const setting=management.addRelation(a,{targetEntityId:b,category:'setting',type:'使用',description:'Old setting'}).relations[0],story=projects.saveRelation(p.id,null,{sourceEntityId:a,targetEntityId:b,type:'遇见',description:'Old plot',expectedRevision:projects.project(p.id).revision}).relations[0];
 let action=async()=>{};const runtime={models:async()=>[{provider:'fixture',id:'fixture'}],open:async({tools})=>({entries:()=>[],session:{subscribe:()=>()=>{},messages:[],dispose(){},async prompt(){await action(tools);}}})};const agents=createAgentWorkspace(store,{runtime,projectService:projects}),s=await agents.createSession({projectId:p.id,entityId:null,purpose:'project-authoring',provider:'fixture',modelId:'fixture'});
 t.after(async()=>{await agents.close();store.db.close();rmSync(root,{recursive:true,force:true});});
 const call=async(tools,name,input)=>JSON.parse((await tools.find(v=>v.name===name).execute(id(),input)).content[0].text);
 async function turn(fn){action=fn;const r=await agents.start(s.id,{requestId:id(),text:'Update fixture relation',referenceAssetIds:[]});for(let n=0;n<100&&agents.run(r.runId).status==='running';n++)await new Promise(r=>setTimeout(r,5));assert.equal(agents.run(r.runId).status,'succeeded');return agents.session(s.id).relationProposals;}
 async function propose(scope='entity-setting',relation=setting){let result;const proposals=await turn(async tools=>{for(const entityId of [a,b])await call(tools,'get_project_entity',{entityId});result=await call(tools,'propose_relation_update',{relationId:relation.relationId,scope,summary:'Change description',changes:{description:'New relation text'}});const pending=agents.session(s.id).relationProposals.find(v=>v.id===result.proposalId);assert.throws(()=>agents.applyRelationProposal(pending.id,{expectedContentHash:pending.contentHash,acknowledgeUpdate:true}),e=>e.status===409);});return proposals.find(v=>v.id===result.proposalId);}
 return {store,projects,management,agents,p,a,b,setting,story,s,call,turn,propose};
}
test('setting update waits for acceptance, preserves endpoints and commits an idempotent receipt',async t=>{
 const f=await fixture(t),before=f.projects.context(f.p.id),proposal=await f.propose();assert.deepEqual(f.projects.context(f.p.id),before);
 const input={expectedContentHash:proposal.contentHash,acknowledgeUpdate:true},receipt=f.agents.applyRelationProposal(proposal.id,input);assert.equal(receipt.alreadyApplied,false);
 const r=f.management.detail(f.a).relations.find(r=>r.relationId===f.setting.relationId);assert.equal(r.description,'New relation text');assert.equal(r.sourceEntityId,f.a);assert.equal(r.targetEntityId,f.b);assert.equal(r.category,'setting');assert.equal(f.projects.project(f.p.id).revision,before.project.revision);
 assert.equal(f.agents.applyRelationProposal(proposal.id,input).alreadyApplied,true);assert.equal(f.store.db.prepare('SELECT count(*) n FROM runs').get().n,0);
});
test('story update affects only its project and proposal body remains immutable',async t=>{
 const f=await fixture(t),other=f.projects.saveProject(null,{name:'Other',brief:'',decisions:'',entityIds:[f.a,f.b]}),before=f.projects.context(other.id),proposal=await f.propose('project-story',f.story);
 assert.throws(()=>f.store.db.prepare('UPDATE agent_relation_proposals SET body=? WHERE id=?').run('{}',proposal.id));
 f.agents.applyRelationProposal(proposal.id,{expectedContentHash:proposal.contentHash,acknowledgeUpdate:true});assert.deepEqual(f.projects.context(other.id),before);assert.equal(f.projects.relations(f.p.id)[0].description,'New relation text');
});
test('unread endpoints, wrong scope, endpoint changes and no-op edits cannot create candidates',async t=>{
 const f=await fixture(t);await f.turn(async tools=>{
 const input={relationId:f.setting.relationId,scope:'entity-setting',summary:'Fixture',changes:{description:'New'}};
 assert.equal((await f.call(tools,'propose_relation_update',input)).status,400);
 for(const entityId of [f.a,f.b])await f.call(tools,'get_project_entity',{entityId});
 for(const raw of [{...input,scope:'project-story'},{...input,changes:{targetEntityId:f.a}},{...input,changes:{description:'Old setting'}},{...input,changes:{type:'派生自'}}])assert.ok([400,404].includes((await f.call(tools,'propose_relation_update',raw)).status));
 });assert.equal(f.agents.session(f.s.id).relationProposals.length,0);
});
test('source edits and wrong hashes block acceptance without mutating relation or receipt',async t=>{
 const f=await fixture(t),proposal=await f.propose(),input={expectedContentHash:proposal.contentHash,acknowledgeUpdate:true};assert.throws(()=>f.agents.applyRelationProposal(proposal.id,{...input,expectedContentHash:'0'.repeat(64)}),e=>e.status===409);
 f.management.changeRelation(f.a,f.setting.relationId,{targetEntityId:f.b,category:'setting',type:'使用',description:'Manual newer',expectedUpdatedAt:f.setting.updatedAt});assert.throws(()=>f.agents.applyRelationProposal(proposal.id,input),e=>e.status===409);assert.equal(f.management.detail(f.a).relations[0].description,'Manual newer');assert.equal(f.agents.session(f.s.id).relationProposals[0].appliedReceipt,null);
});
test('receipt failure rolls back relation text in the same transaction',async t=>{
 const f=await fixture(t),proposal=await f.propose();f.store.db.exec("CREATE TRIGGER fail_relation_receipt BEFORE UPDATE OF applied_receipt ON agent_relation_proposals BEGIN SELECT RAISE(ABORT,'fixture failure');END");
 assert.throws(()=>f.agents.applyRelationProposal(proposal.id,{expectedContentHash:proposal.contentHash,acknowledgeUpdate:true}));assert.equal(f.management.detail(f.a).relations[0].description,'Old setting');assert.equal(f.agents.session(f.s.id).relationProposals[0].appliedReceipt,null);
});
