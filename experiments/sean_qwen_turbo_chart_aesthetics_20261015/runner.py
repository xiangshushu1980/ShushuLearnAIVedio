#!/usr/bin/env python3
"""Owner: Sean. Material reconstruction runner. Adapted from ../sean_qwen_turbo_chart_control_20261015/run.py."""
import json, time, uuid, subprocess, hashlib, shutil, sys
from pathlib import Path
import requests
R=Path(__file__).resolve().parent
P=json.loads((R/'plan.json').read_text())
B='http://127.0.0.1:8188'; C=Path('/home/sean/projects/ComfyUI')
S=requests.Session(); lease=None; lastbeat=0
for d in ['prompts','workflows','runs','images']: (R/d).mkdir(exist_ok=True)
def write(path,obj): path.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
def beat():
 global lastbeat
 if time.monotonic()-lastbeat>90:
  v=subprocess.run(['hive-resource','lease','heartbeat',lease,'--ttl','600000'],capture_output=True,text=True)
  if v.returncode: raise RuntimeError(v.stdout+v.stderr)
  lastbeat=time.monotonic()
def get(path):
 r=S.get(B+path,timeout=20);r.raise_for_status();return r.json()
def execute(job,g):
 target=R/'runs'/f'{job}.json'
 if target.exists():
  old=json.loads(target.read_text())
  if old['status']=='success': return old
 q=get('/queue')
 if q['queue_running'] or q['queue_pending']: raise RuntimeError('Shared queue occupied; stop submitting')
 beat();write(R/'workflows'/f'{job}.json',{'prompt':g})
 start=time.monotonic();r=S.post(B+'/prompt',json={'prompt':g,'client_id':str(uuid.uuid4())},timeout=90)
 if r.status_code!=200: raise RuntimeError(r.text)
 pid=r.json()['prompt_id'];samples=[];prev=0
 while time.monotonic()-start<1800:
  beat();h=get('/history/'+pid).get(pid)
  if time.monotonic()-prev>3:
   raw=subprocess.check_output(['nvidia-smi','--query-gpu=memory.used,utilization.gpu,temperature.gpu','--format=csv,noheader,nounits'],text=True).strip()
   samples.append({'seconds':round(time.monotonic()-start,2),'gpu':raw});prev=time.monotonic()
  if h and h.get('status',{}).get('status_str')=='error': raise RuntimeError(str(h['status']))
  if h and h.get('status',{}).get('completed'): break
  time.sleep(1)
 else: raise TimeoutError(job)
 outputs=h.get('outputs',{}); files=[]
 for node,out in outputs.items():
  for item in out.get('images',[]):
   src=C/'output'/item.get('subfolder','')/item['filename']; dst=R/'images'/f'{job}.png';shutil.copy2(src,dst);src.unlink();files.append(str(dst.relative_to(R)))
  if 'text' in out:
   (R/'prompts'/f'{job}_ui_text.json').write_text(json.dumps(out['text'],ensure_ascii=False))
 # SaveStringKJ reports paths through UI text; archive only this job's owned files.
 for src in (C/'output'/'sean_chart_aesthetics').glob(f'{job}*.txt'):
  dst=R/'prompts'/src.name;shutil.copy2(src,dst);src.unlink();files.append(str(dst.relative_to(R)))
 record={'owner':'Sean','task_id':P['task_id'],'job':job,'status':'success','prompt_id':pid,'elapsed_seconds':round(time.monotonic()-start,2),'files':files,'history':h,'gpu_samples':samples,'lease':lease,'sha256':{f:hashlib.sha256((R/f).read_bytes()).hexdigest() for f in files}}
 write(target,record); print(job,record['elapsed_seconds'],files,flush=True);return record

def graph(prompt,seed,job):
 a=P['sampling'];g={
 '1':{'class_type':'UNETLoader','inputs':{'unet_name':a['weights'],'weight_dtype':'default'}},
 '2':{'class_type':'CLIPLoader','inputs':{'clip_name':a['text_encoder'],'type':'qwen_image'}},
 '3':{'class_type':'VAELoader','inputs':{'vae_name':a['vae']}},
 '4':{'class_type':'CLIPTextEncode','inputs':{'clip':['2',0],'text':prompt}},
 '5':{'class_type':'CLIPTextEncode','inputs':{'clip':['2',0],'text':''}},
 '6':{'class_type':'EmptySD3LatentImage','inputs':{'width':1536,'height':1024,'batch_size':1}},
 '7':{'class_type':'ManualSigmas','inputs':{'sigmas':a['sigmas']}},
 '8':{'class_type':'KSamplerSelect','inputs':{'sampler_name':'euler'}},
 '9':{'class_type':'SamplerCustom','inputs':{'model':['1',0],'add_noise':True,'noise_seed':seed,'cfg':1.0,'positive':['4',0],'negative':['5',0],'sampler':['8',0],'sigmas':['7',0],'latent_image':['6',0]}},
 '10':{'class_type':'VAEDecode','inputs':{'samples':['9',0],'vae':['3',0]}},
 '11':{'class_type':'SaveImage','inputs':{'images':['10',0],'filename_prefix':'sean_chart_aesthetics/'+job}}}
 return g

