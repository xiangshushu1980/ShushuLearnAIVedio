#!/usr/bin/env python3
"""Owner: Sean. Reference-guided Turbo edit, separate from text generation."""
import run as m
import subprocess,re,sys
prompt='只将<image1>的白色背景改为非常浅的暖象牙色。图表的文字、数字、蓝色矩形柱、坐标轴和网格线全部保持原样，精确保留每个位置、尺寸、轮廓和颜色。仅更换背景色，不重新设计图表。'
def main():
 phase=sys.argv[1]
 (m.R/'prompts'/'edit_v2_input.txt').write_text(prompt)
 v=subprocess.run(['hive-resource','lease','acquire','--owner',m.P['task_id'],'--resources','gpu:0','--ttl','600000'],capture_output=True,text=True)
 if v.returncode: raise RuntimeError(v.stdout+v.stderr)
 m.lease=re.search(r'[0-9a-f]{8}-(?:[0-9a-f]{4}-){3}[0-9a-f]{12}',v.stdout).group(0)
 try:
  with (m.R/'reference.png').open('rb') as f:
   r=m.S.post(m.B+'/upload/image',files={'image':('sean_chart_control_reference.png',f,'image/png')},data={'overwrite':'true'},timeout=30)
  r.raise_for_status();name=r.json()['name']
  seeds=m.P['debug_seeds'] if phase=='debug' else [21001,22003,23003,24001,25013,26003,27011,28001,29009,30011,31013,32003,33013,34019,35023,36007,37003,38011,39019,40009]
  for seed in seeds:
   job=f'edit_v2_{phase}_{seed}';g=m.graph(prompt,seed,job)
   g['12']={'class_type':'LoadImage','inputs':{'image':name}}
   g['4']={'class_type':'TextEncodeQwenImage21','inputs':{'clip':['2',0],'vae':['3',0],'prompt':prompt,'negative_prompt':'','resolution':0,'images.image_1':['12',0]}}
   del g['5'];del g['6'];g['9']['inputs'].update({'positive':['4',0],'negative':['4',1],'latent_image':['4',2]})
   m.execute(job,g)
 finally:
  print(subprocess.run(['hive-resource','lease','release',m.lease],capture_output=True,text=True).stdout,flush=True)
if __name__=='__main__':main()
