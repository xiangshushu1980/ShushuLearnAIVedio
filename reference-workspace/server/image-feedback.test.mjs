// Owner: Sean — isolated feedback/correction tests; images, model runtime and dispatch are fixtures.
import test from 'node:test';
import assert from 'node:assert/strict';
import {mkdtempSync,rmSync,writeFileSync} from 'node:fs';
import {join} from 'node:path';
import {tmpdir} from 'node:os';
import sharp from 'sharp';
import {createStore,id} from './store.mjs';
import {createProjectWorkspace} from './project-workspace.mjs';
import {createEntityAuthoring} from './entity-authoring.mjs';
import {createAgentWorkspace} from './agent-workspace.mjs';
import {createRunService} from './runs.mjs';
import {imageReviewSources} from './image-feedback.mjs';
import {createAuthoringBatches} from './authoring-batches.mjs';

async function fixture(t){
  const root=mkdtempSync(join(tmpdir(),'sean-image-feedback-')),store=createStore(root),projects=createProjectWorkspace(store),authoring=createEntityAuthoring(store,{projectService:projects});
  const p=projects.saveProject(null,{name:'Feedback fixture',brief:'Only fixture evidence',decisions:'Never real generation',entityIds:[]});
  const im={key:'overview',label:'Station overview',role:'scene_overview',prompt:'One entrance only.',purpose:'Fixed layout',modelId:'qwen-image-2.1',styleId:'original',referenceAssetIds:[],useMainAppearance:false,useBaseAppearance:false,parameters:{},invariants:['One entrance'],unknowns:['Unseen rooms']};
  const c={key:'station',kind:'scene',profile:{name:'Station',description:'Station fixture',appearance:'One entrance',voiceDescription:'',flags:['场景']},baseEntityId:null,variationOf:null,changes:'',projectRole:{role:'Opening',plotNotes:''},unknowns:[],images:[im,{...im,key:'detail',label:'Clock detail',role:'scene_detail'}]};
  const plan=authoring.save(p.id,{title:'Fixture plan',summary:'Fake scene',candidates:[c],relations:[],questions:[]});authoring.apply(p.id,plan.id,{expectedContentHash:plan.contentHash,acknowledgeNewDesign:true});
  const steps=authoring.steps(p.id),step=steps.find(s=>s.key==='overview'),other=steps.find(s=>s.key==='detail');
  const bytes=await sharp({create:{width:3,height:3,channels:3,background:'#ffffff'}}).png().toBuffer();
  async function output(s){const r=store.createRun(s.entityId,{prompt:s.prompt,references:[],authoring:{stepId:s.id,sourceRevision:s.contentHash,rootStepId:s.rootStepId,version:1}},id()).run;const stage=await store.stageImage(bytes,'Mock output only',s.entityId,'concept',r.id,{source:'fake-feedback'});const asset=store.transaction(()=>store.registerStages([stage]))[0];store.updateRun(r.id,{status:'succeeded'});return asset;}
  const asset=await output(step),otherAsset=await output(other);
  let action=async()=>{};
  const runtime={models:async()=>[{provider:'fixture',id:'fixture'}],open:async({tools})=>({entries:()=>[],session:{subscribe:()=>()=>{},messages:[],dispose(){},async prompt(){await action(tools);}}})};
  const agents=createAgentWorkspace(store,{runtime,projectService:projects,authoringService:authoring});
  t.after(async()=>{await agents.close();store.db.close();rmSync(root,{recursive:true,force:true});});
  const session=await agents.createSession({projectId:p.id,entityId:null,purpose:'project-authoring',provider:'fixture',modelId:'fixture'});
  const call=async(tools,name,input)=>{const r=await tools.find(v=>v.name===name).execute(id(),input);return JSON.parse(r.content[0].text);};
  async function turn(fn,refs=[asset.id]){action=fn;const r=await agents.start(session.id,{requestId:id(),text:'Fixture only',referenceAssetIds:refs});for(let n=0;n<200&&agents.run(r.runId).status==='running';n++)await new Promise(r=>setTimeout(r,5));assert.equal(agents.run(r.runId).status,'succeeded');return r;}
  async function review(){let saved;await turn(async tools=>{await call(tools,'get_project_entity',{entityId:step.entityId});await call(tools,'get_entity_workflow_step',{stepId:step.id});await tools.find(v=>v.name==='view_reference_image').execute(id(),{assetId:asset.id});saved=await call(tools,'propose_image_consistency_review',{summary:'Mock door mismatch, not model quality.',reviewedAssetIds:[asset.id],conclusion:'conflicts',issues:[{entityIds:[step.entityId],assetIds:[asset.id],category:'conflict',description:'Extra entrance',suggestion:'Restore one entrance'}]});});return authoring.imageReview(p.id,saved.proposalId);}
  const revision=(report,target=step,assets=[asset.id])=>({expectedStepHash:target.contentHash,expectedActiveStepId:target.activeStepId,expectedContextHash:authoring.basis(p.id).contextHash,reason:'Correct mock feedback',image:{...im,key:target.key,role:target.role,label:target.label,prompt:'Exactly one entrance; no additional entrance.'},feedback:{reviewId:report.id,expectedReviewHash:report.contentHash,assetIds:assets}});
  return {store,projects,authoring,agents,p,step,other,asset,otherAsset,bytes,turn,call,review,revision};
}

