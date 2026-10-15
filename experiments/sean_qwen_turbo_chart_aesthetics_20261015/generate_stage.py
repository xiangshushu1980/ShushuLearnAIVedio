#!/usr/bin/env python3
"""Owner: Sean. Lease guarded material comparison, raw images archived unchanged."""
import runner as m
import subprocess,re,sys,json,hashlib

def main():
 m.P=json.loads((m.R/sys.argv[1]).read_text())
 phase=sys.argv[2]; conditions=sys.argv[3:] or list(m.P['prompts'])
 seeds=m.P['debug_seeds'] if phase=='debug' else m.P['confirmation_seeds']
 q=m.get('/queue')
 if q['queue_running'] or q['queue_pending']: raise RuntimeError('Shared queue occupied')
 v=subprocess.run(['hive-resource','lease','acquire','--owner',m.P['task_id'],'--resources','gpu:0','--ttl','600000'],capture_output=True,text=True)
 if v.returncode: raise RuntimeError(v.stdout+v.stderr)
 m.lease=re.search(r'[0-9a-f]{8}-(?:[0-9a-f]{4}-){3}[0-9a-f]{12}',v.stdout).group(0)
 print('lease',m.lease,flush=True)
 try:
  m.beat()
  with (m.R/m.P.get('reference','reference.png')).open('rb') as f:
   r=m.S.post(m.B+'/upload/image',files={'image':('sean_chart_aesthetics_stage_reference.png',f,'image/png')},data={'overwrite':'true'},timeout=30)
  r.raise_for_status();name=r.json()['name']
  for condition in conditions:
   prompt=m.P['prompts'][condition]
   (m.R/'prompts'/f'{condition}_actual.txt').write_text(prompt)
   for seed in seeds:
    job=f'{condition}_{phase}_{seed}';g=m.graph(prompt,seed,job)
    g['12']={'class_type':'LoadImage','inputs':{'image':name}}
    g['4']={'class_type':'TextEncodeQwenImage21','inputs':{'clip':['2',0],'vae':['3',0],'prompt':prompt,'negative_prompt':'','resolution':0,'images.image_1':['12',0]}}
    del g['5'];del g['6']
    g['9']['inputs'].update(positive=['4',0],negative=['4',1],latent_image=['4',2])
    m.execute(job,g)
 finally:
  print(subprocess.run(['hive-resource','lease','release',m.lease],capture_output=True,text=True).stdout,flush=True)
if __name__=='__main__':main()
