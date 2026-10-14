#!/usr/bin/env python3
"""Owner: Sean. Generate v2 data-to-infographic cases on shared ComfyUI."""
import hashlib, json, os, shutil, subprocess, time, uuid
from datetime import datetime, timezone
from pathlib import Path
import requests
from PIL import Image

ROOT=Path(__file__).resolve().parent
COMFY=Path('/home/sean/projects/ComfyUI')
BASE='http://127.0.0.1:8188'
LEASE=os.environ['HIVE_RESOURCE_LEASE_ID']
TTL='600000'
TASK='remote-97ccaaac-e730-4c57-875c-c86954ca0518'
MODELS=('qwen21','krea2','flux2')
CASEBOOK=json.loads((ROOT/'casebook.json').read_text())
CASES=CASEBOOK['cases']
session=requests.Session()
proc=subprocess.check_output(['ps','-eo','pid=,args='],text=True).splitlines()
main_pid=next((int(x.strip().split(None,1)[0]) for x in proc if 'python3 main.py --enable-assets' in x),None)
if not main_pid: raise RuntimeError('Cannot identify existing managed ComfyUI process')
lastbeat=time.monotonic()
for name in ('images','workflows','runs'):
 for model in MODELS:(ROOT/name/model).mkdir(parents=True,exist_ok=True)
for p in (ROOT/'images',ROOT/'workflows',ROOT/'runs'):
 (p/'qwen21_pe').mkdir(parents=True,exist_ok=True)
TEMP=COMFY/'output'/'infograph-data-matrix-v2'
TEMP.mkdir(parents=True,exist_ok=True)

def now(): return datetime.now(timezone.utc).isoformat()
def beat(force=False):
 global lastbeat
 if force or time.monotonic()-lastbeat>=90:
  p=subprocess.run(['hive-resource','lease','heartbeat',LEASE,'--ttl',TTL],capture_output=True,text=True)
  if p.returncode: raise RuntimeError('GPU lease heartbeat failed: '+p.stderr+p.stdout)
  lastbeat=time.monotonic()
def sample():
 raw=subprocess.check_output(['nvidia-smi','--query-gpu=memory.used,utilization.gpu,temperature.gpu','--format=csv,noheader,nounits'],text=True).strip().split(',')
 rss=subprocess.check_output(['ps','-o','rss=','-p',str(main_pid)],text=True).strip()
 return {'time':now(),'vram_used_mb':int(raw[0]),'gpu_util_pct':int(raw[1]),'temperature_c':int(raw[2]),'comfy_rss_mb':round(int(rss or 0)/1024)}

