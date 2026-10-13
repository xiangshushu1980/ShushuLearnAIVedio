#!/usr/bin/env python3
"""[Sean] Qwen-Image-2.1 matched comparison for shared costume and weapon."""
import json, time, urllib.parse, urllib.request
from pathlib import Path

ROOT=Path(__file__).resolve().parent
API='http://127.0.0.1:8188'
INPUTS=ROOT/'inputs'; OUTPUTS=ROOT/'outputs'; FLOWS=ROOT/'api_workflows'
MANIFEST=ROOT/'manifest.json'

def api(path,payload=None,data=None,headers=None,timeout=60):
    if payload is not None:
        data=json.dumps(payload).encode(); headers={**(headers or {}),'Content-Type':'application/json'}
    req=urllib.request.Request(API+path,data=data,headers=headers or {})
    with urllib.request.urlopen(req,timeout=timeout) as r: return r.read()

def upload(path,remote):
    boundary='----SeanQwenSharedCostumeWeapon'
    body=(f'--{boundary}\r\nContent-Disposition: form-data; name="image"; filename="{remote}"\r\nContent-Type: image/png\r\n\r\n'.encode()+path.read_bytes()+f'\r\n--{boundary}\r\nContent-Disposition: form-data; name="type"\r\n\r\ninput\r\n--{boundary}\r\nContent-Disposition: form-data; name="overwrite"\r\n\r\ntrue\r\n--{boundary}--\r\n'.encode())
    return json.loads(api('/upload/image',data=body,headers={'Content-Type':f'multipart/form-data; boundary={boundary}'}))['name']

