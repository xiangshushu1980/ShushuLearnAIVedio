#!/usr/bin/env python3
"""[Sean] Qwen-Image-2.1 text-only proportion/height comparison."""
import json, time, urllib.parse, urllib.request
from pathlib import Path

ROOT=Path(__file__).resolve().parent
PROJECT=ROOT.parents[1]
SOURCE=PROJECT/'experiments/qwen_image_2_1_bare_face_uniform_20261002/inputs'
API='http://127.0.0.1:8188'
OUT=ROOT/'outputs'; FLOWS=ROOT/'api_workflows'; MANIFEST=ROOT/'manifest.json'

def api(path,payload=None,data=None,headers=None,timeout=60):
    if payload is not None:
        data=json.dumps(payload).encode(); headers={**(headers or {}),'Content-Type':'application/json'}
    with urllib.request.urlopen(urllib.request.Request(API+path,data=data,headers=headers or {}),timeout=timeout) as r:
        return r.read()

def upload(path,remote):
    boundary='----SeanQwenPropHeight'
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
    pid=json.loads(api('/prompt',{'prompt':g,'client_id':'sean-qwen-proportion-height-20261002'}))['prompt_id']
    start=time.time(); beat=start
    while time.time()-start<2400:
        item=json.loads(api(f'/history/{pid}')).get(pid,{})
        images=[im for n in item.get('outputs',{}).values() for im in n.get('images',[])]
        if images:
            im=images[0]; q=urllib.parse.urlencode({'filename':im['filename'],'subfolder':im.get('subfolder',''),'type':im.get('type','output')})
            local=OUT/f'{name}.png'; local.write_bytes(api(f'/view?{q}'))
            return {'id':name,'prompt_id':pid,'seconds':round(time.time()-start,2),'output':str(local.relative_to(ROOT)),'comfy_image':im}
        if time.time()-beat>45:
            import subprocess
            subprocess.run(['hive-resource','lease','heartbeat',lease,'--ttl','600000'],check=True,capture_output=True); beat=time.time()
        time.sleep(3)
    raise TimeoutError(pid)

def main():
    import argparse, subprocess
    p=argparse.ArgumentParser(); p.add_argument('--lease-id',required=True); a=p.parse_args()
    OUT.mkdir(parents=True,exist_ok=True); FLOWS.mkdir(parents=True,exist_ok=True)
    files=[SOURCE/'face1_bare_portrait.png',SOURCE/'face2_bare_portrait.png',SOURCE/'shared_uniform.png']
    refs=[upload(f,f'sean_propheight_ref{i+1}_20261002.png') for i,f in enumerate(files)]
    prompts={
      '8v9_same_height':'Use <image1> as the left identity and <image2> as the right identity. Both wear the uniform from <image3>. Exactly two full-body women, front view, side by side, same total height and same ground line. Left woman: exactly 8 heads tall, 170 cm. Right woman: exactly 9 heads tall, 170 cm. Hands visible. Plain studio.',
      '9v9_different_height':'Use <image1> as the left identity and <image2> as the right identity. Both wear the uniform from <image3>. Exactly two full-body women, front view, side by side; both exactly 9 heads tall. Left woman is 160 cm tall; right woman is 180 cm tall. Show the height difference clearly, with feet on the same ground line. Hands visible. Plain studio.',
      '8v9_different_height':'Use <image1> as the left identity and <image2> as the right identity. Both wear the uniform from <image3>. Exactly two full-body women, front view, side by side, feet on the same ground line. Left woman: exactly 8 heads tall, 160 cm. Right woman: exactly 9 heads tall, 180 cm. Show the height difference clearly. Hands visible. Plain studio.'
    }
    m=json.loads(MANIFEST.read_text()); m['status']='active'; MANIFEST.write_text(json.dumps(m,indent=2,ensure_ascii=False)+'\n')
    for cond in ('8v9_same_height','9v9_different_height','8v9_different_height'):
        for seed in (6200411,6200412):
            name=f'{cond}_seed{seed}'; g=graph(prompts[cond],seed,f'sean_qwen_propheight_20261002/{name}',refs)
            r=submit(g,name,a.lease_id); r.update({'condition':cond,'seed':seed,'prompt':prompts[cond]})
            m['results'].append(r); MANIFEST.write_text(json.dumps(m,indent=2,ensure_ascii=False)+'\n'); print(json.dumps(r,ensure_ascii=False),flush=True)
    m['status']='review'; MANIFEST.write_text(json.dumps(m,indent=2,ensure_ascii=False)+'\n')

if __name__=='__main__': main()
