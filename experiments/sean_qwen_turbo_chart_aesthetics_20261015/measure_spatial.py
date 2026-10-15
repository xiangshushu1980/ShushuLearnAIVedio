#!/usr/bin/env python3
"""Owner: Sean. Matched front-vertex measurements under registered orthographic projection, visual confirmation mandatory."""
from pathlib import Path
import json
import numpy as np
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parent
out={}
for p in sorted((R/'images').glob('glass_spatial_v1*.png')):
 a=np.array(Image.open(p).convert('RGB')).astype(float);gray=a.mean(2);ticks=[]
 for n in [850,720,590,460,330,200]:
  ys=np.where((gray[n-18:n+19,189:198]<110).sum(1)>=6)[0];ticks.append(float(np.median(ys)+n-18) if len(ys) else None)
 # Front corner is a down-pointing V in screen coordinates, not back/top silhouette.
 def fit(cx,nominal,radius):
  candidates=[];dx=np.arange(-55,56)
  for slope in [.30,32/85,.45]:
   for xshift in [-4,0,4]:
    xs=cx+xshift+dx
    for cy in range(round(nominal)-radius,round(nominal)+radius+1):
     ys=np.rint(cy-slope*np.abs(dx)).astype(int)
     # edge spanning both faces; compare across edge to avoid isolated specular stripe
     delta=np.linalg.norm(a[ys+2,xs]-a[ys-2,xs],axis=1)
     score=float(np.mean(np.minimum(delta,220)))
     candidates.append((score,cy,cx+xshift,slope))
  return sorted(candidates,reverse=True)[:5]
 rec={'axis_ticks_0_to_100':ticks,'bars':[],'method':'Fit front V edge using RGB gradients over111px, slope0.30/0.376/0.45, xshift-4/0/4; top nominal±30px, bottom nominal±20px; candidates require visual correspondence validation. Uses matching front vertices, never full silhouette height.','review_required':True}
 if all(t is not None for t in ticks):
  scale=(ticks[0]-ticks[-1])/100
  for cx,v in zip([350,650,950,1250],[20,70,40,90]):
   top=fit(cx,850-6.5*v,30);bottom=fit(cx,850,20)
   ft=top[0];fb=bottom[0];value=(fb[1]-ft[1])/scale
   rec['bars'].append({'expected':v,'front_top_candidate':list(ft),'front_bottom_candidate':list(fb),'top_alternatives':[list(t) for t in top],'bottom_alternatives':[list(t) for t in bottom],'inferred_value':round(value,3),'error':round(value-v,3)})
  rec['height_candidate_pass']=all(abs(b['error'])<=2 for b in rec['bars'])
 out[p.stem]=rec
(R/'spatial_measurements.json').write_text(json.dumps(out,indent=2)+'\n')
for k,v in out.items():print(k,v.get('height_candidate_pass'),[(b['front_top_candidate'][1],b['front_bottom_candidate'][1],b['error']) for b in v['bars']])
