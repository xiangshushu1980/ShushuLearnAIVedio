#!/usr/bin/env python3
"""[Sean] Run Krea2 front-anchor/back-view consistency cases serially.

The front image is generated first. The back image receives only that front
image plus the parameterized back-view prompt; no other reference is passed.
This script intentionally does not submit H3 or promote assets to canonical.
"""

import argparse
import json
import shutil
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
COMFY_INPUT = Path("/home/sean/projects/ComfyUI/input")
COMFY_OUTPUT = Path("/home/sean/projects/ComfyUI/output")
RUNNER = ROOT / "tools/krea2_identity_edit_runner.py"
PYTHON = Path("/home/sean/projects/ComfyUI/venv/bin/python")


def run_case(case, batch_id, only=None):
    case_id = case["id"]
    spec = case["spec"]
    front_prefix = f"sean_{batch_id}/{case_id}/front"
    back_prefix = f"sean_{batch_id}/{case_id}/back"
    # ComfyUI SaveImage keeps the parent subfolder and uses the final prefix
    # component as the filename stem; it does not create a `front/` folder.
    front_path = COMFY_OUTPUT / f"sean_{batch_id}" / case_id / "front_00001_.png"
    front_input_path = COMFY_INPUT / f"sean_{batch_id}_{case_id}_front.png"
    commands = []
    if only in (None, "front"):
        commands.append([
            str(PYTHON), str(RUNNER),
            "--mode", "front_reference",
            "--character-spec", spec,
            "--width", "1344", "--height", "1536",
            "--steps", "10", "--cfg", "1", "--ref-boost", "4",
            "--grounding-px", "1024", "--seed", str(case["seed_front"]),
            "--prefix", front_prefix,
            "--timeout", "1200",
        ])
    if only in (None, "back"):
        if not front_path.exists():
            raise SystemExit(f"front anchor missing for {case_id}: {front_path}")
        # LoadImage accepts the ComfyUI input staging area, not an output path.
        shutil.copy2(front_path, front_input_path)
        commands.append([
            str(PYTHON), str(RUNNER),
            "--reference", str(front_input_path),
            "--mode", "back_reference",
            "--character-spec", spec,
            "--width", "1344", "--height", "1536",
            "--steps", "10", "--cfg", "1", "--ref-boost", "4",
            "--grounding-px", "1024", "--seed", str(case["seed_back"]),
            "--prefix", back_prefix,
            "--timeout", "1200",
        ])
    for command in commands:
        print("RUN", " ".join(command), flush=True)
        subprocess.run(command, cwd=ROOT, check=True)
    return {
        "id": case_id,
        "front_raw": str(front_path),
        "front_input_staging": str(front_input_path),
        "back_raw": str(COMFY_OUTPUT / f"sean_{batch_id}" / case_id / "back_00001_.png"),
        "status": "generated",
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--case", action="append")
    parser.add_argument("--only", choices=("front", "back"))
    args = parser.parse_args()
    data = json.loads(args.manifest.read_text())
    selected = [c for c in data["cases"] if not args.case or c["id"] in args.case]
    results = [run_case(case, data["batch_id"], args.only) for case in selected]
    print(json.dumps({"results": results}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
