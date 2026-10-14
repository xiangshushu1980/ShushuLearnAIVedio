#!/usr/bin/env python3
"""Owner: Sean. Measure eight grouped bars against exact program reference."""
import json,numpy as np
from pathlib import Path
from PIL import Image
R=Path(__file__).resolve().parent;ref=json.load(open(R/'grouped_reference_geometry.json'));expected=[dict(b,category=g['category']) for g in ref['groups'] for b in g['bars']];out={}
for p in sorted((R/'images').glob('grouped*.png')):
 a=np.array(Image.open(p).convert('RGB')).astype(int)
 blue=(a[:,:,2]>a[:,:,0]+35)&(a[:,:,2]>a[:,:,1]+10)&(a[:,:,1]>a[:,:,0]+15)
 orange=(a[:,:,0]>a[:,:,2]+45)&(a[:,:,1]>a[:,:,2]+25)&(a[:,:,0]>a[:,:,1]+35)
 mask=blue|orange;mask[:175]=False;mask[855:]=False
 on=mask.sum(0)>55;spans=[];start=None
 for x,v in enumerate(list(on)+[False]):
  if v and start is None:start=x
  if not v and start is not None:
   if x-start>30:spans.append((start,x-1))
   start=None
 bars=[]
 for l,r in spans:
  rows=mask[:,l:r+1].sum(1)>(r-l+1)*.65;ys=np.where(rows)[0]
  if len(ys):bars.append({'left':l,'right':r,'top':int(ys.min()),'bottom':int(ys.max()),'color':'blue' if blue[:,l:r+1].sum()>orange[:,l:r+1].sum() else 'orange'})
 rec={'owner':'Sean','bars':bars,'n_bars':len(bars),'method':'Colors segmented; baseline/axis manually verified equal to program reference, y100=190,y0=850. No rescaling.'}
 if len(bars)==8:
  vals=[round((850-b['top'])/660*100,3) for b in bars];errs=[round(v-e['value'],3) for v,e in zip(vals,expected)];bottomerr=max(abs(b['bottom']-850)/660*100 for b in bars)
  colors=all(b['color']==('blue' if i%2==0 else 'orange') for i,b in enumerate(bars));rec.update({'values_interleaved':vals,'errors_interleaved':errs,'max_absolute_error_units':max(map(abs,errs)),'max_baseline_error_units':bottomerr,'series_colors_correct':colors,'geometry_pass':max(map(abs,errs))<=2 and bottomerr<=2 and colors})
 out[p.stem]=rec
json.dump(out,open(R/'grouped_measurements.json','w'),ensure_ascii=False,indent=2)
print('Measured',len(out),'geometry passes',sum(v.get('geometry_pass',False) for v in out.values()))
