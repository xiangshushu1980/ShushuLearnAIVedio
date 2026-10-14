#!/usr/bin/env python3
"""Owner: Sean. Reference-guided Turbo edit, separate from text generation."""
import run as m
import subprocess,re,sys
prompt='将<image1>的准确柱状图变为精致的现代数据报告风格，保留白底和蓝色矩形柱，改善字体与线条质感，标题下加短蓝色装饰线。严格保留原图的所有文字、类别、数值、坐标轴刻度、顺序、柱数、柱宽、柱顶与基线的位置，不能改变任何数据几何关系，不增加其他文字。'
def main():
 phase=sys.argv[1]
 (m.R/'prompts'/'edit_input.txt').write_text(prompt)
 v=subprocess.run(['hive-resource','lease','acquire','--owner',m.P['task_id'],'--resources','gpu:0','--ttl','600000'],capture_output=True,text=True)
 if v.returncode: raise RuntimeError(v.stdout+v.stderr)
 m.lease=re.search(r'[0-9a-f]{8}-(?:[0-9a-f]{4}-){3}[0-9a-f]{12}',v.stdout).group(0)
 try:
  with (m.R/'reference.png').open('rb') as f:
   r=m.S.post(m.B+'/upload/image',files={'image':('sean_chart_control_reference.png',f,'image/png')},data={'overwrite':'true'},timeout=30)
  r.raise_for_status();name=r.json()['name']
  seeds=m.P['debug_seeds'] if phase=='debug' else m.P['confirmation_seeds']
  for seed in seeds:
   job=f'edit_{phase}_{seed}';g=m.graph(prompt,seed,job)
   g['12']={'class_type':'LoadImage','inputs':{'image':name}}
   g['4']={'class_type':'TextEncodeQwenImage21','inputs':{'clip':['2',0],'vae':['3',0],'prompt':prompt,'negative_prompt':'','resolution':0,'images.image_1':['12',0]}}
   del g['5'];del g['6'];g['9']['inputs'].update({'positive':['4',0],'negative':['4',1],'latent_image':['4',2]})
   m.execute(job,g)
 finally:
  print(subprocess.run(['hive-resource','lease','release',m.lease],capture_output=True,text=True).stdout,flush=True)
if __name__=='__main__':main()
