// Owner: Sean — durable, serial image batches with explicit generation authorization and dependency recovery.
import {Router} from 'express';
import {z} from 'zod';
import {createHash} from 'node:crypto';
import {id,now,HttpError} from './store.mjs';
import {canonicalJSON,contentHash} from './content-hash.mjs';
import {projectInput} from './project-workspace.mjs';
import {workflowTemplate,catalog} from './catalog.mjs';
import {sceneSpatialView} from './scene-spatial.mjs';

const control=z.object({expectedRevision:z.number().int().positive(),acknowledgeGeneration:z.literal(true)}).strict();
export function createAuthoringBatches(store,{authoring,projects,runs,autoRun=true,pollMs=1500}){
  const db=store.db,timers=new Map(),busy=new Set();let closed=false;
  db.exec(`CREATE TABLE IF NOT EXISTS authoring_batches(id TEXT PRIMARY KEY,project_id TEXT NOT NULL REFERENCES agent_projects(id),title TEXT NOT NULL,status TEXT NOT NULL,revision INTEGER NOT NULL,basis TEXT NOT NULL,error TEXT,created_at TEXT NOT NULL,updated_at TEXT NOT NULL);
    CREATE UNIQUE INDEX IF NOT EXISTS authoring_one_running_batch ON authoring_batches(status) WHERE status='running';
    CREATE TABLE IF NOT EXISTS authoring_batch_items(id TEXT PRIMARY KEY,batch_id TEXT NOT NULL REFERENCES authoring_batches(id),position INTEGER NOT NULL,step_id TEXT NOT NULL REFERENCES entity_workflow_steps(id),step_hash TEXT NOT NULL,entity_id TEXT NOT NULL REFERENCES entities(id),basis TEXT NOT NULL,status TEXT NOT NULL,prepared TEXT,run_id TEXT,request_key TEXT NOT NULL UNIQUE,error TEXT,UNIQUE(batch_id,position));
    CREATE TABLE IF NOT EXISTS authoring_batch_events(id TEXT PRIMARY KEY,batch_id TEXT NOT NULL REFERENCES authoring_batches(id),type TEXT NOT NULL,body TEXT NOT NULL,created_at TEXT NOT NULL);
    CREATE TRIGGER IF NOT EXISTS batch_scope_immutable BEFORE UPDATE OF project_id,title,basis ON authoring_batches BEGIN SELECT RAISE(ABORT,'immutable batch scope'); END;
    CREATE TRIGGER IF NOT EXISTS batch_item_scope_immutable BEFORE UPDATE OF batch_id,position,step_id,step_hash,entity_id,request_key ON authoring_batch_items BEGIN SELECT RAISE(ABORT,'immutable batch item scope'); END;`);
  const projectFacts=p=>contentHash({revision:p.revision,fields:Object.fromEntries(['brief','synopsis','worldRules','visualStyle','decisions'].map(k=>[k,p[k]]))});
  function entityFacts(e){const entity=store.entity(e);return contentHash({context:entity.context,spatial:{contentHash:sceneSpatialView(store,e,{includeUnconfirmed:false}).contentHash,status:sceneSpatialView(store,e,{includeUnconfirmed:false}).status},
    relations:db.prepare("SELECT * FROM entity_relations WHERE (source_entity_id=? OR target_entity_id=?) AND status='active' ORDER BY id").all(e,e)});}
  function event(batchId,type,body){db.prepare('INSERT INTO authoring_batch_events VALUES (?,?,?,?,?)').run(id(),batchId,type,canonicalJSON({owner:'Sean',...body}),now());}
  function batchRow(projectId,batchId){projects.project(projectId);const b=db.prepare('SELECT * FROM authoring_batches WHERE id=? AND project_id=?').get(batchId,projectId);if(!b)throw new HttpError(404,'生成批次不存在');return b;}
  function items(batchId){return db.prepare('SELECT * FROM authoring_batch_items WHERE batch_id=? ORDER BY position').all(batchId);}
  function get(projectId,batchId){const b=batchRow(projectId,batchId);return {owner:'Sean',id:b.id,projectId,title:b.title,status:b.status,revision:b.revision,error:b.error,createdAt:b.created_at,updatedAt:b.updated_at,
    generationRequiresUser:true,items:items(b.id).map(i=>{let step=null,run=null;try{step=authoring.getStep(projectId,i.step_id);}catch{}if(i.run_id){try{run=store.run(i.run_id);}catch{}}
      return {id:i.id,position:i.position,stepId:i.step_id,entityId:i.entity_id,label:step?.label||'来源步骤不可用',entityName:step?.entityName||'实体不可用',status:i.status==='running'&&run&&['succeeded','failed','cancelled'].includes(run.status)?(run.status==='succeeded'?'succeeded':'failed'):i.status,error:i.error,runId:i.run_id,
        runStatus:run?.status||null,progress:run?.progress??null,outputs:run?.outputs.filter(a=>!a.deletedAt)||[],review:'生成成功不代表一致性已确认'};}),
    events:db.prepare('SELECT type,body,created_at AS createdAt FROM authoring_batch_events WHERE batch_id=? ORDER BY rowid DESC LIMIT 30').all(b.id).map(e=>({...e,body:JSON.parse(e.body)}))};}
  function list(projectId){projects.project(projectId);return db.prepare('SELECT id FROM authoring_batches WHERE project_id=? ORDER BY created_at DESC,rowid DESC LIMIT 100').all(projectId).map(b=>get(projectId,b.id));}
  function update(batchId,status,error=null){db.prepare('UPDATE authoring_batches SET status=?,error=?,revision=revision+1,updated_at=? WHERE id=?').run(status,error,now(),batchId);}
  function capture(projectId,step){projects.member(projectId,step.entityId);const dependency=step.useMainAppearance||step.useBaseAppearance;
    return {facts:entityFacts(step.entityId),templateHash:workflowTemplate(step.modelId).hash,modelHash:contentHash(catalog.models.find(m=>m.id===step.modelId)),styleHash:contentHash(catalog.styles.find(s=>s.id===step.styleId)),referenceEntityId:step.referenceEntityId,
      dependency,referenceFacts:dependency?entityFacts(step.referenceEntityId):null,appearanceId:dependency?store.visualState(step.referenceEntityId).appearance?.id||null:null,
      explicitEntityFacts:Object.fromEntries(step.sourceReferenceAssetIds.map(a=>[a,entityFacts(store.asset(a).entityId)])),
      explicitHashes:Object.fromEntries(step.sourceReferenceAssetIds.map(a=>{const asset=store.asset(a);projects.member(projectId,asset.entityId);const hash=createHash('sha256').update(store.assetBytes(a)).digest('hex');if(hash!==asset.hash)throw new HttpError(409,'参考图内容变化');return [a,hash];}))};}
  function create(projectId,body){const input=projectInput(z.object({title:z.string().trim().min(1).max(100),requestId:z.string().uuid(),steps:z.array(z.object({stepId:z.string().uuid(),expectedStepHash:z.string().length(64)}).strict()).min(1).max(48),acknowledgePlan:z.literal(true)}).strict(),body);
    if(new Set(input.steps.map(s=>s.stepId)).size!==input.steps.length)throw new HttpError(400,'步骤不能重复',{fieldErrors:{steps:['请选择不同步骤']}});
    const fingerprint=contentHash(input);return store.transaction(()=>{
      const previous=db.prepare('SELECT * FROM authoring_batches WHERE id=?').get(input.requestId);if(previous){if(previous.project_id!==projectId||JSON.parse(previous.basis).requestHash!==fingerprint)throw new HttpError(409,'重复请求标识用于不同批次');return get(projectId,previous.id);}
      const p=projects.project(projectId),b={requestHash:fingerprint,projectFacts:projectFacts(p)};db.prepare('INSERT INTO authoring_batches VALUES (?,?,?,\'draft\',1,?,NULL,?,?)').run(input.requestId,projectId,input.title,canonicalJSON(b),now(),now());
      input.steps.forEach((s,position)=>{const step=authoring.getStep(projectId,s.stepId);if(!step.isCurrent||step.contentHash!==s.expectedStepHash)throw new HttpError(409,'步骤选用版本已变化');
        db.prepare('INSERT INTO authoring_batch_items VALUES (?,?,?,?,?,?,?,\'pending\',NULL,NULL,?,NULL)').run(id(),input.requestId,position,step.id,step.contentHash,step.entityId,canonicalJSON(capture(projectId,step)),`batch:${input.requestId}:${position}`);});
      event(input.requestId,'created',{count:input.steps.length,generationSubmitted:false});return get(projectId,input.requestId);
    });
  }
  function check(b,i){const p=projects.project(b.project_id);if(projectFacts(p)!==JSON.parse(b.basis).projectFacts)throw new HttpError(409,'项目规则或剧情已变化，请重新审阅并建立批次');
    const step=authoring.getStep(b.project_id,i.step_id),basis=JSON.parse(i.basis);if(!step.isCurrent||step.contentHash!==i.step_hash)throw new HttpError(409,'步骤版本已变化，请以当前版本建立新批次');
    if(entityFacts(i.entity_id)!==basis.facts)throw new HttpError(409,'实体事实或空间设定已变化，请修订后重新建立批次');
    if(workflowTemplate(step.modelId).hash!==basis.templateHash||contentHash(catalog.models.find(m=>m.id===step.modelId))!==basis.modelHash||contentHash(catalog.styles.find(s=>s.id===step.styleId))!==basis.styleHash)throw new HttpError(409,'生成模板已变化，请重新审阅');
    for(const [a,h] of Object.entries(basis.explicitHashes)){const asset=store.asset(a);projects.member(b.project_id,asset.entityId);if(entityFacts(asset.entityId)!==basis.explicitEntityFacts[a])throw new HttpError(409,'明确引用实体的事实已变化');if(createHash('sha256').update(store.assetBytes(a)).digest('hex')!==h)throw new HttpError(409,'明确引用的图片内容已变化');}
    if(basis.dependency){if(entityFacts(basis.referenceEntityId)!==basis.referenceFacts)throw new HttpError(409,'基础引用实体事实或空间设定已变化');const main=store.visualState(basis.referenceEntityId).appearance;if(!main) return {step,waiting:true};if(basis.appearanceId&&basis.appearanceId!==main.id)throw new HttpError(409,'主图版本已变化，请核对后建立新批次');}
    if(step.issue)throw new HttpError(409,step.issue);return {step,waiting:false};
  }
  function schedule(batchId){if(!autoRun||closed||timers.has(batchId))return;const timer=setTimeout(()=>{timers.delete(batchId);void tick(batchId);},pollMs);timer.unref?.();timers.set(batchId,timer);}
  async function tick(batchId){if(closed||busy.has(batchId))return;busy.add(batchId);try{
    const b=db.prepare('SELECT * FROM authoring_batches WHERE id=?').get(batchId);if(!b||b.status!=='running')return;
    const all=items(batchId);
    for(const i of all.filter(i=>['preparing','running'].includes(i.status))){
      const recorded=i.run_id||db.prepare('SELECT run_id FROM request_keys WHERE key=?').get(i.request_key)?.run_id;
      if(recorded&&!i.run_id)db.prepare('UPDATE authoring_batch_items SET run_id=?,status=\'running\' WHERE id=?').run(recorded,i.id);
      if(recorded){const run=store.run(recorded);if(['queued','running'].includes(run.status)){schedule(batchId);return;}
        if(run.status==='succeeded'){db.prepare('UPDATE authoring_batch_items SET status=\'succeeded\',error=NULL WHERE id=?').run(i.id);event(batchId,'step-succeeded',{itemId:i.id,runId:recorded});}
        else{db.prepare('UPDATE authoring_batch_items SET status=\'failed\',error=? WHERE id=?').run('生成失败或已取消，请检查结果后建立重试批次',i.id);update(batchId,'failed','有步骤生成失败；后续未提交');event(batchId,'step-failed',{itemId:i.id,runId:recorded});return;}
      }
    }
    const pending=items(batchId).filter(i=>['pending','waiting','preparing'].includes(i.status));if(!pending.length){update(batchId,'completed');event(batchId,'completed',{reviewRequired:true});return;}
    let candidate=null;
    for(const i of pending){let checked;try{checked=check(b,i);}catch(e){db.prepare('UPDATE authoring_batch_items SET status=\'review\',error=? WHERE id=?').run(e.status?e.message:'资料无法核对，请检查后重新建立批次',i.id);update(batchId,'waiting','资料需要复核，后续未提交');event(batchId,'review-required',{itemId:i.id});return;}
      if(checked.waiting){db.prepare('UPDATE authoring_batch_items SET status=\'waiting\',error=? WHERE id=?').run('请先选定主图，再恢复批次',i.id);continue;}candidate=i;break;}
    if(!candidate){update(batchId,'waiting','缺少主图；选定后点击恢复');event(batchId,'dependency-wait',{});return;}
    const i=candidate;
    // Persist prepared input before dispatch. Recovery uses the stable request key, never a new attempt.
    const prepared=i.prepared?JSON.parse(i.prepared):authoring.prepareRun(b.project_id,i.step_id,i.step_hash);
    for(const a of prepared.input.references){const asset=store.asset(a);if(asset.entityId!==prepared.entityId||createHash('sha256').update(store.assetBytes(a)).digest('hex')!==asset.hash)throw new HttpError(409,'准备好的引用图片内容或归属已变化');}
    const step=authoring.getStep(b.project_id,i.step_id),captured=JSON.parse(i.basis);if(captured.dependency&&!captured.appearanceId)captured.appearanceId=store.visualState(captured.referenceEntityId).appearance.id;
    db.prepare('UPDATE authoring_batch_items SET status=\'preparing\',prepared=?,basis=?,error=NULL WHERE id=?').run(canonicalJSON(prepared),canonicalJSON(captured),i.id);
    if(db.prepare('SELECT status FROM authoring_batches WHERE id=?').get(batchId).status!=='running')return;
    const run=runs.startPrepared(step.entityId,prepared.input,i.request_key,{stepId:i.step_id,stepHash:i.step_hash,batchId,itemId:i.id});
    db.prepare('UPDATE authoring_batch_items SET status=\'running\',run_id=? WHERE id=?').run(run.id,i.id);event(batchId,'submitted',{itemId:i.id,runId:run.id});schedule(batchId);
  }catch(e){const b=db.prepare('SELECT status FROM authoring_batches WHERE id=?').get(batchId);if(b?.status==='running'){update(batchId,'waiting',e.status?e.message:'批次提交未完成，请核对后恢复');event(batchId,'dispatch-interrupted',{});}}
    finally{busy.delete(batchId);}
  }
  function resume(projectId,batchId,body){const input=projectInput(control,body);store.transaction(()=>{
    const b=batchRow(projectId,batchId);if(b.revision!==input.expectedRevision)throw new HttpError(409,'批次状态已变化，请刷新');if(['completed','cancelled','failed'].includes(b.status))throw new HttpError(409,'此批次已结束；重试请建立新批次');
    if(items(b.id).some(i=>i.status==='review'))throw new HttpError(409,'批次依据已变化，请修订并建立新批次');
    if(db.prepare("SELECT id FROM authoring_batches WHERE status='running' AND id<>?").get(batchId))throw new HttpError(409,'另一个批次正在运行，请等待或暂停');
    update(batchId,'running');event(batchId,'user-authorized',{previousStatus:b.status});
  });schedule(batchId);return get(projectId,batchId);}
  function stop(projectId,batchId,body,cancel=false){const input=projectInput(z.object({expectedRevision:z.number().int().positive()}).strict(),body);store.transaction(()=>{
    const b=batchRow(projectId,batchId);if(b.revision!==input.expectedRevision)throw new HttpError(409,'批次状态已变化，请刷新');if(['completed','cancelled'].includes(b.status))return;
    update(batchId,cancel?'cancelled':'paused',cancel?'后续步骤取消；已提交运行保留':'后续步骤暂停；已提交运行继续');event(batchId,cancel?'cancelled':'paused',{runningContinues:true});
  });clearTimeout(timers.get(batchId));timers.delete(batchId);return get(projectId,batchId);}
  function recover(){for(const b of db.prepare("SELECT id FROM authoring_batches WHERE status='running'").all()){update(b.id,'interrupted','服务重启，未提交新生成；请核对后恢复');event(b.id,'recovered',{automaticSubmission:false});}}
  function close(){closed=true;for(const t of timers.values())clearTimeout(t);timers.clear();}
  return {create,get,list,resume,stop,tick,recover,close};
}
export function authoringBatchesRouter(service){const r=Router();for(const n of ['projectId','batchId'])r.param(n,(_q,_s,next,v)=>{try{projectInput(z.string().uuid(),v);next();}catch(e){next(e);}});
  r.get('/:projectId/batches',(q,s)=>s.json({owner:'Sean',batches:service.list(q.params.projectId)}));r.post('/:projectId/batches',(q,s)=>s.status(201).json(service.create(q.params.projectId,q.body)));
  r.get('/:projectId/batches/:batchId',(q,s)=>s.json(service.get(q.params.projectId,q.params.batchId)));
  r.post('/:projectId/batches/:batchId/resume',(q,s)=>s.json(service.resume(q.params.projectId,q.params.batchId,q.body)));
  r.post('/:projectId/batches/:batchId/pause',(q,s)=>s.json(service.stop(q.params.projectId,q.params.batchId,q.body)));
  r.post('/:projectId/batches/:batchId/cancel',(q,s)=>s.json(service.stop(q.params.projectId,q.params.batchId,q.body,true)));return r;
}
