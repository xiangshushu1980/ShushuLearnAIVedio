#!/usr/bin/env python3
"""Owner: Sean. Roof/body candidate measurements, never repairs generated pixels."""
from pathlib import Path
import numpy as np,json
from PIL import Image
R=Path(__file__).resolve().parent
allm=json.loads((R/'measurements.json').read_text());o={}
for p in sorted((R/'images').glob('glass_building_v1*.png')):
 a=np.array(Image.open(p).convert('RGB')).astype(float);gray=a.mean(2);ticks=[]
 for n in [850,704,558,412,266,120]:
  ids=np.where((gray[n-15:n+16,189:199]<110).sum(1)>=7)[0];ticks.append(float(np.median(ids)+n-15) if len(ids) else None)
 rec={'axis_ticks':ticks,'bars':[],'review_required':True,'method':'Achromatic roof silhouette across central120px at gray210/225/240, >60px occupancy; body lower bound blue mask. Axis measured from generated ticks. Label clusters narrower than60px excluded.'}
 if all(t is not None for t in ticks):
  scale=(ticks[0]-ticks[-1])/100
  for cx,val in zip([350,650,950,1250],[20,70,40,90]):
   tops=[];bottoms=[]
   for t in [210,225,240]:
    ys=np.where((gray[150:880,cx-60:cx+60]<t).sum(1)>60)[0]+150;tops.append(int(ys.min()))
   for t in [8,12,20]:
    mask=(a[:,:,2]-a[:,:,0]>t)&(a[:,:,2]-a[:,:,1]>2)
    ys=np.where(mask[150:880,cx-60:cx+60].sum(1)>60)[0]+150
    if len(ys):bottoms.append(int(ys.max()))
   errors=[abs((ticks[0]-t)/scale-val) for t in tops]
   rec['bars'].append({'expected':val,'top_range':[min(tops),max(tops)],'bottom_range':[min(bottoms),max(bottoms)] if bottoms else None,'max_error':round(max(errors),3),'baseline_error':round(max(abs(b-ticks[0]) for b in bottoms)/scale,3) if bottoms else None})
  rec['geometry_candidate_pass']=all(b['max_error']<=2 and b['baseline_error'] is not None and b['baseline_error']<=2 for b in rec['bars'])
 o[p.stem]=rec
(R/'building_measurements.json').write_text(json.dumps(o,indent=2)+'\n')
for k,v in o.items():print(k,v.get('geometry_candidate_pass'),[b['max_error'] for b in v['bars']])
