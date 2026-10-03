// Owner: Sean — isolated browser fixture; fake dispatch and optional mock Agent, no credentials/provider calls.
import express from 'express';
import {mkdtempSync,rmSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {join,resolve} from 'node:path';
import sharp from 'sharp';
import {createStore,id,now} from '../server/store.mjs';
import {entityManagementRouter} from '../server/entity-management.mjs';
import {createProjectWorkspace,projectWorkspaceRouter} from '../server/project-workspace.mjs';
import {referenceExportRouter} from '../server/reference-export.mjs';
import {createEntityAuthoring,entityAuthoringRouter} from '../server/entity-authoring.mjs';
import {createAuthoringBatches,authoringBatchesRouter} from '../server/authoring-batches.mjs';
import {catalog} from '../server/catalog.mjs';
import {localAccess} from '../server/local-access.mjs';
const root=mkdtempSync(join(tmpdir(),'sean-scene-ui-')),store=createStore(root),entityId=id();
store.db.prepare('INSERT INTO entities VALUES (?,?,?,?)').run(entityId,'隔离测试候车厅',JSON.stringify({type:'scene',flags:['场景'],description:'测试资料：入口与长凳区相邻，长凳区通向站台门。',appearance:'浏览器验证用色块，不是真实生成结果。'}),now());
let overview;
for(const [name,color,role] of [['总览','#7a8ca0','scene_overview'],['反向角度','#956f6f','scene_angle'],['长凳细节','#7d9975','scene_detail']]){
  const bytes=await sharp({create:{width:320,height:180,channels:3,background:color}}).png().toBuffer();
  const stage=await store.stageImage(bytes,name,entityId,'concept',null,{source:'browser-fixture',authoring:{role}});
  const asset=store.transaction(()=>store.registerStages([stage]))[0];overview ||= asset;
}
store.confirmAppearance(entityId,overview.id,null);
const projects=createProjectWorkspace(store),project=projects.saveProject(null,{name:'隔离图片步骤修订项目',brief:'只验证界面，不生成图片。',decisions:'测试资料不写入正式项目。',entityIds:[entityId]}),authoring=createEntityAuthoring(store,{projectService:projects});
const image={key:'overview',label:'测试总览步骤',role:'scene_overview',prompt:'Existing entrance and bench zone. Do not invent a compass direction.',purpose:'Fixture layout',modelId:'qwen-image-2.1',styleId:'original',referenceAssetIds:[],useMainAppearance:false,useBaseAppearance:false,parameters:{},invariants:['入口相邻长凳区'],unknowns:['绝对方向未知']};
const plan=authoring.save(project.id,{title:'浏览器修订验证方案',summary:'隔离候选，只用于验证版本操作',candidates:[{key:'hall',kind:'scene',profile:{name:'修订测试场景',description:'入口相邻长凳区',appearance:'测试场景',voiceDescription:'',flags:['场景']},baseEntityId:null,variationOf:null,changes:'',projectRole:{role:'测试场所',plotNotes:''},unknowns:[],images:[image,{...image,key:'detail',label:'测试场景细节',role:'scene_detail',useMainAppearance:true}]}],relations:[],questions:[]});
authoring.apply(project.id,plan.id,{expectedContentHash:plan.contentHash,acknowledgeNewDesign:true});
const existingImagesFixture=process.env.REFERENCE_EXISTING_IMAGES_FIXTURE==='1'?(await import('./existing-images-fixture.mjs')).installExistingImagesFixture(store,projects,authoring,project.id,entityId):null;
const multiviewFixture=process.env.REFERENCE_MULTIVIEW_FIXTURE==='1'?await (await import('./authoring-multiview-fixture.mjs')).installMultiviewFixture(store,projects,authoring,project.id):null;
const fakeRuns={startPrepared(entityId,input,key,origin){const saved=store.createRun(entityId,{prompt:input.prompt,references:input.references.map(a=>({id:a})),...(input.appearanceId?{stage:'multiview',appearance:{id:input.appearanceId}}:{}),authoring:{...origin,sourceRevision:origin.stepHash},model:{id:input.modelId},style:{id:input.styleId}},key);if(saved.created)queueMicrotask(async()=>{try{const stage=await store.stageImage(store.assetBytes(overview.id),'模拟批次图片（不是真实生成）',entityId,input.appearanceId?'multiview':'concept',saved.run.id,{source:'browser-fixture',authoring:origin});store.transaction(()=>store.registerStages([stage]));store.updateRun(saved.run.id,{status:'succeeded'});}catch{store.updateRun(saved.run.id,{status:'failed'});}});return saved.run;}};
const batches=createAuthoringBatches(store,{authoring,projects,runs:fakeRuns,pollMs:100});
const feedback=process.env.REFERENCE_ENTITY_CHANGE_FIXTURE==='1'?await (await import('./entity-change-fixture.mjs')).installEntityChangeFixture(store,projects,authoring):process.env.REFERENCE_FEEDBACK_FIXTURE==='1'?await (await import('./image-feedback-fixture.mjs')).installImageFeedbackFixture(store,projects,authoring,fakeRuns):null;
const app=express();app.use(localAccess);app.use(express.json());app.use('/api/manage',entityManagementRouter(store));app.use('/api/projects',projectWorkspaceRouter(projects));app.use('/api/authoring',entityAuthoringRouter(authoring));app.use('/api/authoring',authoringBatchesRouter(batches));app.use('/api/reference/v1',referenceExportRouter(store));
if(feedback)app.use('/api/agents',feedback.router);
app.get('/api/catalog',(_q,r)=>r.json(catalog));app.get('/api/entities',(_q,r)=>r.json(store.db.prepare('SELECT id,name FROM entities ORDER BY created_at').all()));
app.get('/api/entities/:id/workspace',(q,r)=>{store.entity(q.params.id);r.json({entity:store.entity(q.params.id),assets:store.db.prepare('SELECT * FROM assets WHERE entity_id=?').all(q.params.id).map(store.assetView),runs:store.db.prepare('SELECT * FROM runs WHERE entity_id=? ORDER BY created_at DESC').all(q.params.id).map(store.runView),visualState:store.visualState(q.params.id),voiceState:store.voiceState(q.params.id),draft:null,multiviewDraft:null,voiceDraft:null});});
app.post('/api/entities/:id/appearance',(q,r)=>r.json(store.confirmAppearance(q.params.id,q.body.assetId,q.body.expectedAppearanceId)));
app.get('/api/assets/:id/content',(q,r)=>{const a=store.asset(q.params.id);r.type(a.mime).sendFile(store.assetPath(a.id));});
app.get('/api/execution-status',(_q,r)=>r.json({connected:false,running:0,queued:0}));
app.use('/api',(_q,r)=>r.status(404).json({error:'Fixture endpoint unavailable'}));app.use(express.static(resolve('dist')));app.get('/{*path}',(_q,r)=>r.sendFile(resolve('dist/index.html')));
app.use((e,_q,r,_n)=>r.status(e.status||500).json({error:e.message,details:e.details}));
const server=app.listen(0,'127.0.0.1',()=>console.log(JSON.stringify({owner:'Sean',url:`http://127.0.0.1:${server.address().port}/?view=library&entity=${entityId}`,root,entityId,multiviewFixture,existingImagesFixture,...(feedback?{reportId:feedback.reportId,sessionId:feedback.sessionId,assetId:feedback.assetId,proposalId:feedback.proposalId,changeEntityId:feedback.changeEntityId}:{}),workflowUrl:`http://127.0.0.1:${server.address().port}/?view=projects&project=${project.id}`})));
async function stop(){batches.close();await feedback?.agents.close();server.close(()=>{store.db.close();rmSync(root,{recursive:true,force:true});process.exit(0);});}
process.on('SIGTERM',stop);process.on('SIGINT',stop);