def graph(model,prompt,seed,job):
 if model=='qwen21':
  return {'1':{'class_type':'UNETLoader','inputs':{'unet_name':'qwen_image_2.1_bf16.safetensors','weight_dtype':'default'}},
   '2':{'class_type':'CLIPLoader','inputs':{'clip_name':'qwen3.5_9b_qwen_image_2.1_pe_t2i.int8_convrot.safetensors','type':'qwen_image'}},
   '3':{'class_type':'CLIPLoader','inputs':{'clip_name':'qwen3vl_8b_bf16.safetensors','type':'qwen_image'}},
   '4':{'class_type':'VAELoader','inputs':{'vae_name':'qwen_image_2.1_vae_bf16.safetensors'}},
   '5':{'class_type':'QwenImage21_T2IPromptRewrite','inputs':{'clip':['2',0],'prompt':prompt,'temperature':1.0,'top_p':0.95,'top_k':20,'presence_penalty':1.5,'max_new_tokens':16256,'seed':seed}},
   '6':{'class_type':'CLIPTextEncode','inputs':{'clip':['3',0],'text':['5',0]}},'7':{'class_type':'CLIPTextEncode','inputs':{'clip':['3',0],'text':['5',1]}},
   '8':{'class_type':'EmptyLatentImage','inputs':{'width':1536,'height':1024,'batch_size':1}},
   '9':{'class_type':'KSampler','inputs':{'model':['1',0],'positive':['6',0],'negative':['7',0],'latent_image':['8',0],'seed':seed,'steps':40,'cfg':1.0,'sampler_name':'euler','scheduler':'simple','denoise':1.0}},
   '10':{'class_type':'VAEDecode','inputs':{'samples':['9',0],'vae':['4',0]}},'11':{'class_type':'SaveImage','inputs':{'images':['10',0],'filename_prefix':f'infograph-data-matrix-v2/{job}'}},
   '12':{'class_type':'SaveText','inputs':{'text':['5',0],'filename_prefix':f'infograph-data-matrix-v2/{job}','format':'txt'}}}
 if model=='krea2':
  return {'1':{'class_type':'UNETLoader','inputs':{'unet_name':'krea2_raw_bf16.safetensors','weight_dtype':'default'}},'2':{'class_type':'CLIPLoader','inputs':{'clip_name':'qwen3vl_4b_bf16.safetensors','type':'krea2'}},'3':{'class_type':'VAELoader','inputs':{'vae_name':'qwen_image_vae.safetensors'}},
   '4':{'class_type':'CLIPTextEncode','inputs':{'clip':['2',0],'text':prompt}},'5':{'class_type':'CLIPTextEncode','inputs':{'clip':['2',0],'text':'watermark, logo, blurry'}},'6':{'class_type':'EmptySD3LatentImage','inputs':{'width':1536,'height':1024,'batch_size':1}},
   '7':{'class_type':'KSampler','inputs':{'model':['1',0],'positive':['4',0],'negative':['5',0],'latent_image':['6',0],'seed':seed,'steps':52,'cfg':3.5,'sampler_name':'euler','scheduler':'simple','denoise':1.0}},'8':{'class_type':'VAEDecode','inputs':{'samples':['7',0],'vae':['3',0]}},'9':{'class_type':'SaveImage','inputs':{'images':['8',0],'filename_prefix':f'infograph-data-matrix-v2/{job}'}}
  }
 return {'1':{'class_type':'UNETLoader','inputs':{'unet_name':'flux-2-klein-9b.safetensors','weight_dtype':'default'}},'2':{'class_type':'CLIPLoader','inputs':{'clip_name':'qwen_3_8b.safetensors','type':'flux2'}},'3':{'class_type':'VAELoader','inputs':{'vae_name':'flux2-vae.safetensors'}},
  '4':{'class_type':'CLIPTextEncode','inputs':{'clip':['2',0],'text':prompt}},'5':{'class_type':'CLIPTextEncode','inputs':{'clip':['2',0],'text':''}},'6':{'class_type':'EmptyFlux2LatentImage','inputs':{'width':1536,'height':1024,'batch_size':1}},'7':{'class_type':'Flux2Scheduler','inputs':{'steps':50,'width':1536,'height':1024}},
  '8':{'class_type':'CFGGuider','inputs':{'model':['1',0],'positive':['4',0],'negative':['5',0],'cfg':3.5}},'9':{'class_type':'RandomNoise','inputs':{'noise_seed':seed}},'10':{'class_type':'KSamplerSelect','inputs':{'sampler_name':'euler'}},'11':{'class_type':'SamplerCustomAdvanced','inputs':{'noise':['9',0],'guider':['8',0],'sampler':['10',0],'sigmas':['7',0],'latent_image':['6',0]}},'12':{'class_type':'VAEDecode','inputs':{'samples':['11',0],'vae':['3',0]}},'13':{'class_type':'SaveImage','inputs':{'images':['12',0],'filename_prefix':f'infograph-data-matrix-v2/{job}'}}
 }

