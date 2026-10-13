#!/usr/bin/env python3
"""[Sean] Generate DynamicCharacterSheet structured-prompt comparison batch."""

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


def make_prompt(case):
    locks = "\n".join(f"- {item}" for item in case["identity_locks"])
    return f"""[TASK: ENTITY_SHEET_GENERATION]
[TEMPLATE: MULTI_ANGLE_ENTITY_SHEET_V1]
[ENTITY_TYPE: {case['entity_type']}]
[ENTITY_ID: {case['id']}]

Convert the subject in Image 1 into one standardized advanced Character Sheet. Image 1 is the sole identity and design reference. Preserve the exact same design, proportions, colors, materials, markings, asymmetries, clothing, equipment and signature details. Do not redesign, beautify, age-shift or simplify the subject.

FIXED LANDSCAPE SHEET FORMAT
Use a clean 3:2 landscape canvas with a warm off-white studio background and clear separation between zones. Organize one coherent sheet with these fixed zones:
1. LEFT METADATA COLUMN: short English name, entity type, core mood and visual signature only.
2. LARGE CENTER HERO VIEW: one dominant full-body or complete-creature three-quarter view.
3. TOP-RIGHT TURNAROUND ROW: neutral FRONT FULL BODY, STRICT SIDE FULL BODY and BACK FULL BODY views at matching scale, with all extremities visible.
4. MID-RIGHT ACTION POSES: three readable poses that express the subject's characteristic function without changing identity or costume.
5. BOTTOM-LEFT SILHOUETTE STUDY: three solid silhouettes preserving the exact outer shape.
6. BOTTOM-CENTER EXPRESSION OR STATE STUDY: one neutral face close-up plus three compact expressions or meaningful creature states.
7. BOTTOM-RIGHT DETAIL STUDY: six close-up crops of the most identity-critical face, hair, materials, armor, markings and accessories.

IDENTITY LOCKS
{locks}
- Keep handedness, asymmetry, markings, costume, hardware and color placement consistent in every zone.
- Use the reference image as the sole identity source; do not invent a second subject.

VISIBLE TEXT
English labels only, short and legible. Do not invent lore paragraphs.

NEGATIVE CONSTRAINTS
No extra character, identity drift, species drift, wardrobe drift, material drift, inconsistent markings, changed proportions, duplicated limbs, merged views, overlapping panels, mirrored front/back details, logo, watermark or unrelated decoration."""


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("source_manifest", type=Path)
    parser.add_argument("batch_id")
    parser.add_argument("--lora-name", default="DynamicCharacterSheet_krea2_v1.safetensors")
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
            raise SystemExit(f"missing preserved anchor: {case_id}")
        staging = COMFY_INPUT / f"sean_{args.batch_id}_{case_id}_front.png"
        shutil.copy2(source_front, staging)
        prefix = f"sean_{args.batch_id}/{case_id}/dynamic"
        command = [
            str(PYTHON), str(RUNNER), "--reference", str(staging), "--mode", "front_reference",
            "--model-lora", args.lora_name, "--prompt-override", make_prompt(case),
            "--positive-grounding-px", "0", "--width", str(args.width), "--height", str(args.height),
            "--steps", str(args.steps), "--cfg", "1", "--sampler", "lcm", "--scheduler", "simple",
            "--ref-boost", str(args.ref_boost),
            "--grounding-px", "768", "--seed", str(case["seed_front"] + 3000),
            "--prefix", prefix, "--timeout", "1200",
        ]
        started = time.monotonic()
        print("RUN", case_id, flush=True)
        subprocess.run(command, cwd=ROOT, check=True)
        result = {"id": case_id, "seconds": round(time.monotonic() - started, 3), "status": "generated"}
        results.append(result)
        print(json.dumps(result, ensure_ascii=False), flush=True)
    print(json.dumps({"results": results}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
