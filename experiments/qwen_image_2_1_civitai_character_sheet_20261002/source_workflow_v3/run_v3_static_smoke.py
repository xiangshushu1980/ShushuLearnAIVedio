#!/usr/bin/env python3
"""[Sean] Run the V3 Simple static prompt through the local Qwen int8 route."""
import json, os, shutil, subprocess, time, urllib.parse, urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
API='http://127.0.0.1:8188'; LEASE=os.environ['HIVE_LEASE_ID']
PREFIX='sean_qwen_civitai_character_sheet_v3_static_20261002'
SOURCE=ROOT/'inputs/qwen_generated_fullbody.png'
REMOTE='sean_qwen_civitai_v3_static_source_20261002.png'

def request(path,payload=None,data=None,headers=None):
 if payload is not None:
  data=json.dumps(payload).encode(); headers={**(headers or {}),'Content-Type':'application/json'}
 return urllib.request.urlopen(urllib.request.Request(API+path,data=data,headers=headers or {}),timeout=60).read()

def upload(path):
 b='----SeanQwenCivitaiV3Static20261002'
 body=(f'--{b}\r\nContent-Disposition: form-data; name="image"; filename="{REMOTE}"\r\nContent-Type: image/png\r\n\r\n'.encode()+path.read_bytes()+f'\r\n--{b}\r\nContent-Disposition: form-data; name="type"\r\n\r\ninput\r\n--{b}\r\nContent-Disposition: form-data; name="overwrite"\r\n\r\ntrue\r\n--{b}--\r\n'.encode())
 request('/upload/image',data=body,headers={'Content-Type':f'multipart/form-data; boundary={b}'})

def main():
 graph=json.loads((ROOT/'source_workflow_v3/v3_simple_static_adapted_api.json').read_text())
 queue=json.loads(request('/queue'))
 if queue.get('queue_running') or queue.get('queue_pending'): raise RuntimeError('Shared ComfyUI queue is busy')
 upload(SOURCE)
 pid=json.loads(request('/prompt',{'prompt':graph,'client_id':'sean-qwen-civitai-v3-static-20261002'}))['prompt_id']
 start=time.time(); beat=start
 while time.time()-start<900:
  history=json.loads(request('/history/'+pid)).get(pid,{})
  if history.get('status',{}).get('status_str')=='error': raise RuntimeError(json.dumps(history.get('status'),ensure_ascii=False))
  images=[im for n in history.get('outputs',{}).values() for im in n.get('images',[])]
  if images:
   im=images[0]; q=urllib.parse.urlencode({'filename':im['filename'],'subfolder':im.get('subfolder',''),'type':im.get('type','output')})
   dest=ROOT/'outputs/v3_simple_static.png'; dest.write_bytes(request('/view?'+q))
   result={'id':'v3_simple_static','prompt_id':pid,'seconds':round(time.time()-start,2),'output':'outputs/v3_simple_static.png','seed':6200605,'output_size':'1536x1024','comfy_image':im,'adaptation':'V3 Simple built-in static prompt; local Qwen Image 2.1 int8 stack; standard VAE decode substituted for unavailable VAEDeGrid; 1.57MP output.'}
   manifest_path=ROOT/'manifest.json'; manifest=json.loads(manifest_path.read_text())
   manifest['v3_simple_static_smoke']=result; manifest['results'].append(result)
   manifest['runtime']['v3_workflow_adaptation']='V3 Simple static prompt; no PE model needed; VAEDeGrid replaced with standard VAE decode; Qwen3VL 8B int8 and 1536x1024 retained from local baseline.'
   manifest_path.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
   subprocess.run(['hive-resource','observe','--resource','gpu:0','--job','qwen_image_2_1_civitai_v3_static_20261002','--metrics',json.dumps({'elapsedSeconds':result['seconds'],'peakVramMeasured':False,'result':'success'})],check=True,capture_output=True)
   subprocess.run(['hive-resource','lease','release',LEASE],check=True,capture_output=True)
   tmp=Path('/home/sean/projects/ComfyUI/output')/PREFIX
   expected={im['filename']}
   if tmp.exists():
    actual={p.name for p in tmp.iterdir() if p.is_file()}
    if actual!=expected: raise RuntimeError(f'Unexpected temp output files: {actual-expected}')
    shutil.rmtree(tmp)
   ip=Path('/home/sean/projects/ComfyUI/input')/REMOTE
   if ip.exists(): ip.unlink()
   print(json.dumps(result,ensure_ascii=False),flush=True); return
  if time.time()-beat>45:
   subprocess.run(['hive-resource','lease','heartbeat',LEASE,'--ttl','600000'],check=True,capture_output=True); beat=time.time()
  time.sleep(2)
 raise TimeoutError(pid)

if __name__=='__main__': main()
