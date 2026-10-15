#!/usr/bin/env python3
"""Owner: Sean. Join measured evidence and explicit visual decisions, preserving unverified spatial geometry."""
from pathlib import Path
import json,hashlib,collections
R=Path(__file__).resolve().parent
def load(f):return json.loads((R/f).read_text())
def write(f,x):(R/f).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
m=load('measurements.json');ov=load('measurement_overrides.json');reviews=load('visual_review.json');bm=load('building_measurements.json');sm=load('spatial_measurements.json');qc={};summary={};records=[]
for path in sorted((R/'runs').glob('*.json')):
 run=load(str(path.relative_to(R)));k=path.stem;condition=k.split('_confirm_')[0] if '_confirm_' in k else k.split('_debug_')[0];debug='_debug_' in k
 rec={'owner':'Sean','phase':'debug' if debug else 'confirmation','condition':condition,'seed':int(k.rsplit('_',1)[1]),'image':run['files'][0],'text_pass':True,'category_value_binding_count_order_pass':True,'extra_or_missing_data':False,'aesthetic_scores':{'material':3 if condition!='metal_v1' else 2,'finish':2,'substantive_change':3 if condition=='glass_building_v1' else 2},'reviewer':'Codex main; nonblind; reviewed all output images on contact sheets, selected raw full resolution and QC vertex sheets','review_refs':['visual_review.json'],'joint_pass':False}
 if condition in ['glass_v1','metal_v1','paper_v1']:
  v=m[k];bars=ov[k]['bars'] if k in ov else v['bars'];scale=(v['axis_tick_centers_0_to_100'][0]-v['axis_tick_centers_0_to_100'][-1])/100
  body_error=max(abs((bot+1-top)/scale-b['expected']) for b in bars for top in b['top_range'] for bot in b['bottom_range'])
  base_error=max(abs(bot-v['axis_tick_centers_0_to_100'][0])/scale for b in bars for bot in b['bottom_range'])
  top_error=max(abs((v['axis_tick_centers_0_to_100'][0]-top)/scale-b['expected']) for b in bars for top in b['top_range'])
  rec.update(actual_body_height_max_error=round(body_error,3),baseline_max_error=round(base_error,3),top_registration_max_error=round(top_error,3),geometry_pass=body_error<=2 and base_error<=2 and top_error<=2 and v['axis_tick_max_error_units']<=2,geometry_refs=['measurements.json']+(['measurement_overrides.json'] if k in ov else []))
  rec['joint_pass']=rec['geometry_pass'];rec['geometry_status']='pass' if rec['geometry_pass'] else 'fail'
 elif condition=='glass_building_v1':
  v=bm[k];rec.update(geometry_refs=['building_measurements.json'],geometry_status='indeterminate_equal_footprint_and_camera' if v.get('geometry_candidate_pass') else 'fail_or_indeterminate',projected_top_baseline_candidate_pass=bool(v.get('geometry_candidate_pass')),geometry_pass=False,form_recognizable=True,note='8/20 satisfy necessary projected top/baseline checks; not a certified joint count. Roof/base additions and unequal facades/depth make strict equal-footprint front-view success unestablished. No inverse physical3D claim.')
 elif condition=='glass_cylinder_v1':
  rec.update(geometry_status='camera_constraint_fail',geometry_pass=False,form_recognizable=True,note='Both debug outputs show elliptical top caps despite registered horizontal front camera. No formal stability claim.')
 elif condition=='glass_spatial_v1':
  v=sm[k];verified_fail=k in ['glass_spatial_v1_confirm_110009','glass_spatial_v1_confirm_109019','glass_spatial_v1_confirm_94001']
  rec.update(geometry_refs=['spatial_measurements.json','spatial_review_sheets.py'],height_candidate_pass=bool(v.get('height_candidate_pass')),geometry_pass=False,geometry_status='verified_fail' if verified_fail else 'indeterminate_full_projection',note='RGB V-fit candidates visually checked on QC copies; not all side-corner and equal-footprint constraints independently recoverable in transparent raster. Do not promote 8/20 front-height candidates to full3D pass. At least3 clear failures rule out18/20 stability even if all other17 passed.')
  if verified_fail:rec['failure_detail']={'glass_spatial_v1_confirm_110009':'90 front edge approx y241..848, generated axis6.5px/unit =>93.385; exceeds tolerance with2px endpoint uncertainty.','glass_spatial_v1_confirm_109019':'Front body bottom90 approx867, axis0 tick850 and separate horizontal line867: original zero calibration not preserved;90 edge y253..867 is too long.','glass_spatial_v1_confirm_94001':'40 front edge approx568..843, calibrated42.669; >2 error even allowing2px uncertainty at each endpoint.'}[k]
 qc[k]=rec;records.append({'job':k,'condition':condition,'seed':rec['seed'],'phase':rec['phase'],'prompt_id':run['prompt_id'],'elapsed_seconds':run['elapsed_seconds'],'sha256':run['sha256'],'lease':run['lease']})
