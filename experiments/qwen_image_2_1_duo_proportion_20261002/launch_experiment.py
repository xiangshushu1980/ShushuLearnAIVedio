#!/usr/bin/env python3
"""[Sean] Run Qwen proportion test under a shared GPU lease."""
import json,os,re,runpy,subprocess,sys,threading
from pathlib import Path
ROOT=Path(__file__).resolve().parent;job='qwen_image_2_1_duo_proportion_20261002'
raw=subprocess.check_output(['hive-resource','lease','acquire','--owner',job,'--resources','gpu:0','--pid',str(os.getpid()),'--ttl','600000'],text=True);m=re.search(r'租约 ([0-9a-f-]{36}) 已授予',raw)
if not m:raise RuntimeError(raw)
lease=m.group(1);peak={'memory_used_mb':0,'utilization_gpu_pct':0};stop=threading.Event()
def sample():
 while not stop.is_set():
  try:
   row=subprocess.check_output(['nvidia-smi','--query-gpu=memory.used,utilization.gpu','--format=csv,noheader,nounits'],text=True,timeout=5).strip().splitlines()[0];v,u=[int(x.strip()) for x in row.split(',')];peak['memory_used_mb']=max(peak['memory_used_mb'],v);peak['utilization_gpu_pct']=max(peak['utilization_gpu_pct'],u)
  except Exception:pass
  stop.wait(2)
t=threading.Thread(target=sample,daemon=True);t.start()
try:
 sys.argv=[str(ROOT/'run_experiment.py'),'--lease-id',lease,*sys.argv[1:]];runpy.run_path(sys.argv[0],run_name='__main__');peak['sampled_during_run']=True;subprocess.run(['hive-resource','observe','--resource','gpu:0','--job',job,'--metrics',json.dumps(peak)],check=True)
finally:stop.set();t.join(timeout=6);subprocess.run(['hive-resource','lease','release',lease],check=False)
