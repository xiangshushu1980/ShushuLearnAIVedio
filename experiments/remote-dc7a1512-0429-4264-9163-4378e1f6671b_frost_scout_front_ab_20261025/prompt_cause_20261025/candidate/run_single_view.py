#!/usr/bin/env python3
"""Task-local single-view reference + depth runner candidate.

Usage: HIVE_LEASE_ID=<acquired-id> python run_single_view.py request.json
The caller owns task/resource preflight. The supplied active lease must belong
to this conversation and include gpu:0. An uncertain POST is never retried.
"""
import copy, json, os, subprocess, sys, time, urllib.parse, uuid
from pathlib import Path
import requests

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent))
import run_prompt_cause as common

PHRASES={'front':'strict straight-on frontal','left_profile':'strict left-facing side profile'}
TEMPLATE=json.loads((HERE/'api_graph.template.json').read_text())
COMFY=common.COMFY; BASE=common.BASE; LEASE=common.LEASE_ID
MAX_SEED=18446744073709551615
ALLOWED={'appearance_path','depth_path','view','seed','output_dir'}

def save(p,obj): common.save(p,obj)

def validate_request(req):
    if not isinstance(req,dict): raise ValueError('request must be a JSON object')
    unknown=set(req)-ALLOWED
    missing=ALLOWED-set(req)
    if unknown or missing: raise ValueError(f'unknown keys={sorted(unknown)} missing keys={sorted(missing)}')
    if req['view'] not in PHRASES: raise ValueError('runner supports front and left_profile only; back is unvalidated')
    if type(req['seed']) is not int or not 0<=req['seed']<=MAX_SEED: raise ValueError('seed must be an integer in [0, 2^64-1]; booleans/strings are rejected')
    for key in ('appearance_path','depth_path','output_dir'):
        if not isinstance(req[key],str) or not Path(req[key]).is_absolute(): raise ValueError(f'{key} must be an absolute path string')
    app=Path(req['appearance_path']); depth=Path(req['depth_path']); outdir=Path(req['output_dir'])
    for p in (app,depth):
        if not p.is_file(): raise FileNotFoundError(p)
    return app,depth,outdir

def verify_owned_lease():
    occ=json.loads(subprocess.check_output(['hive-resource','occupancy','--json'],text=True,timeout=30))
    item=occ.get('leases',{}).get(LEASE)
    if not item: raise RuntimeError('supplied GPU lease is not active')
    meta=item.get('metadata',{})
    contexts={name:os.environ[name] for name in ('CODEX_THREAD_ID','HIVE_CONVERSATION_ID','PI_SESSION_ID') if os.environ.get(name)}
    if not contexts: raise RuntimeError('no host conversation identity env is set (CODEX_THREAD_ID, HIVE_CONVERSATION_ID, PI_SESSION_ID)')
    if len(set(contexts.values()))!=1: raise RuntimeError(f'host conversation identity env values disagree: {contexts}')
    expected=next(iter(contexts.values()))
    actuals={meta[name] for name in ('conversationId','threadId') if meta.get(name)}
    if len(actuals)!=1 or expected not in actuals: raise RuntimeError(f'lease conversation metadata mismatch: host={contexts}, lease={meta}')
    if 'gpu:0' not in item.get('resources',[]): raise RuntimeError('supplied lease does not include gpu:0')
    return occ

def live_schemas():
    names=['UNETLoader','CLIPLoader','VAELoader','ModelPatchLoader','LoadImage','TextEncodeQwenImageEditPlus','QwenImageDiffsynthControlnet','QwenImage21Cache','EmptySD3LatentImage','ConditioningZeroOut','KSampler','VAEDecode','SaveImage']
    result={}
    for name in names:
        data=common.api('GET','/object_info/'+name).json()
        if name not in data: raise RuntimeError('missing live node schema: '+name)
        result[name]=data[name]
    choices=[('UNETLoader','unet_name','qwen_image_2.1_bf16.safetensors'),('CLIPLoader','clip_name','qwen3vl_8b_int8_convrot.safetensors'),('VAELoader','vae_name','qwen_image_2.1_vae_bf16.safetensors'),('ModelPatchLoader','name','qwen_image_2.1_fun_controlnet_union_bf16.safetensors')]
    for node,key,value in choices:
        if value not in result[node]['input']['required'][key][0]: raise RuntimeError('model absent from live choices: '+value)
    return result

