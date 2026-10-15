"""Owner: Sean. Validate frozen inputs, per-output receipts and content hashes."""
import json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parent
issues=[];runs=[]
for path in sorted((R/'runs').glob('*.json')):
 d=json.loads(path.read_text());runs.append(d['job'])
 for f,sha in d.get('sha256',{}).items():
  if not (R/f).is_file() or hashlib.sha256((R/f).read_bytes()).hexdigest()!=sha:issues.append(f)
p=json.loads((R/'plan.json').read_text())
a=set(p['debug_seeds']);b=set(p['confirmation_seeds']);c=set(p['transfer_seeds'])
assert not(a&b or a&c or b&c)
assert len(b)==20 and len(c)==20
out={'owner':'Sean','runs':runs,'issues':issues,'frozen_sha256':{f:hashlib.sha256((R/f).read_bytes()).hexdigest() for f in ['plan.json','preregister.json']},'note':'No image repair; missing/unjudgeable QC cannot pass.'}
(R/'integrity.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(out,ensure_ascii=False))
assert not issues
