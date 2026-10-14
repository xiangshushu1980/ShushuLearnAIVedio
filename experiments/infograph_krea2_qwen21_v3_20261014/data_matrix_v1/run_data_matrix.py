#!/usr/bin/env python3
"""Owner: Sean. Generate the [Sean] data-to-infographic matrix v1."""
import json, os, shutil, subprocess, time, uuid
from datetime import datetime, timezone
from pathlib import Path
import requests
from PIL import Image

ROOT=Path(__file__).resolve().parent
COMFY=Path('/home/sean/projects/ComfyUI')
BASE='http://127.0.0.1:8188'
LEASE=os.environ['HIVE_RESOURCE_LEASE_ID']
TTL='600000'
CASES=json.loads((ROOT/'casebook.json').read_text())['cases']
PROMPTS=ROOT/'prompts'; IMAGES=ROOT/'images'; WORKFLOWS=ROOT/'workflows'; RUNS=ROOT/'runs'
TEMP=COMFY/'output'/'infograph-data-matrix-v1'
for p in (IMAGES,WORKFLOWS,RUNS,TEMP): p.mkdir(parents=True,exist_ok=True)
s=requests.Session()
procs=subprocess.check_output(['ps','-eo','pid=,args='],text=True).splitlines()
main_pid=next((int(x.strip().split(None,1)[0]) for x in procs if 'python3 main.py --enable-assets' in x),None)
if not main_pid: raise RuntimeError('Cannot identify managed ComfyUI process')
lastbeat=time.monotonic()
def now(): return datetime.now(timezone.utc).isoformat()
def beat(force=False):
 global lastbeat
 if force or time.monotonic()-lastbeat>90:
  r=subprocess.run(['hive-resource','lease','heartbeat',LEASE,'--ttl',TTL],capture_output=True,text=True)
  if r.returncode: raise RuntimeError('GPU lease heartbeat failed: '+r.stderr+r.stdout)
  lastbeat=time.monotonic()
def sample():
 vals=subprocess.check_output(['nvidia-smi','--query-gpu=memory.used,utilization.gpu,temperature.gpu','--format=csv,noheader,nounits'],text=True).strip().split(',')
 rss=subprocess.check_output(['ps','-o','rss=','-p',str(main_pid)],text=True).strip()
 return {'time':now(),'vram_used_mb':int(vals[0]),'gpu_util_pct':int(vals[1]),'temperature_c':int(vals[2]),'comfy_rss_mb':round(int(rss or 0)/1024)}
