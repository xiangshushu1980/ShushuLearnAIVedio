#!/usr/bin/env python3
"""[Sean] Qwen single-character body-type prompt comparison."""
import json,time,urllib.parse,urllib.request
from pathlib import Path

ROOT=Path(__file__).resolve().parent
API='http://127.0.0.1:8188'
INPUTS=ROOT/'inputs'; OUTPUTS=ROOT/'outputs'; FLOWS=ROOT/'api_workflows'; MANIFEST=ROOT/'manifest.json'

def api(path,payload=None,data=None,headers=None,timeout=60):
    if payload is not None:
        data=json.dumps(payload).encode(); headers={**(headers or {}),'Content-Type':'application/json'}
    with urllib.request.urlopen(urllib.request.Request(API+path,data=data,headers=headers or {}),timeout=timeout) as r:
        return r.read()

def upload(path,remote):
    boundary='----SeanQwenSingleBodyType'
    body=(f'--{boundary}\r\nContent-Disposition: form-data; name="image"; filename="{remote}"\r\nContent-Type: image/png\r\n\r\n'.encode()+path.read_bytes()+f'\r\n--{boundary}\r\nContent-Disposition: form-data; name="type"\r\n\r\ninput\r\n--{boundary}\r\nContent-Disposition: form-data; name="overwrite"\r\n\r\ntrue\r\n--{boundary}--\r\n'.encode())
    return json.loads(api('/upload/image',data=body,headers={'Content-Type':f'multipart/form-data; boundary={boundary}'}))['name']

def graph(prompt,seed,prefix,refs):
    g={
      '1':{'class_type':'UNETLoader','inputs':{'unet_name':'qwen_image_2.1_int8_convrot.safetensors','weight_dtype':'default'}},
      '2':{'class_type':'CLIPLoader','inputs':{'clip_name':'qwen3vl_8b_int8_convrot.safetensors','type':'qwen_image','device':'default'}},
      '3':{'class_type':'VAELoader','inputs':{'vae_name':'qwen_image_2.1_vae_bf16.safetensors'}},
      '4':{'class_type':'QwenImage21Cache','inputs':{'model':['1',0],'device':'auto','dtype':'default'}},
      '5':{'class_type':'TextEncodeQwenImage21','inputs':{'clip':['2',0],'prompt':prompt,'negative_prompt':'','resolution':1024,'vae':['3',0]}},
      '6':{'class_type':'KSampler','inputs':{'model':['4',0],'positive':['5',0],'negative':['5',1],'latent_image':['5',2],'seed':seed,'steps':25,'cfg':1.0,'sampler_name':'euler','scheduler':'simple','denoise':1.0}},
      '7':{'class_type':'VAEDecode','inputs':{'samples':['6',0],'vae':['3',0]}},
      '8':{'class_type':'SaveImage','inputs':{'images':['7',0],'filename_prefix':prefix}}
    }
    for i,name in enumerate(refs,1):
        node=str(8+i); g[node]={'class_type':'LoadImage','inputs':{'image':name}}; g['5']['inputs'][f'images.image_{i}']=[node,0]
    return g

def submit(g,name,lease):
    (FLOWS/f'{name}.json').write_text(json.dumps(g,indent=2,ensure_ascii=False)+'\n')
    pid=json.loads(api('/prompt',{'prompt':g,'client_id':'sean-qwen-single-body-type-20261002'}))['prompt_id']
    start=time.time(); beat=start
    while time.time()-start<2400:
        item=json.loads(api(f'/history/{pid}')).get(pid,{})
        images=[im for n in item.get('outputs',{}).values() for im in n.get('images',[])]
        if images:
            im=images[0]; q=urllib.parse.urlencode({'filename':im['filename'],'subfolder':im.get('subfolder',''),'type':im.get('type','output')})
            local=OUTPUTS/f'{name}.png'; local.write_bytes(api(f'/view?{q}'))
            return {'id':name,'prompt_id':pid,'seconds':round(time.time()-start,2),'output':str(local.relative_to(ROOT)),'comfy_image':im}
        if time.time()-beat>45:
            import subprocess
            subprocess.run(['hive-resource','lease','heartbeat',lease,'--ttl','600000'],check=True,capture_output=True); beat=time.time()
        time.sleep(3)
    raise TimeoutError(pid)

def main():
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--lease-id',required=True);args=p.parse_args()
    OUTPUTS.mkdir(parents=True,exist_ok=True); FLOWS.mkdir(parents=True,exist_ok=True)
    ref_paths=[INPUTS/n for n in ('identity_face.png','uniform_reference.png','katana_reference.png','courtyard_scene.png')]
    refs=[upload(path,f'sean_single_body_type_ref{i+1}_20261002.png') for i,path in enumerate(ref_paths)]
    common='Use <image1> only for the woman’s face and hairstyle. Use <image2> only for the uniform design, <image3> for the katana design, and <image4> for the moonlit stone courtyard. Create one adult East Asian swordswoman, full body from head to boots, standing upright in a relaxed three-quarter view. Keep the pose, camera distance, apparent height, face, uniform, sword, and scene the same across results. She wears the uniform and carries exactly one sheathed black katana at her left hip. Single coherent painterly fantasy game illustration; no extra people, duplicate weapons, inset panels, or text.'
    builds={
      'slender':'Body build: slender and fine-boned, narrow shoulders and hips, slim arms and legs, long lean silhouette.',
      'athletic':'Body build: athletic and fit, moderately broad shoulders, firm waist, defined forearms and thighs, balanced limbs, not bulky.',
      'powerful':'Body build: powerful and compact, broad shoulders, solid torso, thick forearms, muscular thighs and calves.'
    }
    m=json.loads(MANIFEST.read_text());m['status']='active';MANIFEST.write_text(json.dumps(m,indent=2,ensure_ascii=False)+'\n')
    for condition in ('slender','athletic','powerful'):
        prompt=common+' '+builds[condition]
        for seed in (6200511,6200512):
            name=f'{condition}_seed{seed}';g=graph(prompt,seed,f'sean_qwen_single_body_type_20261002/{name}',refs)
            result=submit(g,name,args.lease_id);result.update({'condition':condition,'seed':seed,'references':['identity_face','uniform_reference','katana_reference','courtyard_scene'],'prompt':prompt})
            m['results'].append(result);MANIFEST.write_text(json.dumps(m,indent=2,ensure_ascii=False)+'\n');print(json.dumps(result,ensure_ascii=False),flush=True)
    m['status']='review';MANIFEST.write_text(json.dumps(m,indent=2,ensure_ascii=False)+'\n')

if __name__=='__main__':main()
