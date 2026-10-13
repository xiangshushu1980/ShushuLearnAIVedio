// Owner: Sean — read-only archive and decode/join checks for a selected diagnostic cut.
// Usage: node collect-cut-evidence.mjs <FILM_DATA_DIR> <projectId> [http://127.0.0.1:4194]
import {readFileSync,writeFileSync,mkdirSync} from 'node:fs';
import {execFileSync} from 'node:child_process';
import {dirname,join} from 'node:path';
import {fileURLToPath} from 'node:url';
import {hash} from '../../film-editor/server/store.mjs';
import {mediaTool} from '../../film-editor/server/render.mjs';
const [dataDir,projectId,base='http://127.0.0.1:4194']=process.argv.slice(2),dir=dirname(fileURLToPath(import.meta.url));
if(!dataDir||!projectId)throw Error('需要独立数据目录及项目ID');
const response=await fetch(`${base}/api/projects/${projectId}`);if(!response.ok)throw Error(`读取失败:${response.status}`);const p=await response.json(),cut=p.cuts.find(c=>c.id===p.selectedCutId);if(!cut)throw Error('没有选定成片');
for(const name of ['outputs','frames'])mkdirSync(join(dir,name),{recursive:true});
const stem=`sean_cut_${cut.id}`,file=join(dir,'outputs',stem+'.mp4'),bytes=readFileSync(join(dataDir,'blobs',cut.media.hash));if(hash(bytes)!==cut.media.hash)throw Error('成片字节哈希不匹配');writeFileSync(file,bytes);
execFileSync(mediaTool('ffmpeg'),['-v','error','-i',file,'-map','0:v:0','-map','0:a:0','-f','null','-'],{timeout:60000,maxBuffer:1024*1024});
let cumulative=0;const joins=[];
for(let i=0;i<cut.input.shots.length-1;i++){
 cumulative+=cut.input.shots[i].actualDurationSec;const times=[cumulative-.12,cumulative+.12],frames=[];
 for(let j=0;j<2;j++){const frame=join(dir,'frames',`${stem}_join_${i*2+j}.png`);execFileSync(mediaTool('ffmpeg'),['-v','error','-y','-ss',String(times[j]),'-i',file,'-frames:v','1','-vf','scale=768:-2',frame],{timeout:30000});frames.push({timeSec:times[j],file:frame,frameHash:hash(readFileSync(frame))});}
 joins.push({from:cut.input.shots[i].candidateId,to:cut.input.shots[i+1].candidateId,approximateBoundarySec:cumulative,frames});
}
const contact=join(dir,'frames',stem+'_joins_contact.png');execFileSync(mediaTool('ffmpeg'),['-v','error','-y','-f','image2','-framerate','1','-start_number','0','-i',join(dir,'frames',stem+'_join_%d.png'),'-vf',`tile=2x${joins.length}`,'-frames:v','1',contact],{timeout:30000});
writeFileSync(join(dir,stem+'_manifest.json'),JSON.stringify({owner:'Sean',scope:'diagnostic only; not automatic visual/audio acceptance',projectId,revision:p.revision,cut,file,fullDecode:'passed video and audio streams',joins,joinTimeScope:'cumulative source container duration, samples +/-0.12 sec; not frame-exact edit timestamps',contact},null,2));console.log(JSON.stringify({cutId:cut.id,duration:cut.probe.format.duration,file,contact,decode:'passed'}));