def graph(model,prompt,seed,job):
 if model=='qwen21':
  g={'1':{'class_type':'UNETLoader','inputs':{'unet_name':'qwen_image_2.1_bf16.safetensors','weight_dtype':'default'}},'2':{'class_type':'CLIPLoader','inputs':{'clip_name':'qwen3vl_8b_bf16.safetensors','type':'qwen_image'}},'3':{'class_type':'VAELoader','inputs':{'vae_name':'qwen_image_2.1_vae_bf16.safetensors'}},'4':{'class_type':'CLIPTextEncode','inputs':{'clip':['2',0],'text':prompt}},'5':{'class_type':'CLIPTextEncode','inputs':{'clip':['2',0],'text':''}},'6':{'class_type':'EmptyLatentImage','inputs':{'width':1536,'height':1024,'batch_size':1}},'7':{'class_type':'KSampler','inputs':{'model':['1',0],'positive':['4',0],'negative':['5',0],'latent_image':['6',0],'seed':seed,'steps':40,'cfg':1.0,'sampler_name':'euler','scheduler':'simple','denoise':1.0}},'8':{'class_type':'VAEDecode','inputs':{'samples':['7',0],'vae':['3',0]}},'9':{'class_type':'SaveImage','inputs':{'images':['8',0],'filename_prefix':f'infograph-data-matrix-v1/{job}'}}}
 elif model in ('krea2','krea2_opt'):
  g={'1':{'class_type':'UNETLoader','inputs':{'unet_name':'krea2_raw_bf16.safetensors','weight_dtype':'default'}},'2':{'class_type':'CLIPLoader','inputs':{'clip_name':'qwen3vl_4b_bf16.safetensors','type':'krea2'}},'3':{'class_type':'VAELoader','inputs':{'vae_name':'qwen_image_vae.safetensors'}},'4':{'class_type':'CLIPTextEncode','inputs':{'clip':['2',0],'text':prompt}},'5':{'class_type':'CLIPTextEncode','inputs':{'clip':['2',0],'text':'watermark, logo, blurry' if model=='krea2_opt' else 'text, watermark, logo, blurry'}},'6':{'class_type':'EmptySD3LatentImage','inputs':{'width':1536,'height':1024,'batch_size':1}},'7':{'class_type':'KSampler','inputs':{'model':['1',0],'positive':['4',0],'negative':['5',0],'latent_image':['6',0],'seed':seed,'steps':52,'cfg':3.5,'sampler_name':'euler','scheduler':'simple','denoise':1.0}},'8':{'class_type':'VAEDecode','inputs':{'samples':['7',0],'vae':['3',0]}},'9':{'class_type':'SaveImage','inputs':{'images':['8',0],'filename_prefix':f'infograph-data-matrix-v1/{job}'}}}
 else:
  g={'1':{'class_type':'UNETLoader','inputs':{'unet_name':'flux-2-klein-9b.safetensors','weight_dtype':'default'}},'2':{'class_type':'CLIPLoader','inputs':{'clip_name':'qwen_3_8b.safetensors','type':'flux2'}},'3':{'class_type':'VAELoader','inputs':{'vae_name':'flux2-vae.safetensors'}},'4':{'class_type':'CLIPTextEncode','inputs':{'clip':['2',0],'text':prompt}},'5':{'class_type':'CLIPTextEncode','inputs':{'clip':['2',0],'text':''}},'6':{'class_type':'EmptyFlux2LatentImage','inputs':{'width':1536,'height':1024,'batch_size':1}},'7':{'class_type':'Flux2Scheduler','inputs':{'steps':50,'width':1536,'height':1024}},'8':{'class_type':'CFGGuider','inputs':{'model':['1',0],'positive':['4',0],'negative':['5',0],'cfg':3.5}},'9':{'class_type':'RandomNoise','inputs':{'noise_seed':seed}},'10':{'class_type':'KSamplerSelect','inputs':{'sampler_name':'euler'}},'11':{'class_type':'SamplerCustomAdvanced','inputs':{'noise':['9',0],'guider':['8',0],'sampler':['10',0],'sigmas':['7',0],'latent_image':['6',0]}},'12':{'class_type':'VAEDecode','inputs':{'samples':['11',0],'vae':['3',0]}},'13':{'class_type':'SaveImage','inputs':{'images':['12',0],'filename_prefix':f'infograph-data-matrix-v1/{job}'}}}
 return g

