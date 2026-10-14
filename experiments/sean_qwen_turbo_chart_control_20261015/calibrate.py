#!/usr/bin/env python3
"""Owner: Sean. Axis-label row candidates and geometric QC; human verifies tick identities."""
import json
from pathlib import Path
import numpy as np
from PIL import Image
R=Path(__file__).resolve().parent
measure=json.loads((R/'measurements.json').read_text())
def groups(on):
 spans=[];start=None
 for y,v in enumerate(list(on)+[False]):
  if v and start is None:start=y
  if not v and start is not None:
   spans.append((start,y-1));start=None
 return spans
for job,rec in measure.items():
 bars=rec['bars']
 if len(bars)!=4:continue
 a=np.array(Image.open(R/rec['image']).convert('RGB'));baseline=int(np.median([b['bottom'] for b in bars]))+1
 xend=min(b['left'] for b in bars)-100
 gray=a.mean(2);mask=(gray<170);mask[:,xend:]=False;mask[:90]=False;mask[baseline+25:]=False
 mask[:,mask.sum(0)>100]=False
 # join small row gaps within digits
 ys=groups(mask.sum(1)>2);merged=[]
 for l,u in ys:
  if merged and l-merged[-1][1]<=5:merged[-1][1]=u
  else:merged.append([l,u])
 candidates=[(l+u)/2 for l,u in merged if u-l>=10]
 fits=[]
 for top in candidates:
  if baseline-top<450:continue
  expected=[top+(baseline-top)*i/5 for i in range(5)]
  selected=[min(candidates,key=lambda c:abs(c-y)) for y in expected]
  if len(set(selected))!=5:continue
  residual=max(abs(c-y) for c,y in zip(selected,expected))
  fits.append((residual,top,selected))
 rec.update({'baseline_y':baseline,'tick_text_y_candidates':candidates})
 if fits:
  residual,y100,ticks=min(fits); y0=baseline;height=y0-y100
  vals=[round((y0-b['top'])/height*100,2) for b in bars];errors=[round(v-t,2) for v,t in zip(vals,[20,70,40,90])]
  rec.update({'tick_text_y_top_to_bottom':ticks+[y0],'tick_fit_residual_pixels':round(residual,2),'inferred_values':vals,'value_errors':errors,'max_absolute_error':max(map(abs,errors)),'geometry_pass_candidate':max(map(abs,errors))<=2,'axis_calibration_candidate_valid':residual<=10})
(R/'measurements.json').write_text(json.dumps(measure,ensure_ascii=False,indent=2)+'\n')
for j,r in measure.items():print(j,r.get('tick_text_y_candidates'),r.get('inferred_values'))
