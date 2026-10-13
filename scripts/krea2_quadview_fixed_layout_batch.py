#!/usr/bin/env python3
"""[Sean] Generate multiple roles with the fixed wide-face QuadView layout."""

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
    args = ap.parse_args()
    data = json.loads(args.manifest.read_text())
    prompt_path = args.manifest.parent / data["prompt_file"]
    prompt = prompt_path.read_text().split("```text", 1)[1].split("```", 1)[0].strip()
    batch_id = data["batch_id"]
    results = []
    for case in data["cases"]:
        staged = COMFY_INPUT / f"sean_{batch_id}_{case['id']}_front.png"
        shutil.copy2(case["source"], staged)
        cmd = [
            str(PYTHON), str(RUNNER), "--reference", str(staged), "--mode", "front_reference",
            "--model-lora", data["parameters"]["lora"], "--prompt-override", prompt,
            "--positive-grounding-px", "0", "--grounding-px", "768",
            "--width", str(data["parameters"]["width"]), "--height", str(data["parameters"]["height"]),
            "--steps", str(data["parameters"]["steps"]), "--cfg", str(data["parameters"]["cfg"]),
            "--ref-boost", str(data["parameters"]["ref_boost"]),
            "--sampler", data["parameters"]["sampler"], "--scheduler", data["parameters"]["scheduler"],
            "--seed", str(case["seed"]), "--prefix", f"sean_{batch_id}/{case['id']}/wideface",
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
