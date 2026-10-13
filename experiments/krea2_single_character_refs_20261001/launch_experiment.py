#!/usr/bin/env python3
"""[Sean] Acquire the shared GPU, run the experiment, observe peak, and release."""

import json
import re
import subprocess
import sys
import threading
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parent
lease_text = subprocess.check_output([
    "hive-resource", "lease", "acquire", "--owner", "krea2_single_character_refs_20261001",
    "--resources", "gpu:0", "--pid", str(__import__("os").getpid()), "--ttl", "600000",
], text=True)
match = re.search(r"租约 ([0-9a-f-]{36}) 已授予", lease_text)
if not match:
    raise RuntimeError(f"Could not parse GPU lease ID: {lease_text}")
lease_id = match.group(1)
peak = {"memory_used_mb": 0, "utilization_gpu_pct": 0}
stop = threading.Event()


def sample_gpu():
    while not stop.is_set():
        try:
            raw = subprocess.check_output([
                "nvidia-smi", "--query-gpu=memory.used,utilization.gpu", "--format=csv,noheader,nounits"
            ], text=True, timeout=5).strip().splitlines()[0]
            used, util = [int(value.strip()) for value in raw.split(",")]
            peak["memory_used_mb"] = max(peak["memory_used_mb"], used)
            peak["utilization_gpu_pct"] = max(peak["utilization_gpu_pct"], util)
        except Exception:
            pass
        stop.wait(2)


thread = threading.Thread(target=sample_gpu, daemon=True)
thread.start()
try:
    import runpy
    sys.argv = [str(ROOT / "run_experiment.py"), "--lease-id", lease_id, *sys.argv[1:]]
    runpy.run_path(sys.argv[0], run_name="__main__")
    peak["sampled_during_run"] = True
    subprocess.run([
        "hive-resource", "observe", "--resource", "gpu:0", "--job", "krea2_single_character_refs_20261001",
        "--metrics", json.dumps(peak),
    ], check=True)
finally:
    stop.set()
    thread.join(timeout=6)
    subprocess.run(["hive-resource", "lease", "release", lease_id], check=False)
