#!/usr/bin/env python3
"""Owner: Sean. Review sheets only; never substitute them for raw outputs."""
from pathlib import Path
from PIL import Image,ImageDraw
import sys
R=Path(__file__).resolve().parent
for condition in sys.argv[1:] or ['glass_v1','metal_v1','paper_v1']:
 fs=sorted((R/'images').glob(condition+'_confirm_*.png'))
 for start in range(0,len(fs),8):
  batch=fs[start:start+8];sheet=Image.new('RGB',(1536,550*((len(batch)+1)//2)),'#dddddd');d=ImageDraw.Draw(sheet)
  for i,p in enumerate(batch):
   im=Image.open(p).convert('RGB');im.thumbnail((768,512));x=i%2*768;y=i//2*550;sheet.paste(im,(x,y+30));d.text((x+12,y+8),p.stem,fill='black')
  sheet.save(R/f'contact_{condition}_{start}.jpg',quality=92)