for c in sorted(set(v['condition'] for v in qc.values())):
 vals=[v for v in qc.values() if v['condition']==c and v['phase']=='confirmation'];dbg=[v for v in qc.values() if v['condition']==c and v['phase']=='debug']
 s={'confirmation_n':len(vals),'debug_n':len(dbg),'text_passes':sum(v['text_pass'] for v in vals),'aesthetic_passes':sum(min(v['aesthetic_scores'].values())>=2 for v in vals)}
 if c in ['glass_v1','metal_v1','paper_v1']:s.update(joint_passes=sum(v['joint_pass'] for v in vals),maximum_body_height_error=max(v['actual_body_height_max_error'] for v in vals))
 elif c=='glass_building_v1':s.update(projected_necessary_checks_pass=sum(v.get('projected_top_baseline_candidate_pass',False) for v in vals),joint_success='not established; <=necessary-check count',stability='not demonstrated')
 elif c=='glass_spatial_v1':s.update(front_height_candidates=sum(v.get('height_candidate_pass',False) for v in vals),verified_failures=sum(v['geometry_status']=='verified_fail' for v in vals),joint_success='not certified; <=17/20 from at least3 clear failures',stability='not demonstrated')
 else:s.update(stability='debug camera failure; no confirmation')
 summary[c]=s
samples=[]
for p in (R/'runs').glob('*.json'):samples+=load(str(p.relative_to(R)))['gpu_samples']
metrics=[]
for s in samples:
 try:metrics.append([float(x.strip()) for x in s['gpu'].split(',')])
 except ValueError:pass
manifest={'owner':'Sean','task_id':load('plan.json')['task_id'],'counts':{'images':len(records),'confirmation':sum(r['phase']=='confirmation' for r in records),'debug':sum(r['phase']=='debug' for r in records),'pe_rewrites':0},'summary':summary,'total_recorded_execution_seconds':round(sum(r['elapsed_seconds'] for r in records),2),'observed_peak_vram_mb':max(x[0] for x in metrics),'observed_peak_temperature_c':max(x[2] for x in metrics),'resource_note':'GPU sampled about every3s; instantaneous peaks may be missed. Each batch owns its resource lease, heartbeat<=90s TTL600s, finally release. Final snapshots separate.','records':records,'files_sha256':{str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(R.rglob('*')) if p.is_file() and p.suffix in ['.json','.py','.txt','.png'] and p.name not in ['manifest.json','qc.json'] and '__pycache__' not in str(p)},'no_repairs':True,'models_hash_provenance':'component_hashes.json; previous full hashes with same size/mtime verified. Unused T2I PE not used in this experiment.'}
write('qc.json',qc);write('manifest.json',manifest);write('summary.json',summary)
print(json.dumps({k:manifest[k] for k in ['counts','summary','total_recorded_execution_seconds','observed_peak_vram_mb','observed_peak_temperature_c']},ensure_ascii=False,indent=2))
