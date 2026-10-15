"""Owner: Sean. Sequential lease guarded concept/edit batches."""
import runner as m
import subprocess,re,sys,json

def upload(path):
 with path.open('rb') as f:
  r=m.S.post(m.B+'/upload/image',files={'image':('sean_concept_'+path.name,f,'image/png')},data={'overwrite':'true'},timeout=30)
 r.raise_for_status();return r.json()['name']

def main():
 phase=sys.argv[1]; names=sys.argv[2:] or list(m.P['prompts'])
 q=m.get('/queue')
 if q['queue_running'] or q['queue_pending']: raise RuntimeError('Shared queue occupied')
 v=subprocess.run(['hive-resource','lease','acquire','--owner',m.P['task_id'],'--resources','gpu:0','--ttl','600000'],capture_output=True,text=True)
 if v.returncode: raise RuntimeError(v.stdout+v.stderr)
 m.lease=re.search(r'[0-9a-f]{8}-(?:[0-9a-f]{4}-){3}[0-9a-f]{12}',v.stdout).group(0)
 print('lease',m.lease,flush=True)
 try:
  m.beat()
  for name in names:
   if phase=='concept':
    spec={'prompt':m.P['prompts'][name],'images':[]};seeds=m.P['debug_seeds']
   else:
    spec=json.loads((m.R/'conditions.json').read_text())[name]
    seeds=m.P['debug_seeds'] if phase=='debug' else m.P['confirmation_seeds'] if phase=='confirm' else m.P['transfer_seeds']
   inputs=[upload(m.R/f) for f in spec['images']]
   for seed in seeds:
    job=f'{name}_{phase}_{seed}';g=m.graph(spec['prompt'],seed,job)
    (m.R/'prompts'/f'{job}.txt').write_text(spec['prompt'])
    if inputs:
     for i,f in enumerate(inputs):g[str(12+i)]={'class_type':'LoadImage','inputs':{'image':f}}
     g['4']={'class_type':'TextEncodeQwenImage21','inputs':{'clip':['2',0],'vae':['3',0],'prompt':spec['prompt'],'negative_prompt':'','resolution':0,**{f'images.image_{i+1}':[str(12+i),0] for i in range(len(inputs))}}}
     del g['5'];del g['6'];g['9']['inputs'].update(positive=['4',0],negative=['4',1],latent_image=['4',2])
    m.execute(job,g)
 finally:
  print(subprocess.run(['hive-resource','lease','release',m.lease],capture_output=True,text=True).stdout,flush=True)
if __name__=='__main__':main()
