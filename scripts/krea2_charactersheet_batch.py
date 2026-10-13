#!/usr/bin/env python3
"""[Sean] Generate the Krea2 CharacterSheet QuadView comparison batch."""

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
PROMPT = "Convert the character in the image to a Character Sheet showing a face close-up, front full body, side full body and back full body views"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("source_manifest", type=Path)
    parser.add_argument("batch_id")
    parser.add_argument("--lora-name", default="QuadView_krea2_v1.safetensors")
    parser.add_argument("--width", type=int, default=1536)
    parser.add_argument("--height", type=int, default=1024)
    parser.add_argument("--steps", type=int, default=10)
    parser.add_argument("--ref-boost", type=float, default=1.0)
    args = parser.parse_args()

    source = json.loads(args.source_manifest.read_text())
    results = []
    for case in source["cases"]:
        case_id = case["id"]
        source_front = COMFY_OUTPUT / "sean_krea2_front_back_consistency_20260926_v2" / case_id / "front_00001_.png"
        if not source_front.exists():
            source_front = COMFY_OUTPUT / "sean_sean_krea2_turnaround_sheet_batch_20260926_v2" / case_id / "turnaround_sheet_00001_.png"
        if not source_front.exists():
            raise SystemExit(f"missing preserved anchor: {case_id}")
        staging = COMFY_INPUT / f"sean_{args.batch_id}_{case_id}_front.png"
        shutil.copy2(source_front, staging)
        prefix = f"sean_{args.batch_id}/{case_id}/quadview"
        command = [
            str(PYTHON), str(RUNNER),
            "--reference", str(staging),
            "--mode", "front_reference",
            "--model-lora", args.lora_name,
            "--prompt-override", PROMPT,
            "--positive-grounding-px", "0",
            "--width", str(args.width), "--height", str(args.height),
            "--steps", str(args.steps), "--cfg", "1", "--ref-boost", str(args.ref_boost),
            "--grounding-px", "768", "--seed", str(case["seed_front"] + 2000),
            "--prefix", prefix, "--timeout", "1200",
        ]
        started = time.monotonic()
        print("RUN", case_id, flush=True)
        subprocess.run(command, cwd=ROOT, check=True)
        elapsed = time.monotonic() - started
        results.append({"id": case_id, "seconds": round(elapsed, 3), "status": "generated"})
        print(json.dumps(results[-1], ensure_ascii=False), flush=True)
    print(json.dumps({"results": results}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
