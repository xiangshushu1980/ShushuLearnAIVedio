#!/usr/bin/env python3
"""[Sean] Generate every saved QuadView layout for the comparison matrix."""

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


def prompt_from(path: Path) -> str:
    text = path.read_text()
    return text.split("```text", 1)[1].split("```", 1)[0].strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("manifest", type=Path)
    args = ap.parse_args()
    data = json.loads(args.manifest.read_text())
    batch_id = data["batch_id"]
    results = []
    layout_items = list(data["layouts"].items())
    for case_index, case in enumerate(data["cases"]):
        staged = COMFY_INPUT / f"sean_{batch_id}_{case['id']}_front.png"
        shutil.copy2(case["source"], staged)
        for layout_index, (layout_id, size) in enumerate(layout_items):
            prompt = prompt_from(args.manifest.parent / data["prompt_files"][layout_id])
            seed = case["seed_base"] + layout_index
            prefix = f"sean_{batch_id}/{case['id']}/{layout_id}"
            cmd = [
                str(PYTHON), str(RUNNER), "--reference", str(staged), "--mode", "front_reference",
                "--model-lora", data["parameters"]["lora"], "--prompt-override", prompt,
                "--positive-grounding-px", "0", "--grounding-px", "768",
                "--width", str(size["width"]), "--height", str(size["height"]),
                "--steps", str(data["parameters"]["steps"]), "--cfg", str(data["parameters"]["cfg"]),
                "--ref-boost", str(data["parameters"]["ref_boost"]),
                "--sampler", data["parameters"]["sampler"], "--scheduler", data["parameters"]["scheduler"],
                "--seed", str(seed), "--prefix", prefix, "--timeout", "1200",
            ]
            print("RUN", case["id"], layout_id, flush=True)
            started = time.monotonic()
            subprocess.run(cmd, cwd=ROOT, check=True)
            result = {"case": case["id"], "layout": layout_id, "seed": seed, "seconds": round(time.monotonic() - started, 3), "status": "generated"}
            results.append(result)
            print(json.dumps(result, ensure_ascii=False), flush=True)
    print(json.dumps({"results": results}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
