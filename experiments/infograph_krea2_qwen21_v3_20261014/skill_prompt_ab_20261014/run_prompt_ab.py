#!/usr/bin/env python3
"""Owner: Sean. Run a matched Qwen-Image-2.1 prompt-method comparison on shared ComfyUI."""
import hashlib, json, os, shutil, subprocess, time, uuid
from datetime import datetime, timezone
from pathlib import Path
import requests
from PIL import Image

ROOT = Path(__file__).resolve().parent
COMFY = Path('/home/sean/projects/ComfyUI')
BASE = 'http://127.0.0.1:8188'
TASK = 'remote-97ccaaac-e730-4c57-875c-c86954ca0518'
LEASE = os.environ['HIVE_RESOURCE_LEASE_ID']
TTL = '600000'
SEEDS = [42, 1337]
ARMS = ['baseline', 'skill_guided']
cases = json.loads((ROOT/'casebook.json').read_text())['cases']
session = requests.Session()
proc = subprocess.check_output(['ps','-eo','pid=,args='], text=True).splitlines()
main_pid = next((int(x.strip().split(None,1)[0]) for x in proc if 'python3 main.py --enable-assets' in x), None)
if not main_pid: raise RuntimeError('Cannot identify existing managed ComfyUI process')
lastbeat = time.monotonic()
TEMP = COMFY/'output'/'infograph-skill-prompt-ab-20261014'
TEMP.mkdir(parents=True, exist_ok=True)
for folder in ['images','workflows','runs','prompts/qwen_pe_outputs']:
    (ROOT/folder).mkdir(parents=True, exist_ok=True)

def now(): return datetime.now(timezone.utc).isoformat()
def beat(force=False):
    global lastbeat
    if force or time.monotonic()-lastbeat >= 90:
        p = subprocess.run(['hive-resource','lease','heartbeat',LEASE,'--ttl',TTL],capture_output=True,text=True)
        if p.returncode: raise RuntimeError('GPU lease heartbeat failed: '+p.stderr+p.stdout)
        lastbeat = time.monotonic()
def sample():
    raw = subprocess.check_output(['nvidia-smi','--query-gpu=memory.used,utilization.gpu,temperature.gpu','--format=csv,noheader,nounits'],text=True).strip().split(',')
    rss = subprocess.check_output(['ps','-o','rss=','-p',str(main_pid)],text=True).strip()
    return {'time':now(),'vram_used_mb':int(raw[0]),'gpu_util_pct':int(raw[1]),'temperature_c':int(raw[2]),'comfy_rss_mb':round(int(rss or 0)/1024)}

def graph(prompt, seed, job):
    return {
      '1':{'class_type':'UNETLoader','inputs':{'unet_name':'qwen_image_2.1_bf16.safetensors','weight_dtype':'default'}},
      '2':{'class_type':'CLIPLoader','inputs':{'clip_name':'qwen3.5_9b_qwen_image_2.1_pe_t2i.int8_convrot.safetensors','type':'qwen_image'}},
      '3':{'class_type':'CLIPLoader','inputs':{'clip_name':'qwen3vl_8b_bf16.safetensors','type':'qwen_image'}},
      '4':{'class_type':'VAELoader','inputs':{'vae_name':'qwen_image_2.1_vae_bf16.safetensors'}},
      '5':{'class_type':'QwenImage21_T2IPromptRewrite','inputs':{'clip':['2',0],'prompt':prompt,'temperature':1.0,'top_p':0.95,'top_k':20,'presence_penalty':1.5,'max_new_tokens':16256,'seed':seed}},
      '6':{'class_type':'CLIPTextEncode','inputs':{'clip':['3',0],'text':['5',0]}},
      '7':{'class_type':'CLIPTextEncode','inputs':{'clip':['3',0],'text':['5',1]}},
      '8':{'class_type':'EmptyLatentImage','inputs':{'width':1536,'height':1024,'batch_size':1}},
      '9':{'class_type':'KSampler','inputs':{'model':['1',0],'positive':['6',0],'negative':['7',0],'latent_image':['8',0],'seed':seed,'steps':40,'cfg':1.0,'sampler_name':'euler','scheduler':'simple','denoise':1.0}},
      '10':{'class_type':'VAEDecode','inputs':{'samples':['9',0],'vae':['4',0]}},
      '11':{'class_type':'SaveImage','inputs':{'images':['10',0],'filename_prefix':f'infograph-skill-prompt-ab-20261014/{job}'}},
      '12':{'class_type':'SaveText','inputs':{'text':['5',0],'filename_prefix':f'infograph-skill-prompt-ab-20261014/{job}','format':'txt'}}
    }