test('observed report links original step; assistant correction remains pending until user adoption and explicit new batch',async t=>{
  const f=await fixture(t),report=await f.review();assert.equal(report.stale,false);assert.equal(report.workflowSources[0].workflow.stepId,f.step.id);assert.equal(report.workflowSources[0].workflow.fullStepRead,true);
  let unread,result;
  await f.turn(async tools=>{await f.call(tools,'get_entity_workflow_step',{stepId:f.step.id});const {expectedContextHash,...input}=f.revision(report);unread=await f.call(tools,'propose_image_step_revision',{stepId:f.step.id,...input});await f.call(tools,'get_image_consistency_review',{reviewId:report.id});result=await f.call(tools,'propose_image_step_revision',{stepId:f.step.id,...input});assert.equal(result.savedAs,'proposal-only');const next=f.authoring.getStep(f.p.id,result.stepId);assert.throws(()=>f.authoring.adoptStep(f.p.id,next.id,{expectedStepHash:next.contentHash,expectedActiveStepId:f.step.id,acknowledgeReview:true}),e=>e.status===409);});
  assert.equal(unread.status,400);const next=f.authoring.getStep(f.p.id,result.stepId);assert.equal(next.revisionStatus,'proposal');assert.equal(next.revisionBasis.feedback.reviewId,report.id);assert.equal(next.revisionBasis.feedback.assets[0].workflow.version,1);assert.equal(f.authoring.getStep(f.p.id,f.step.id).isCurrent,true);
  f.authoring.adoptStep(f.p.id,next.id,{expectedStepHash:next.contentHash,expectedActiveStepId:f.step.id,acknowledgeReview:true});
  const prepared=f.authoring.prepareRun(f.p.id,next.id,next.contentHash),preview=createRunService(f.store).previewPrepared(next.entityId,prepared.input,{stepId:next.id,stepHash:next.contentHash});assert.equal(preview.authoring.feedback.reviewId,report.id);
  let submissions=0;const runs={startPrepared(entityId,input,key){submissions++;return f.store.createRun(entityId,{prompt:input.prompt,references:input.references.map(id=>({id}))},key).run;}};
  const batches=createAuthoringBatches(f.store,{authoring:f.authoring,projects:f.projects,runs,autoRun:false});t.after(()=>batches.close());
  const b=batches.create(f.p.id,{title:'Corrected experiment',requestId:id(),steps:[{stepId:next.id,expectedStepHash:next.contentHash}],acknowledgePlan:true});await batches.tick(b.id);assert.equal(submissions,0);batches.resume(f.p.id,b.id,{expectedRevision:b.revision,acknowledgeGeneration:true});await batches.tick(b.id);assert.equal(submissions,1);assert.equal(f.authoring.getStep(f.p.id,f.step.id).prompt,f.step.prompt);assert.equal(f.store.db.prepare('SELECT count(*) n FROM entities').get().n,1);
});

test('feedback scope rejects wrong logical step, wrong report hash, unreviewed image and foreign project',async t=>{
  const f=await fixture(t),r=await f.review();assert.throws(()=>f.authoring.reviseStep(f.p.id,f.other.id,f.revision(r,f.other)),e=>e.status===400);assert.throws(()=>f.authoring.reviseStep(f.p.id,f.step.id,f.revision(r,f.step,[f.otherAsset.id])),e=>e.status===400);const input=f.revision(r);assert.throws(()=>f.authoring.reviseStep(f.p.id,f.step.id,{...input,feedback:{...input.feedback,expectedReviewHash:'0'.repeat(64)}}),e=>e.status===409);const foreign=f.projects.saveProject(null,{name:'Foreign',brief:'',decisions:'',entityIds:[]});assert.throws(()=>f.authoring.imageReview(foreign.id,r.id),e=>e.status===404);
});

