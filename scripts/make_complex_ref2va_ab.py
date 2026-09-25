import json
from pathlib import Path

base = json.loads(Path('experiments/h3_ref2v/cases_fr_pair.json').read_text())[:1]
base[0]['width'], base[0]['height'], base[0]['length'] = 768, 448, 99
base[0]['prompt'] += '\nMake the staging complex: all three subjects remain visible at different depths, with foreground rain, a moving camera, an interaction, and detailed background activity.'
base[0]['ref_images'] = ['ref2v_scene_cyberpunk.png','ref2v_char_swordswoman.png','ref2v_char_cybergirl.png']
base[0]['name'] = 'complex_cyber_20'; base[0]['steps']=20; base[0]['sampler']='res_multistep'; base[0].pop('lora',None); base[0]['prefix']='video/ref2va_complex_ab_20260912/complex_cyber_20'
cases=[]
for src in base:
    for name, steps, sampler, lora in [
        ('complex_cyber_20',20,'res_multistep',None),
        ('complex_cyber_8',8,'res_multistep','minimax_h3_ref2v_turbo_8step_v1.0_768p_comfyui_bf16.safetensors'),
        ('complex_cyber_4',4,'euler','minimax_h3_ref2v_turbo_4step_v0.1_comfyui_bf16.safetensors')]:
        c=dict(src); c['name']=name; c['steps']=steps; c['sampler']=sampler; c['seed']=20260920; c['prefix']='video/ref2va_complex_ab_20260912/'+name
        if lora: c['lora']=lora; c['lora_strength']=1.0
        else: c.pop('lora',None); c.pop('lora_strength',None)
        cases.append(c)
Path('experiments/h3_ref2v/cases_complex_ab_20260912.json').write_text(json.dumps(cases,ensure_ascii=False,indent=1))
