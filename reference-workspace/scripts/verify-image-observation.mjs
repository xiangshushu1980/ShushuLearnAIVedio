// Owner: Sean — real Pi pixel-input probe; synthetic diagnostic, no ComfyUI or generation provider.
import {mkdtempSync,mkdirSync,copyFileSync,existsSync,writeFileSync,rmSync} from 'node:fs';
import {tmpdir} from 'node:os';import {join,resolve} from 'node:path';import assert from 'node:assert/strict';import sharp from 'sharp';
import {createStore,id} from '../server/store.mjs';import {createProjectWorkspace} from '../server/project-workspace.mjs';import {createAgentWorkspace} from '../server/agent-workspace.mjs';
const appRoot=resolve(new URL('..',import.meta.url).pathname),root=mkdtempSync(join(tmpdir(),'sean-pi-pixels-')),agentRoot=join(root,'agent');mkdirSync(agentRoot,{mode:0o700});
for(const name of ['auth.json','models.json','models-store.json','preferences.json']){const source=join(appRoot,'.data/agent',name);if(existsSync(source))copyFileSync(source,join(agentRoot,name));}
const store=createStore(root),projects=createProjectWorkspace(store),agents=createAgentWorkspace(store,{projectService:projects});
const out=resolve(appRoot,'../experiments/sean_reference_authoring_goal_20261004/pixel-observation-'+Date.now()+'.json');
const expected=[{position:'left',color:'red',whiteCircleCount:2},{position:'middle',color:'green',whiteCircleCount:1},{position:'right',color:'blue',whiteCircleCount:3}];
const evidence={owner:'Sean',scope:'synthetic pixel delivery and elementary perception only; not scene/character quality',expected,createdAt:new Date().toISOString()};
try{
 const svg='<svg xmlns="http://www.w3.org/2000/svg" width="900" height="300"><rect width="300" height="300" fill="#e02020"/><rect x="300" width="300" height="300" fill="#169a36"/><rect x="600" width="300" height="300" fill="#2050e0"/><g fill="white"><circle cx="90" cy="150" r="28"/><circle cx="210" cy="150" r="28"/><circle cx="450" cy="150" r="28"/><circle cx="660" cy="150" r="28"/><circle cx="750" cy="150" r="28"/><circle cx="840" cy="150" r="28"/></g></svg>';
 const bytes=await sharp(Buffer.from(svg)).png().toBuffer();writeFileSync(out.replace('.json','.png'),bytes);
 const p=projects.saveProject(null,{name:'视觉输入诊断',brief:'只检查诊断图的像素送达，不是真实场景。',decisions:'颜色与数量没有写入实体文字，必须调用图片观察工具。',entityIds:[]});
 const entity=projects.createEntity(p.id,{profile:{name:'诊断图',description:'三个并排区域，仅作工具输入测试。',flags:['场景']},expectedRevision:p.revision}).entity;
 const stage=await store.stageImage(bytes,'参考图',entity.id,'setting'),asset=store.transaction(()=>store.registerStages([stage]))[0];
 const models=await agents.models(),model=models.find(m=>m.provider==='deepseek'&&m.id==='deepseek-flash')||models[0];if(!model)throw Error('No configured model');evidence.model={provider:model.provider,id:model.id};
 const session=await agents.createSession({projectId:p.id,entityId:null,purpose:'project-authoring',provider:model.provider,modelId:model.id});
 const run=await agents.start(session.id,{requestId:id(),referenceAssetIds:[asset.id],text:`这是接口诊断，不是真实场景。先读取实体 ${entity.id}，再逐张调用图片观察工具查看选图。仅依据像素识别从左到右三个区域的主要颜色和每区白色圆点数量。保存图片报告，conclusion 为 inconclusive、issues 为空（不判断真实场景质量）。summary 必须是 JSON 数组字符串，恰好三个对象，字段 position 为 left/middle/right，color 用英文 red/green/blue 等基本颜色，whiteCircleCount 为整数。不要根据名称或文字猜测。`});
 console.log(JSON.stringify({owner:'Sean',status:'running',runId:run.runId}));
 const deadline=Date.now()+300000;while(agents.run(run.runId).status==='running'&&Date.now()<deadline)await new Promise(r=>setTimeout(r,500));if(agents.run(run.runId).status==='running')await agents.cancel(run.runId);
 const status=agents.run(run.runId),chat=agents.session(session.id);evidence.runStatus=status.status;evidence.messages=chat.messages;evidence.reports=chat.projectProposals;evidence.generationRunCount=store.db.prepare('SELECT count(*) n FROM runs').get().n;
 assert.equal(status.status,'succeeded');const report=chat.projectProposals.find(r=>r.kind==='image-review');assert.ok(report);assert.deepEqual(report.coverage.viewedImageAssetIds,[asset.id]);
 const observation=JSON.parse(report.summary);evidence.observation=observation;assert.deepEqual(observation,expected);assert.equal(evidence.generationRunCount,0);evidence.pixelProbePassed=true;
}catch(error){evidence.pixelProbePassed=false;evidence.failure=error.code==='ERR_ASSERTION'?'Pixel or structural assertion failed; inspect evidence.':'Probe failed; inspect sanitized evidence.';process.exitCode=1;}finally{writeFileSync(out,JSON.stringify(evidence,null,2));console.log(JSON.stringify({owner:'Sean',passed:evidence.pixelProbePassed,evidence:out}));await agents.close();store.db.close();rmSync(root,{recursive:true,force:true});}
