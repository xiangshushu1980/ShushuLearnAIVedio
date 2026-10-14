#!/usr/bin/env python3
"""Owner: Sean. Pixel measurement candidates, requiring human tick calibration."""
import json,sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw
R=Path(__file__).resolve().parent
out={}
for path in sorted((R/'images').glob(sys.argv[1] if len(sys.argv)>1 else '*.png')):
 a=np.array(Image.open(path).convert('RGB')).astype(int)
 mask=(a[:,:,2]>a[:,:,0]+35)&(a[:,:,2]>a[:,:,1]+10)&(a[:,:,1]>a[:,:,0]+15)
 mask[:150,:]=False;mask[950:,:]=False
 counts=mask.sum(0);on=counts>55
 spans=[]; start=None
 for x,v in enumerate(list(on)+[False]):
  if v and start is None:start=x
  if not v and start is not None:
   if x-start>30:spans.append((start,x-1))
   start=None
 bars=[]
 for l,r in spans:
  section=mask[:,l:r+1];rows=section.sum(1)>(r-l+1)*.65;ys=np.where(rows)[0]
  if len(ys):bars.append({'left':l,'right':r,'top':int(ys.min()),'bottom':int(ys.max()),'height':int(ys.max()-ys.min()+1)})
 out[path.stem]={'image':str(path.relative_to(R)),'bars':bars,'text_review':'pending','axis_calibration':'pending','geometry_note':'Blue mask candidates only, human must verify bar boundaries and axis tick centers before pass judgment.'}
(R/'measurements.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(out,ensure_ascii=False,indent=2))
