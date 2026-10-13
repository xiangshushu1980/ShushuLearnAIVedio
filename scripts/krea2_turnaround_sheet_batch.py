#!/usr/bin/env python3
"""[Sean] Generate one front/back turnaround sheet per case, serially."""

import argparse
import json
import shutil
import subprocess
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
COMFY_INPUT = Path("/home/sean/projects/ComfyUI/input")
COMFY_OUTPUT = Path("/home/sean/projects/ComfyUI/output")
RUNNER = ROOT / "tools/krea2_identity_edit_runner.py"
PYTHON = Path("/home/sean/projects/ComfyUI/venv/bin/python")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("source_manifest", type=Path)
    parser.add_argument("output_batch_id")
    parser.add_argument("--width", type=int, default=1536)
    parser.add_argument("--height", type=int, default=1024)
    args = parser.parse_args()

    source = json.loads(args.source_manifest.read_text())
    results = []
    for case in source["cases"]:
        case_id = case["id"]
        source_front = COMFY_OUTPUT / "sean_krea2_front_back_consistency_20260926_v2" / case_id / "front_00001_.png"
        staging = COMFY_INPUT / f"sean_{args.output_batch_id}_{case_id}_front.png"
        if not source_front.exists():
            raise SystemExit(f"missing front anchor: {source_front}")
        shutil.copy2(source_front, staging)
        prefix = f"sean_{args.output_batch_id}/{case_id}/turnaround_sheet"
        output = COMFY_OUTPUT / f"sean_{args.output_batch_id}" / case_id / "turnaround_sheet_00001_.png"
        command = [
            str(PYTHON), str(RUNNER),
            "--reference", str(staging),
            "--mode", "turnaround_sheet",
            "--character-spec", case["spec"],
            "--width", str(args.width), "--height", str(args.height),
            "--steps", "10", "--cfg", "1", "--ref-boost", "4",
            "--grounding-px", "1024", "--seed", str(case["seed_front"] + 1000),
            "--prefix", prefix, "--timeout", "1200",
        ]
        started = time.monotonic()
        print("RUN", case_id, flush=True)
        subprocess.run(command, cwd=ROOT, check=True)
        elapsed = time.monotonic() - started
        results.append({
            "id": case_id,
            "input_staging": str(staging),
            "output": str(output),
            "seconds": round(elapsed, 3),
            "status": "generated",
        })
        print(json.dumps(results[-1], ensure_ascii=False), flush=True)
    print(json.dumps({"results": results}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
