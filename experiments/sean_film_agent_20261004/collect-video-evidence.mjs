// Owner: Sean — read-only collection; never submits a model request or GPU job.
// Usage: node collect-video-evidence.mjs <FILM_DATA_DIR> <projectId> [http://127.0.0.1:4194]
import {readFileSync,writeFileSync,mkdirSync,existsSync} from 'node:fs';
import {execFileSync} from 'node:child_process';
import {dirname,join} from 'node:path';
import {fileURLToPath} from 'node:url';
import {hash} from '../../film-editor/server/store.mjs';
import {mediaTool} from '../../film-editor/server/render.mjs';
const [dataDir,projectId,base='http://127.0.0.1:4194']=process.argv.slice(2),dir=dirname(fileURLToPath(import.meta.url));
if(!dataDir||!projectId)throw Error('需要独立数据目录和测试项目ID');
const response=await fetch(`${base}/api/projects/${projectId}`);if(!response.ok)throw Error(`项目读取失败:${response.status}`);const p=await response.json();
for(const name of ['outputs','frames','references'])mkdirSync(join(dir,name),{recursive:true});
const clips=[];let prior=[];try{prior=JSON.parse(readFileSync(join(dir,'sean_video_manifest.json'))).clips;}catch{}
for(const c of p.candidates.filter(c=>c.status==='succeeded'&&c.media)){
  const n=p.shots.findIndex(s=>s.id===c.shotId)+1,stem=`sean_s${String(n).padStart(2,'0')}_${c.id}`,file=join(dir,'outputs',stem+'.mp4'),bytes=readFileSync(join(dataDir,'blobs',c.media.hash));if(hash(bytes)!==c.media.hash)throw Error('源视频哈希不匹配');
  if(!existsSync(file)||hash(readFileSync(file))!==c.media.hash)writeFileSync(file,bytes);
  const old=prior.find(v=>v.candidateId===c.id),probe=old?.probe||JSON.parse(execFileSync(mediaTool('ffprobe'),['-v','error','-show_format','-show_streams','-of','json',file],{encoding:'utf8',timeout:30000}));
  const duration=Number(probe.format.duration),times=[.1,duration/2,duration-.15],frames=[];
  for(const [j,t] of times.entries()){const frame=join(dir,'frames',`${stem}_${j}.png`);if(!existsSync(frame))execFileSync(mediaTool('ffmpeg'),['-v','error','-ss',String(t),'-i',file,'-frames:v','1','-vf','scale=768:-2',frame],{timeout:30000});frames.push({path:frame,timeSec:t});}
  const contact=join(dir,'frames',stem+'_contact.png');if(!existsSync(contact))execFileSync(mediaTool('ffmpeg'),['-v','error','-f','image2','-framerate','1','-start_number','0','-i',join(dir,'frames',stem+'_%d.png'),'-vf','tile=3x1','-frames:v','1',contact],{timeout:30000});
  clips.push({owner:'Sean',candidateId:c.id,shotId:c.shotId,file,hash:c.media.hash,probe,frames,contact,input:c.input,promptId:c.promptId,workflow:c.workflow,elapsedSec:c.elapsedSec,peakVramMb:c.peakVramMb,leaseId:c.leaseId});
}
const assets=[...new Map(clips.flatMap(c=>c.input.images).map(a=>[a.assetId,a])).values()],refs=[];
for(const a of assets){const bytes=readFileSync(join(dataDir,'blobs',a.localHash));if(hash(bytes)!==a.localHash)throw Error('参考图片哈希不匹配');const ext=({'image/png':'png','image/jpeg':'jpg','image/webp':'webp'})[a.mime]||'bin',file=`references/sean_${a.assetId}.${ext}`;writeFileSync(join(dir,file),bytes);refs.push({owner:'Sean',assetId:a.assetId,entityId:a.entityId,role:a.role,hash:a.localHash,file,...(a.provenance?{provenance:a.provenance}:{})});}
writeFileSync(join(dir,'sean_reference_index.json'),JSON.stringify({owner:'Sean',assets:refs},null,2));writeFileSync(join(dir,'sean_video_manifest.json'),JSON.stringify({owner:'Sean',at:new Date().toISOString(),projectId:p.id,revision:p.revision,sourceUserProject:'5269e95a-d8b7-4c66-b8fd-603be396ef4c',scope:'isolated test copy',clips},null,2));writeFileSync(join(dir,'sean_test_project.json'),JSON.stringify({owner:'Sean',...p},null,2));
console.log(JSON.stringify(clips.map(c=>({candidateId:c.candidateId,duration:c.probe.format.duration,contact:c.contact}))));
