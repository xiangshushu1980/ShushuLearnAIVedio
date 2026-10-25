#!/usr/bin/env python3
"""Thin, resumable-by-inspection executor for generic_validation/plan.json.

Uses the reviewed API/upload/lease/cache helpers in ../run_prompt_cause.py.
Requires HIVE_LEASE_ID; this candidate must not run before the plan submit gate passes.
"""
import copy, json, os, sys, time, urllib.parse
from pathlib import Path
import requests

ROOT=Path(__file__).resolve().parent
PLAN=json.loads((ROOT/'plan.json').read_text())
HELPER_DIR=ROOT.parent
sys.path.insert(0,str(HELPER_DIR))
import run_prompt_cause as common

BASE=common.BASE
LEASE_ID=common.LEASE_ID
COMFY=common.COMFY
TEMPLATE=json.loads((ROOT.parent/'candidate/api_graph.template.json').read_text())

def schema_snapshot():
    kinds=['UNETLoader','CLIPLoader','VAELoader','ModelPatchLoader','LoadImage','TextEncodeQwenImageEditPlus','QwenImageDiffsynthControlnet','QwenImage21Cache','EmptySD3LatentImage','ConditioningZeroOut','KSampler','VAEDecode','SaveImage']
    schemas={}
    for k in kinds:
        d=common.api('GET','/object_info/'+k).json()
        if k not in d: raise RuntimeError('missing live node schema: '+k)
        schemas[k]=d[k]
    fixed=PLAN['fixed']
    for node,key,val in [('UNETLoader','unet_name',fixed['base_model']),('CLIPLoader','clip_name',fixed['text_encoder']),('VAELoader','vae_name',fixed['vae']),('ModelPatchLoader','name',fixed['depth_control_patch'])]:
        if val not in schemas[node]['input']['required'][key][0]: raise RuntimeError('model absent from live schema choices: '+val)
    return schemas

def prompt_for(row):
    return PLAN['prompts'][row['prompt_key']]

def workflow_for(row,refs):
    g=copy.deepcopy(TEMPLATE)
    g['5']['inputs']['image']=refs['side_depth']['uploaded']['name'] if row['view']=='left_profile' and row['use_depth'] else ''
    g['6']['inputs']['image']=refs['appearance']['uploaded']['name']
    g['7']['inputs']['prompt']=prompt_for(row)
    g['12']['inputs']['seed']=row['seed']
    g['14']['inputs']['filename_prefix']=f"remote_dc7a1512_generic_{row['view']}_{row['seed']}_{row['condition']}"
    if row['use_depth']:
        g['8']['inputs']['strength']=row['depth_strength']
        g['8']['inputs']['start_percent']=row['depth_start_percent']
        g['8']['inputs']['end_percent']=row['depth_end_percent']
    else:
        # Appearance-only means the entire ControlNet branch is absent.
        del g['4']; del g['5']; del g['8']
        g['9']['inputs']['model']=['1',0]
    return g

def matrix_gate():
    root=ROOT.parent
    plan=json.loads((root/'plan.json').read_text())
    for row in plan['matrix']:
        p=root/f"seed_{row['seed']}"/row['condition']/'receipt.json'
        if not p.is_file(): raise RuntimeError(f'prompt-cause matrix incomplete; missing {p}')
        d=json.loads(p.read_text())
        if d.get('status')!='completed': raise RuntimeError(f'prompt-cause matrix not terminal-successful: {p}')
        for out in d.get('outputs',[]):
            q=Path(out['path'])
            if not q.is_file() or common.sha(q)!=out['sha256']: raise RuntimeError(f'prompt-cause output hash mismatch: {q}')

