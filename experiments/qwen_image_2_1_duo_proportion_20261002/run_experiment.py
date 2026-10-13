#!/usr/bin/env python3
"""[Sean] Qwen head-to-body proportion control A/B."""
import json,time,urllib.parse,urllib.request,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parent;PROJECT=ROOT.parents[1]
API='http://127.0.0.1:8188';INPUTS=ROOT/'inputs';OUTPUTS=ROOT/'outputs';FLOWS=ROOT/'api_workflows';MANIFEST=ROOT/'manifest.json'
SOURCE=PROJECT/'experiments/qwen_image_2_1_bare_face_uniform_20261002'

def api(path,payload=None,data=None,headers=None,timeout=60):
 if payload is not None:data=json.dumps(payload).encode();headers={**(headers or {}),'Content-Type':'application/json'}
 with urllib.request.urlopen(urllib.request.Request(API+path,data=data,headers=headers or {}),timeout=timeout) as r:return r.read()
def upload(path,remote):
 b='----SeanQwenDuoProportion';body=(f'--{b}\r\nContent-Disposition: form-data; name="image"; filename="{remote}"\r\nContent-Type: image/png\r\n\r\n'.encode()+path.read_bytes()+f'\r\n--{b}\r\nContent-Disposition: form-data; name="type"\r\n\r\ninput\r\n--{b}\r\nContent-Disposition: form-data; name="overwrite"\r\n\r\ntrue\r\n--{b}--\r\n'.encode())
 return json.loads(api('/upload/image',data=body,headers={'Content-Type':f'multipart/form-data; boundary={b}'}))['name']

def graph(prompt,seed,prefix,refs):
 g={'1':{'class_type':'UNETLoader','inputs':{'unet_name':'qwen_image_2.1_int8_convrot.safetensors','weight_dtype':'default'}},
 '2':{'class_type':'CLIPLoader','inputs':{'clip_name':'qwen3vl_8b_int8_convrot.safetensors','type':'qwen_image','device':'default'}},
 '3':{'class_type':'VAELoader','inputs':{'vae_name':'qwen_image_2.1_vae_bf16.safetensors'}},
 '4':{'class_type':'QwenImage21Cache','inputs':{'model':['1',0],'device':'auto','dtype':'default'}},
 '5':{'class_type':'TextEncodeQwenImage21','inputs':{'clip':['2',0],'prompt':prompt,'negative_prompt':'','resolution':1024,'vae':['3',0]}},
 '6':{'class_type':'KSampler','inputs':{'model':['4',0],'positive':['5',0],'negative':['5',1],'latent_image':['5',2],'seed':seed,'steps':25,'cfg':1.0,'sampler_name':'euler','scheduler':'simple','denoise':1.0}},
 '7':{'class_type':'VAEDecode','inputs':{'samples':['6',0],'vae':['3',0]}},
 '8':{'class_type':'SaveImage','inputs':{'images':['7',0],'filename_prefix':prefix}}}
 for i,name in enumerate(refs,1):
  node=str(8+i);g[node]={'class_type':'LoadImage','inputs':{'image':name}};g['5']['inputs'][f'images.image_{i}']=[node,0]
 return g

def submit(g,name,lease):
 (FLOWS/f'{name}.json').write_text(json.dumps(g,indent=2,ensure_ascii=False)+'\n')
 pid=json.loads(api('/prompt',{'prompt':g,'client_id':'sean-qwen-duo-proportion-20261002'}))['prompt_id'];start=time.time();beat=start
 while time.time()-start<2400:
  item=json.loads(api(f'/history/{pid}')).get(pid,{})
  ims=[im for n in item.get('outputs',{}).values() for im in n.get('images',[])]
  if ims:
   im=ims[0];q=urllib.parse.urlencode({'filename':im['filename'],'subfolder':im.get('subfolder',''),'type':im.get('type','output')});local=OUTPUTS/f'{name}.png';local.write_bytes(api(f'/view?{q}'))
   return {'id':name,'prompt_id':pid,'seconds':round(time.time()-start,2),'output':str(local.relative_to(ROOT)),'comfy_image':im}
  if time.time()-beat>45:
   import subprocess;subprocess.run(['hive-resource','lease','heartbeat',lease,'--ttl','600000'],check=True,capture_output=True);beat=time.time()
  time.sleep(3)
 raise TimeoutError(pid)