def run(arm, case, seed):
    job = f'{case["id"]}__{arm}__seed{seed}'
    image = ROOT/'images'/f'{job}.png'; record = ROOT/'runs'/f'{job}.json'
    wf = ROOT/'workflows'/f'{job}.json'; samples_file = ROOT/'runs'/f'{job}_gpu_samples.jsonl'
    if record.exists() and image.exists() and json.loads(record.read_text()).get('status') == 'success': return json.loads(record.read_text())
    promptfile = ROOT/'prompts'/arm/f'{case["id"]}.txt'; prompt = promptfile.read_text().strip()
    beat(True)
    q = session.get(BASE+'/queue',timeout=15).json()
    if q.get('queue_running') or q.get('queue_pending'): raise RuntimeError('Shared ComfyUI queue is not empty; refusing to submit')
    g = graph(prompt,seed,job)
    wf.write_text(json.dumps({'prompt':g},ensure_ascii=False,indent=2)+'\n')
    params = {'resolution':'1536x1024','seed':seed,'diffusion_weights':'BF16','text_encoder':'qwen3vl_8b_bf16.safetensors','prompt_enhancer':'qwen3.5_9b_qwen_image_2.1_pe_t2i.int8_convrot.safetensors','pe_temperature':1.0,'pe_top_p':0.95,'pe_top_k':20,'pe_presence_penalty':1.5,'vae':'qwen_image_2.1_vae_bf16.safetensors','sampler':'euler','steps':40,'cfg':1.0,'scheduler':'simple','lora':None}
    rec = {'owner':'Sean','task_id':TASK,'experiment':'skill_prompt_ab_20261014','job':job,'case_id':case['id'],'prompt_arm':arm,'language':'en','seed':seed,'takeaway':case['takeaway'],'topology':case['topology'],'data_source':case['data_source'],'source_url':case['source_url'],'ground_truth':case['rows'],'input_prompt_file':str(promptfile.relative_to(ROOT)),'input_prompt':prompt,'parameters':params,'workflow':str(wf.relative_to(ROOT)),'image':str(image.relative_to(ROOT)),'resource_lease_id':LEASE,'started_at':now()}
    started = time.monotonic(); response = session.post(BASE+'/prompt',json={'prompt':g,'client_id':str(uuid.uuid4())},timeout=60); response.raise_for_status(); pid=response.json()['prompt_id']; rec['prompt_id']=pid
    samples=[]; last=0; lastseen=time.monotonic()
    while time.monotonic()-started < 3600:
        beat()
        if time.monotonic()-last >= 3: samples.append(sample()); last=time.monotonic()
        hist=session.get(f'{BASE}/history/{pid}',timeout=15).json().get(pid)
        if hist and hist.get('status',{}).get('completed'): break
        if hist and hist.get('status',{}).get('status_str')=='error': raise RuntimeError(str(hist.get('status',{}).get('messages')))
        if not hist:
            q=session.get(BASE+'/queue',timeout=15).json(); active=q.get('queue_running',[])+q.get('queue_pending',[])
            if any(str(x[1])==pid for x in active): lastseen=time.monotonic()
            elif time.monotonic()-lastseen>120: raise RuntimeError('Prompt disappeared without completion')
        time.sleep(2)
    else: raise TimeoutError('Generation exceeded one hour')
    imgs=hist.get('outputs',{}).get('11',{}).get('images',[])
    if not imgs: raise RuntimeError('No image in ComfyUI history')
    out=imgs[0]; src=COMFY/'output'/out.get('subfolder','')/out['filename']; shutil.copy2(src,image); src.unlink()
    pefiles=list(TEMP.glob('*.txt'))
    if not pefiles: raise RuntimeError('Qwen PE SaveText output missing')
    latest=max(pefiles,key=lambda p:p.stat().st_mtime); pe=ROOT/'prompts/qwen_pe_outputs'/f'{job}.txt'; shutil.copy2(latest,pe); latest.unlink()
    with Image.open(image) as im: im.load(); dims=list(im.size)
    if dims != [1536,1024]: raise RuntimeError(f'Unexpected dimensions {dims}')
    samples_file.write_text(''.join(json.dumps(x)+'\n' for x in samples))
    digest=hashlib.sha256(image.read_bytes()).hexdigest()
    rec.update({'status':'success','completed_at':now(),'elapsed_seconds':round(time.monotonic()-started,2),'dimensions':dims,'image_sha256':digest,'actual_pe_prompt_file':str(pe.relative_to(ROOT)),'peak_vram_mb_observed':max((x['vram_used_mb'] for x in samples),default=None),'peak_comfy_rss_mb_observed':max((x['comfy_rss_mb'] for x in samples),default=None),'peak_temperature_c_observed':max((x['temperature_c'] for x in samples),default=None),'gpu_samples_file':str(samples_file.relative_to(ROOT)),'gpu_sample_count':len(samples)})
    record.write_text(json.dumps(rec,ensure_ascii=False,indent=2)+'\n')
    print(f'{job}: {rec["elapsed_seconds"]}s, VRAM {rec["peak_vram_mb_observed"]} MB',flush=True)
    return rec

results=[]
for case in cases:
    for seed in SEEDS:
        for arm in ARMS:
            try: results.append(run(arm,case,seed))
            except Exception as e:
                fail={'owner':'Sean','task_id':TASK,'experiment':'skill_prompt_ab_20261014','job':f'{case["id"]}__{arm}__seed{seed}','case_id':case['id'],'prompt_arm':arm,'seed':seed,'status':'failed','error':repr(e),'failed_at':now(),'resource_lease_id':LEASE}
                (ROOT/'runs'/f'{fail["job"]}.json').write_text(json.dumps(fail,ensure_ascii=False,indent=2)+'\n'); results.append(fail); print(fail['job'],'FAILED',fail['error'],flush=True)
                if 'lease heartbeat failed' in repr(e).lower(): break
manifest={'owner':'Sean','task_id':TASK,'experiment':'skill_prompt_ab_20261014','version':'skill-prompt-ab-v1','cases':len(cases),'arms':ARMS,'seeds':SEEDS,'planned_images':len(cases)*len(ARMS)*len(SEEDS),'successes':sum(x.get('status')=='success' for x in results),'failures':sum(x.get('status')=='failed' for x in results),'resource_lease_id':LEASE,'results':results}
(ROOT/'runs/manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
print(f'BATCH COMPLETE {manifest["successes"]}/{manifest["planned_images"]}',flush=True)