def run_one(row,refs,schemas,hb):
    folder=ROOT/f"{row['view']}_seed_{row['seed']}"/row['condition']
    folder.mkdir(parents=True,exist_ok=True)
    existing=folder/'receipt.json'
    if existing.exists():
        d=json.loads(existing.read_text())
        if d.get('status')=='completed':
            outputs=d.get('outputs',[])
            if not outputs: raise RuntimeError(f'completed receipt has no outputs; refusing skip: {existing}')
            for x in outputs:
                p=Path(x['path'])
                if not p.is_file() or common.sha(p)!=x['sha256']: raise RuntimeError(f'completed output hash mismatch; refusing duplicate: {p}')
            return
        raise RuntimeError(f'non-completed receipt needs manual recovery; refusing resubmit: {existing}')
    q=common.api('GET','/queue').json()
    if q.get('queue_running') or q.get('queue_pending'): raise RuntimeError(f'shared queue not empty: {q}')
    stats=common.api('GET','/system_stats').json(); free=stats['devices'][0].get('vram_free',0)
    if free<common.MIN_FREE_BYTES: raise RuntimeError(f'free VRAM below conservative experiment guard before upload: {free}')
    g=workflow_for(row,refs)
    for n in g.values():
        if n['class_type'] not in schemas: raise RuntimeError('workflow class missing live schema: '+n['class_type'])
    prompt=prompt_for(row)
    (folder/'prompt.txt').write_text(prompt+'\n')
    common.save(folder/'workflow.json',g)
    common.save(folder/'request.json',{'view':row['view'],'seed':row['seed'],'condition':row['condition'],'use_depth':row['use_depth'],'prompt':prompt,'fixed':PLAN['fixed'],'references':refs,'depth_strength':row.get('depth_strength'),'queue_preflight':q,'system_stats_preflight':stats,'lease_id':LEASE_ID})
    receipt={'status':'ready_to_submit','view':row['view'],'seed':row['seed'],'condition':row['condition'],'lease_id':LEASE_ID,'queue_preflight':q,'vram_free_preflight':free}
    common.save(folder/'receipt.json',receipt)
    client_id=__import__('uuid').uuid4().hex
    try:
        response=requests.post(BASE+'/prompt',json={'prompt':g,'client_id':client_id},timeout=90)
        response.raise_for_status(); sub=response.json()
    except requests.RequestException as exc:
        receipt.update({'status':'unresolved','client_id':client_id,'error':str(exc),'recovery':'Check queue/history; do not resubmit.'}); common.save(folder/'receipt.json',receipt)
        # A POST timeout is ambiguous: retain the lease and never retry POST.
        # Continue renewing while waiting for explicit read-only reconciliation.
        while True:
            if hb.error:
                receipt['lease_heartbeat_error']=hb.error
                common.save(folder/'receipt.json',receipt)
            time.sleep(30)
    pid=sub['prompt_id']; common.save(folder/'submission.json',sub)
    receipt.update({'status':'running','client_id':client_id,'prompt_id':pid}); common.save(folder/'receipt.json',receipt)
    while True:
        if hb.error:
            receipt['lease_heartbeat_error']=hb.error
            common.save(folder/'receipt.json',receipt)
        else:
            receipt.pop('lease_heartbeat_error',None)
            common.save(folder/'receipt.json',receipt)
        try:
            hist=common.api('GET','/history/'+pid).json()
        except requests.RequestException as exc:
            receipt['history_poll_error']=str(exc)
            common.save(folder/'receipt.json',receipt)
            time.sleep(10)
            continue
        if pid in hist:
            item=hist[pid]; st=item.get('status',{})
            if st.get('completed') or st.get('status_str') in ('success','error'): break
        time.sleep(5)
    common.save(folder/'history.json',item)
    if not st.get('completed'):
        receipt.update({'status':'failed','history_status':st}); common.save(folder/'receipt.json',receipt)
        raise RuntimeError(f'terminal Comfy failure; stop and inspect {folder}')
    imgs=item.get('outputs',{}).get('14',{}).get('images',[])
    if not imgs: raise RuntimeError('terminal success without SaveImage output')
    saved=[]
    for i,img in enumerate(imgs):
        qs=urllib.parse.urlencode({'filename':img['filename'],'subfolder':img.get('subfolder',''),'type':img.get('type','output')})
        data=common.api('GET','/view?'+qs).content
        dst=folder/('output.png' if i==0 else f'output_{i+1:02d}.png'); dst.write_bytes(data)
        digest=common.sha_bytes(data); saved.append({'path':str(dst),'sha256':digest,'bytes':len(data),'comfy_output':img})
        tmp=(COMFY/'output'/img.get('subfolder','')/img['filename']).resolve()
        if tmp.is_relative_to((COMFY/'output').resolve()) and tmp.is_file() and common.sha(tmp)==digest: tmp.unlink()
    receipt.update({'status':'completed','outputs':saved}); common.save(folder/'receipt.json',receipt)