def main():
 import argparse
 p=argparse.ArgumentParser();p.add_argument('--lease-id',required=True);p.add_argument('--stage',choices=['guide','compare'],required=True);a=p.parse_args()
 INPUTS.mkdir(parents=True,exist_ok=True);OUTPUTS.mkdir(parents=True,exist_ok=True);FLOWS.mkdir(parents=True,exist_ok=True)
 m=json.loads(MANIFEST.read_text());m['status']='active';MANIFEST.write_text(json.dumps(m,indent=2,ensure_ascii=False)+'\n')
 if a.stage=='guide':
  text='One full-body reference sheet with exactly two anonymous adult women standing side by side, front-facing and the same height. Both have natural adult anatomy and are exactly eight heads tall: head height is one eighth of total figure height from crown to soles. Arms relaxed slightly away from their sides, both hands visible and empty. They wear identical plain seamless matte-gray bodysuits with no markings, jewelry, armor, or accessories. Plain light-gray studio background, clear silhouettes, no text.'
  g=graph(text,6200399,'sean_qwen_duo_proportion_20261002/two_figure_guide',[]);r=submit(g,'two_figure_proportion_guide',a.lease_id);r.update({'kind':'proportion_guide','prompt':text});shutil.copy2(OUTPUTS/'two_figure_proportion_guide.png',INPUTS/'two_figure_proportion_guide.png');m['results'].append(r);MANIFEST.write_text(json.dumps(m,indent=2,ensure_ascii=False)+'\n');print(json.dumps(r,ensure_ascii=False),flush=True)
 else:
  local={'face1':SOURCE/'inputs/face1_bare_portrait.png','face2':SOURCE/'inputs/face2_bare_portrait.png','uniform':SOURCE/'inputs/shared_uniform.png','guide':INPUTS/'two_figure_proportion_guide.png'}
  refs={k:upload(v,f'sean_duo_proportion_{k}_20261002.png') for k,v in local.items()}
  prompts={
   'text_8_head_proportion':('Use <image1> as the left identity and <image2> as the right identity. Both wear the uniform from <image3>. Exactly two full-body adult women, front view, side by side. Each is eight heads tall; each head is one eighth of body height. Hands visible. Plain studio.'),
   'body_guide_8_head_proportion':("Follow <image1> only for the two-person pose and adult body proportions. Use <image2> as the left identity, <image3> as the right identity; both wear the uniform from <image4>. Exactly two full-body women side by side. Preserve the guide's 8-head-tall proportions, equal figure height and visible hands. Plain studio.")}
  cases=[('text_8_head_proportion',['face1','face2','uniform']),('body_guide_8_head_proportion',['guide','face1','face2','uniform'])]
  for condition,names in cases:
   for seed in (6200311,6200312):
    job=f'{condition}_seed{seed}';g=graph(prompts[condition],seed,f'sean_qwen_duo_proportion_20261002/{job}',[refs[k] for k in names]);r=submit(g,job,a.lease_id);r.update({'kind':'scored_output','condition':condition,'seed':seed,'references':names,'prompt':prompts[condition]});m['results'].append(r);MANIFEST.write_text(json.dumps(m,indent=2,ensure_ascii=False)+'\n');print(json.dumps(r,ensure_ascii=False),flush=True)
  m['status']='review';MANIFEST.write_text(json.dumps(m,indent=2,ensure_ascii=False)+'\n')
if __name__=='__main__':main()
