#!/usr/bin/env python3
"""Owner: Sean. Orthographic yaw45 elevation asin(32/85); equal squares and equal camera depth."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,math
R=Path(__file__).resolve().parent
im=Image.new('RGB',(1536,1024),'white');d=ImageDraw.Draw(im)
fpath='/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc'
f=ImageFont.truetype(fpath,38);small=ImageFont.truetype(fpath,32);title=ImageFont.truetype(fpath,54)
def text(cx,y,s,font):
 box=d.textbbox((0,0),s,font=font);d.text((cx-(box[2]-box[0])/2,y),s,font=font,fill='black')
text(768,28,'测试数据',title)
d.line([(200,200),(200,850),(1430,850)],fill='black',width=3)
for v in range(0,101,20):
 y=850-6.5*v;d.line([(188,y),(200,y)],fill='black',width=3);box=d.textbbox((0,0),str(v),font=small);d.text((174-(box[2]-box[0]),y-23),str(v),font=small,fill='black')
rec={'owner':'Sean','canvas':[1536,1024],'encoding':'height only; not overall silhouette extent','projection':{'type':'orthographic','yaw_degrees':45,'elevation_degrees':math.degrees(math.asin(32/85)),'scale_vertical_pixels_per_value':6.5,'equal_camera_depth_centers':True,'equal_square_footprints':True,'formula':'screenX=(X-Z)/sqrt(2); screenY=sin(elev)*(X+Z)/sqrt(2)-cos(elev)*H; centers obey X+Z=constant','footprint_half_diagonals_pixels':[85,32]},'axis_y0':850,'axis_y100':200,'bars':[]}
for cx,c,v in zip([350,650,950,1250],['甲','乙','丙','丁'],[20,70,40,90]):
 h=6.5*v;base={'front':[cx,850],'right':[cx+85,818],'back':[cx,786],'left':[cx-85,818]};top={k:[p[0],p[1]-h] for k,p in base.items()}
 d.polygon([base['front'],base['left'],top['left'],top['front']],fill='#4379d6',outline='#254b95')
 d.polygon([base['front'],base['right'],top['right'],top['front']],fill='#2350ac',outline='#254b95')
 d.polygon([top['front'],top['left'],top['back'],top['right']],fill='#84b5ff',outline='#254b95')
 text(cx,top['back'][1]-50,str(v),small);text(cx,884,c,f)
 rec['bars'].append({'category':c,'value':v,'base':base,'top':top,'physical_height_in_projected_value_units':v,'note':'Measure any corresponding vertical base/top corner pair. Max silhouette height adds64px footprint term; never use it as height.'})
im.save(R/'spatial_reference.png');(R/'spatial_reference_geometry.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2)+'\n')
