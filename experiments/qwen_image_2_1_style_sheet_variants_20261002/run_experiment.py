#!/usr/bin/env python3
"""[Sean] Qwen style variants from one fixed video main-image candidate."""
import json, os, subprocess, time, urllib.parse, urllib.request
from pathlib import Path

ROOT=Path(__file__).resolve().parent
API='http://127.0.0.1:8188'
LEASE=os.environ['HIVE_LEASE_ID']
PREFIX='sean_qwen_style_sheet_variants_20261002'
SOURCE=ROOT/'inputs/source_fullbody.png'
SEED=6200801
STYLES={
 'anime_cel':'Restyle the supplied character as polished Japanese 2D anime key art: clean confident contours, expressive but faithful facial features, crisp cel shading, controlled highlights, refined anime character design.',
 'painterly_concept':'Restyle the supplied character as refined semi-realistic digital fantasy concept art: visible painterly brushwork, nuanced soft edges, rich but restrained color, carefully painted metallic armor and fabric.',
 '3d_game_render':'Restyle the supplied character as a polished stylized-realistic 3D game character: clearly rendered 3D forms, refined physically based fabric and metal materials, soft studio lighting, high-end game concept render.',
 'graphic_novel':'Restyle the supplied character as high-quality 2D graphic novel art: elegant ink outlines, selective crosshatching, simplified shadow shapes, restrained color blocks, mature illustrated proportions.',
 'watercolor_gouache':'Restyle the supplied character as a carefully painted watercolor and gouache illustration: visible pigment texture, soft layered washes, delicate gouache highlights, subtle paper grain, muted coherent palette.'
}
COMMON=(' Preserve the same adult woman, recognizable face, tied-back black hair, body proportions, navy uniform, silver shoulder and forearm armor, black boots, belt, and exactly one black sheathed katana. Show one complete single-person full-body character, front-facing and standing upright, with hands visible and relaxed; keep the whole figure including boots in frame. Use a plain warm off-white background and clean studio lighting. No panels, text, labels, borders, other people, extra weapons, or added accessories. Change only the rendering style.')

def req(path,payload=None,data=None,headers=None,timeout=60):
 if payload is not None:
  data=json.dumps(payload).encode(); headers={**(headers or {}),'Content-Type':'application/json'}
 return urllib.request.urlopen(urllib.request.Request(API+path,data=data,headers=headers or {}),timeout=timeout).read()

def upload(path):
 boundary='----SeanQwenStyleSheet20261002'; name=f'{PREFIX}_source.png'
 body=(f'--{boundary}\r\nContent-Disposition: form-data; name="image"; filename="{name}"\r\nContent-Type: image/png\r\n\r\n'.encode()+path.read_bytes()+f'\r\n--{boundary}\r\nContent-Disposition: form-data; name="type"\r\n\r\ninput\r\n--{boundary}\r\nContent-Disposition: form-data; name="overwrite"\r\n\r\ntrue\r\n--{boundary}--\r\n'.encode())
 return json.loads(req('/upload/image',data=body,headers={'Content-Type':f'multipart/form-data; boundary={boundary}'}))['name']

def make_graph(prompt,ref):
 g={
 '1':{'class_type':'UNETLoader','inputs':{'unet_name':'qwen_image_2.1_int8_convrot.safetensors','weight_dtype':'default'}},
 '2':{'class_type':'CLIPLoader','inputs':{'clip_name':'qwen3vl_8b_int8_convrot.safetensors','type':'qwen_image','device':'default'}},
 '3':{'class_type':'VAELoader','inputs':{'vae_name':'qwen_image_2.1_vae_bf16.safetensors'}},
 '4':{'class_type':'QwenImage21Cache','inputs':{'model':['1',0],'device':'auto','dtype':'default'}},
 '5':{'class_type':'TextEncodeQwenImage21','inputs':{'clip':['2',0],'prompt':prompt,'negative_prompt':'','resolution':1024,'vae':['3',0],'images.image_1':['10',0]}},
 '6':{'class_type':'EmptyLatentImage','inputs':{'width':1536,'height':1024,'batch_size':1}},
 '7':{'class_type':'KSampler','inputs':{'model':['4',0],'positive':['5',0],'negative':['5',1],'latent_image':['6',0],'seed':SEED,'steps':25,'cfg':1.0,'sampler_name':'euler','scheduler':'simple','denoise':1.0}},
 '8':{'class_type':'VAEDecode','inputs':{'samples':['7',0],'vae':['3',0]}},
 '9':{'class_type':'SaveImage','inputs':{'images':['8',0],'filename_prefix':f'{PREFIX}/STYLE'}},
 '10':{'class_type':'LoadImage','inputs':{'image':ref}}
 }
 return g

