#!/usr/bin/env python3
"""[Sean] Hold a GPU lease for the exact PID running the validation batch."""
import json
import re
import runpy
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
lease_id = None

try:
    acquired = subprocess.run(
        ["hive-resource", "lease", "acquire", "--owner", "Agent", "--resources", "gpu:0", "--pid", str(__import__("os").getpid()), "--ttl", "600000"],
        check=True, capture_output=True, text=True,
    )
    match = re.search(r"租约 ([0-9a-f-]+) 已授予", acquired.stdout)
    if not match:
        raise RuntimeError("Could not parse lease ID: " + acquired.stdout)
    lease_id = match.group(1)
    __import__("os").environ["HIVE_LEASE_ID"] = lease_id
    runpy.run_path(str(ROOT / "run_validation.py"), run_name="__main__")
finally:
    if lease_id:
        manifest_path = ROOT / "manifest.json"
        if manifest_path.is_file():
            try:
                manifest = json.loads(manifest_path.read_text())
                subprocess.run(
                    ["hive-resource", "observe", "--resource", "gpu:0", "--job", ROOT.name, "--metrics", json.dumps({"runs": len(manifest.get("results", [])), "status": manifest.get("status"), "peakVramMeasured": False})],
                    check=False, capture_output=True, text=True,
                )
            except Exception as exc:
                print(f"resource observation warning: {exc}", file=sys.stderr)
        released = subprocess.run(["hive-resource", "lease", "release", lease_id], check=False, capture_output=True, text=True)
        if released.returncode:
            print(f"lease release warning: {released.stderr or released.stdout}", file=sys.stderr)
