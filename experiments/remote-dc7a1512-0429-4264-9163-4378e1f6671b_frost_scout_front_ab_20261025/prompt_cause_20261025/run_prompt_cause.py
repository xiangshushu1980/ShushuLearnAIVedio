#!/usr/bin/env python3
"""Sequential, restartable-by-inspection runner for the frozen prompt cause matrix.

Requires a caller-acquired HIVE_LEASE_ID. It never retries POST /prompt and records
the prompt_id before polling. If a run is unresolved, stop and recover by receipt/history.
"""
import hashlib, json, mimetypes, os, subprocess, threading, time, urllib.parse, uuid
from pathlib import Path
import requests

ROOT = Path(__file__).resolve().parent
PLAN = json.loads((ROOT / 'plan.json').read_text())
BASE = 'http://127.0.0.1:8188'
COMFY = Path('/home/sean/projects/ComfyUI')
LEASE_ID = os.environ['HIVE_LEASE_ID']
MIN_FREE_BYTES = 2303689644  # minimum recorded before the immediately preceding successful 8-image Qwen batch

def sha_bytes(data): return hashlib.sha256(data).hexdigest()
def sha(path): return sha_bytes(path.read_bytes())
def save(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n')
def api(method, route, **kwargs):
    timeout=kwargs.pop('timeout',60)
    attempts=3 if method.upper()=='GET' else 1
    for attempt in range(attempts):
        try:
            r=requests.request(method,BASE+route,timeout=timeout,**kwargs)
            if method.upper()=='GET' and r.status_code in (502,503,504) and attempt+1<attempts:
                time.sleep(1+attempt); continue
            r.raise_for_status(); return r
        except (requests.ConnectionError,requests.Timeout):
            if method.upper()!='GET' or attempt+1>=attempts: raise
            time.sleep(1+attempt)
def lease(*args):
    return subprocess.run(['hive-resource', *args], check=True, capture_output=True, text=True, timeout=30)

class Heartbeat:
    def __init__(self): self.stop_event=threading.Event(); self.error=None
    def loop(self):
        while not self.stop_event.wait(150):
            try:
                lease('lease','heartbeat',LEASE_ID,'--ttl','600000')
                self.error=None
            except Exception as e:
                # Keep retrying; callers stop new submissions while this is set.
                self.error=str(e)
    def start(self): self.thread=threading.Thread(target=self.loop,daemon=True); self.thread.start()
    def stop(self): self.stop_event.set(); self.thread.join(timeout=3)

def upload(path, token, label):
    name=f'codex_{token}_{label}{path.suffix.lower()}'
    with path.open('rb') as f:
        r=requests.post(BASE+'/upload/image',files={'image':(name,f,mimetypes.guess_type(name)[0] or 'application/octet-stream')},data={'type':'input','overwrite':'true'},timeout=90)
    r.raise_for_status(); info=r.json()
    q=urllib.parse.urlencode({'filename':info['name'],'subfolder':info.get('subfolder',''),'type':'input'})
    if sha_bytes(api('GET','/view?'+q).content)!=sha(path): raise RuntimeError('uploaded input hash mismatch')
    return {'local_path':str(path),'sha256':sha(path),'uploaded':info}

def graph(seed, condition, appearance_name, depth_name):
    f=PLAN['fixed']; prompt=PLAN['prompts'][condition]
    return {
      '1':{'class_type':'UNETLoader','inputs':{'unet_name':f['base_model'],'weight_dtype':'default'}},
      '2':{'class_type':'CLIPLoader','inputs':{'clip_name':f['text_encoder'],'type':'qwen_image','device':'default'}},
      '3':{'class_type':'VAELoader','inputs':{'vae_name':f['vae']}},
      '4':{'class_type':'ModelPatchLoader','inputs':{'name':f['depth_control_patch']}},
      '5':{'class_type':'LoadImage','inputs':{'image':depth_name}},
      '6':{'class_type':'LoadImage','inputs':{'image':appearance_name}},
      '7':{'class_type':'TextEncodeQwenImageEditPlus','inputs':{'clip':['2',0],'prompt':prompt,'vae':['3',0],'image1':['6',0]}},
      '8':{'class_type':'QwenImageDiffsynthControlnet','inputs':{'model':['1',0],'model_patch':['4',0],'vae':['3',0],'image':['5',0],'strength':f['control_strength'],'start_percent':f['control_start_percent'],'end_percent':f['control_end_percent']}},
      '9':{'class_type':'QwenImage21Cache','inputs':{'model':['8',0],'device':'auto','dtype':'default'}},
      '10':{'class_type':'EmptySD3LatentImage','inputs':{'width':f['width'],'height':f['height'],'batch_size':1}},
      '11':{'class_type':'ConditioningZeroOut','inputs':{'conditioning':['7',0]}},
      '12':{'class_type':'KSampler','inputs':{'model':['9',0],'positive':['7',0],'negative':['11',0],'latent_image':['10',0],'seed':seed,'steps':f['steps'],'cfg':f['cfg'],'sampler_name':f['sampler'],'scheduler':f['scheduler'],'denoise':1.0}},
      '13':{'class_type':'VAEDecode','inputs':{'samples':['12',0],'vae':['3',0]}},
      '14':{'class_type':'SaveImage','inputs':{'images':['13',0],'filename_prefix':f'remote_dc7a1512_prompt_cause_{seed}_{condition}'}}
    }

def run_one(row, refs, schemas, hb):
    seed, condition=row['seed'],row['condition']; folder=ROOT/f'seed_{seed}'/condition; folder.mkdir(parents=True,exist_ok=True)
    old=folder/'receipt.json'
    if old.exists():
        previous=json.loads(old.read_text())
        if previous.get('status')=='completed':
            for out in previous.get('outputs',[]):
                p=Path(out['path'])
                if not p.is_file() or sha(p)!=out['sha256']: raise RuntimeError(f'completed output missing/hash mismatch; refusing resubmit: {p}')
            return True
        raise RuntimeError(f'existing {previous.get("status")} receipt requires explicit recovery review; refusing duplicate submit: {old}')
    q=api('GET','/queue').json()
    if q.get('queue_running') or q.get('queue_pending'): raise RuntimeError(f'shared queue not empty: {q}')
    stats=api('GET','/system_stats').json(); dev=stats['devices'][0]; free=dev.get('vram_free',0)
    if free<MIN_FREE_BYTES: raise RuntimeError(f'VRAM below recorded successful floor: free={free}, floor={MIN_FREE_BYTES}; no prompt submitted')
    wf=graph(seed,condition,refs['appearance']['uploaded']['name'],refs['depth']['uploaded']['name'])
    for n in wf.values():
        if n['class_type'] not in schemas: raise RuntimeError('node schema missing: '+n['class_type'])
    save(folder/'workflow.json',wf)
    (folder/'prompt.txt').write_text(PLAN['prompts'][condition]+'\n')
    save(folder/'request.json',{'seed':seed,'condition':condition,'prompt':PLAN['prompts'][condition],**PLAN['fixed'],'appearance_reference':refs['appearance'],'front_depth':refs['depth'],'graph_contract':PLAN['graph_contract'],'queue_preflight':q,'system_stats_preflight':stats,'lease_id':LEASE_ID})
    receipt={'status':'ready_to_submit','seed':seed,'condition':condition,'lease_id':LEASE_ID,'queue_preflight':q,'vram_free_preflight':free}
    save(folder/'receipt.json',receipt)
    client_id=str(uuid.uuid4())
    try:
        res=requests.post(BASE+'/prompt',json={'prompt':wf,'client_id':client_id},timeout=90)
        res.raise_for_status(); sub=res.json(); pid=sub['prompt_id']
    except requests.RequestException as e:
        receipt.update({'status':'unresolved','error':str(e),'client_id':client_id,'recovery':'Check shared queue and Comfy history; do not resubmit.'}); save(folder/'receipt.json',receipt); return False
    save(folder/'submission.json',sub); receipt.update({'status':'running','prompt_id':pid,'client_id':client_id}); save(folder/'receipt.json',receipt)
    deadline=time.time()+3600
    while time.time()<deadline:
        if hb.error: raise RuntimeError('lease heartbeat failure: '+hb.error)
        hist=api('GET','/history/'+pid).json()
        if pid in hist and (hist[pid].get('status',{}).get('completed') or hist[pid].get('status',{}).get('status_str') in ('success','error')): break
        time.sleep(5)
    else:
        receipt.update({'status':'unresolved','recovery':'Continue polling this prompt history; do not resubmit; preserve lease and heartbeat.'}); save(folder/'receipt.json',receipt); return False
    item=hist[pid]; save(folder/'history.json',item)
    if not item.get('status',{}).get('completed'):
        receipt.update({'status':'failed','history_status':item.get('status')}); save(folder/'receipt.json',receipt); return True
    outputs=item.get('outputs',{}).get('14',{}).get('images',[])
    if not outputs: raise RuntimeError('terminal success with no SaveImage output')
    saved=[]
    for i,out in enumerate(outputs):
        qs=urllib.parse.urlencode({'filename':out['filename'],'subfolder':out.get('subfolder',''),'type':out.get('type','output')})
        data=api('GET','/view?'+qs).content; dest=folder/('output.png' if i==0 else f'output_{i+1:02d}.png'); dest.write_bytes(data)
        saved.append({'path':str(dest),'sha256':sha_bytes(data),'bytes':len(data),'comfy_output':out})
        temp=(COMFY/'output'/out.get('subfolder','')/out['filename']).resolve()
        if temp.is_relative_to((COMFY/'output').resolve()) and temp.is_file() and sha(temp)==sha_bytes(data): temp.unlink()
    receipt.update({'status':'completed','outputs':saved}); save(folder/'receipt.json',receipt)
    return True

def release_idle_cache_if_needed(artifact_root=ROOT):
    """After a terminal image only, free this task's idle Comfy cache if needed.

    This uses the user's explicit cache-release authorization. POST is never retried;
    after a request error only read-only state checks are performed.
    """
    stats=api('GET','/system_stats').json(); free=stats['devices'][0].get('vram_free',0)
    if free>=MIN_FREE_BYTES: return
    q=api('GET','/queue').json()
    if q.get('queue_running') or q.get('queue_pending'): raise RuntimeError('refusing idle cache release while shared ComfyUI queue is nonempty')
    occ=json.loads(subprocess.check_output(['hive-resource','occupancy','--json'],text=True,timeout=30))
    if list(occ.get('leases',{})) != [LEASE_ID]: raise RuntimeError('refusing idle cache release because another GPU lease is active')
    path=Path(artifact_root)/'cache_lifecycle.json'
    record=json.loads(path.read_text()) if path.exists() else {'events':[]}
    event={'action':'POST /free','requested_by':'explicit user authorization to release unused ComfyUI cache','reason':'terminal image left free VRAM below this experiment conservative guard','queue_before':q,'occupancy_before':occ,'stats_before':stats,'post_attempted':True}
    record['events'].append(event); save(path,record)
    try:
        response=requests.post(BASE+'/free',json={'unload_models':True,'free_memory':True},timeout=60)
        event['http_status']=response.status_code
        try: event['response']=response.json()
        except Exception: event['response_text']=response.text[:1000]
    except requests.RequestException as exc:
        event['post_error']=str(exc)
    time.sleep(2)
    try:
        event['queue_after']=api('GET','/queue').json()
        event['stats_after']=api('GET','/system_stats').json()
    except requests.RequestException as exc:
        event['read_after_error']=str(exc)
    save(path,record)
    if event.get('post_error') or event.get('http_status')!=200: raise RuntimeError('cache-release POST uncertain/failed; POST was not retried; inspect cache_lifecycle.json')
    if event.get('queue_after',{}).get('queue_running') or event.get('queue_after',{}).get('queue_pending'): raise RuntimeError('unexpected queue activity after idle cache release')
    after=event.get('stats_after',{}).get('devices',[{}])[0].get('vram_free',0)
    if after<MIN_FREE_BYTES: raise RuntimeError(f'VRAM remains below conservative guard after authorized cache release: {after}')

def main():
    lease('lease','heartbeat',LEASE_ID,'--ttl','600000')
    refs_paths={k:Path(v['path']) for k,v in PLAN['inputs'].items()}
    for k,p in refs_paths.items():
        if not p.is_file() or sha(p)!=PLAN['inputs'][k]['sha256']: raise RuntimeError(f'input hash mismatch: {p}')
    q=api('GET','/queue').json()
    if q.get('queue_running') or q.get('queue_pending'): raise RuntimeError(f'shared queue not empty: {q}')
    kinds=['UNETLoader','CLIPLoader','VAELoader','ModelPatchLoader','LoadImage','TextEncodeQwenImageEditPlus','QwenImageDiffsynthControlnet','QwenImage21Cache','EmptySD3LatentImage','ConditioningZeroOut','KSampler','VAEDecode','SaveImage']
    schemas={}
    for kind in kinds:
        obj=api('GET','/object_info/'+kind).json()
        if kind not in obj: raise RuntimeError('missing node: '+kind)
        schemas[kind]=obj[kind]
    model_checks=[('UNETLoader','unet_name',PLAN['fixed']['base_model']),('CLIPLoader','clip_name',PLAN['fixed']['text_encoder']),('VAELoader','vae_name',PLAN['fixed']['vae']),('ModelPatchLoader','name',PLAN['fixed']['depth_control_patch'])]
    for kind,key,value in model_checks:
        options=schemas[kind]['input']['required'][key][0]
        if value not in options: raise RuntimeError(f'model not listed by live schema: {value}')
    stats=api('GET','/system_stats').json()
    free=stats['devices'][0].get('vram_free',0)
    if free<MIN_FREE_BYTES: raise RuntimeError(f'VRAM below recorded successful floor: free={free}, floor={MIN_FREE_BYTES}; no input upload or prompt submitted')
    token=uuid.uuid4().hex[:12]
    uploaded={k:upload(p,token,k) for k,p in refs_paths.items()}
    refs={'appearance':uploaded['appearance_reference'],'depth':uploaded['front_depth']}
    # Task-local immutable input copies, for a self-contained experiment folder.
    (ROOT/'inputs').mkdir(exist_ok=True)
    for k,p in refs_paths.items():
        dst=ROOT/'inputs'/('appearance_reference.png' if k=='appearance_reference' else 'front_depth.png')
        if not dst.exists(): dst.write_bytes(p.read_bytes())
        if sha(dst)!=sha(p): raise RuntimeError('task-local copy hash mismatch')
    save(ROOT/'preflight.json',{'queue':q,'system_stats':stats,'node_schemas':schemas,'uploaded_inputs':refs,'lease_id':LEASE_ID,'minimum_vram_free_bytes':MIN_FREE_BYTES})
    hb=Heartbeat(); hb.start(); completed_all=False; terminal_all=False
    try:
        for row in PLAN['matrix']:
            if not run_one(row,refs,schemas,hb):
                # Keep renewing the lease while an accepted prompt is unresolved.
                # The operator must inspect receipt/history and stop this process only
                # after confirming terminal state; no later matrix item is submitted.
                receipt_path=ROOT/f"seed_{row['seed']}"/row['condition']/'receipt.json'
                print(f'UNRESOLVED {receipt_path}; retaining lease heartbeat; do not resubmit',flush=True)
                while True: time.sleep(60)
            receipt_path=ROOT/f"seed_{row['seed']}"/row['condition']/'receipt.json'
            receipt=json.loads(receipt_path.read_text())
            if receipt.get('status')!='completed': raise RuntimeError(f'terminal image did not complete successfully: {receipt_path}')
            release_idle_cache_if_needed()
        completed_all=True
        terminal_all=True
    finally:
        if not (not completed_all and any(json.loads(p.read_text()).get('status')=='unresolved' for p in ROOT.glob('seed_*/**/receipt.json'))):
            hb.stop()
        if terminal_all:
            removed=[]
            for ref in refs.values():
                info=ref['uploaded']; p=(COMFY/'input'/info.get('subfolder','')/info['name']).resolve()
                if p.is_relative_to((COMFY/'input').resolve()) and p.is_file() and sha(p)==ref['sha256']: p.unlink(); removed.append(str(p))
            save(ROOT/'temporary_inputs_removed.json',{'exact_files':removed})
            save(ROOT/'postrun_queue.json',api('GET','/queue').json())
            lease('lease','release',LEASE_ID)
            save(ROOT/'lease_released.json',{'lease_id':LEASE_ID,'released':True})

if __name__=='__main__': main()
