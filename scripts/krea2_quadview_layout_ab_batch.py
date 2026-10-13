#!/usr/bin/env python3
"""[Sean] Run QuadView face/front/back and upper/front/back layout A/B."""

import argparse
import json
import shutil
import subprocess
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "tools/krea2_identity_edit_runner.py"
PYTHON = Path("/home/sean/projects/ComfyUI/venv/bin/python")
COMFY_INPUT = Path("/home/sean/projects/ComfyUI/input")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("manifest", type=Path)
    ap.add_argument("batch_id")
    args = ap.parse_args()
    data = json.loads(args.manifest.read_text())
    results = []
    for case in data["cases"]:
        staged = COMFY_INPUT / f"sean_{args.batch_id}_{case['id']}_front.png"
        shutil.copy2(case["source"], staged)
        cmd = [
            str(PYTHON), str(RUNNER), "--reference", str(staged), "--mode", "front_reference",
            "--model-lora", "QuadView_krea2_v1.safetensors", "--prompt-override", case["prompt"],
            "--positive-grounding-px", "0", "--grounding-px", "768",
            "--width", "1536", "--height", "1024", "--steps", "10", "--cfg", "1",
            "--ref-boost", "1", "--sampler", "euler", "--scheduler", "simple",
            "--seed", str(case["seed"]), "--prefix", f"sean_{args.batch_id}/{case['id']}/layout",
            "--timeout", "1200",
        ]
        started = time.monotonic()
        print("RUN", case["id"], flush=True)
        subprocess.run(cmd, cwd=ROOT, check=True)
        result = {"id": case["id"], "seconds": round(time.monotonic() - started, 3), "status": "generated"}
        results.append(result)
        print(json.dumps(result, ensure_ascii=False), flush=True)
    print(json.dumps({"results": results}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
