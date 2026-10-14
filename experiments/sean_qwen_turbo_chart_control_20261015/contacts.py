#!/usr/bin/env python3
"""Owner: Sean. Review sheets; original PNGs remain authoritative."""
from PIL import Image,ImageDraw
from pathlib import Path
R=Path(__file__).resolve().parent
for group in ['confirm_minimal_off','confirm_minimal_on','confirm_detailed_off','confirm_detailed_on','edit_debug','edit_confirm','v2_confirm','edit_v2_confirm','grouped_confirm']:
 fs=sorted((R/'images').glob(group+'_*.png'))
 for start in range(0,len(fs),8):
  selected=fs[start:start+8];out=Image.new('RGB',(1536,544*((len(selected)+1)//2)),'white');d=ImageDraw.Draw(out)
  for i,f in enumerate(selected):
   im=Image.open(f);im.thumbnail((768,512));x=i%2*768;y=i//2*544;out.paste(im,(x,y+32));d.text((x+10,y+5),f.stem,fill='black')
  out.save(R/f'contact_{group}_{start}.jpg')
