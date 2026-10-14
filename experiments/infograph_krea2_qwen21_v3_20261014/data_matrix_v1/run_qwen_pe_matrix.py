#!/usr/bin/env python3
"""Owner: Sean. Qwen-Image-2.1 Prompt Enhancer arm for the data matrix."""
import json,os,shutil,subprocess,time,uuid
from pathlib import Path
from datetime import datetime,timezone
import requests
from PIL import Image
ROOT=Path(__file__).resolve().parent; COMFY=Path('/home/sean/projects/ComfyUI'); BASE='http://127.0.0.1:8188'; LEASE=os.environ['HIVE_RESOURCE_LEASE_ID']; TTL='600000'
CASES=json.loads((ROOT/'casebook.json').read_text())['cases']; s=requests.Session(); lastbeat=time.monotonic()
for p in ('images/qwen21_pe','workflows/qwen21_pe','runs/qwen21_pe','prompts/qwen21_pe_outputs'):(ROOT/p).mkdir(parents=True,exist_ok=True)
TEMP=COMFY/'output'/'infograph-data-matrix-v1'/'qwen_pe'; TEMP.mkdir(parents=True,exist_ok=True)
procs=subprocess.check_output(['ps','-eo','pid=,args='],text=True).splitlines(); pid_main=next((int(x.strip().split(None,1)[0]) for x in procs if 'python3 main.py --enable-assets' in x),None)
def now():return datetime.now(timezone.utc).isoformat()
def beat(force=False):
 global lastbeat
 if force or time.monotonic()-lastbeat>90:
  p=subprocess.run(['hive-resource','lease','heartbeat',LEASE,'--ttl',TTL],capture_output=True,text=True)
  if p.returncode:raise RuntimeError('lease heartbeat failed '+p.stderr+p.stdout)
  lastbeat=time.monotonic()
