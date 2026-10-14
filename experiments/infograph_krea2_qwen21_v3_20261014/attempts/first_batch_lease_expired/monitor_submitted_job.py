#!/usr/bin/env python3
"""Owner: Sean. Monitor and archive an already-submitted ComfyUI job."""
import json, shutil, subprocess, time
from datetime import datetime, timezone
from pathlib import Path
import requests

ROOT = Path(__file__).resolve().parent
COMFY = Path('/home/sean/projects/ComfyUI')
BASE = 'http://127.0.0.1:8188'
JOB = 'krea2_raw_fp8_zh'
PROMPT_ID = '539ff888-634f-4d08-986c-8165a539acdb'
LEASE = '929cdf4c-8f15-43fa-aa2c-682f2207246e'
TTL = '600000'
session = requests.Session()
pid = int(subprocess.check_output(['systemctl','--user','show','comfyui.service','-p','MainPID','--value'], text=True).strip())

def now(): return datetime.now(timezone.utc).isoformat()

q = session.get(f'{BASE}/queue', timeout=10).json()
entry = next((e for e in q.get('queue_running',[]) + q.get('queue_pending',[]) if e[1] == PROMPT_ID), None)
started_ms = (entry[3].get('create_time') if entry and len(entry) > 3 else None) or int(time.time()*1000)
started_at = datetime.fromtimestamp(started_ms/1000, timezone.utc).isoformat()
samples=[]; last_sample=0; last_beat=time.monotonic()
while True:
    if time.monotonic()-last_beat >= 90:
        cp=subprocess.run(['hive-resource','lease','heartbeat',LEASE,'--ttl',TTL],text=True,capture_output=True)
        if cp.returncode: raise RuntimeError(f'Lease heartbeat failed: {cp.stderr or cp.stdout}')
        last_beat=time.monotonic()
    if time.monotonic()-last_sample >= 3:
        raw=subprocess.check_output(['nvidia-smi','--query-gpu=memory.used,utilization.gpu,temperature.gpu','--format=csv,noheader,nounits'],text=True).strip().split(',')
        rss=subprocess.check_output(['ps','-o','rss=','-p',str(pid)],text=True).strip()
        sample={'time':now(),'vram_used_mb':int(raw[0]),'gpu_util_pct':int(raw[1]),'temperature_c':int(raw[2]),'comfy_rss_mb':round(int(rss or 0)/1024)}
        samples.append(sample)
        with (ROOT/'runs'/f'{JOB}_gpu_samples.jsonl').open('a',encoding='utf-8') as f: f.write(json.dumps(sample)+'\n')
        last_sample=time.monotonic()
    hist=session.get(f'{BASE}/history/{PROMPT_ID}',timeout=10).json().get(PROMPT_ID)
    if hist:
        status=hist.get('status',{})
        if status.get('completed'): break
        if status.get('status_str')=='error': raise RuntimeError(json.dumps(status.get('messages',[]),ensure_ascii=False))
    time.sleep(2)

images=hist.get('outputs',{}).get('9',{}).get('images',[])
if not images: raise RuntimeError(f'No image output: {hist.get("outputs",{})}')
item=images[0]
source=COMFY/'output'/item.get('subfolder','')/item['filename']
target=ROOT/'images'/f'{JOB}.png'
shutil.copy2(source,target); source.unlink()
elapsed=round(time.time()-started_ms/1000,2)
run={'job':JOB,'owner':'Sean','status':'success','submitted_at':started_at,'completed_at':now(),'elapsed_seconds':elapsed,'workflow':'workflows/krea2_raw_fp8_zh.json','input_prompt':(ROOT/'prompts'/'krea2_raw_zh.txt').read_text(encoding='utf-8').strip(),'seed':42,'resolution':'1536x1024','image':str(target.relative_to(ROOT)),'image_file':item,'peak_vram_mb_observed':max(s['vram_used_mb'] for s in samples),'peak_comfy_rss_mb_observed':max(s['comfy_rss_mb'] for s in samples),'peak_temperature_c_observed':max(s['temperature_c'] for s in samples),'peak_gpu_utilization_pct_observed':max(s['gpu_util_pct'] for s in samples),'gpu_samples':len(samples),'comfy_history_status':hist.get('status',{}),'recovery_note':'The prompt had been accepted before the previous lease-expiry check. Monitoring resumed only after a new gpu:0 lease was granted.'}
(ROOT/'runs'/f'{JOB}.json').write_text(json.dumps(run,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
with (ROOT/'runs'/'runs.jsonl').open('a',encoding='utf-8') as f: f.write(json.dumps(run,ensure_ascii=False)+'\n')
print(json.dumps(run,ensure_ascii=False,indent=2))
