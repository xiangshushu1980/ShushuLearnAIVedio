#!/usr/bin/env python3
"""[Sean] Generate matched QuadView stability comparisons for task T48."""

import argparse
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPERIMENT = ROOT / "experiments/krea2_quadview_stability_20260927"
MANIFEST = EXPERIMENT / "manifest.json"
COMFY_INPUT = Path("/home/sean/projects/ComfyUI/input")
COMFY_OUTPUT = Path("/home/sean/projects/ComfyUI/output")
PYTHON = Path("/home/sean/projects/ComfyUI/venv/bin/python")
RUNNER = ROOT / "tools/krea2_identity_edit_runner.py"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--wait-for-go", action="store_true")
    args = parser.parse_args()

    if args.wait_for_go:
        print(json.dumps({"ready": True, "pid": __import__("os").getpid()}), flush=True)
        if input().strip().lower() != "go":
            raise SystemExit("start gate was not opened")

    manifest = json.loads(MANIFEST.read_text())
    existing = {
        (result["variant"], result["case_id"]): result
        for result in manifest.get("results", [])
        if result.get("status") == "success"
    }
    layouts = manifest["prompt_variants"]
    results = manifest.setdefault("results", [])
    run_log = EXPERIMENT / "run.log"

    for variant, prompt_file in layouts.items():
        prompt = (EXPERIMENT / prompt_file).read_text().split("\n\n", 1)[1].strip()
        for case in manifest["cases"]:
            case_id = case["id"]
            key = (variant, case_id)
            if key in existing:
                existing[key]["prompt_used"] = prompt
                print(f"SKIP {variant} {case_id}: already successful", flush=True)
                continue

            source = Path(case["source"])
            if not source.is_file():
                raise SystemExit(f"missing input anchor: {source}")
            staging = COMFY_INPUT / f"sean_t48_quadview_stability_{case_id}.png"
            shutil.copy2(source, staging)
            prefix = f"sean_t48_quadview_stability_20260927_v1/{variant}/{case_id}/result"
            output = COMFY_OUTPUT / (prefix + "_00001_.png")
            command = [
                str(PYTHON), str(RUNNER),
                "--reference", str(staging),
                "--mode", "front_reference",
                "--model-lora", manifest["lora"],
                "--prompt-override", prompt,
                "--positive-grounding-px", "0",
                "--width", str(manifest["parameters"]["width"]),
                "--height", str(manifest["parameters"]["height"]),
                "--steps", str(manifest["parameters"]["steps"]),
                "--cfg", str(manifest["parameters"]["cfg"]),
                "--sampler", manifest["parameters"]["sampler"],
                "--scheduler", manifest["parameters"]["scheduler"],
                "--ref-boost", str(manifest["parameters"]["ref_boost"]),
                "--grounding-px", str(manifest["parameters"]["grounding_px"]),
                "--seed", str(case["seed"]),
                "--prefix", prefix,
                "--timeout", "1200",
            ]
            print(f"RUN {variant} {case_id} seed={case['seed']}", flush=True)
            started = time.monotonic()
            proc = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
            elapsed = round(time.monotonic() - started, 2)
            if proc.stdout:
                print(proc.stdout.rstrip(), flush=True)
            if proc.stderr:
                print(proc.stderr.rstrip(), file=sys.stderr, flush=True)

            record = {
                "variant": variant,
                "case_id": case_id,
                "seed": case["seed"],
                "prompt_used": prompt,
                "prompt_id": None,
                "output": str(output),
                "seconds": elapsed,
                "status": "failed",
            }
            for line in reversed(proc.stdout.splitlines()):
                try:
                    candidate = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if "prompt_id" in candidate:
                    record["prompt_id"] = candidate["prompt_id"]
                if "status" in candidate:
                    record["status"] = candidate["status"]
                    record["outputs"] = candidate.get("outputs", {})
                    break
            results.append(record)
            manifest["status"] = "running"
            MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
            with run_log.open("a") as stream:
                stream.write(json.dumps(record, ensure_ascii=False) + "\n")
            if proc.returncode != 0 or record["status"] != "success":
                raise SystemExit(f"generation failed: {variant} {case_id}")
            existing[key] = record

    manifest["status"] = "awaiting_qc"
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    print("BATCH_COMPLETE awaiting_qc", flush=True)


if __name__ == "__main__":
    main()