def run(c):
 job=c['id']; image=ROOT/'images/qwen21_pe'/f'{job}.png'; runp=ROOT/'runs/qwen21_pe'/f'{job}.json'; wf=ROOT/'workflows/qwen21_pe'/f'{job}.json'; prompt=(ROOT/'prompts'/f'{job}__qwen21.txt').read_text().strip(); seed=42
 beat(True); q=s.get(BASE+'/queue',timeout=15).json()
 if q['queue_running'] or q['queue_pending']:raise RuntimeError('ComfyUI shared queue not empty')
 g={'1':{'class_type':'UNETLoader','inputs':{'unet_name':'qwen_image_2.1_bf16.safetensors','weight_dtype':'default'}},'2':{'class_type':'CLIPLoader','inputs':{'clip_name':'qwen3.5_9b_qwen_image_2.1_pe_t2i.int8_convrot.safetensors','type':'qwen_image'}},'3':{'class_type':'CLIPLoader','inputs':{'clip_name':'qwen3vl_8b_bf16.safetensors','type':'qwen_image'}},'4':{'class_type':'VAELoader','inputs':{'vae_name':'qwen_image_2.1_vae_bf16.safetensors'}},'5':{'class_type':'QwenImage21_T2IPromptRewrite','inputs':{'clip':['2',0],'prompt':prompt,'temperature':1.0,'top_p':0.95,'top_k':20,'presence_penalty':1.5,'max_new_tokens':16256,'seed':seed}},'6':{'class_type':'CLIPTextEncode','inputs':{'clip':['3',0],'text':['5',0]}},'7':{'class_type':'CLIPTextEncode','inputs':{'clip':['3',0],'text':['5',1]}},'8':{'class_type':'EmptyLatentImage','inputs':{'width':1536,'height':1024,'batch_size':1}},'9':{'class_type':'KSampler','inputs':{'model':['1',0],'positive':['6',0],'negative':['7',0],'latent_image':['8',0],'seed':seed,'steps':40,'cfg':1.0,'sampler_name':'euler','scheduler':'simple','denoise':1.0}},'10':{'class_type':'VAEDecode','inputs':{'samples':['9',0],'vae':['4',0]}},'11':{'class_type':'SaveImage','inputs':{'images':['10',0],'filename_prefix':f'infograph-data-matrix-v1/qwen_pe/{job}'}},'12':{'class_type':'SaveText','inputs':{'text':['5',0],'filename_prefix':f'infograph-data-matrix-v1/qwen_pe/{job}','format':'txt'}}}
 wf.write_text(json.dumps({'prompt':g},ensure_ascii=False,indent=2)+'\n'); t=time.monotonic(); response=s.post(BASE+'/prompt',json={'prompt':g,'client_id':str(uuid.uuid4())},timeout=60)
 if not response.ok:raise RuntimeError(f'ComfyUI HTTP {response.status_code}: {response.text}')
 p_id=response.json()['prompt_id']; samples=[]; last=0; lastseen=time.monotonic()
 while time.monotonic()-t<7200:
  beat()
  if time.monotonic()-last>3:
   vals=subprocess.check_output(['nvidia-smi','--query-gpu=memory.used,utilization.gpu,temperature.gpu','--format=csv,noheader,nounits'],text=True).strip().split(','); rss=subprocess.check_output(['ps','-o','rss=','-p',str(pid_main)],text=True).strip()
   samples.append({'time':now(),'vram_used_mb':int(vals[0]),'gpu_util_pct':int(vals[1]),'temperature_c':int(vals[2]),'comfy_rss_mb':round(int(rss or 0)/1024)});last=time.monotonic()
  h=s.get(BASE+f'/history/{p_id}',timeout=15).json().get(p_id)
  if h and h.get('status',{}).get('completed'):break
  if h and h.get('status',{}).get('status_str')=='error':raise RuntimeError(str(h['status'].get('messages')))
  if not h:
   q=s.get(BASE+'/queue',timeout=15).json(); active=q['queue_running']+q['queue_pending']
   if any(str(x[1])==p_id for x in active):lastseen=time.monotonic()
   elif time.monotonic()-lastseen>120:raise RuntimeError('prompt disappeared')
  time.sleep(2)
 else:raise TimeoutError('generation timeout')
 elapsed=round(time.monotonic()-t,2); imgs=h.get('outputs',{}).get('11',{}).get('images',[])
 if not imgs:raise RuntimeError('no image saved')
 im=imgs[0]; src=COMFY/'output'/im.get('subfolder','')/im['filename']; shutil.copy2(src,image);src.unlink()
 # SaveText is an output node; copy the exact prompt it received into the long-term experiment.
 textfiles=list(TEMP.glob('*.txt'))
 if not textfiles:raise RuntimeError('Qwen PE output text file not found')
 latest=max(textfiles,key=lambda x:x.stat().st_mtime); pe_path=ROOT/'prompts/qwen21_pe_outputs'/f'{job}.txt';shutil.copy2(latest,pe_path);latest.unlink()
 with Image.open(image) as out:out.load();dims=list(out.size)
 result={'owner':'Sean','task_id':'remote-97ccaaac-e730-4c57-875c-c86954ca0518','job':job,'case_id':job,'model':'Qwen-Image-2.1 BF16 + Qwen Image 2.1 T2I Prompt Rewrite PE','language':c['lang'],'seed':seed,'source_data':c['data_source'],'case_ground_truth':c['rows'],'input_prompt':prompt,'actual_pe_prompt_file':str(pe_path.relative_to(ROOT)),'parameters':{'resolution':'1536x1024','steps':40,'cfg':1.0,'sampler':'euler','scheduler':'simple','diffusion_model':'qwen_image_2.1_bf16.safetensors','text_encoder':'qwen3vl_8b_bf16.safetensors','prompt_enhancer':'qwen3.5_9b_qwen_image_2.1_pe_t2i.int8_convrot.safetensors','pe_temperature':1.0,'pe_top_p':0.95,'pe_top_k':20,'pe_presence_penalty':1.5},'workflow':str(wf.relative_to(ROOT)),'image':str(image.relative_to(ROOT)),'prompt_id':p_id,'resource_lease_id':LEASE,'elapsed_seconds':elapsed,'image_dimensions':dims,'status':'success','peak_vram_mb_observed':max((x['vram_used_mb'] for x in samples),default=None),'peak_comfy_rss_mb_observed':max((x['comfy_rss_mb'] for x in samples),default=None),'peak_temperature_c_observed':max((x['temperature_c'] for x in samples),default=None),'peak_gpu_utilization_pct_observed':max((x['gpu_util_pct'] for x in samples),default=None),'gpu_samples':len(samples),'completed_at':now()}
 (ROOT/'runs/qwen21_pe'/f'{job}_gpu_samples.jsonl').write_text(''.join(json.dumps(x)+'\n' for x in samples));runp.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(job,elapsed,'s, peak VRAM',result['peak_vram_mb_observed'],'MB',flush=True)
results=[]
for c in CASES:
 try:run(c);results.append(json.loads((ROOT/'runs/qwen21_pe'/f"{c['id']}.json").read_text()))
 except Exception as e:
  d={'job':c['id'],'case_id':c['id'],'model':'Qwen-Image-2.1 BF16 + PE','status':'failed','error':repr(e),'failed_at':now()};(ROOT/'runs/qwen21_pe'/f"{c['id']}.json").write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n');print(c['id'],'FAILED',repr(e),flush=True)
summary={'owner':'Sean','task_id':'remote-97ccaaac-e730-4c57-875c-c86954ca0518','arm':'Qwen PE optimized prompts','planned':8,'completed':sum(x.get('status')=='success' for x in results),'results':results}
(ROOT/'runs/qwen21_pe/manifest.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