def wait_for_empty_queue(hb,receipt,path,receipt_path):
    while True:
        try:
            q=common.api('GET','/queue').json()
            save(path,q)
            if not q.get('queue_running') and not q.get('queue_pending'): return q
            receipt['terminal_waiting_for_queue']=q
        except requests.RequestException as exc:
            receipt['terminal_queue_poll_error']=str(exc)
        if hb.error: receipt['lease_heartbeat_error']=hb.error
        else: receipt.pop('lease_heartbeat_error',None)
        save(receipt_path,receipt)
        time.sleep(10)

def main():
    if len(sys.argv)!=2: raise SystemExit('usage: run_single_view.py request.json')
    request_path=Path(sys.argv[1]).resolve(); req=json.loads(request_path.read_text())
    app,depth,outdir=validate_request(req); outdir.mkdir(parents=True,exist_ok=True)
    app_sha=common.sha(app); depth_sha=common.sha(depth)
    raw=(HERE/'generic_prompt.txt').read_text().strip()
    prompt=raw.replace('{view_phrase}',PHRASES[req['view']])
    receipt_path=outdir/'receipt.json'
    if receipt_path.exists():
        old=json.loads(receipt_path.read_text())
        if old.get('status')=='completed' and old.get('outputs'):
            frozen_path=outdir/'request_frozen.json'
            if not frozen_path.is_file(): raise RuntimeError('completed receipt lacks frozen request; refusing reuse')
            frozen=json.loads(frozen_path.read_text())
            saved_inputs=frozen.get('inputs',{})
            if frozen.get('request')!=req: raise RuntimeError('request differs from completed frozen request; use a new output_dir')
            if saved_inputs.get('appearance',{}).get('sha256')!=app_sha or saved_inputs.get('depth',{}).get('sha256')!=depth_sha: raise RuntimeError('input hashes differ from completed request; use a new output_dir')
            if frozen.get('prompt')!=prompt: raise RuntimeError('rendered prompt differs from completed request; use a new output_dir')
            for x in old['outputs']:
                p=Path(x['path'])
                if not p.is_file() or common.sha(p)!=x['sha256']: raise RuntimeError('completed output hash mismatch; refusing duplicate')
            print('already completed; verified outputs. Caller retains responsibility for any newly acquired lease.')
            return
        raise RuntimeError('existing non-success receipt requires manual reconciliation; refusing duplicate')

    occupancy=verify_owned_lease()
    common.lease('lease','heartbeat',LEASE,'--ttl','600000')
    queue=common.api('GET','/queue').json()
    if queue.get('queue_running') or queue.get('queue_pending'): raise RuntimeError('shared queue must be empty')
    stats=common.api('GET','/system_stats').json(); free=stats['devices'][0].get('vram_free',0)
    if free<common.MIN_FREE_BYTES: raise RuntimeError('free VRAM is below conservative experiment guard')
    schemas=live_schemas()
    for src,label,digest in ((app,'appearance',app_sha),(depth,'depth',depth_sha)):
        dest=outdir/f'input_{label}{src.suffix.lower()}'
        if not dest.exists(): dest.write_bytes(src.read_bytes())
        if common.sha(dest)!=digest: raise RuntimeError('task-local input copy hash mismatch')
    refs={'appearance':common.upload(app,uuid.uuid4().hex[:12],'appearance'),'depth':common.upload(depth,uuid.uuid4().hex[:12],'depth')}
    graph=copy.deepcopy(TEMPLATE)
    graph['5']['inputs']['image']=refs['depth']['uploaded']['name']; graph['6']['inputs']['image']=refs['appearance']['uploaded']['name']
    graph['7']['inputs']['prompt']=prompt; graph['12']['inputs']['seed']=req['seed']
    graph['14']['inputs']['filename_prefix']=f"generic_candidate_{req['view']}_{req['seed']}"
    for n in graph.values():
        if n['class_type'] not in schemas: raise RuntimeError('live schema missing graph node '+n['class_type'])
    save(outdir/'node_schemas.json',schemas)
    frozen={'request':req,'prompt':prompt,'inputs':{'appearance':{'path':str(app),'sha256':app_sha,'upload':refs['appearance']},'depth':{'path':str(depth),'sha256':depth_sha,'upload':refs['depth']}},'queue_preflight':queue,'system_stats_preflight':stats,'occupancy_preflight':occupancy,'lease_id':LEASE,'runner_sha256':common.sha(Path(__file__)),'helper_sha256':common.sha(Path(common.__file__)),'api_graph_template_sha256':common.sha(HERE/'api_graph.template.json'),'prompt_template_sha256':common.sha(HERE/'generic_prompt.txt')}
    save(outdir/'request_frozen.json',frozen); save(outdir/'workflow.json',graph); (outdir/'prompt.txt').write_text(prompt+'\n')
    receipt={'status':'ready_to_submit','lease_id':LEASE,'queue_preflight':queue,'free_vram_bytes':free}; save(receipt_path,receipt)
    hb=common.Heartbeat(); hb.start(); client=uuid.uuid4().hex
    try:
        response=requests.post(BASE+'/prompt',json={'prompt':graph,'client_id':client},timeout=90)
        response.raise_for_status(); submission=response.json()
    except requests.RequestException as exc:
        receipt.update({'status':'unresolved','client_id':client,'error':str(exc),'recovery':'POST is ambiguous. Heartbeat is retained. Reconcile queue/history read-only; never resubmit.'}); save(receipt_path,receipt)
        while True:
            if hb.error: receipt['lease_heartbeat_error']=hb.error
            save(receipt_path,receipt); time.sleep(30)
    pid=submission['prompt_id']; save(outdir/'submission.json',submission)
    receipt.update({'status':'running','client_id':client,'prompt_id':pid}); save(receipt_path,receipt)
    while True:
        if hb.error: receipt['lease_heartbeat_error']=hb.error
        else: receipt.pop('lease_heartbeat_error',None)
        try: history_map=common.api('GET','/history/'+pid).json()
        except requests.RequestException as exc:
            receipt['history_poll_error']=str(exc); save(receipt_path,receipt); time.sleep(10); continue
        if pid in history_map:
            status=history_map[pid].get('status',{})
            if status.get('completed') or status.get('status_str') in ('success','error'): break
        save(receipt_path,receipt); time.sleep(5)
    history=history_map[pid]; save(outdir/'history.json',history)
    if not status.get('completed'):
        receipt.update({'status':'failed','history_status':status}); save(receipt_path,receipt)
    else:
        try:
            images=history.get('outputs',{}).get('14',{}).get('images',[])
            if not images: raise RuntimeError('completed history has no SaveImage output')
            outputs=[]
            for i,img in enumerate(images):
                query=urllib.parse.urlencode({'filename':img['filename'],'subfolder':img.get('subfolder',''),'type':img.get('type','output')})
                data=common.api('GET','/view?'+query).content; dest=outdir/('output.png' if i==0 else f'output_{i+1:02d}.png'); dest.write_bytes(data)
                digest=common.sha_bytes(data); outputs.append({'path':str(dest),'sha256':digest,'comfy_output':img})
                temp=(COMFY/'output'/img.get('subfolder','')/img['filename']).resolve()
                if temp.is_relative_to((COMFY/'output').resolve()) and temp.is_file() and common.sha(temp)==digest: temp.unlink()
            receipt.update({'status':'completed','outputs':outputs})
        except Exception as exc:
            receipt.update({'status':'terminal_output_collection_error','error':str(exc),'recovery':'Comfy prompt is terminal; preserve prompt_id/history and collect output manually.'})
        save(receipt_path,receipt)
    # Prompt has a terminal history state. Keep renewing while any shared queue
    # activity remains; release only after the queue is empty.
    wait_for_empty_queue(hb,receipt,outdir/'postrun_queue.json',receipt_path)
    hb.stop()
    removed=[]
    if 'refs' in locals():
        for label,ref,digest in [('appearance',refs['appearance'],app_sha),('depth',refs['depth'],depth_sha)]:
            info=ref['uploaded']; temp=(COMFY/'input'/info.get('subfolder','')/info['name']).resolve()
            if temp.is_relative_to((COMFY/'input').resolve()) and temp.is_file() and common.sha(temp)==digest: temp.unlink(); removed.append(str(temp))
    save(outdir/'temporary_inputs_removed.json',{'exact_files':removed})
    common.lease('lease','release',LEASE)
    save(outdir/'lease_released.json',{'lease_id':LEASE,'released':True,'prompt_terminal':True})
    if receipt.get('status')!='completed': raise SystemExit(f"runner exited with terminal status {receipt.get('status')}; inspect {receipt_path}")

if __name__=='__main__': main()
