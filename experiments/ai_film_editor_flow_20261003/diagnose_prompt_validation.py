#!/usr/bin/env python3
"""Owner: Sean — ask ComfyUI to validate one graph with a forced-invalid output field.

The deliberately invalid SaveVideo prefix guarantees the request is rejected before
queueing. The response captures node_errors that the legacy batch runner truncates.
"""
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parents[1]))
from scripts.h3_batch_runner import build_wf  # noqa: E402

case = json.loads((ROOT / "h3_cases.json").read_text(encoding="utf-8"))[0]
workflow = build_wf(case)
workflow["15"]["inputs"]["filename_prefix"] = None  # known invalid type; no valid output can queue
body = json.dumps({"prompt": workflow, "client_id": "sean-film-validation-probe"}).encode()
request = urllib.request.Request(
    "http://127.0.0.1:8188/prompt",
    data=body,
    headers={"Content-Type": "application/json"},
)
try:
    with urllib.request.urlopen(request, timeout=30) as response:
        result = {"httpStatus": response.status, "response": json.loads(response.read())}
except urllib.error.HTTPError as error:
    result = {"httpStatus": error.code, "response": json.loads(error.read())}

if result["httpStatus"] < 400:
    raise SystemExit("Unexpectedly accepted the deliberately invalid graph; inspect immediately before any follow-up.")

out = ROOT / "comfy_validation_diagnostic.json"
out.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(json.dumps(result, indent=2, ensure_ascii=False))
