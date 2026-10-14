#!/usr/bin/env python3
"""Owner: Sean. Frozen controlled Qwen Turbo chart experiment."""
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
 for src in (C/'output'/'sean_chart_control').glob(f'{job}*.txt'):
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
 '11':{'class_type':'SaveImage','inputs':{'images':['10',0],'filename_prefix':'sean_chart_control/'+job}}}
 return g

def main():
 global lease
 phase=sys.argv[1]
 v=subprocess.run(['hive-resource','lease','acquire','--owner',P['task_id'],'--resources','gpu:0','--ttl','600000','--json'],capture_output=True,text=True)
 if v.returncode: raise RuntimeError(v.stdout+v.stderr)
 import re
 lease=re.search(r'[0-9a-f]{8}-(?:[0-9a-f]{4}-){3}[0-9a-f]{12}',v.stdout).group(0)
 if not lease: raise RuntimeError('Unrecognized lease: '+v.stdout)
 print('lease',lease,flush=True)
 try:
  for detail in ['minimal','detailed']:
   prompt=P['minimal_prompt']+(P['detail_append'] if detail=='detailed' else '')
   (R/'prompts'/f'{detail}_input.txt').write_text(prompt)
   if phase=='pe':
    job='pe_'+detail
    g={'1':{'class_type':'CLIPLoader','inputs':{'clip_name':'qwen3.5_9b_qwen_image_2.1_pe_t2i.int8_convrot.safetensors','type':'qwen_image'}},'2':{'class_type':'QwenImage21_T2IPromptRewrite','inputs':{'clip':['1',0],'prompt':prompt,'temperature':1.0,'top_p':0.95,'top_k':20,'presence_penalty':1.5,'max_new_tokens':16256,'seed':P['pe_seed']}},'3':{'class_type':'SaveStringKJ','inputs':{'string':['2',0],'filename_prefix':job+'_positive','output_folder':'sean_chart_control'}},'4':{'class_type':'SaveStringKJ','inputs':{'string':['2',3],'filename_prefix':job+'_thinking','output_folder':'sean_chart_control'}}}
    execute(job,g)
   else:
    for pe in ['off','on']:
     actual=prompt if pe=='off' else next((R/'prompts').glob('pe_'+detail+'_positive*.txt')).read_text()
     (R/'prompts'/f'{detail}_{pe}_actual.txt').write_text(actual)
     seeds=P['debug_seeds'] if phase=='debug' else P['confirmation_seeds']
     for seed in seeds:
      job=f'{phase}_{detail}_{pe}_{seed}'
      execute(job,graph(actual,seed,job))
 finally:
  if lease:
   print(subprocess.run(['hive-resource','lease','release',lease],capture_output=True,text=True).stdout,flush=True)
if __name__=='__main__': main()
