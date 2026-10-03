// Owner: Sean — scene variation identity and spatial draft inheritance without real generation.
import test from 'node:test';
import assert from 'node:assert/strict';
import {mkdtempSync,rmSync} from 'node:fs';
import {join} from 'node:path';
import {tmpdir} from 'node:os';
import sharp from 'sharp';
import {createStore,id,now} from './store.mjs';
import {createProjectWorkspace} from './project-workspace.mjs';
import {createEntityManagement} from './entity-management.mjs';
import {createEntityAuthoring} from './entity-authoring.mjs';
import {createReferenceExport} from './reference-export.mjs';
import {canonicalJSON,contentHash} from './content-hash.mjs';

const image={key:'overview',label:'State overview',role:'scene_overview',prompt:'Image 1 is the same station. Change only the declared window condition.',purpose:'State comparison',modelId:'qwen-image-2.1',styleId:'original',referenceAssetIds:[],useMainAppearance:false,useBaseAppearance:false,parameters:{},invariants:['Preserve the entrance and platform relationship'],unknowns:['Absolute orientation unknown']};
const candidate=(key,baseEntityId=null)=>({key,kind:'scene',profile:{name:key,description:'A station state',appearance:'Window condition only',voiceDescription:'',flags:['场景']},baseEntityId,variationOf:null,changes:baseEntityId?'A broken window only':'',projectRole:{role:'Fixture',plotNotes:''},unknowns:[],images:[{...image}]});
async function fixture(t){
  const root=mkdtempSync(join(tmpdir(),'sean-scene-variant-')),s=createStore(root),projects=createProjectWorkspace(s),m=createEntityManagement(s),a=createEntityAuthoring(s,{projectService:projects}),p=projects.saveProject(null,{name:'Test scene variations',brief:'Explicit fixed layout only',decisions:'No real generation',entityIds:[]});
  const base=projects.createEntity(p.id,{profile:{name:'Base station',flags:['场景'],description:'Entrance adjacent to bench area',appearance:'Two windows'},expectedRevision:p.revision}).entity;
  const bytes=await sharp({create:{width:3,height:3,channels:3,background:'#777777'}}).png().toBuffer(),stage=await s.stageImage(bytes,'Fixture overview',base.id,'concept',null),asset=s.transaction(()=>s.registerStages([stage]))[0];s.confirmAppearance(base.id,asset.id,null);
  const document={owner:'Sean',schemaVersion:1,scope:'fixed_scene_space',frame:{description:'Use entrance wall as the local front, not a compass direction',status:'known'},elements:[{id:'entrance',kind:'structure',label:'Entrance',description:'Fixed entrance',position:'Adjacent to bench area',orientation:'',scale:'',status:'known'},{id:'bench',kind:'area',label:'Bench area',description:'Bench area',position:'Adjacent to entrance',orientation:'',scale:'',status:'known'}],links:[{id:'adjacent',from:'entrance',to:'bench',description:'Adjacent, no further alignment inferred',status:'known'}],routes:[{id:'walk',label:'Passage',via:['entrance','bench'],description:'Fixed passage, no character motion',status:'known'}],unknowns:['Exact size pending'],referenceAssetIds:[asset.id]};
  const draft=m.spatial.save(base.id,{expectedVersionId:null,document});m.spatial.confirm(base.id,{expectedVersionId:draft.expectedVersionId,expectedContentHash:draft.summary.contentHash,expectedEvidenceStateHash:draft.evidenceStateHash,acknowledgeConsistency:true});
  t.after(()=>{s.db.close();rmSync(root,{recursive:true,force:true});});
  function plan(candidates=[candidate('damaged',base.id)]){return a.save(p.id,{title:'Scene state experiment',summary:'Same space, altered window condition',candidates,relations:[],questions:[]});}
  function apply(plan){return a.apply(p.id,plan.id,{expectedContentHash:plan.contentHash,acknowledgeNewDesign:true});}
  return {s,projects,m,a,p,base,asset,document,plan,apply};
}