def prompt(condition):
    binds={
      'faces_prompt_only':'Use <image1> only as the left woman’s face and hairstyle identity, and <image2> only as the right woman’s face and hairstyle identity. Do not copy clothing or armor from these cropped identity references.',
      'faces_plus_uniform':'Use <image1> only as the left woman’s face and hairstyle identity, and <image2> only as the right woman’s face and hairstyle identity. Do not copy clothing or armor from these cropped identity references. Use <image3> only as the exact shared uniform design; put the same uniform on both women.',
      'faces_plus_weapon':'Use <image1> only as the left woman’s face and hairstyle identity, and <image2> only as the right woman’s face and hairstyle identity. Do not copy clothing or armor from these cropped identity references. Use <image3> only as the exact katana design; make one identical copy for each woman.',
      'faces_plus_uniform_weapon':'Use <image1> only as the left woman’s face and hairstyle identity, and <image2> only as the right woman’s face and hairstyle identity. Do not copy clothing or armor from these cropped identity references. Use <image3> only as the exact shared uniform design; put the same uniform on both women. Use <image4> only as the exact katana design; make one identical copy for each woman.',
      'faces_plus_uniform_weapon_single_sheathed':'Use <image1> only as the left woman’s face and hairstyle identity, and <image2> only as the right woman’s face and hairstyle identity. Do not copy clothing or armor from these cropped identity references. Use <image3> only as the exact shared uniform design; put the same uniform on both women. Use <image4> only as the exact katana design; put one identical, fully sheathed katana at each woman’s left hip.'}
    binds['faces_uniform_prompt_single_katana']='Use <image1> only as the left woman’s face and hairstyle identity, and <image2> only as the right woman’s face and hairstyle identity. Use <image3> only as the exact shared uniform design; put the same uniform on both women. For each woman, show exactly one complete katana, fully sheathed and worn at her left hip. The visible grip, guard and scabbard are parts of this one sheathed sword.'
    binds['faces_uniform_weapon_prompt_single_katana']='Use <image1> only as the left woman’s face and hairstyle identity, and <image2> only as the right woman’s face and hairstyle identity. Use <image3> only as the exact shared uniform design; put the same uniform on both women. Use <image4> only as the design of the single katana each woman wears fully sheathed at her left hip. Each sword is one complete assembly: one visible grip and guard attached to one scabbard containing the blade.'
    if condition in ('faces_uniform_prompt_single_katana','faces_uniform_weapon_prompt_single_katana'):
        return (binds[condition]+' Create one coherent fantasy game concept-art illustration with exactly two adult women, full body from head to boots, standing side by side at equal scale. '
          'The left woman has the East Asian face, almond-shaped dark-brown eyes and black high ponytail tied with red cord from <image1>. '
          'The right woman has the freckled oval face, green-hazel eyes and copper-red braided ponytail from <image2>. Keep the two identities distinct. '
          'Both women wear exactly the same ivory high-collar tunic, deep navy fitted split coat with red lining, red waist sash, dark trousers, black knee boots and one lacquered shoulder guard. Match all outfit cuts, colors and details. '
          'There are exactly two weapons in the whole image: one katana worn at the left hip of each woman. Each is fully sheathed; show one grip and guard connected to its own single black lacquer scabbard. Do not draw either blade. Do not put a sword in either hand. Do not add a second hilt, sword, sheath, dagger, wakizashi or back-mounted weapon. Keep the hilt and scabbard visually connected as one item on the same belt. '
          'Use a plain warm-gray studio background, unified painterly rendering and light. Keep both full silhouettes inside the square image. No extra people, detached props, panels, borders, labels, text or watermark.')
    if condition=='faces_plus_uniform_weapon_single_sheathed':
        return (binds[condition]+' Create one coherent wide landscape fantasy game concept-art illustration, target aspect ratio 3:2, a single continuous studio scene. '
          'Show exactly two adult women, full body from head to boots, standing side by side at equal scale with clear space between them. '
          'The left woman has the East Asian face, almond-shaped dark-brown eyes and black high ponytail tied with red cord from <image1>. '
          'The right woman has the freckled oval face, green-hazel eyes and copper-red braided ponytail from <image2>. Keep these two identities and hairstyles distinct. '
          'Both women wear exactly the same uniform: identical ivory high-collar tunic, deep navy fitted split coat with red lining, red waist sash, dark trousers, black knee boots, and one simple lacquered shoulder guard. Match the cut, colors, materials, proportions and details between both women. '
          'Each woman wears exactly one complete katana at her left hip, fully inside its black lacquer scabbard. The two sheathed katanas have matching curved silhouettes, dark wrapped grips and restrained bronze fittings. No drawn blade, no hand-held weapon, no second sword, no additional sheath, and no other weapon parts. '
          'Use a simple warm-gray studio backdrop, coherent painterly fantasy game concept art, unified light and perspective, both full silhouettes inside frame. Do not add other people, extra weapons, costume variations, floating garments, panels, borders, labels, text or watermark.')
    return (binds[condition]+' Create one coherent wide landscape fantasy game concept-art illustration, target aspect ratio 3:2, a single continuous studio scene. '
      'Show exactly two adult women, full body from head to boots, standing side by side at equal scale with clear space between them. '
      'The left woman has the East Asian face, almond-shaped dark-brown eyes and black high ponytail tied with red cord from <image1>. '
      'The right woman has the freckled oval face, green-hazel eyes and copper-red braided ponytail from <image2>. Keep these two identities and hairstyles distinct. '
      'Both women wear exactly the same uniform: identical ivory high-collar tunic, deep navy fitted split coat with red lining, red waist sash, dark trousers, black knee boots, and one simple lacquered shoulder guard. Match the cut, colors, materials, proportions and details between both women. '
      'Each woman carries exactly one matching curved katana in her hands. Both weapons have the same black lacquer scabbard, dark wrapped grip and restrained bronze fittings. Show one weapon per person, clearly separated and fully visible. '
      'Use a simple warm-gray studio backdrop, coherent painterly fantasy game concept art, unified light and perspective, both full silhouettes inside frame. Do not add other people, extra weapons, costume variations, floating garments, panels, borders, labels, text or watermark.')

