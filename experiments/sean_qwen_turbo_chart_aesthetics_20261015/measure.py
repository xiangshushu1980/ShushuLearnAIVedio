#!/usr/bin/env python3
"""Owner: Sean. Candidate measurements; visual review must confirm real contour, labels and material."""
from pathlib import Path
import json
import numpy as np
from PIL import Image
R=Path(__file__).resolve().parent
out={}
for p in sorted((R/'images').glob('*.png')):
 a=np.array(Image.open(p).convert('RGB')).astype(float);gray=a.mean(2)
 ticks=[]
 for nominal in [850,704,558,412,266,120]:
  rows=(gray[nominal-15:nominal+16,189:199]<110).sum(1);ids=np.where(rows>=7)[0]
  ticks.append(float(np.median(ids)+nominal-15) if len(ids) else None)
 rec={'owner':'Sean','image':str(p.relative_to(R)),'axis_tick_centers_0_to_100':ticks,'visual_review_required':True,'method':'blue chroma mask across central 120px of each nominal bar; threshold sensitivity 8/12/20 B-R, B-G>2. Axis ticks dark pixels x189:199. Bottom excludes cast shadow only after visual confirmation. Range includes threshold uncertainty; no image repair.'}
 bars=[]
 if all(t is not None for t in ticks):
  scale=(ticks[0]-ticks[-1])/100
  for x,val in zip([350,650,950,1250],[20,70,40,90]):
   bounds=[]
   for thr in [8,12,20]:
    mask=(a[:,:,2]-a[:,:,0]>thr)&(a[:,:,2]-a[:,:,1]>2)
    ys=np.where(mask[150:870,x-60:x+60].sum(1)>60)[0]+150
    if len(ys): bounds.append([int(ys.min()),int(ys.max())])
   if len(bounds)!=3:bars.append({'ambiguous':True});continue
   top_lo=min(b[0] for b in bounds);top_hi=max(b[0] for b in bounds)
   value_range=[(ticks[0]-top_hi)/scale,(ticks[0]-top_lo)/scale]
   bars.append({'expected':val,'top_range': [top_lo,top_hi],'bottom_range':[min(b[1] for b in bounds),max(b[1] for b in bounds)],'inferred_value_range':[round(v,3) for v in value_range],'max_error_with_threshold_uncertainty':round(max(abs(v-val) for v in value_range),3)})
  rec.update(bars=bars,axis_tick_max_error_units=round(max(abs(t-(ticks[0]-(ticks[0]-ticks[-1])*i/5)) for i,t in enumerate(ticks))/scale,3))
  rec['geometry_candidate_pass']=len(bars)==4 and all(not b.get('ambiguous') and b['max_error_with_threshold_uncertainty']<=2 and max(abs(bd-ticks[0]) for bd in b['bottom_range'])/scale<=2 for b in bars) and rec['axis_tick_max_error_units']<=2
 out[p.stem]=rec
(R/'measurements.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
for k,v in out.items():print(k,v.get('geometry_candidate_pass'),[b.get('max_error_with_threshold_uncertainty') for b in v.get('bars',[])])
