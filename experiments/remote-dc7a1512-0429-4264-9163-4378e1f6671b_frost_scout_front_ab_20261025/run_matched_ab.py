#!/usr/bin/env python3
import hashlib, json, mimetypes, os, subprocess, threading, time, urllib.parse, uuid
from pathlib import Path
import requests

ROOT = Path(__file__).resolve().parent
PLAN = json.loads((ROOT / 'plan.json').read_text())
BASE = 'http://127.0.0.1:8188'
COMFY = Path('/home/sean/projects/ComfyUI')
LEASE = os.environ['HIVE_LEASE_ID']
APPEARANCE = Path(PLAN['inputs']['appearance_reference']['path'])
DEPTH = Path(PLAN['inputs']['front_depth']['path'])
PROMPT = PLAN['prompt']


def sha_bytes(data): return hashlib.sha256(data).hexdigest()
def sha(path): return sha_bytes(path.read_bytes())
def save(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')
def api(method, route, **kwargs):
    r = requests.request(method, BASE + route, timeout=kwargs.pop('timeout', 60), **kwargs)
    r.raise_for_status()
    return r

def lease(*args):
    return subprocess.run(['hive-resource', *args], check=True, capture_output=True, text=True, timeout=30)

class Heartbeat:
    def __init__(self):
        self.stop_flag = threading.Event(); self.error = None
        self.thread = threading.Thread(target=self.loop, daemon=True)
    def loop(self):
        while not self.stop_flag.wait(150):
            try: lease('lease', 'heartbeat', LEASE, '--ttl', '600000')
            except Exception as e: self.error = str(e); return
    def start(self): self.thread.start()
    def stop(self): self.stop_flag.set(); self.thread.join(timeout=3)


def upload(path, token, label):
    name = f'codex_{token}_{label}{path.suffix.lower()}'
    mime = mimetypes.guess_type(name)[0] or 'application/octet-stream'
    with path.open('rb') as f:
        r = requests.post(BASE + '/upload/image', files={'image': (name, f, mime)}, data={'type':'input','overwrite':'true'}, timeout=90)
    r.raise_for_status(); info = r.json()
    params = urllib.parse.urlencode({'filename': info['name'], 'subfolder': info.get('subfolder',''), 'type':'input'})
    remote = api('GET', '/view?' + params).content
    if sha_bytes(remote) != sha(path): raise RuntimeError(f'Upload hash mismatch: {path}')
    return {'local_path': str(path), 'sha256': sha(path), 'uploaded': info}


def graph(seed, appearance_name, depth_name=None):
    nodes = {
      '1': {'class_type':'UNETLoader','inputs':{'unet_name':'qwen_image_2.1_bf16.safetensors','weight_dtype':'default'}},
      '2': {'class_type':'CLIPLoader','inputs':{'clip_name':'qwen3vl_8b_int8_convrot.safetensors','type':'qwen_image','device':'default'}},
      '3': {'class_type':'VAELoader','inputs':{'vae_name':'qwen_image_2.1_vae_bf16.safetensors'}},
      '6': {'class_type':'LoadImage','inputs':{'image':appearance_name}},
      '7': {'class_type':'TextEncodeQwenImageEditPlus','inputs':{'clip':['2',0],'prompt':PROMPT,'vae':['3',0],'image1':['6',0]}},
      '9': {'class_type':'QwenImage21Cache','inputs':{'model':['1',0] if depth_name is None else ['8',0],'device':'auto','dtype':'default'}},
      '10': {'class_type':'EmptySD3LatentImage','inputs':{'width':PLAN['fixed']['width'],'height':PLAN['fixed']['height'],'batch_size':1}},
      '11': {'class_type':'ConditioningZeroOut','inputs':{'conditioning':['7',0]}},
      '12': {'class_type':'KSampler','inputs':{'model':['9',0],'positive':['7',0],'negative':['11',0],'latent_image':['10',0],'seed':seed,'steps':PLAN['fixed']['steps'],'cfg':PLAN['fixed']['cfg'],'sampler_name':PLAN['fixed']['sampler'],'scheduler':PLAN['fixed']['scheduler'],'denoise':1.0}},
      '13': {'class_type':'VAEDecode','inputs':{'samples':['12',0],'vae':['3',0]}},
      '14': {'class_type':'SaveImage','inputs':{'images':['13',0],'filename_prefix':f'remote_dc7a1512_frost_front_{seed}_' + ('depth' if depth_name else 'appearance')}},
    }
    if depth_name is not None:
      nodes.update({
        '4': {'class_type':'ModelPatchLoader','inputs':{'name':'qwen_image_2.1_fun_controlnet_union_bf16.safetensors'}},
        '5': {'class_type':'LoadImage','inputs':{'image':depth_name}},
        '8': {'class_type':'QwenImageDiffsynthControlnet','inputs':{'model':['1',0],'model_patch':['4',0],'vae':['3',0],'image':['5',0],'strength':PLAN['fixed']['depth_strength'],'start_percent':PLAN['fixed']['depth_start_percent'],'end_percent':PLAN['fixed']['depth_end_percent']}},
      })
    return nodes


def run_one(seed, mode, refs, schemas):
    is_depth = mode == 'depth-guided'
    folder = ROOT / f'seed_{seed}' / mode
    folder.mkdir(parents=True, exist_ok=True)
    queue = api('GET','/queue').json()
    if queue.get('queue_running') or queue.get('queue_pending'):
        raise RuntimeError(f'ComfyUI shared queue not empty: {queue}')
    image_name = refs['appearance']['uploaded']['name']
    depth_name = refs['depth']['uploaded']['name'] if is_depth else None
    workflow = graph(seed, image_name, depth_name)
    for node_id, node in workflow.items():
        if node['class_type'] not in schemas: raise RuntimeError('Missing schema ' + node['class_type'])
    save(folder/'workflow.json', workflow)
    save(folder/'request.json', {
      'seed':seed,'mode':mode,'prompt':PROMPT,'width':PLAN['fixed']['width'],'height':PLAN['fixed']['height'],
      'steps':PLAN['fixed']['steps'],'cfg':PLAN['fixed']['cfg'],'sampler':PLAN['fixed']['sampler'],'scheduler':PLAN['fixed']['scheduler'],
      'depth_strength': PLAN['fixed']['depth_strength'] if is_depth else None,
      'references': {'appearance': refs['appearance'], 'depth': refs['depth'] if is_depth else None},
      'graph_contract': {
        'TextEncodeQwenImageEditPlus.image1':'appearance reference only',
        'TextEncodeQwenImageEditPlus.image2':'disconnected',
        'QwenImageDiffsynthControlnet.image':'depth map only' if is_depth else 'no ControlNet node in graph'
      }
    })
    client_id = str(uuid.uuid4())
    receipt = {'status':'ready_to_submit','endpoint':BASE,'client_id':client_id,'lease_id':LEASE,'seed':seed,'mode':mode,'queue_preflight':queue}
    save(folder/'receipt.json', receipt)
    payload = {'prompt':workflow,'client_id':client_id}
    submitted = False
    try:
        res = requests.post(BASE+'/prompt', json=payload, timeout=90)
        submitted = True
        res.raise_for_status(); sub = res.json(); pid = sub['prompt_id']
        save(folder/'submission.json', sub)
        receipt.update({'status':'running','prompt_id':pid}); save(folder/'receipt.json',receipt)
        deadline = time.time()+3600
        while time.time()<deadline:
            if hb.error: raise RuntimeError('GPU lease heartbeat failed: '+hb.error)
            hist = api('GET','/history/'+pid).json()
            if pid in hist:
                item=hist[pid]; st=item.get('status',{})
                if st.get('completed') or st.get('status_str') in {'success','error'}:
                    break
            time.sleep(5)
        else:
            receipt.update({'status':'unresolved','recovery':'Continue polling this prompt history; do not resubmit. Keep lease alive.'})
            save(folder/'receipt.json',receipt)
            return False
        save(folder/'history.json',item)
        if not st.get('completed'):
            receipt.update({'status':'failed','history_status':st}); save(folder/'receipt.json',receipt)
            return True
        outputs=item.get('outputs',{}).get('14',{}).get('images',[])
        if not outputs: raise RuntimeError('Completed without SaveImage output')
        saved=[]
        for i,out in enumerate(outputs):
            q=urllib.parse.urlencode({'filename':out['filename'],'subfolder':out.get('subfolder',''),'type':out.get('type','output')})
            data=api('GET','/view?'+q).content
            dest=folder/('output.png' if i==0 else f'output_{i+1:02d}.png')
            dest.write_bytes(data)
            saved.append({'path':str(dest),'sha256':sha_bytes(data),'bytes':len(data),'comfy_output':out})
        receipt.update({'status':'completed','outputs':saved}); save(folder/'receipt.json',receipt)
        cleanup=[]
        for out in outputs:
            p=(COMFY/'output'/out.get('subfolder','')/out['filename']).resolve()
            if p.is_relative_to((COMFY/'output').resolve()) and p.is_file():
                record=next((x for x in saved if x['comfy_output']==out),None)
                if record and sha(p)==record['sha256']: p.unlink(); cleanup.append(str(p))
        save(folder/'temporary_files_removed.json',{'output_files':cleanup})
        return True
    except requests.Timeout as e:
        receipt.update({'status':'unresolved','error':str(e),'recovery':'Check queue/history by client_id and do not resubmit.'})
        save(folder/'receipt.json',receipt)
        return False


ROOT.mkdir(parents=True,exist_ok=True)
for label,path in [('appearance',APPEARANCE),('depth',DEPTH)]:
    expected=PLAN['inputs']['appearance_reference' if label=='appearance' else 'front_depth']['sha256']
    if not path.is_file() or sha(path)!=expected: raise RuntimeError(f'Input hash mismatch: {path}')
# Keep task-local copies so the archived run remains self-contained; originals are read only.
inputs=ROOT/'inputs'; inputs.mkdir(exist_ok=True)
for src,name in [(APPEARANCE,'appearance_reference.png'),(DEPTH,'front_depth.png')]:
    dest=inputs/name
    if not dest.exists(): dest.write_bytes(src.read_bytes())
    if sha(dest)!=sha(src): raise RuntimeError('Task-local input copy hash mismatch')
lease('lease','heartbeat',LEASE,'--ttl','600000')
queue=api('GET','/queue').json()
if queue.get('queue_running') or queue.get('queue_pending'): raise RuntimeError(f'ComfyUI shared queue not empty: {queue}')
kinds=['UNETLoader','CLIPLoader','VAELoader','ModelPatchLoader','LoadImage','TextEncodeQwenImageEditPlus','QwenImageDiffsynthControlnet','QwenImage21Cache','EmptySD3LatentImage','ConditioningZeroOut','KSampler','VAEDecode','SaveImage']
schemas={}
for kind in kinds:
    d=api('GET','/object_info/'+kind).json()
    if kind not in d: raise RuntimeError('Node unavailable: '+kind)
    schemas[kind]=d[kind]
for kind,key,value in [('UNETLoader','unet_name','qwen_image_2.1_bf16.safetensors'),('CLIPLoader','clip_name','qwen3vl_8b_int8_convrot.safetensors'),('VAELoader','vae_name','qwen_image_2.1_vae_bf16.safetensors'),('ModelPatchLoader','name','qwen_image_2.1_fun_controlnet_union_bf16.safetensors')]:
    if value not in schemas[kind]['input']['required'][key][0]: raise RuntimeError(f'Model not listed: {value}')
refs={}
token=uuid.uuid4().hex[:12]
refs['appearance']=upload(APPEARANCE,token,'appearance')
refs['depth']=upload(DEPTH,token,'depth')
save(ROOT/'preflight.json',{'queue':queue,'system_stats':api('GET','/system_stats').json(),'node_schemas':schemas,'inputs':refs,'lease_id':LEASE})
hb=Heartbeat(); hb.start(); success_terminal=False
try:
    for seed in PLAN['seeds']:
        for mode in ['appearance-only','depth-guided']:
            terminal=run_one(seed,mode,refs,schemas)
            if not terminal:
                print(f'UNRESOLVED seed={seed} mode={mode}; lease retained',flush=True)
                raise SystemExit(2)
    success_terminal=True
finally:
    hb.stop()
    if success_terminal:
        cleanup=[]
        for label in ['appearance','depth']:
            info=refs[label]['uploaded']; name=info['name']; sub=info.get('subfolder','')
            p=(COMFY/'input'/sub/name).resolve()
            expected=refs[label]['sha256']
            if p.is_relative_to((COMFY/'input').resolve()) and p.is_file() and sha(p)==expected:
                p.unlink(); cleanup.append(str(p))
        save(ROOT/'temporary_inputs_removed.json',{'exact_files':cleanup})
        after=api('GET','/queue').json()
        save(ROOT/'postrun_queue.json',after)
        lease('lease','release',LEASE)
        save(ROOT/'lease_released.json',{'lease_id':LEASE,'released':True})
        print('COMPLETED all matched runs; queue='+json.dumps(after),flush=True)