def run(model,c,seed=42):
 job=f"{c['id']}__{model}"; dest=IMAGES/f'{job}.png'; rec=RUNS/f'{job}.json'; wf=WORKFLOWS/f'{job}.json'
 if rec.exists() and dest.exists() and json.loads(rec.read_text()).get('status')=='success': print(f'{job}: already complete',flush=True); return
 beat(True)
 q=s.get(BASE+'/queue',timeout=15).json()
 if q.get('queue_running') or q.get('queue_pending'): raise RuntimeError('Shared ComfyUI queue is not empty; refusing to submit')
 prompt_file=(PROMPTS/'krea2_optimized'/f'{c["id"]}.txt') if model=='krea2_opt' else (PROMPTS/f'{c["id"]}__{model}.txt')
 prompt=prompt_file.read_text().strip(); g=graph(model,prompt,seed,job)
 wf.write_text(json.dumps({'prompt':g},ensure_ascii=False,indent=2)+'\n')
 params={'resolution':'1536x1024','seed':seed,'sampler':'euler','scheduler':'simple' if model!='flux2' else 'Flux2Scheduler','prompt_file':str(prompt_file.relative_to(ROOT))}
 if model=='qwen21': params.update({'steps':40,'cfg':1.0,'diffusion_model':'qwen_image_2.1_bf16.safetensors','text_encoder':'qwen3vl_8b_bf16.safetensors (Qwen native encoder; PE not used to protect exact data strings)','vae':'qwen_image_2.1_vae_bf16.safetensors'})
 elif model in ('krea2','krea2_opt'): params.update({'steps':52,'cfg':3.5,'diffusion_model':'krea2_raw_bf16.safetensors','text_encoder':'qwen3vl_4b_bf16.safetensors','vae':'qwen_image_vae.safetensors'})
 else: params.update({'steps':50,'cfg':3.5,'diffusion_model':'flux-2-klein-9b.safetensors','text_encoder':'qwen_3_8b.safetensors','vae':'flux2-vae.safetensors'})
 run={'owner':'Sean','task_id':'remote-97ccaaac-e730-4c57-875c-c86954ca0518','job':job,'case_id':c['id'],'model':model,'language':c['lang'],'seed':seed,'source_data':c['data_source'],'case_ground_truth':c['rows'],'input_prompt':prompt,'parameters':params,'workflow':str(wf.relative_to(ROOT)),'image':str(dest.relative_to(ROOT)),'resource_lease_id':LEASE,'started_at':now()}
 t=time.monotonic(); resp=s.post(BASE+'/prompt',json={'prompt':g,'client_id':str(uuid.uuid4())},timeout=60)
 if not resp.ok: raise RuntimeError(f'ComfyUI HTTP {resp.status_code}: {resp.text}')
 pid=resp.json()['prompt_id']; run['prompt_id']=pid
 samples=[]; last=0; lastseen=time.monotonic()
 while time.monotonic()-t<7200:
  beat()
  if time.monotonic()-last>=3: samples.append(sample()); last=time.monotonic()
  h=s.get(f'{BASE}/history/{pid}',timeout=15).json().get(pid)
  if h and h.get('status',{}).get('completed'): break
  if h and h.get('status',{}).get('status_str')=='error': raise RuntimeError(str(h.get('status',{}).get('messages')))
  if not h:
   q=s.get(BASE+'/queue',timeout=15).json(); active=q.get('queue_running',[])+q.get('queue_pending',[])
   if any(str(i[1])==pid for i in active): lastseen=time.monotonic()
   elif time.monotonic()-lastseen>120: raise RuntimeError('Prompt disappeared without completion')
  time.sleep(2)
 else: raise TimeoutError('generation exceeded two hours')
 outnode='13' if model=='flux2' else '9'; imgs=h.get('outputs',{}).get(outnode,{}).get('images',[])
 if not imgs: raise RuntimeError('No saved output in ComfyUI history')
 im=imgs[0]; src=COMFY/'output'/im.get('subfolder','')/im['filename']; shutil.copy2(src,dest); src.unlink()
 with Image.open(dest) as pic: pic.load(); dims=list(pic.size)
 if dims != [1536,1024]: raise RuntimeError(f'unexpected dimensions: {dims}')
 run.update({'status':'success','completed_at':now(),'elapsed_seconds':round(time.monotonic()-t,2),'image_dimensions':dims,'peak_vram_mb_observed':max((x['vram_used_mb'] for x in samples),default=None),'peak_comfy_rss_mb_observed':max((x['comfy_rss_mb'] for x in samples),default=None),'peak_temperature_c_observed':max((x['temperature_c'] for x in samples),default=None),'peak_gpu_utilization_pct_observed':max((x['gpu_util_pct'] for x in samples),default=None),'gpu_samples':len(samples),'image_filename':im})
 (RUNS/f'{job}_gpu_samples.jsonl').write_text(''.join(json.dumps(x)+'\n' for x in samples))
 rec.write_text(json.dumps(run,ensure_ascii=False,indent=2)+'\n')
 with (RUNS/'runs.jsonl').open('a') as f: f.write(json.dumps(run,ensure_ascii=False)+'\n')
 print(f"{job}: {run['elapsed_seconds']}s, peakVRAM={run['peak_vram_mb_observed']}MB",flush=True)

results=[]
import sys
models=('krea2_opt',) if '--krea2-opt-only' in sys.argv else ('qwen21','krea2','flux2')
for model in models:
 for c in CASES:
  try: run(model,c)
  except Exception as e:
   err={'owner':'Sean','task_id':'remote-97ccaaac-e730-4c57-875c-c86954ca0518','job':f"{c['id']}__{model}",'case_id':c['id'],'model':model,'status':'failed','failed_at':now(),'error':repr(e),'resource_lease_id':LEASE}
   (RUNS/(err['job']+'.json')).write_text(json.dumps(err,ensure_ascii=False,indent=2)+'\n'); print(f"{err['job']} FAILED: {e}",flush=True); results.append(err)
  else: results.append(json.loads((RUNS/f"{c['id']}__{model}.json").read_text()))
  if any(x.get('status')=='failed' for x in results[-1:]) and 'heartbeat failed' in results[-1].get('error','').lower(): break
summary={'owner':'Sean','task_id':'remote-97ccaaac-e730-4c57-875c-c86954ca0518','experiment':'data_matrix_v1','models':list(models),'cases':len(CASES),'planned_images':len(CASES)*len(models),'successes':sum(x.get('status')=='success' for x in results),'failures':sum(x.get('status')=='failed' for x in results),'resource_lease_id':LEASE,'results':results}
summary_path=RUNS/'krea2_optimized'/'manifest.json' if '--krea2-opt-only' in sys.argv else RUNS/'base_matrix_manifest.json'
summary_path.parent.mkdir(parents=True,exist_ok=True)
summary_path.write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
print('MATRIX COMPLETE',summary['successes'],'/',summary['planned_images'],flush=True)
