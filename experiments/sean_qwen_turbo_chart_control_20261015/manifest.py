#!/usr/bin/env python3
"""Owner: Sean. Rebuild traceable manifest from archived per-job receipts."""
import json,hashlib,subprocess
from pathlib import Path
from PIL import Image
R=Path(__file__).resolve().parent
out={'owner':'Sean','task_id':'remote-31c37e9c-c14a-45ca-a261-963e846990c2','date_local':'2026-10-15 Asia/Shanghai','configuration':json.load(open(R/'plan.json')),'jobs':[],'artifacts':{},'git_policy':'Generated PNGs and contact JPGs retained locally (ignored), all hashes/receipts/QC/scripts/reference inputs tracked. No remote in infograph-research.'}
for path in sorted((R/'runs').glob('*.json')):
 rec=json.load(open(path));wf=json.load(open(R/'workflows'/f"{rec['job']}.json"))['prompt'];imgs=[f for f in rec['files'] if f.endswith('.png')];row={k:rec[k] for k in ['job','status','prompt_id','elapsed_seconds','lease','sha256','files']};row['workflow']=f"workflows/{rec['job']}.json";row['receipt']=str(path.relative_to(R));row['seed']=wf.get('9',{}).get('inputs',{}).get('noise_seed');row['route']='reference-guided image edit' if any(n['class_type']=='TextEncodeQwenImage21' for n in wf.values()) else ('official PE rewrite' if rec['job'].startswith('pe_') else 'text-to-image');row['gpu_peak_vram_mb_observed']=max((int(x['gpu'].split(',')[0]) for x in rec['gpu_samples']),default=None);row['gpu_peak_temp_c_observed']=max((int(x['gpu'].split(',')[2]) for x in rec['gpu_samples']),default=None)
 for f in imgs:
  with Image.open(R/f) as im:row['dimensions']=list(im.size)
 out['jobs'].append(row)
for pat in ['*reference*.png','*plan.json','prompts/*.txt','*measurements.json','text_review*.json']:
 for p in R.glob(pat):out['artifacts'][str(p.relative_to(R))]={'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
out['generated_image_count']=sum(j['route']!='official PE rewrite' for j in out['jobs']);out['total_elapsed_seconds']=round(sum(j['elapsed_seconds'] for j in out['jobs']),2);out['gpu_peak_vram_mb_observed']=max(j['gpu_peak_vram_mb_observed'] or 0 for j in out['jobs']);out['gpu_peak_temp_c_observed']=max(j['gpu_peak_temp_c_observed'] or 0 for j in out['jobs']);out['versions']={p:subprocess.check_output(['git','-C',p,'rev-parse','HEAD'],text=True).strip() for p in ['/home/sean/projects/ComfyUI','/home/sean/projects/ComfyUI/custom_nodes/ComfyUI-Qwen-Image-2.1-Prompt-Enhancer']}
if (R/'component_hashes.json').exists():out['component_hashes']=json.load(open(R/'component_hashes.json'))
json.dump(out,open(R/'manifest.json','w'),ensure_ascii=False,indent=2);print('manifest:',len(out['jobs']),'jobs',out['generated_image_count'],'images',out['total_elapsed_seconds'],'seconds')
