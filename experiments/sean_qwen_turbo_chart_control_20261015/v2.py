#!/usr/bin/env python3
"""Owner: Sean. Geometry-explicit observer prompt; fresh holdouts."""
import run as m
import subprocess,re,sys
seeds=[21001,22003,23003,24001,25013,26003,27011,28001,29009,30011,31013,32003,33013,34019,35023,36007,37003,38011,39019,40009]
prompt=(m.R/'prompts/v2_input.txt').read_text()
m.write(m.R/'v2_plan.json',{'owner':'Sean','purpose':'Post-baseline iteration, explicit percent and gridline encoding, no PE','debug_seeds':[42,1337],'confirmation_seeds':seeds,'threshold':m.P['acceptance'],'prompt':prompt,'data':{'categories':m.P['categories'],'values':m.P['values']}})
def main():
 phase=sys.argv[1];v=subprocess.run(['hive-resource','lease','acquire','--owner',m.P['task_id'],'--resources','gpu:0','--ttl','600000'],capture_output=True,text=True)
 if v.returncode:raise RuntimeError(v.stdout+v.stderr)
 m.lease=re.search(r'[0-9a-f]{8}-(?:[0-9a-f]{4}-){3}[0-9a-f]{12}',v.stdout).group(0)
 try:
  for seed in m.P['debug_seeds'] if phase=='debug' else seeds:
   job=f'v2_{phase}_{seed}';m.execute(job,m.graph(prompt,seed,job))
 finally:print(subprocess.run(['hive-resource','lease','release',m.lease],capture_output=True,text=True).stdout,flush=True)
if __name__=='__main__': main()
