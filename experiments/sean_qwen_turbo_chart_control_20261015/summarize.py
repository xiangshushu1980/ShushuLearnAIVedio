#!/usr/bin/env python3
"""Owner: Sean. Produce per-image complete QC and paired-condition summary."""
import json,math,statistics
from pathlib import Path
R=Path(__file__).resolve().parent;measure=json.load(open(R/'measurements.json'));text={}
for name,prefix in [('text_review_detailed_off.json','confirm_detailed_off'),('text_review_edit.json','edit_confirm'),('text_review_grouped.json','grouped_confirm')]:
 p=R/name
 if p.exists():
  d=json.load(open(p))
  for x in d['images']:text[f"{prefix}_{x['seed']}"]={'pass':x['text_review_pass'],'details':x,'reviewer':'Luna subagent, unblinded original PNG inspection'}
for name in ['text_review_primary.json','text_review_v2.json','text_review_edit_v2.json']:
 for j,x in json.load(open(R/name)).items():text[j]={'pass':all(x[k] for k in ['title_correct','value_labels_correct','categories_correct','category_order_correct','four_bars','no_extra_data_text','tick_text_correct','tick_order_correct']),'details':x,'reviewer':'Codex primary, unblinded review'}
rows=[];groups=['confirm_minimal_off','confirm_minimal_on','confirm_detailed_off','confirm_detailed_on','v2_confirm','edit_confirm','edit_v2_confirm','grouped_confirm'];gm=json.load(open(R/'grouped_measurements.json')) if (R/'grouped_measurements.json').exists() else {}
for group in groups:
 for j,t in text.items():
  if not j.startswith(group+'_'):continue
  if group=='grouped_confirm':
   g=gm[j];gp=g.get('geometry_pass',False);vals=g.get('values_interleaved');maxerr=g.get('max_absolute_error_units');axis=True;rank=True
  else:
   g=measure[j];gp=g.get('geometry_pass_candidate',False);vals=g.get('inferred_values');maxerr=g.get('max_absolute_error');axis=g.get('axis_spacing_pass',True)
   if 'axis_spacing_pass' not in g and g.get('tick_text_y_top_to_bottom'):
    ticks=g['tick_text_y_top_to_bottom'];height=ticks[-1]-ticks[0];axis=max(abs(y-(ticks[0]+height*i/5))/height*100 for i,y in enumerate(ticks))<=2
   rank=bool(vals and vals[0]<vals[2]<vals[1]<vals[3])
  codes=[]
  if not t['pass']:codes.append('text_or_inventory')
  if not gp:codes.append('geometry')
  if not axis:codes.append('axis_spacing')
  if not rank:codes.append('ordering')
  rows.append({'owner':'Sean','job':j,'condition':group,'seed':int(j.rsplit('_',1)[1]),'text_pass':t['pass'],'geometry_pass':gp,'axis_spacing_pass':axis,'ordering_pass':rank,'complete_pass':not codes,'failure_codes':codes,'inferred_values':vals,'max_absolute_error_units':maxerr,'text_evidence':t['details'],'geometry_evidence':'grouped_measurements.json' if group=='grouped_confirm' else 'measurements.json'})
def wilson(k,n):
 z=1.95996398454;p=k/n;den=1+z*z/n;mid=(p+z*z/(2*n))/den;half=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/den;return [round(max(0,mid-half),4),round(min(1,mid+half),4)]
summary={}
for group in groups:
 rs=[x for x in rows if x['condition']==group];n=len(rs)
 if not n:continue
 k=sum(x['complete_pass'] for x in rs);errors=[x['max_absolute_error_units'] for x in rs if x['max_absolute_error_units'] is not None]
 summary[group]={'n':n,'complete_passes':k,'text_passes':sum(x['text_pass'] for x in rs),'geometry_passes':sum(x['geometry_pass'] for x in rs),'ordering_passes':sum(x['ordering_pass'] for x in rs),'axis_spacing_passes':sum(x['axis_spacing_pass'] for x in rs),'wilson95':wilson(k,n),'meets_operational_threshold':n==20 and k>=18,'mean_per_image_max_error_units':round(statistics.mean(errors),3),'worst_max_error_units':max(errors),'pass_seeds':[x['seed'] for x in rs if x['complete_pass']]}
json.dump({'owner':'Sean','rubric':'Frozen 2 unit absolute geometry and tick-spacing tolerance; exact inventory/order, no added/missing data. Human text and numeric pixel measurements. Non-blind, not independent benchmark.','images':rows,'summary':summary},open(R/'qc.json','w'),ensure_ascii=False,indent=2);print(json.dumps(summary,ensure_ascii=False,indent=2))
