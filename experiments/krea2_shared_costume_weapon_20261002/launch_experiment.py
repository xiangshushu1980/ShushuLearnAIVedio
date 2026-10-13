#!/usr/bin/env python3
"""[Sean] Lease shared GPU, run the Krea2 experiment, observe and release."""
import json, os, re, runpy, subprocess, sys, threading
from pathlib import Path

ROOT = Path(__file__).resolve().parent
job = "krea2_shared_costume_weapon_20261002"
lease_text = subprocess.check_output(["hive-resource", "lease", "acquire", "--owner", job, "--resources", "gpu:0", "--pid", str(os.getpid()), "--ttl", "600000"], text=True)
match = re.search(r"租约 ([0-9a-f-]{36}) 已授予", lease_text)
if not match:
    raise RuntimeError(f"Could not parse GPU lease ID: {lease_text}")
lease_id = match.group(1)
peak = {"memory_used_mb": 0, "utilization_gpu_pct": 0}
stop = threading.Event()

def sample():
    while not stop.is_set():
        try:
            raw = subprocess.check_output(["nvidia-smi", "--query-gpu=memory.used,utilization.gpu", "--format=csv,noheader,nounits"], text=True, timeout=5).strip().splitlines()[0]
            used, util = [int(x.strip()) for x in raw.split(",")]
            peak["memory_used_mb"] = max(peak["memory_used_mb"], used)
            peak["utilization_gpu_pct"] = max(peak["utilization_gpu_pct"], util)
        except Exception:
            pass
        stop.wait(2)

thread = threading.Thread(target=sample, daemon=True)
thread.start()
try:
    sys.argv = [str(ROOT / "run_experiment.py"), "--lease-id", lease_id]
    runpy.run_path(sys.argv[0], run_name="__main__")
    peak["sampled_during_run"] = True
    subprocess.run(["hive-resource", "observe", "--resource", "gpu:0", "--job", job, "--metrics", json.dumps(peak)], check=True)
finally:
    stop.set()
    thread.join(timeout=6)
    subprocess.run(["hive-resource", "lease", "release", lease_id], check=False)
