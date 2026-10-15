#!/usr/bin/env python3
"""Owner: Sean. Annotated QC copies, isolated from raw output evidence."""
from pathlib import Path
from PIL import Image,ImageDraw
import json
R=Path(__file__).resolve().parent;m=json.loads((R/'spatial_measurements.json').read_text());items=[(k,v) for k,v in m.items() if '_confirm_' in k]
for start in range(0,len(items),8):
 batch=items[start:start+8];s=Image.new('RGB',(1536,550*((len(batch)+1)//2)),'#dddddd');sd=ImageDraw.Draw(s)
 for i,(k,v) in enumerate(batch):
  im=Image.open(R/'images'/f'{k}.png').convert('RGB');d=ImageDraw.Draw(im)
  for b in v['bars']:
   for field,col in [('front_top_candidate','red'),('front_bottom_candidate','green')]:
    score,y,x,slope=b[field];d.line([(x-45,y-45*slope),(x,y),(x+45,y-45*slope)],fill=col,width=2);d.ellipse((x-3,y-3,x+3,y+3),fill=col)
   d.text((b['front_top_candidate'][2]+6,b['front_top_candidate'][1]+12),str(b['error']),fill='red')
  im.thumbnail((768,512));x=i%2*768;y=i//2*550;s.paste(im,(x,y+30));sd.text((x+8,y+6),k,fill='black')
 s.save(R/f'contact_spatial_qc_{start}.jpg',quality=95)
