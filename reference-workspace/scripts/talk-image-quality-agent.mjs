// Owner: Sean — real Pi dialogue over persistent isolated generated assets; no generation or fact confirmation.
import {mkdirSync,readFileSync,writeFileSync,copyFileSync,existsSync,rmSync} from 'node:fs';
import {join,resolve} from 'node:path';
import {createStore,id} from '../server/store.mjs';
import {createProjectWorkspace} from '../server/project-workspace.mjs';
import {createEntityAuthoring} from '../server/entity-authoring.mjs';
import {createAgentWorkspace} from '../server/agent-workspace.mjs';
const options=Object.fromEntries(process.argv.slice(2).map(s=>s.split(/=(.*)/s).slice(0,2)));
if(!options['--task']||!options['--text-file'])throw new Error('Require --task and --text-file.');
if(!/^[a-z0-9_-]+$/.test(options['--task']))throw new Error('Invalid task key.');
const appRoot=resolve(new URL('..',import.meta.url).pathname),root=resolve(appRoot,'../experiments/sean_reference_authoring_goal_20261004/real-image-workspace');
const state=JSON.parse(readFileSync(join(root,'experiment.json'),'utf8')),agentRoot=join(root,'agent');
const out=join(root,`${options['--task']}-agent.json`);
if(existsSync(out))throw new Error('Evidence already exists; inspect it rather than duplicating a model call.');
if(existsSync(agentRoot))throw new Error('Private credential directory already exists; do not overwrite an active agent.');
mkdirSync(agentRoot,{mode:0o700});
for(const name of ['auth.json','models.json','models-store.json','preferences.json']){const source=join(appRoot,'.data/agent',name);if(existsSync(source))copyFileSync(source,join(agentRoot,name));}
const store=createStore(root),projects=createProjectWorkspace(store),authoring=createEntityAuthoring(store,{projectService:projects}),agents=createAgentWorkspace(store,{projectService:projects,authoringService:authoring});
const evidence={owner:'Sean',createdAt:new Date().toISOString(),task:options['--task'],scope:'Actual Pi observes existing generated assets and saves proposals only; isolated experiment data.',generationSubmitted:false};
let session,run;
const save=()=>writeFileSync(out,JSON.stringify(evidence,null,2));
try{
  if(options['--accept-first-images']==='true'){
    evidence.userAcceptance={text:'我看图片没问题。你的目标是场景一致性，还是agent控制？',scope:'Select the two inspected initial images as visual design; not approval of inferred spatial anchors.'};
    for(const {key,runId}of state.runs.filter(r=>['base-concept','hall-overview'].includes(r.key))){const r=store.run(runId);if(r.status!=='succeeded'||r.outputs.length!==1)throw Error('Expected one successful first image.');const current=store.visualState(r.entityId).appearance;if(current&&current.assetId!==r.outputs[0].id)throw Error('Main image changed; no overwrite.');if(!current)store.confirmAppearance(r.entityId,r.outputs[0].id,null);}
  }
  const refs=(options['--refs']||'hall-overview').split(',').map(key=>{const r=state.runs.find(r=>r.key===key);if(!r)throw Error('Unknown selected output.');const output=store.run(r.runId).outputs;if(output.length!==1)throw Error('Explicit single output selection required.');return output[0].id;});
  const models=await agents.models(),model=models.find(m=>m.provider==='deepseek'&&m.id==='deepseek-flash')||models[0];if(!model)throw Error('No configured model.');
  const purpose=options['--purpose']||'project-authoring',entityId=options['--entity']?state.entities[options['--entity']]:null;
  if(options['--session']){session=agents.session(options['--session']);if(session.projectId!==state.projectId||session.purpose!==purpose||session.entityId!==entityId)throw Error('Session scope mismatch.');}
  else session=await agents.createSession({projectId:state.projectId,entityId,purpose,provider:model.provider,modelId:model.id});
  const text=readFileSync(resolve(options['--text-file']),'utf8');
  evidence.sessionId=session.id;evidence.model={provider:model.provider,id:model.id};evidence.selectedAssetIds=refs;evidence.beforeContext=projects.context(state.projectId);
  run=await agents.start(session.id,{requestId:id(),text,referenceAssetIds:refs});evidence.runId=run.runId;save();
  console.log(JSON.stringify({owner:'Sean',task:evidence.task,runId:run.runId,status:'running'}));
  const deadline=Date.now()+330000;
  while(agents.run(run.runId).status==='running'&&Date.now()<deadline){evidence.status=agents.run(run.runId).status;evidence.events=agents.events(run.runId,0);save();await new Promise(r=>setTimeout(r,1000));}
  if(agents.run(run.runId).status==='running')await agents.cancel(run.runId);
  evidence.run=agents.run(run.runId);evidence.status=evidence.run.status;evidence.session=agents.session(session.id);evidence.plans=authoring.list(state.projectId).filter(p=>p.runId===run.runId);evidence.steps=authoring.steps(state.projectId).filter(s=>s.runId===run.runId);
  evidence.afterContext=projects.context(state.projectId);evidence.events=agents.events(run.runId,0);evidence.generationRunCount=store.db.prepare('SELECT count(*) n FROM runs').get().n;save();
  if(evidence.run.status!=='succeeded')process.exitCode=1;
  console.log(JSON.stringify({owner:'Sean',task:evidence.task,status:evidence.run.status,spatialProposals:evidence.session.proposals.length,entityProposals:evidence.session.entityProposals.length,stepRevisions:evidence.session.stepRevisions.length,evidence:out}));
}catch(error){evidence.status='failed';evidence.error='Agent experiment did not complete; inspect saved dialogue and local state.';save();process.exitCode=1;console.error(JSON.stringify({owner:'Sean',status:'failed',evidence:out}));}
finally{await agents.close();store.db.close();rmSync(agentRoot,{recursive:true,force:true});}
