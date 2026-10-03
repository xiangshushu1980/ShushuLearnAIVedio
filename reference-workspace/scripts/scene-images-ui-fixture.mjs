// Owner: Sean — isolated browser fixture; never imports generation services, agents or credentials.
import express from 'express';
import {mkdtempSync,rmSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {join,resolve} from 'node:path';
import sharp from 'sharp';
import {createStore,id,now} from '../server/store.mjs';
import {entityManagementRouter} from '../server/entity-management.mjs';
import {createProjectWorkspace,projectWorkspaceRouter} from '../server/project-workspace.mjs';
import {referenceExportRouter} from '../server/reference-export.mjs';
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
const app=express();app.use(localAccess);app.use(express.json());app.use('/api/manage',entityManagementRouter(store));app.use('/api/projects',projectWorkspaceRouter(createProjectWorkspace(store)));app.use('/api/reference/v1',referenceExportRouter(store));
app.get('/api/catalog',(_q,r)=>r.json(catalog));app.get('/api/entities',(_q,r)=>r.json([{id:entityId,name:'隔离测试候车厅'}]));
app.get('/api/entities/:id/workspace',(q,r)=>{store.entity(q.params.id);r.json({entity:store.entity(q.params.id),assets:store.db.prepare('SELECT * FROM assets WHERE entity_id=?').all(q.params.id).map(store.assetView),runs:[],visualState:store.visualState(q.params.id),voiceState:store.voiceState(q.params.id),draft:null,multiviewDraft:null,voiceDraft:null});});
app.get('/api/assets/:id/content',(q,r)=>{const a=store.asset(q.params.id);r.type(a.mime).sendFile(store.assetPath(a.id));});
app.get('/api/execution-status',(_q,r)=>r.json({connected:false,running:0,queued:0}));
app.use('/api',(_q,r)=>r.status(404).json({error:'Fixture endpoint unavailable'}));app.use(express.static(resolve('dist')));app.get('/{*path}',(_q,r)=>r.sendFile(resolve('dist/index.html')));
app.use((e,_q,r,_n)=>r.status(e.status||500).json({error:e.message,details:e.details}));
const server=app.listen(0,'127.0.0.1',()=>console.log(JSON.stringify({owner:'Sean',url:`http://127.0.0.1:${server.address().port}/?view=library&entity=${entityId}`,root,entityId})));
function stop(){server.close(()=>{store.db.close();rmSync(root,{recursive:true,force:true});process.exit(0);});}
process.on('SIGTERM',stop);process.on('SIGINT',stop);
