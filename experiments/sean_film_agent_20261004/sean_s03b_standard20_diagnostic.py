#!/usr/bin/env python3
"""Owner: Sean — one frozen-input sampler diagnostic; never edits/selects editor candidates."""
import copy, hashlib, json, pathlib, subprocess, time, urllib.parse, urllib.request

ROOT = pathlib.Path(__file__).resolve().parent
BASE = 'http://127.0.0.1:8188'
KEY = 'sean_split_v82_s03b_1532_standard20'
def api(route, data=None):
    req = urllib.request.Request(BASE + route, data=json.dumps(data).encode() if data is not None else None,
                                headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)
def resource(*args):
    return subprocess.check_output(['hive-resource', *args], text=True)
def write(value):
    (ROOT / (KEY + '_diagnostic.json')).write_text(json.dumps(value, ensure_ascii=False, indent=2))
def queue_empty():
    q = api('/queue')
    if q['queue_running'] or q['queue_pending']:
        raise RuntimeError('Shared queue occupied; no submission.')

p = json.loads((ROOT / 'sean_revision83_project.json').read_text())
c = next(c for c in p['candidates'] if c['id'] == '1532bf29-f888-4ad6-9974-34fd41ac0b16')
g = copy.deepcopy(c['workflow'])
assert g['6']['inputs']['prompt'] == c['input']['shot']['prompt']
del g['18']
g['23']['inputs']['model'] = ['1', 0]
g['7']['inputs']['sampler_name'] = 'res_multistep'
g['8']['inputs']['steps'] = 20
g['11']['inputs']['sigmas'] = ['8', 0]
g['15']['inputs']['filename_prefix'] = 'video/' + KEY + '/clip'
record = {'owner': 'Sean', 'kind': 'diagnostic-not-editor-candidate', 'sourceCandidateId': c['id'],
          'frozenInput': c['input'], 'originalWorkflow': c['workflow'], 'workflow': g,
          'hypothesis': 'PDD8 may constrain body motion; compare native20 without changing prompt/seed/references/duration.',
          'status': 'preflight', 'selectionAllowed': False}
write(record)
queue_empty()
lease = None
started = time.time()
try:
    import os, re
    granted = resource('lease', 'acquire', '--owner', KEY, '--resources', 'gpu:0', '--pid', str(os.getpid()), '--ttl', '600000')
    lease = re.search(r'租约\s+([a-f0-9-]+)\s+已授予', granted).group(1)
    record['leaseId'] = lease
    for index, asset in enumerate(c['input']['images']):
        name = g[str(100 + index)]['inputs']['image']
        query = urllib.parse.urlencode({'filename': name, 'type': 'input'})
        with urllib.request.urlopen(BASE + '/view?' + query, timeout=30) as r:
            assert hashlib.sha256(r.read()).hexdigest() == asset['localHash'], 'Frozen reference mismatch'
    queue_empty()
    submitted = api('/prompt', {'prompt': g, 'client_id': KEY, 'extra_data': {'owner': 'Sean', 'diagnostic': KEY}})
    record.update(status='running', promptId=submitted['prompt_id']); write(record)
    print(json.dumps({'status': 'running', 'promptId': record['promptId']}), flush=True)
    beat = time.time()
    while time.time() - started < 1200:
        if time.time() - beat > 30:
            resource('lease', 'heartbeat', lease, '--ttl', '600000'); beat = time.time()
        h = api('/history/' + record['promptId']).get(record['promptId'])
        if h and h.get('status', {}).get('status_str') == 'error':
            record['history'] = h; raise RuntimeError('Native20 diagnostic failed; see retained history')
        if h and h.get('status', {}).get('completed'):
            out = next(o for node in h['outputs'].values() for o in node.get('images', []) if o['filename'].endswith('.mp4'))
            with urllib.request.urlopen(BASE + '/view?' + urllib.parse.urlencode(out), timeout=30) as r:
                data = r.read()
            (ROOT / (KEY + '.mp4')).write_bytes(data)
            record.update(status='succeeded', history=h, mediaHash=hashlib.sha256(data).hexdigest(), elapsedSec=time.time()-started)
            write(record)
            temp = pathlib.Path('/home/sean/projects/ComfyUI/output') / 'video' / KEY / out['filename']
            assert out['subfolder'] == 'video/' + KEY and pathlib.Path(out['filename']).name == out['filename']
            if temp.exists() and hashlib.sha256(temp.read_bytes()).hexdigest() == record['mediaHash']:
                temp.unlink()
            print(json.dumps({'status': 'succeeded', 'elapsedSec': record['elapsedSec']}), flush=True)
            break
        time.sleep(5)
    else:
        raise RuntimeError('Observation deadline; original task remains tracked, do not resubmit')
except Exception as e:
    record.update(status='failed', error=str(e)); write(record); raise
finally:
    if lease:
        while record.get('promptId'):
            q = api('/queue')
            if not any(item[1] == record['promptId'] for item in q['queue_running'] + q['queue_pending']):
                break
            resource('lease', 'heartbeat', lease, '--ttl', '600000'); time.sleep(10)
        resource('observe', '--resource', 'gpu:0', '--job', KEY, '--metrics', json.dumps({'elapsedSec': time.time()-started, 'result': record['status']}))
        resource('lease', 'release', lease)