test('scene variant uses base overview and persists unconfirmed stable anchors; default export never promotes them',async t=>{
  const f=await fixture(t),plan=f.plan();assert.equal(plan.candidates[0].images[0].useBaseAppearance,true);assert.equal(plan.candidates[0].copySpatialDraft,true);const applied=f.apply(plan),entityId=applied.entities.damaged,step=f.a.steps(f.p.id).find(s=>s.entityId===entityId);assert.equal(step.referenceEntityId,f.base.id);assert.deepEqual(step.referenceAssetIds,[f.asset.id]);
  const state=f.m.spatial.get(entityId);assert.equal(state.summary.status,'draft');assert.deepEqual(state.document.elements.map(e=>e.id),['entrance','bench']);assert.equal(state.document.frame.status,'pending');assert.ok(state.document.elements.every(e=>e.status==='pending'));assert.ok(state.document.links.every(e=>e.status==='pending'));assert.ok(state.document.routes.every(e=>e.status==='pending'));assert.deepEqual(state.document.referenceAssetIds,[]);assert.equal(state.document.unknowns.some(v=>v.includes('broken window')),true);
  const detail=f.m.detail(entityId);assert.equal(detail.derivedFrom.options.sourceSpatialVersionId,f.m.spatial.get(f.base.id).expectedVersionId);const prepared=f.a.prepareRun(f.p.id,step.id,step.contentHash);assert.equal(f.s.asset(prepared.input.references[0]).metadata.inheritance.sourceAssetId,f.asset.id);assert.equal(f.s.db.prepare('SELECT count(*) n FROM runs').get().n,0);
  const snapshot=createReferenceExport(f.s).create({entityIds:[entityId],includeUnconfirmed:false});assert.equal(snapshot.entities[0].sceneSpatial.status,'draft');assert.deepEqual(snapshot.entities[0].sceneSpatial.elements,[]);assert.equal(snapshot.entities[0].sceneSpatial.promptContext,'');
});

test('explicitly disabling layout inheritance keeps a separate spatial draft and still fixes visual identity',async t=>{
  const f=await fixture(t),c={...candidate('reconfigured',f.base.id),copySpatialDraft:false,changes:'User requested a new doorway arrangement'},plan=f.plan([c]),applied=f.apply(plan),step=f.a.steps(f.p.id).find(s=>s.entityId===applied.entities.reconfigured);assert.equal(f.m.spatial.get(step.entityId).summary.status,'missing');assert.equal(step.useBaseAppearance,true);assert.equal(f.m.detail(step.entityId).derivedFrom.options.copySpatialDraft,false);
});

test('scene state in same plan waits for base main image; explicit references remain explicit',async t=>{
  const f=await fixture(t),base=candidate('newBase'),variant={...candidate('next'),variationOf:'newBase',changes:'Rain damage only'},plan=f.plan([base,variant]);assert.equal(plan.candidates[1].images[0].useBaseAppearance,true);const applied=f.apply(plan),step=f.a.steps(f.p.id).find(s=>s.entityId===applied.entities.next);assert.match(step.issue,/基础实体主形象/);assert.throws(()=>f.a.prepareRun(f.p.id,step.id,step.contentHash),e=>e.status===409);assert.equal(f.m.spatial.get(step.entityId).summary.status,'missing');
  const explicit={...candidate('explicit',f.base.id),images:[{...image,referenceAssetIds:[f.asset.id]}]};const next=f.plan([explicit]);assert.equal(next.candidates[0].images[0].useBaseAppearance,false);assert.deepEqual(next.candidates[0].images[0].referenceAssetIds,[f.asset.id]);
});

test('layout inheritance rejects non-scene base and invalid policy; old plan defaults are not silently rewritten',async t=>{
  const f=await fixture(t),project=f.projects.project(f.p.id),person=f.projects.createEntity(f.p.id,{profile:{name:'Person',flags:['人物']},expectedRevision:project.revision});assert.throws(()=>f.plan([candidate('invalid',person.entity.id)]),e=>e.status===400);assert.throws(()=>f.plan([{...candidate('noBase'),copySpatialDraft:true}]),e=>e.status===400);
  const body={title:'Legacy scene plan',summary:'Pre-policy request',candidates:[{...candidate('legacy',f.base.id)}],relations:[],questions:[]},planId=id(),basis={...f.a.basis(f.p.id),imageHashes:{}};f.s.db.prepare('INSERT INTO entity_authoring_plans VALUES (?,?,?,?,?,?,?,?,?)').run(planId,f.p.id,null,null,canonicalJSON(body),canonicalJSON(basis),contentHash(body),null,now());const old=f.a.get(f.p.id,planId),applied=f.apply(old),step=f.a.steps(f.p.id).find(s=>s.entityId===applied.entities.legacy);assert.equal(step.useBaseAppearance,false);assert.equal(f.m.spatial.get(step.entityId).summary.status,'missing');
});

test('spatial inheritance bounds unknowns and keeps the base version immutable',async t=>{
  const f=await fixture(t),current=f.m.spatial.get(f.base.id);const document={...current.document,unknowns:Array.from({length:100},(_,i)=>'Unknown '+i)};f.m.spatial.save(f.base.id,{expectedVersionId:current.expectedVersionId,document});const before=canonicalJSON(f.m.spatial.get(f.base.id)),plan=f.plan(),applied=f.apply(plan),derived=f.m.spatial.get(applied.entities.damaged);assert.equal(derived.document.unknowns.length,100);assert.deepEqual(derived.document.unknowns,document.unknowns);assert.equal(canonicalJSON(f.m.spatial.get(f.base.id)),before);assert.equal(derived.summary.status,'draft');
});