def submit(style,descriptor,ref):
 name='style_'+style; prompt=descriptor+COMMON
 (ROOT/'prompts'/f'{name}.txt').write_text(prompt+'\n')
 g=make_graph(prompt,ref); g['9']['inputs']['filename_prefix']=f'{PREFIX}/{name}'
 (ROOT/'api_workflows'/f'{name}.json').write_text(json.dumps(g,ensure_ascii=False,indent=2)+'\n')
 queue=json.loads(req('/queue'))
 if queue.get('queue_running') or queue.get('queue_pending'): raise RuntimeError('ComfyUI shared queue is busy; aborting')
 pid=json.loads(req('/prompt',{'prompt':g,'client_id':'sean-qwen-style-sheet-20261002'}))['prompt_id']
 start=time.time(); last=start
 while time.time()-start<1200:
  item=json.loads(req('/history/'+pid)).get(pid,{})
  if item.get('status',{}).get('status_str')=='error': raise RuntimeError(json.dumps(item.get('status'),ensure_ascii=False))
  ims=[im for n in item.get('outputs',{}).values() for im in n.get('images',[])]
  if ims:
   im=ims[0]; query=urllib.parse.urlencode({'filename':im['filename'],'subfolder':im.get('subfolder',''),'type':im.get('type','output')})
   dest=ROOT/'outputs'/f'{name}.png'; dest.write_bytes(req('/view?'+query))
   return {'id':name,'style':style,'prompt_id':pid,'seed':SEED,'seconds':round(time.time()-start,2),'output':str(dest.relative_to(ROOT)),'comfy_image':im}
  if time.time()-last>45:
   subprocess.run(['hive-resource','lease','heartbeat',LEASE,'--ttl','600000'],check=True,capture_output=True); last=time.time()
  time.sleep(2)
 raise TimeoutError(pid)

def main():
 SOURCE.parent.mkdir(parents=True,exist_ok=True); (ROOT/'outputs').mkdir(exist_ok=True); (ROOT/'prompts').mkdir(exist_ok=True); (ROOT/'api_workflows').mkdir(exist_ok=True)
 source=Path('/home/sean/projects/comfy-ops/experiments/qwen_image_2_1_staged_character_reference_20261002/outputs/character_candidate_02.png')
 SOURCE.write_bytes(source.read_bytes()); ref=upload(SOURCE)
 manifest={'owner':'Sean','experiment':ROOT.name,'status':'active','purpose':'Compare Qwen rendering styles on one full-body character main-image candidate intended for later H3 video-reference derivation. These are experimental main-image candidates, not canonical H3 reference assets.','source_image':'inputs/source_fullbody.png','style_variants':[],'runtime':{'comfyui':API,'unet':'qwen_image_2.1_int8_convrot.safetensors','clip':'qwen3vl_8b_int8_convrot.safetensors','vae':'qwen_image_2.1_vae_bf16.safetensors','krea2_used':False,'lora':None,'size':'1536x1024','steps':25,'cfg':1.0,'sampler':'euler','scheduler':'simple','seed':SEED}}
 (ROOT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
 for style,descriptor in STYLES.items():
  result=submit(style,descriptor,ref); manifest['style_variants'].append(result); (ROOT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n'); print(json.dumps(result,ensure_ascii=False),flush=True)
 manifest['status']='review'; manifest['peak_vram_measured']=False; (ROOT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps({'status':'review','count':len(manifest['style_variants'])}),flush=True)

if __name__=='__main__': main()
