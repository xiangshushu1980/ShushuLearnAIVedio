// Owner: Sean — V3 dependencies and real dispatch validation, without provider calls.
import test from 'node:test';
import assert from 'node:assert/strict';
import {mkdtempSync,rmSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import sharp from 'sharp';
import {createStore,id} from './store.mjs';
import {createProjectWorkspace} from './project-workspace.mjs';
import {createEntityAuthoring} from './entity-authoring.mjs';
import {createAuthoringBatches} from './authoring-batches.mjs';
import {createRunService} from './runs.mjs';
import {createAgentWorkspace} from './agent-workspace.mjs';
import {catalog,multiviewPrompt} from './catalog.mjs';
function fixture(t){
  const root=mkdtempSync(join(tmpdir(),'sean-v3-authoring-')),store=createStore(root),projects=createProjectWorkspace(store),authoring=createEntityAuthoring(store,{projectService:projects});
  const p=projects.saveProject(null,{name:'V3 test',brief:'',decisions:'',entityIds:[]});t.after(()=>{store.db.close();rmSync(root,{recursive:true,force:true});});
  const image={key:'views',label:'人物多视图',role:'three_view',prompt:multiviewPrompt('qwen-v3-simple-three','original'),purpose:'Fixture',modelId:'qwen-v3-simple-three',styleId:'original',referenceAssetIds:[],useMainAppearance:true,useBaseAppearance:false,parameters:{},invariants:['同一服装和比例'],unknowns:[]};
  const candidate={key:'base',kind:'character',profile:{name:'Base',description:'Character',appearance:'Grey coat',voiceDescription:'',flags:[]},baseEntityId:null,variationOf:null,changes:'',projectRole:{role:'',plotNotes:''},unknowns:[],images:[image]};
  const plan={title:'V3 experiment',summary:'Test only',candidates:[candidate],relations:[],questions:[]};
  const apply=body=>{const saved=authoring.save(p.id,body);return authoring.apply(p.id,saved.id,{expectedContentHash:saved.contentHash,acknowledgeNewDesign:true});};
  async function select(entityId){const bytes=await sharp({create:{width:3,height:3,channels:3,background:'#7a8899'}}).png().toBuffer();const stage=await store.stageImage(bytes,'Mock concept',entityId,'concept',null);const asset=store.transaction(()=>store.registerStages([stage]))[0];return store.confirmAppearance(entityId,asset.id,store.visualState(entityId).appearance?.id||null).appearance;}
  return {store,projects,authoring,p,plan,image,candidate,apply,select};
}
test('all V3 layouts compile against the chosen current appearance without submitting generation',async t=>{
  const f=fixture(t);f.plan.candidates[0].images=catalog.multiview.map(m=>({...f.image,key:m.layout,modelId:m.id,prompt:m.promptsByStyle.original}));const applied=f.apply(f.plan);
  for(const step of f.authoring.steps(f.p.id)){assert.match(step.issue,/主形象/);assert.throws(()=>f.authoring.preview(f.p.id,step.id),e=>e.status===409);}
  const main=await f.select(applied.entities.base),runs=createRunService(f.store);
  for(const step of f.authoring.steps(f.p.id)){
    const preview=f.authoring.preview(f.p.id,step.id);assert.equal(preview.previewOnly,true);assert.equal(preview.workflow['5'].inputs.prompt.includes(step.prompt),true);
    const prepared=f.authoring.prepareRun(f.p.id,step.id,step.contentHash);assert.equal(prepared.input.appearanceId,main.id);assert.deepEqual(prepared.input.references,[main.assetId]);
    const origin={stepId:step.id,stepHash:step.contentHash,batchId:id(),itemId:id()},proof=runs.previewPrepared(step.entityId,prepared.input,origin);assert.equal(proof.authoring.role,'three_view');assert.equal(proof.template.hash,preview.template.hash);assert.throws(()=>runs.previewPrepared(step.entityId,{...prepared.input,appearanceId:id()},origin),e=>e.status===409);
  }
  assert.equal(f.store.db.prepare('SELECT count(*) n FROM runs').get().n,0);
});
test('scene V3, non-V3 view model and missing current-appearance dependency are rejected',t=>{
  const f=fixture(t);for(const patch of [{kind:'scene'},{images:[{...f.image,modelId:'qwen-image-2.1'}]},{images:[{...f.image,useMainAppearance:false}]},{images:[{...f.image,role:'concept'}]}]){const body=structuredClone(f.plan);Object.assign(body.candidates[0],patch);assert.throws(()=>f.authoring.save(f.p.id,body),e=>e.status===400);}
  assert.equal(f.store.db.prepare('SELECT count(*) n FROM entity_authoring_plans').get().n,0);
});
test('variant views wait for variant own main image even when base appearance exists',async t=>{
  const f=fixture(t);f.plan.candidates.push({...f.candidate,key:'injured',profile:{...f.candidate.profile,name:'Injured'},variationOf:'base',changes:'Wrist bandage',images:[{...f.image}]});const result=f.apply(f.plan);await f.select(result.entities.base);
  const step=f.authoring.steps(f.p.id).find(s=>s.candidateKey==='injured');assert.equal(step.useBaseAppearance,false);assert.equal(step.referenceEntityId,result.entities.injured);assert.match(step.issue,/主形象/);const main=await f.select(result.entities.injured),input=f.authoring.prepareRun(f.p.id,step.id,step.contentHash).input;assert.equal(input.appearanceId,main.id);assert.deepEqual(input.references,[main.assetId]);
});
test('batch waits for manual main selection, resumes V3 input and rejects subsequent main change',async t=>{
  const f=fixture(t);f.apply(f.plan);const step=f.authoring.steps(f.p.id)[0],submitted=[],real=createRunService(f.store),runs={startPrepared(e,input,key,origin){real.previewPrepared(e,input,origin);submitted.push(input);return f.store.createRun(e,{model:{id:input.modelId},prompt:input.prompt,references:input.references.map(id=>({id})),appearance:{id:input.appearanceId},stage:'multiview'},key).run;}};
  const batches=createAuthoringBatches(f.store,{authoring:f.authoring,projects:f.projects,runs,autoRun:false});t.after(()=>batches.close());const make=()=>batches.create(f.p.id,{title:'V3 batch',requestId:id(),steps:[{stepId:step.id,expectedStepHash:step.contentHash}],acknowledgePlan:true});
  let b=make();batches.resume(f.p.id,b.id,{expectedRevision:b.revision,acknowledgeGeneration:true});await batches.tick(b.id);b=batches.get(f.p.id,b.id);assert.equal(b.status,'waiting');assert.equal(submitted.length,0);
  const main=await f.select(step.entityId);batches.resume(f.p.id,b.id,{expectedRevision:b.revision,acknowledgeGeneration:true});await batches.tick(b.id);assert.equal(submitted.length,1);assert.equal(submitted[0].appearanceId,main.id);f.store.updateRun(batches.get(f.p.id,b.id).items[0].runId,{status:'succeeded'});await batches.tick(b.id);assert.equal(batches.get(f.p.id,b.id).status,'completed');
  const next=make();await f.select(step.entityId);batches.resume(f.p.id,next.id,{expectedRevision:next.revision,acknowledgeGeneration:true});await batches.tick(next.id);assert.equal(batches.get(f.p.id,next.id).items[0].status,'review');assert.equal(submitted.length,1);
});

test('Agent catalog exposes V3 template prompts and saves a three_view proposal without creating entities',async t=>{
  const f=fixture(t);let seen;const runtime={models:async()=>[{provider:'fixture',id:'fixture'}],open:async({tools})=>({entries:()=>[],session:{subscribe:()=>()=>{},messages:[],dispose(){},async prompt(){seen=JSON.parse((await tools.find(t=>t.name==='get_entity_workflow_catalog').execute('catalog',{})).content[0].text);const result=JSON.parse((await tools.find(t=>t.name==='propose_entity_workflow').execute('propose',f.plan)).content[0].text);assert.equal(result.savedAs,'proposal-only');}}})};
  const agents=createAgentWorkspace(f.store,{runtime,projectService:f.projects,authoringService:f.authoring});t.after(()=>agents.close());const session=await agents.createSession({projectId:f.p.id,entityId:null,purpose:'project-authoring',provider:'fixture',modelId:'fixture'}),run=await agents.start(session.id,{requestId:id(),text:'安排人物三视图',referenceAssetIds:[]});
  for(let n=0;n<100&&agents.run(run.runId).status==='running';n++)await new Promise(r=>setTimeout(r,5));assert.equal(agents.run(run.runId).status,'succeeded');assert.equal(seen.multiview.length,3);assert.ok(seen.models.some(m=>m.stage==='multiview'));assert.ok(seen.multiview.every(m=>m.promptsByStyle.original));assert.equal(f.authoring.list(f.p.id)[0].candidates[0].images[0].role,'three_view');assert.equal(f.projects.project(f.p.id).entityIds.length,0);assert.equal(f.store.db.prepare('SELECT count(*) n FROM runs').get().n,0);
});
