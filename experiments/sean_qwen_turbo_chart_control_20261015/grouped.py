#!/usr/bin/env python3
"""Owner: Sean. Stepwise extension after single-series edit stability."""
import run as m
import subprocess,re,sys
seeds=[41011,42013,43019,44017,45007,46021,47017,48017,49003,50021,51001,52009,53003,54001,55001,56003,57037,58013,59009,60013]
prompt='只将<image1>的白色背景改为非常浅的暖象牙色。图表的文字、数字、蓝色和橙色矩形柱、图例、坐标轴全部保持原样，精确保留每个位置、尺寸、轮廓和颜色。仅更换背景色，不重新设计图表。'
def main():
 phase=sys.argv[1]
 m.write(m.R/'grouped_plan.json',{'owner':'Sean','task_id':m.P['task_id'],'route':'reference-guided background-only edit','prompt':prompt,'categories':m.P['categories'],'series':{'系列一':[20,70,40,90],'系列二':[50,30,80,60]},'debug_seeds':[42,1337],'confirmation_seeds':seeds,'acceptance':m.P['acceptance'],'gate':'single-series background-only edit complete20/20, maximum error0.14 units before this phase'})
 (m.R/'prompts'/'grouped_input.txt').write_text(prompt)
 v=subprocess.run(['hive-resource','lease','acquire','--owner',m.P['task_id'],'--resources','gpu:0','--ttl','600000'],capture_output=True,text=True)
 if v.returncode:raise RuntimeError(v.stdout+v.stderr)
 m.lease=re.search(r'[0-9a-f]{8}-(?:[0-9a-f]{4}-){3}[0-9a-f]{12}',v.stdout).group(0)
 try:
  with (m.R/'grouped_reference.png').open('rb') as f:r=m.S.post(m.B+'/upload/image',files={'image':('sean_grouped_chart_control_reference.png',f,'image/png')},data={'overwrite':'true'},timeout=30)
  r.raise_for_status();name=r.json()['name']
  for seed in [42,1337] if phase=='debug' else seeds:
   job=f'grouped_{phase}_{seed}';g=m.graph(prompt,seed,job);g['12']={'class_type':'LoadImage','inputs':{'image':name}};g['4']={'class_type':'TextEncodeQwenImage21','inputs':{'clip':['2',0],'vae':['3',0],'prompt':prompt,'negative_prompt':'','resolution':0,'images.image_1':['12',0]}};del g['5'];del g['6'];g['9']['inputs'].update({'positive':['4',0],'negative':['4',1],'latent_image':['4',2]});m.execute(job,g)
 finally:print(subprocess.run(['hive-resource','lease','release',m.lease],capture_output=True,text=True).stdout,flush=True)
if __name__=='__main__':main()
