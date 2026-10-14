#!/usr/bin/env python3
"""Owner: Sean. Prefer physical tick marks over text bounding boxes for edit QC."""
import json,numpy as np
from PIL import Image
from pathlib import Path
R=Path(__file__).resolve().parent;d=json.load(open(R/'measurements.json'))
for j,x in d.items():
 if not j.startswith('edit') or len(x['bars'])!=4:continue
 a=np.array(Image.open(R/x['image']).convert('RGB'));m=(a.mean(2)<150)&(a.max(2)-a.min(2)<30);m[:90]=False;m[x['baseline_y']+10:]=False
 left=min(b['left'] for b in x['bars']);cols=m.sum(0);ax=int(np.argmax(cols[40:left-20]))+40
 ys=np.where(m[:,ax-11:ax-3].sum(1)>=5)[0];groups=[]
 for y in ys:
  if groups and y-groups[-1][-1]<5:groups[-1].append(int(y))
  else:groups.append([int(y)])
 ticks=[sum(g)/len(g) for g in groups]
 if len(ticks)==6:
  x['calibration_method']='physical left-axis tick marks';x['physical_tick_y']=ticks;y100=ticks[0];y0=ticks[-1]
 else:
  x['calibration_method']='human-confirmed top tick label center + measured baseline (physical tick detector incomplete)';y100=x['tick_text_y_top_to_bottom'][0];y0=x['baseline_y']
 vals=[round((y0-b['top'])/(y0-y100)*100,2) for b in x['bars']];errors=[round(v-t,2) for v,t in zip(vals,[20,70,40,90])]
 x.update({'inferred_values':vals,'value_errors':errors,'max_absolute_error':max(map(abs,errors)),'geometry_pass_candidate':max(map(abs,errors))<=2})
 if len(ticks)==6:
  axiserror=max(abs(y-(y100+(y0-y100)*i/5))/(y0-y100)*100 for i,y in enumerate(ticks));x['axis_linearity_error_units']=round(axiserror,2);x['axis_spacing_pass']=axiserror<=2
json.dump(d,open(R/'measurements.json','w'),ensure_ascii=False,indent=2)
for j,x in d.items():
 if j.startswith('edit'):print(j,x.get('inferred_values'),x.get('geometry_pass_candidate'),x.get('axis_spacing_pass'))