test('changed evidence or project context invalidates report and blocks proposed revision adoption',async t=>{
  const f=await fixture(t),r=await f.review(),result=f.authoring.reviseStep(f.p.id,f.step.id,f.revision(r)),next=f.authoring.getStep(f.p.id,result.stepId);
  writeFileSync(f.store.assetPath(f.asset.id),Buffer.from('Changed fixture bytes'));assert.equal(f.authoring.imageReview(f.p.id,r.id).stale,true);assert.throws(()=>f.authoring.adoptStep(f.p.id,next.id,{expectedStepHash:next.contentHash,expectedActiveStepId:f.step.id,acknowledgeReview:true}),e=>e.status===409);writeFileSync(f.store.assetPath(f.asset.id),f.bytes);
  const p=f.projects.project(f.p.id);f.projects.saveProject(f.p.id,{name:p.name,brief:'New project brief',decisions:p.decisions,entityIds:p.entityIds,expectedRevision:p.revision});assert.equal(f.authoring.imageReview(f.p.id,r.id).stale,true);assert.throws(()=>f.authoring.reviseStep(f.p.id,f.step.id,f.revision(r)),e=>e.status===409);
});

test('review cannot name an unobserved issue image or claim conflicts without a conflict finding',async t=>{
  const f=await fixture(t);let badImage,badConclusion;await f.turn(async tools=>{await tools.find(v=>v.name==='view_reference_image').execute(id(),{assetId:f.asset.id});const report={summary:'Fixture',reviewedAssetIds:[f.asset.id],conclusion:'conflicts',issues:[{entityIds:[f.step.entityId],assetIds:[f.otherAsset.id],category:'conflict',description:'Wrong scope',suggestion:'Test'}]};badImage=await f.call(tools,'propose_image_consistency_review',report);badConclusion=await f.call(tools,'propose_image_consistency_review',{...report,issues:[]});});assert.equal(badImage.status,400);assert.equal(badConclusion.status,400);assert.equal(f.agents.session(f.agents.sessions(f.p.id,null,'project-authoring')[0].id).projectProposals.length,0);
});

test('assistant may retain previously explicit references, but may not silently add an unselected reference',async t=>{
  const f=await fixture(t),input=f.revision({id:id(),contentHash:'0'.repeat(64)});delete input.feedback;input.image.referenceAssetIds=[f.otherAsset.id];const v=f.authoring.reviseStep(f.p.id,f.step.id,input),old=f.authoring.getStep(f.p.id,v.stepId);f.authoring.adoptStep(f.p.id,old.id,{expectedStepHash:old.contentHash,expectedActiveStepId:f.step.id,acknowledgeReview:true});const current=f.authoring.getStep(f.p.id,old.id);let retained,added;await f.turn(async tools=>{await f.call(tools,'get_entity_workflow_step',{stepId:old.id});const {expectedContextHash,feedback,...raw}=f.revision({id:id(),contentHash:'0'.repeat(64)},current);raw.image.referenceAssetIds=[f.otherAsset.id];retained=await f.call(tools,'propose_image_step_revision',{stepId:old.id,...raw});added=await f.call(tools,'propose_image_step_revision',{stepId:old.id,...raw,image:{...raw.image,referenceAssetIds:[f.asset.id]}});},[]);assert.equal(retained.savedAs,'proposal-only');assert.equal(added.status,400);
});

test('uploaded image metadata cannot fabricate a generation workflow source',async t=>{
  const f=await fixture(t),stage=await f.store.stageImage(f.bytes,'Imported fixture',f.step.entityId,'setting',null,{authoring:{stepId:f.step.id,sourceRevision:f.step.contentHash}}),a=f.store.transaction(()=>f.store.registerStages([stage]))[0];const source=imageReviewSources(f.store,f.authoring,f.p.id,[a.id])[0];assert.equal(source.workflow,null);assert.equal(source.runId,null);
});

