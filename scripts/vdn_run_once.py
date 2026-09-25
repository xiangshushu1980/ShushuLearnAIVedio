#!/usr/bin/env python3
import json, sys, time, urllib.request, urllib.error

HOST = 'http://127.0.0.1:8188'
wf = json.load(open(sys.argv[1]))
if len(sys.argv) > 2:
    wf['6']['inputs']['length'] = int(sys.argv[2])
    wf['15']['inputs']['filename_prefix'] = 'video/h3_vdn_ref2va/vdn_r' + sys.argv[2] + '_576sq'
if len(sys.argv) > 3 and sys.argv[3] == 'baseline':
    wf.pop('17', None)
    wf['8']['inputs']['model'] = ['1', 0]
    wf['9']['inputs']['model'] = ['1', 0]
    wf['8']['inputs']['steps'] = 20
    wf['15']['inputs']['filename_prefix'] = 'video/h3_vdn_ref2va/baseline_r' + sys.argv[2] + '_576sq'
req = urllib.request.Request(HOST + '/prompt', data=json.dumps({'prompt': wf, 'client_id': 'vdn-r1'}).encode(), headers={'Content-Type':'application/json'})
t0 = time.time()
try:
    with urllib.request.urlopen(req, timeout=60) as r:
        pid = json.load(r)['prompt_id']
except urllib.error.HTTPError as e:
    print(e.read().decode(), file=sys.stderr)
    raise
print('prompt_id=', pid, flush=True)
while True:
    time.sleep(10)
    with urllib.request.urlopen(HOST + '/history/' + pid, timeout=30) as r:
        h = json.load(r)
    if pid in h:
        item = h[pid]
        status = item.get('status', {})
        print(json.dumps({'prompt_id':pid, 'seconds':round(time.time()-t0), 'status':status, 'outputs':item.get('outputs',{})}, ensure_ascii=False), flush=True)
        break
