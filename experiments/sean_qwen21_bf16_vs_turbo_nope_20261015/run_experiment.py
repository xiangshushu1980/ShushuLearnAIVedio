#!/usr/bin/env python3
"""Owner: Sean. Run the Qwen 2.1 BF16 vs Turbo no-PE bake-off."""
import hashlib, json, os, shutil, subprocess, time, uuid
from datetime import datetime, timezone
from pathlib import Path
import requests
from PIL import Image

ROOT=Path(__file__).resolve().parent
COMFY=Path('/home/sean/projects/ComfyUI')
BASE='http://127.0.0.1:8188'
TASK='remote-97ccaaac-e730-4c57-875c-c86954ca0518'
LEASE=os.environ['HIVE_RESOURCE_LEASE_ID']
TTL='600000'
SEEDS=[42,1337]
MODELS=['qwen21_bf16','qwen21_turbo_int8']
CASES=json.loads((ROOT/'source_casebook.json').read_text())['cases']
session=requests.Session()
lastbeat=time.monotonic()

def now(): return datetime.now(timezone.utc).isoformat()

def beat(force=False):
    global lastbeat
    if force or time.monotonic()-lastbeat>=90:
        p=subprocess.run(['hive-resource','lease','heartbeat',LEASE,'--ttl',TTL],capture_output=True,text=True)
        if p.returncode: raise RuntimeError('GPU lease heartbeat failed: '+p.stderr+p.stdout)
        lastbeat=time.monotonic()

def comfy_pid():
    rows=subprocess.check_output(['ps','-eo','pid=,args='],text=True).splitlines()
    for row in rows:
        if 'python3 main.py --enable-assets --enable-cors-header --fast fp16_accumulation' in row:
            return int(row.strip().split(None,1)[0])
    raise RuntimeError('Cannot identify the existing managed ComfyUI process')

def sample(pid):
    raw=subprocess.check_output(['nvidia-smi','--query-gpu=memory.used,utilization.gpu,temperature.gpu','--format=csv,noheader,nounits'],text=True).strip().split(',')
    rss=subprocess.check_output(['ps','-o','rss=','-p',str(pid)],text=True).strip()
    return {'time':now(),'vram_used_mb':int(raw[0]),'gpu_util_pct':int(raw[1]),'temperature_c':int(raw[2]),'comfy_rss_mb':round(int(rss or 0)/1024)}

def queue():
    r=session.get(BASE+'/queue',timeout=15); r.raise_for_status(); return r.json()

def wait_for_empty(timeout=900):
    start=time.monotonic()
    while True:
        beat()
        q=queue()
        if not q.get('queue_running') and not q.get('queue_pending'): return
        if time.monotonic()-start>timeout: raise TimeoutError('Shared ComfyUI queue remained occupied; not submitting another job')
        time.sleep(5)

def sha256(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda:f.read(8*1024*1024),b''): h.update(block)
    return h.hexdigest()