def run(model,c,seed=42):
 job=f"{c['id']}__{model}"
 promptfile=ROOT/'prompts'/model/f"{c['id']}.txt"
 prompt=promptfile.read_text().strip()
 imgdir=ROOT/'images'/model; wfdir=ROOT/'workflows'/model; rundir=ROOT/'runs'/model
 image=imgdir/f'{job}.png'; record=rundir/f'{job}.json'; workflow=wfdir/f'{job}.json'; samplesfile=rundir/f'{job}_gpu_samples.jsonl'
 if record.exists() and image.exists() and json.loads(record.read_text()).get('status')=='success': return json.loads(record.read_text())
 beat(True)
 q=session.get(BASE+'/queue',timeout=15).json()
 if q.get('queue_running') or q.get('queue_pending'): raise RuntimeError('Shared ComfyUI queue is not empty; refusing to submit')
 g=graph(model,prompt,seed,job)
 workflow.write_text(json.dumps({'prompt':g},ensure_ascii=False,indent=2)+'\n')
 wf_rel=str(workflow.relative_to(ROOT)); image_rel=str(image.relative_to(ROOT))
 params={'resolution':'1536x1024','seed':seed,'diffusion_weights':'BF16','sampler':'euler','steps':40,'cfg':1.0,'scheduler':'simple'}
 if model=='qwen21': params.update({'text_encoder':'qwen3vl_8b_bf16.safetensors','prompt_enhancer':'qwen3.5_9b_qwen_image_2.1_pe_t2i.int8_convrot.safetensors','pe_temperature':1.0,'pe_top_p':0.95,'pe_top_k':20,'pe_presence_penalty':1.5,'vae':'qwen_image_2.1_vae_bf16.safetensors'})
 elif model=='krea2': params.update({'steps':52,'cfg':3.5,'text_encoder':'qwen3vl_4b_bf16.safetensors','negative_prompt':'watermark, logo, blurry','vae':'qwen_image_vae.safetensors'})
 else: params.update({'steps':50,'cfg':3.5,'scheduler':'Flux2Scheduler','text_encoder':'qwen_3_8b.safetensors','vae':'flux2-vae.safetensors'})
 runrec={'owner':'Sean','task_id':TASK,'experiment':'data_matrix_v2','job':job,'case_id':c['id'],'model':model,'language':c['lang'],'seed':seed,'data_source':c['data_source'],'source_url':c.get('source_url'),'ground_truth':c['rows'],'key_claim':c['key'],'input_prompt_file':str(promptfile.relative_to(ROOT)),'input_prompt':prompt,'parameters':params,'workflow':wf_rel,'image':image_rel,'resource_lease_id':LEASE,'started_at':now()}
 started=time.monotonic(); response=session.post(BASE+'/prompt',json={'prompt':g,'client_id':str(uuid.uuid4())},timeout=60); response.raise_for_status(); pid=response.json()['prompt_id']; runrec['prompt_id']=pid
 samples=[]; last=0; lastseen=time.monotonic()
 while time.monotonic()-started<7200:
  beat()
  if time.monotonic()-last>=3: samples.append(sample()); last=time.monotonic()
  history=session.get(f'{BASE}/history/{pid}',timeout=15).json().get(pid)
  if history and history.get('status',{}).get('completed'): break
  if history and history.get('status',{}).get('status_str')=='error': raise RuntimeError(str(history.get('status',{}).get('messages')))
  if not history:
   q=session.get(BASE+'/queue',timeout=15).json(); active=q.get('queue_running',[])+q.get('queue_pending',[])
   if any(str(x[1])==pid for x in active): lastseen=time.monotonic()
   elif time.monotonic()-lastseen>120: raise RuntimeError('Prompt disappeared without completion')
  time.sleep(2)
 else: raise TimeoutError('Generation exceeded two hours')
 output_node='11' if model=='qwen21' else ('9' if model=='krea2' else '13')
 imgs=history.get('outputs',{}).get(output_node,{}).get('images',[])
 if not imgs: raise RuntimeError('No image saved in ComfyUI history')
 out=imgs[0]; src=COMFY/'output'/out.get('subfolder','')/out['filename']; shutil.copy2(src,image); src.unlink()
 pe_rel=None
 if model=='qwen21':
  txts=list(TEMP.glob('*.txt'))
  if not txts: raise RuntimeError('Qwen PE produced no saved prompt text')
  pe_dest=ROOT/'prompts'/'qwen21_pe_outputs'/f'{job}.txt'; pe_dest.parent.mkdir(parents=True,exist_ok=True)
  latest=max(txts,key=lambda p:p.stat().st_mtime); shutil.copy2(latest,pe_dest); latest.unlink(); pe_rel=str(pe_dest.relative_to(ROOT))
 with Image.open(image) as pic: pic.load(); dims=list(pic.size)
 if dims!=[1536,1024]: raise RuntimeError(f'Unexpected dimensions {dims}')
 samplesfile.write_text(''.join(json.dumps(x)+'\n' for x in samples))
 with image.open('rb') as f: digest=hashlib.sha256(f.read()).hexdigest()
 runrec.update({'status':'success','completed_at':now(),'elapsed_seconds':round(time.monotonic()-started,2),'dimensions':dims,'image_sha256':digest,'actual_pe_prompt_file':pe_rel,'peak_vram_mb_observed':max((x['vram_used_mb'] for x in samples),default=None),'peak_comfy_rss_mb_observed':max((x['comfy_rss_mb'] for x in samples),default=None),'peak_temperature_c_observed':max((x['temperature_c'] for x in samples),default=None),'gpu_samples_file':str(samplesfile.relative_to(ROOT)),'gpu_sample_count':len(samples)})
 record.write_text(json.dumps(runrec,ensure_ascii=False,indent=2)+'\n')
 with (ROOT/'runs'/'runs.jsonl').open('a') as f:f.write(json.dumps(runrec,ensure_ascii=False)+'\n')
 print(f"{job}: {runrec['elapsed_seconds']}s, VRAM {runrec['peak_vram_mb_observed']} MB",flush=True)
 return runrec

results=[]
for model in MODELS:
 for case in CASES:
  job=f"{case['id']}__{model}"
  try: result=run(model,case); results.append(result)
  except Exception as exc:
   result={'owner':'Sean','task_id':TASK,'experiment':'data_matrix_v2','job':job,'case_id':case['id'],'model':model,'status':'failed','failed_at':now(),'error':repr(exc),'resource_lease_id':LEASE}
   (ROOT/'runs'/model/f'{job}.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n'); results.append(result); print(job,'FAILED',repr(exc),flush=True)
   if 'lease heartbeat failed' in repr(exc).lower(): break
manifest={'owner':'Sean','task_id':TASK,'version':'v2','cases':len(CASES),'models':list(MODELS),'planned_images':len(CASES)*len(MODELS),'successes':sum(x.get('status')=='success' for x in results),'failures':sum(x.get('status')=='failed' for x in results),'resource_lease_id':LEASE,'results':results}
(ROOT/'runs'/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
print(f"V2 COMPLETE {manifest['successes']}/{manifest['planned_images']}",flush=True)