def make_graph(condition,seed,remote_refs):
    text=prompt(condition)
    graph={
      '1':{'class_type':'UNETLoader','inputs':{'unet_name':'qwen_image_2.1_int8_convrot.safetensors','weight_dtype':'default'}},
      '2':{'class_type':'CLIPLoader','inputs':{'clip_name':'qwen3vl_8b_int8_convrot.safetensors','type':'qwen_image','device':'default'}},
      '3':{'class_type':'VAELoader','inputs':{'vae_name':'qwen_image_2.1_vae_bf16.safetensors'}},
      '4':{'class_type':'QwenImage21Cache','inputs':{'model':['1',0],'device':'auto','dtype':'default'}},
      '5':{'class_type':'TextEncodeQwenImage21','inputs':{'clip':['2',0],'prompt':text,'negative_prompt':'','resolution':1024,'vae':['3',0]}},
      '6':{'class_type':'KSampler','inputs':{'model':['4',0],'positive':['5',0],'negative':['5',1],'latent_image':['5',2],'seed':seed,'steps':25,'cfg':1.0,'sampler_name':'euler','scheduler':'simple','denoise':1.0}},
      '7':{'class_type':'VAEDecode','inputs':{'samples':['6',0],'vae':['3',0]}},
      '8':{'class_type':'SaveImage','inputs':{'images':['7',0],'filename_prefix':f'sean_qwen21_shared_costume_weapon_20261002/{condition}_seed{seed}'}}
    }
    for slot,ref in enumerate(remote_refs,1):
        node=str(8+slot)
        graph[node]={'class_type':'LoadImage','inputs':{'image':ref}}
        graph['5']['inputs'][f'images.image_{slot}']=[node,0]
    return graph,text

def submit(graph,job,lease_id):
    (FLOWS/f'{job}.json').write_text(json.dumps(graph,indent=2,ensure_ascii=False)+'\n')
    pid=json.loads(api('/prompt',{'prompt':graph,'client_id':'sean-qwen-shared-costume-20261002'}))['prompt_id']
    start=time.time(); heartbeat=start
    while time.time()-start<2400:
        item=json.loads(api(f'/history/{pid}')).get(pid,{})
        images=[im for node in item.get('outputs',{}).values() for im in node.get('images',[])]
        if images:
            im=images[0]; query=urllib.parse.urlencode({'filename':im['filename'],'subfolder':im.get('subfolder',''),'type':im.get('type','output')})
            local=OUTPUTS/f'{job}.png'; local.write_bytes(api(f'/view?{query}'))
            return {'id':job,'prompt_id':pid,'seconds':round(time.time()-start,2),'output':str(local.relative_to(ROOT)),'comfy_image':im}
        if time.time()-heartbeat>45:
            import subprocess
            subprocess.run(['hive-resource','lease','heartbeat',lease_id,'--ttl','600000'],check=True,capture_output=True)
            heartbeat=time.time()
        time.sleep(3)
    raise TimeoutError(pid)

def main():
    import argparse
    p=argparse.ArgumentParser(); p.add_argument('--lease-id',required=True); p.add_argument('--refinement-only',action='store_true'); p.add_argument('--single-sword-test-only',action='store_true'); a=p.parse_args()
    manifest=json.loads(MANIFEST.read_text()); manifest['status']='active'; MANIFEST.write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+'\n')
    refs={name:upload(INPUTS/f'{name}.png',f'sean_qwen_shared_{name}_20261002.png') for name in ['face1','face2','uniform','weapon']}
    conditions=([('faces_uniform_prompt_single_katana',['face1','face2','uniform']),('faces_uniform_weapon_prompt_single_katana',['face1','face2','uniform','weapon'])] if a.single_sword_test_only else ([('faces_plus_uniform_weapon_single_sheathed',['face1','face2','uniform','weapon'])] if a.refinement_only else [('faces_prompt_only',['face1','face2']),('faces_plus_uniform',['face1','face2','uniform']),('faces_plus_weapon',['face1','face2','weapon']),('faces_plus_uniform_weapon',['face1','face2','uniform','weapon'])]))
    for condition,names in conditions:
        seeds=(6200213,6200214) if a.single_sword_test_only else (6200211,6200212)
        for seed in seeds:
            job=f'{condition}_seed{seed}'; graph,text=make_graph(condition,seed,[refs[n] for n in names])
            result=submit(graph,job,a.lease_id)
            result.update({'kind':'scored_output','condition':condition,'seed':seed,'references':names,'prompt':text})
            manifest['results'].append(result); MANIFEST.write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+'\n')
            print(json.dumps(result,ensure_ascii=False),flush=True)
    manifest['status']='review'; MANIFEST.write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+'\n')

if __name__=='__main__': main()
