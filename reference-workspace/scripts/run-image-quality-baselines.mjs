// Owner: Sean — isolated real generation; never selects a main image or retries a failed run.
import {mkdirSync,readFileSync,writeFileSync,existsSync} from 'node:fs';
import {resolve,join} from 'node:path';
import {createStore,id} from '../server/store.mjs';
import {createProjectWorkspace} from '../server/project-workspace.mjs';
import {createEntityAuthoring} from '../server/entity-authoring.mjs';
import {createRunService} from '../server/runs.mjs';

if(!process.argv.includes('--execute-authorized'))throw new Error('Explicit bounded execution flag required.');
const directory=resolve(new URL('../../experiments/sean_reference_authoring_goal_20261004',import.meta.url).pathname);
const root=join(directory,'real-image-workspace');mkdirSync(root,{recursive:true});
const stateFile=join(root,'experiment.json'),store=createStore(root);
const projects=createProjectWorkspace(store),authoring=createEntityAuthoring(store,{projectService:projects}),runs=createRunService(store);
let state;
try{
  if(existsSync(stateFile))state=JSON.parse(readFileSync(stateFile,'utf8'));
  else{
    const source=JSON.parse(readFileSync(join(directory,'pending-image-quality-experiment.json'),'utf8')).plan;
    const input=Object.fromEntries(['title','summary','candidates','relations','questions'].map(k=>[k,source[k]]));
    const project=projects.saveProject(null,{name:'实际图片质量实验',brief:'隔离人物与场景验证，不写生产资料。',worldRules:'普通现实城市，无魔法。仅使用候选明确设计；未知空间不编造。',decisions:'人工选定主图后继续；最多八次基线与一次修订，无自动重试。',entityIds:[]});
    const plan=authoring.save(project.id,input);
    const applied=authoring.apply(project.id,plan.id,{expectedContentHash:plan.contentHash,acknowledgeNewDesign:true});
    state={owner:'Sean',createdAt:new Date().toISOString(),projectId:project.id,planId:plan.id,entities:applied.entities,maxBaselineGenerations:8,maxCorrectionGenerations:1,productionWrites:false,runs:[],status:'initial-baselines'};
    writeFileSync(stateFile,JSON.stringify(state,null,2));
  }
  // Explicitly selected steps retain their manual main-image dependency gate.
  const agentTable=store.db.prepare("SELECT name FROM sqlite_master WHERE type='table' AND name='agent_runs'").get();
  if(agentTable&&store.db.prepare("SELECT count(*) n FROM agent_runs WHERE status='running'").get().n)throw new Error('Agent dialogue is running; generating now would invalidate its source context.');
  const keys=(process.argv.find(s=>s.startsWith('--steps='))?.slice(8)||'base-concept,hall-overview').split(',');
  const allowed=['base-concept','hall-overview','base-v3','variant-concept','hall-angle','hall-detail','hall-variant-overview','hall-variant-angle'];
  if(!keys.length||new Set(keys).size!==keys.length||keys.some(k=>!allowed.includes(k)))throw new Error('Invalid baseline step selection.');
  for(const key of keys){
    const step=authoring.steps(state.projectId).find(s=>s.key===key&&s.isCurrent);
    if(!step)throw new Error('Current step missing.');
    const prior=store.db.prepare('SELECT id,snapshot FROM runs').all().find(r=>{const a=JSON.parse(r.snapshot).authoring;return a&&(a.rootStepId||a.stepId)===step.rootStepId;});
    if(prior){const previous=store.run(prior.id);console.log(JSON.stringify({key,status:previous.status,notice:'Existing attempt preserved; no retry.'}));if(previous.status!=='succeeded')throw new Error('Existing attempt needs explicit recovery or review; no resubmission.');continue;}
    if(store.db.prepare('SELECT count(*) n FROM runs').get().n>=8)throw new Error('Baseline generation cap reached.');
    const queue=await (await fetch('http://127.0.0.1:8188/queue',{signal:AbortSignal.timeout(10000)})).json();
    if(queue.queue_running.length||queue.queue_pending.length)throw new Error('Shared queue occupied; no submission.');
    const prepared=authoring.prepareRun(state.projectId,step.id,step.contentHash);
    const origin={stepId:step.id,stepHash:step.contentHash,batchId:id(),itemId:id()};
    runs.previewPrepared(step.entityId,prepared.input,origin);
    const run=runs.startPrepared(step.entityId,prepared.input,`sean-quality:${step.id}`,origin);
    state.runs.push({key,runId:run.id});writeFileSync(stateFile,JSON.stringify(state,null,2));
    let phase='';
    for(;;){
      const current=store.run(run.id);
      const evidence={owner:'Sean',step,run:current,execution:JSON.parse(store.db.prepare('SELECT execution FROM runs WHERE id=?').get(run.id).execution||'null')};
      writeFileSync(join(root,`${key}.json`),JSON.stringify(evidence,null,2));
      if(current.phase!==phase){phase=current.phase;console.log(JSON.stringify({key,status:current.status,phase,promptId:current.promptId}));}
      if(['succeeded','failed','cancelled'].includes(current.status)){
        for(const asset of current.outputs)writeFileSync(join(root,`${key}-${asset.id}.png`),store.assetBytes(asset.id));
        console.log(JSON.stringify({key,status:current.status,error:current.error,outputs:current.outputs.map(a=>({assetId:a.id,hash:a.hash,width:a.width,height:a.height}))}));
        // Give the generation service time to release its lease before the next independent run.
        await new Promise(r=>setTimeout(r,2000));
        if(current.status!=='succeeded')throw new Error(`${key} failed; no automatic retry: ${current.error}`);
        break;
      }
      await new Promise(r=>setTimeout(r,2000));
    }
  }
  state.status='awaiting-human-image-review';state.updatedAt=new Date().toISOString();
  writeFileSync(stateFile,JSON.stringify(state,null,2));
  console.log(JSON.stringify({owner:'Sean',status:state.status,root,runCount:store.db.prepare('SELECT count(*) n FROM runs').get().n}));
}catch(error){if(state){state.status='stopped';state.error=error.message;state.updatedAt=new Date().toISOString();writeFileSync(stateFile,JSON.stringify(state,null,2));}throw error;}
finally{store.db.close();}