test('consistent image reports require full owner and source-step reads, while inconclusive observations remain saveable',async t=>{
  const f=await fixture(t);let missingOwner,missingStep,complete;
  await f.turn(async tools=>{
    await tools.find(v=>v.name==='view_reference_image').execute(id(),{assetId:f.asset.id});
    const input={summary:'Fixture read coverage only',reviewedAssetIds:[f.asset.id],conclusion:'consistent',issues:[]};
    missingOwner=await f.call(tools,'propose_image_consistency_review',input);
    const partial=await f.call(tools,'propose_image_consistency_review',{...input,conclusion:'inconclusive'});
    assert.ok(partial.proposalId);
    await f.call(tools,'get_project_entity',{entityId:f.step.entityId});
    missingStep=await f.call(tools,'propose_image_consistency_review',input);
    await f.call(tools,'get_entity_workflow_step',{stepId:f.step.id});
    complete=await f.call(tools,'propose_image_consistency_review',input);
  });
  assert.equal(missingOwner.status,400);assert.equal(missingStep.status,400);
  assert.equal(missingOwner.details.comparisonCoverage.missingEntityIds[0],f.step.entityId);
  assert.equal(missingStep.details.comparisonCoverage.unreadStepIds[0],f.step.id);
  const saved=f.authoring.imageReview(f.p.id,complete.proposalId);
  assert.equal(saved.comparisonCoverage.status,'complete');assert.deepEqual(saved.comparisonCoverage.unreadStepIds,[]);
  assert.equal(f.store.db.prepare('SELECT count(*) n FROM runs').get().n,2);
});

test('every observed output source step is required; reading one view cannot cover another',async t=>{
  const f=await fixture(t);let partial,complete;
  await f.turn(async tools=>{
    await f.call(tools,'get_project_entity',{entityId:f.step.entityId});
    await f.call(tools,'get_entity_workflow_step',{stepId:f.step.id});
    for(const asset of [f.asset,f.otherAsset])await tools.find(v=>v.name==='view_reference_image').execute(id(),{assetId:asset.id});
    const input={summary:'Two-view fixture',reviewedAssetIds:[f.asset.id,f.otherAsset.id],conclusion:'consistent',issues:[]};
    partial=await f.call(tools,'propose_image_consistency_review',input);
    await f.call(tools,'get_entity_workflow_step',{stepId:f.other.id});
    complete=await f.call(tools,'propose_image_consistency_review',input);
  },[f.asset.id,f.otherAsset.id]);
  assert.equal(partial.status,400);assert.deepEqual(partial.details.comparisonCoverage.unreadStepIds,[f.other.id]);
  assert.equal(f.authoring.imageReview(f.p.id,complete.proposalId).comparisonCoverage.stepIds.length,2);
});

test('imported pictures compare with entity text without fabricated generation-step provenance',async t=>{
  const f=await fixture(t),stage=await f.store.stageImage(f.bytes,'Imported coverage fixture',f.step.entityId,'setting'),asset=f.store.transaction(()=>f.store.registerStages([stage]))[0];let result;
  await f.turn(async tools=>{
    await f.call(tools,'get_project_entity',{entityId:f.step.entityId});
    await tools.find(v=>v.name==='view_reference_image').execute(id(),{assetId:asset.id});
    result=await f.call(tools,'propose_image_consistency_review',{summary:'Registered text comparison only',reviewedAssetIds:[asset.id],conclusion:'consistent',issues:[]});
  },[asset.id]);
  const report=f.authoring.imageReview(f.p.id,result.proposalId);
  assert.equal(report.comparisonCoverage.status,'complete');assert.deepEqual(report.comparisonCoverage.stepIds,[]);assert.deepEqual(report.comparisonCoverage.untrackedAssetIds,[asset.id]);
});


test('image observation returns Pi SDK data/mimeType content with decodable pixels and repeat-view cache',async t=>{
 const f=await fixture(t);await f.turn(async tools=>{
  const view=tools.find(v=>v.name==='view_reference_image');
  const result=await view.execute(id(),{assetId:f.asset.id}),image=result.content.find(v=>v.type==='image');
  assert.equal(image.mimeType,'image/png');assert.equal(typeof image.data,'string');assert.equal(image.source,undefined);
  const metadata=await sharp(Buffer.from(image.data,'base64')).metadata();assert.equal(metadata.width,3);assert.equal(metadata.height,3);
  const again=await view.execute(id(),{assetId:f.asset.id});assert.ok(!again.content.some(v=>v.type==='image'));assert.equal(JSON.parse(again.content[0].text).alreadyViewed,true);
 });
});