def update_manifest(manifest):
    manifest['successes']=sum(x.get('status')=='success' for x in manifest.get('results',[]))
    manifest['failures']=sum(x.get('status')=='failed' for x in manifest.get('results',[]))
    manifest['status']='running' if manifest['successes']+manifest['failures']<manifest['planned_images'] else ('complete' if manifest['failures']==0 else 'complete_with_failures')
    (ROOT/'runs'/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')

def run(model,case,seed,pid,manifest):
    job=f"{case['id']}__{model}__seed{seed}"
    record_path=ROOT/'runs'/f'{job}.json'
    image_path=ROOT/'images'/model/f'{job}.png'
    workflow_path=ROOT/'workflows'/f'{job}.json'
    if record_path.exists() and image_path.exists():
        old=json.loads(record_path.read_text())
        if old.get('status')=='success': return old
    prompt=next(j['prompt'] for j in manifest['jobs'] if j['job']==job)
    workflow=json.loads(workflow_path.read_text())['prompt']
    wait_for_empty()
    beat(True)
    started_at=now(); began=time.monotonic(); samples=[]; last_sample=0
    response=session.post(BASE+'/prompt',json={'prompt':workflow,'client_id':str(uuid.uuid4())},timeout=90)
    response.raise_for_status(); prompt_id=response.json()['prompt_id']
    output_node='9' if model=='qwen21_bf16' else '11'
    lastseen=time.monotonic(); history=None
    while time.monotonic()-began<7200:
        beat()
        if time.monotonic()-last_sample>=2:
            samples.append(sample(pid)); last_sample=time.monotonic()
        r=session.get(f'{BASE}/history/{prompt_id}',timeout=20); r.raise_for_status(); history=r.json().get(prompt_id)
        if history and history.get('status',{}).get('completed'): break
        if history and history.get('status',{}).get('status_str')=='error':
            raise RuntimeError(str(history.get('status',{}).get('messages')))
        if not history:
            q=queue(); active=q.get('queue_running',[])+q.get('queue_pending',[])
            if any(str(x[1])==prompt_id for x in active): lastseen=time.monotonic()
            elif time.monotonic()-lastseen>180: raise RuntimeError('Prompt disappeared from queue without completion')
        time.sleep(1)
    else: raise TimeoutError('Generation exceeded two hours')
    images=history.get('outputs',{}).get(output_node,{}).get('images',[])
    if not images: raise RuntimeError(f'No image in output node {output_node}')
    item=images[0]; temporary=COMFY/'output'/item.get('subfolder','')/item['filename']
    image_path.parent.mkdir(parents=True,exist_ok=True)
    shutil.copy2(temporary,image_path)
    with Image.open(image_path) as image:
        image.load(); dimensions=list(image.size)
    if dimensions != [1536,1024]: raise RuntimeError(f'Unexpected image dimensions: {dimensions}')
    digest=sha256(image_path)
    temporary.unlink()
    try: temporary.parent.rmdir()
    except OSError: pass
    sample_path=ROOT/'runs'/f'{job}_gpu_samples.jsonl'
    sample_path.write_text(''.join(json.dumps(x,ensure_ascii=False)+'\n' for x in samples))
    model_info=manifest['models'][model]
    result={'owner':'Sean','task_id':TASK,'experiment':ROOT.name,'job':job,'case_id':case['id'],'model':model,'checkpoint':model_info['weights'],'checkpoint_sha256':manifest['model_hashes'][model_info['weights']]['sha256'],'language':case['lang'],'seed':seed,'input_prompt':prompt,'prompt_file':f"prompts/{case['id']}.txt",'workflow_file':str(workflow_path.relative_to(ROOT)),'workflow':workflow,'prompt_id':prompt_id,'resolution':[1536,1024],'parameters':model_info,'image_file':str(image_path.relative_to(ROOT)),'image_sha256':digest,'dimensions':dimensions,'status':'success','started_at':started_at,'completed_at':now(),'elapsed_seconds':round(time.monotonic()-began,2),'gpu_lease_id':LEASE,'gpu_samples_file':str(sample_path.relative_to(ROOT)),'gpu_sample_count':len(samples),'peak_vram_mb_observed':max((x['vram_used_mb'] for x in samples),default=None),'peak_comfy_rss_mb_observed':max((x['comfy_rss_mb'] for x in samples),default=None),'peak_temperature_c_observed':max((x['temperature_c'] for x in samples),default=None)}
    record_path.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    manifest['results'].append({'job':job,'model':model,'case_id':case['id'],'seed':seed,'status':'success','seconds':result['elapsed_seconds'],'image':result['image_file'],'record':str(record_path.relative_to(ROOT)),'sha256':digest})
    update_manifest(manifest)
    print(f"{job}: {result['elapsed_seconds']}s, peak VRAM {result['peak_vram_mb_observed']} MB",flush=True)
    return result

def main():
    if not LEASE: raise RuntimeError('HIVE_RESOURCE_LEASE_ID is required')
    pid=comfy_pid()
    manifest=json.loads((ROOT/'runs'/'manifest.json').read_text())
    manifest['created_at']=manifest.get('created_at') or now()
    manifest['execution_started_at']=now(); manifest['comfyui_pid']=pid
    manifest['comfyui_url']=BASE
    manifest['results']=manifest.get('results',[])
    manifest['model_hashes']={}
    for item in manifest['models'].values():
        path=Path('/home/sean/models/comfy/diffusion_models')/item['weights']
        if not path.is_file(): raise FileNotFoundError(path)
        manifest['model_hashes'][item['weights']]={'path':str(path),'size_bytes':path.stat().st_size,'sha256':sha256(path)}
    enc=Path('/home/sean/models/comfy/text_encoders/qwen3vl_8b_bf16.safetensors')
    vae=Path('/home/sean/models/comfy/vae/qwen_image_2.1_vae_bf16.safetensors')
    manifest['shared_component_hashes']={str(p):{'size_bytes':p.stat().st_size,'sha256':sha256(p)} for p in (enc,vae)}
    update_manifest(manifest)
    print(f"Starting {manifest['planned_images']} images; ComfyUI pid={pid}; lease={LEASE}",flush=True)
    for model in MODELS:
        for case in CASES:
            for seed in SEEDS:
                try: run(model,case,seed,pid,manifest)
                except Exception as exc:
                    job=f"{case['id']}__{model}__seed{seed}"
                    failure={'owner':'Sean','task_id':TASK,'experiment':ROOT.name,'job':job,'case_id':case['id'],'model':model,'seed':seed,'status':'failed','failed_at':now(),'error':repr(exc),'gpu_lease_id':LEASE}
                    (ROOT/'runs'/f'{job}.json').write_text(json.dumps(failure,ensure_ascii=False,indent=2)+'\n')
                    manifest['results'].append({'job':job,'model':model,'case_id':case['id'],'seed':seed,'status':'failed','error':repr(exc),'record':f"runs/{job}.json"})
                    update_manifest(manifest)
                    print(f"{job} FAILED: {exc!r}",flush=True)
                    if 'lease heartbeat failed' in str(exc).lower(): return 2
    manifest['execution_finished_at']=now(); update_manifest(manifest)
    print(f"Finished {manifest['successes']}/{manifest['planned_images']} images",flush=True)
    return 0 if manifest['failures']==0 else 1

if __name__=='__main__':
    exit_code=0
    try:
        exit_code=main()
    except BaseException as exc:
        manifest_path=ROOT/'runs'/'manifest.json'
        if manifest_path.exists():
            manifest=json.loads(manifest_path.read_text())
            manifest['runner_error']=repr(exc); manifest['execution_interrupted_at']=now(); manifest['status']='interrupted'
            manifest_path.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
        print(f'Runner interrupted: {exc!r}',flush=True)
        if isinstance(exc,SystemExit): raise
        exit_code=2
    finally:
        released=subprocess.run(['hive-resource','lease','release',LEASE],capture_output=True,text=True)
        print('GPU lease release: '+(released.stdout.strip() or released.stderr.strip()),flush=True)
        if released.returncode and exit_code==0: exit_code=released.returncode
    raise SystemExit(exit_code)