def main():
    matrix_gate()
    common.lease('lease','heartbeat',LEASE_ID,'--ttl','600000')
    q=common.api('GET','/queue').json()
    if q.get('queue_running') or q.get('queue_pending'): raise RuntimeError('shared queue must be empty at phase start')
    schemas=schema_snapshot()
    p=PLAN['inputs']; paths={k:Path(v['path']) for k,v in p.items()}
    for k,path in paths.items():
        if not path.is_file() or common.sha(path)!=p[k]['sha256']: raise RuntimeError(f'input missing/hash mismatch: {path}')
    up={'appearance':common.upload(paths['appearance_reference'],__import__('uuid').uuid4().hex[:12],'appearance')}
    up['side_depth']=common.upload(paths['side_depth'],__import__('uuid').uuid4().hex[:12],'side_depth')
    common.save(ROOT/'preflight.json',{'queue':q,'system_stats':common.api('GET','/system_stats').json(),'node_schemas':schemas,'uploads':up,'lease_id':LEASE_ID})
    hb=common.Heartbeat(); hb.start(); completed=False
    try:
        for row in PLAN['matrix']:
            if hb.error: raise RuntimeError('lease heartbeat is failing; stop before submitting next image: '+hb.error)
            run_one(row,up,schemas,hb)
            common.release_idle_cache_if_needed(artifact_root=ROOT)
        completed=True
    finally:
        # Terminal errors are releasable; only running/unresolved receipts or an
        # active shared queue keep this executor's lease and uploaded inputs alive.
        receipts=[json.loads(p.read_text()) for p in ROOT.glob('**/receipt.json')]
        unresolved=any(r.get('status') in ('running','unresolved') for r in receipts)
        try: final_queue=common.api('GET','/queue').json()
        except requests.RequestException: final_queue={'queue_running':['unknown'],'queue_pending':[]}
        try: final_occ=json.loads(__import__('subprocess').check_output(['hive-resource','occupancy','--json'],text=True,timeout=30))
        except Exception: final_occ={'leases':{LEASE_ID:{}}}
        safe_terminal=not unresolved and not final_queue.get('queue_running') and not final_queue.get('queue_pending')
        if safe_terminal:
            hb.stop()
            # Delete only request-owned input files verified by the original input hashes.
            removed=[]
            expected={'appearance':p['appearance_reference']['sha256'],'side_depth':p['side_depth']['sha256']}
            for label,ref in up.items():
                info=ref['uploaded']; f=(COMFY/'input'/info.get('subfolder','')/info['name']).resolve()
                if f.is_relative_to((COMFY/'input').resolve()) and f.is_file() and common.sha(f)==expected[label]: f.unlink(); removed.append(str(f))
            common.save(ROOT/'temporary_inputs_removed.json',{'exact_files':removed})
            common.save(ROOT/'postrun_queue.json',final_queue)
            if LEASE_ID in final_occ.get('leases',{}):
                common.lease('lease','release',LEASE_ID)
                released=True
            else: released=False
            common.save(ROOT/'lease_released.json',{'lease_id':LEASE_ID,'released':released,'matrix_completed':completed})
        else:
            common.save(ROOT/'unresolved_retained_lease.json',{'lease_id':LEASE_ID,'queue':final_queue,'unresolved_receipts':[str(p) for p in ROOT.glob('**/receipt.json') if json.loads(p.read_text()).get('status') in ('running','unresolved')],'action':'Heartbeat remains active. Reconcile recorded prompt IDs with read-only queue/history; do not resubmit or release until terminal.'})
            print('UNRESOLVED: lease heartbeat retained; do not resubmit or release. Reconcile receipt/history.',flush=True)
            while True: time.sleep(30)

if __name__=='__main__': main()
