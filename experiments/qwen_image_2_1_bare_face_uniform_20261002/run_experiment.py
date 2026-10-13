#!/usr/bin/env python3
"""[Sean] Compare clothed face crops and neutral bare-shoulder identity refs."""
import json,time,urllib.parse,urllib.request
from pathlib import Path

ROOT=Path(__file__).resolve().parent; PROJECT=ROOT.parents[1]
API='http://127.0.0.1:8188'; INPUTS=ROOT/'inputs'; OUTPUTS=ROOT/'outputs'; FLOWS=ROOT/'api_workflows'; MANIFEST=ROOT/'manifest.json'
ANCHORS=PROJECT/'experiments/krea2_quadview_stability_20260928/role_anchors/outputs'
UNIFORM=PROJECT/'experiments/krea2_shared_costume_weapon_20261002/outputs/uniform_reference.png'

def api(path,payload=None,data=None,headers=None,timeout=60):
    if payload is not None: data=json.dumps(payload).encode(); headers={**(headers or {}),'Content-Type':'application/json'}
    with urllib.request.urlopen(urllib.request.Request(API+path,data=data,headers=headers or {}),timeout=timeout) as r:return r.read()

def upload(path,remote):
    b='----SeanQwenBareFaceUniform'; body=(f'--{b}\r\nContent-Disposition: form-data; name="image"; filename="{remote}"\r\nContent-Type: image/png\r\n\r\n'.encode()+path.read_bytes()+f'\r\n--{b}\r\nContent-Disposition: form-data; name="type"\r\n\r\ninput\r\n--{b}\r\nContent-Disposition: form-data; name="overwrite"\r\n\r\ntrue\r\n--{b}--\r\n'.encode())
    return json.loads(api('/upload/image',data=body,headers={'Content-Type':f'multipart/form-data; boundary={b}'}))['name']

def base_graph(prompt,seed,prefix,images,edit=False):
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
    for slot,name in enumerate(images,1):
        node=str(8+slot); g[node]={'class_type':'LoadImage','inputs':{'image':name}}
        g['5']['inputs'][f'images.image_{slot}']=[node,0]
    return g

def submit(g,name,lease):
    (FLOWS/f'{name}.json').write_text(json.dumps(g,indent=2,ensure_ascii=False)+'\n')
    pid=json.loads(api('/prompt',{'prompt':g,'client_id':'sean-qwen-bare-face-uniform-20261002'}))['prompt_id']; start=time.time(); beat=start
    while time.time()-start<2400:
        item=json.loads(api(f'/history/{pid}')).get(pid,{})
        ims=[im for node in item.get('outputs',{}).values() for im in node.get('images',[])]
        if ims:
            im=ims[0];q=urllib.parse.urlencode({'filename':im['filename'],'subfolder':im.get('subfolder',''),'type':im.get('type','output')})
            local=OUTPUTS/f'{name}.png';local.write_bytes(api(f'/view?{q}'))
            return {'id':name,'prompt_id':pid,'seconds':round(time.time()-start,2),'output':str(local.relative_to(ROOT)),'comfy_image':im}
        if time.time()-beat>45:
            import subprocess;subprocess.run(['hive-resource','lease','heartbeat',lease,'--ttl','600000'],check=True,capture_output=True);beat=time.time()
        time.sleep(3)
    raise TimeoutError(pid)

def main():
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--lease-id',required=True);p.add_argument('--stage',choices=['portraits','duos'],required=True);a=p.parse_args()
    from PIL import Image
    import shutil
    INPUTS.mkdir(parents=True,exist_ok=True);OUTPUTS.mkdir(parents=True,exist_ok=True);FLOWS.mkdir(parents=True,exist_ok=True)
    paths={
      'face1':ANCHORS/'sean_eastern_swordswoman_role_front_seed4803001.png',
      'face2':ANCHORS/'sean_red_mage_role_front_seed4803002.png'}
    for key,path in paths.items():
        out=INPUTS/f'{key}_clothed_crop.png'
        if not out.exists(): Image.open(path).crop((256,0,768,512)).save(out)
    shutil.copy2(UNIFORM,INPUTS/'shared_uniform.png')
    manifest=json.loads(MANIFEST.read_text());manifest['status']='active';MANIFEST.write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+'\n')
    if a.stage=='portraits':
        for key in ('face1','face2'):
            src=upload(INPUTS/f'{key}_clothed_crop.png',f'sean_{key}_identity_crop_20261002.png')
            prompt='Keep the exact face, hairstyle, expression and head-to-shoulder proportions from the input image. Make a neutral head-and-shoulders identity portrait on plain gray. Show bare neck and shoulders, with no clothing, armor, jewelry or props visible.'
            g=base_graph(prompt,6200401 if key=='face1' else 6200402,f'sean_qwen_bare_face_uniform_20261002/{key}_bare_shoulders',[src],edit=True)
            result=submit(g,f'{key}_bare_portrait',a.lease_id);result.update({'kind':'identity_reference','source':f'inputs/{key}_clothed_crop.png','prompt':prompt})
            shutil.copy2(OUTPUTS/f'{key}_bare_portrait.png',INPUTS/f'{key}_bare_portrait.png')
            manifest['results'].append(result);MANIFEST.write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+'\n');print(json.dumps(result,ensure_ascii=False),flush=True)
    else:
        refs={}
        for key in ('face1_clothed_crop','face2_clothed_crop','face1_bare_portrait','face2_bare_portrait','shared_uniform'):
            refs[key]=upload(INPUTS/f'{key}.png',f'sean_{key}_20261002.png')
        prompt='Use <image1> as the left woman’s identity and <image2> as the right woman’s identity. Both wear the same uniform from <image3>. Exactly two adult women, full-body, front-facing. Arms slightly away; hands visible and empty. Plain studio background. No objects.'
        cases=[('clothed_face_crops',['face1_clothed_crop','face2_clothed_crop','shared_uniform']),('bare_neck_portraits',['face1_bare_portrait','face2_bare_portrait','shared_uniform'])]
        for condition,names in cases:
            for seed in (6200301,6200302):
                job=f'{condition}_seed{seed}';g=base_graph(prompt,seed,f'sean_qwen_bare_face_uniform_20261002/{job}',[refs[n] for n in names])
                result=submit(g,job,a.lease_id);result.update({'kind':'duo_output','condition':condition,'seed':seed,'references':names,'prompt':prompt})
                manifest['results'].append(result);MANIFEST.write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+'\n');print(json.dumps(result,ensure_ascii=False),flush=True)
        manifest['status']='review';MANIFEST.write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+'\n')

if __name__=='__main__':main()
