#!/usr/bin/env python3
"""[Sean] Run fixed three-view Krea2 reference cases from a small manifest."""

import json
import shutil
import subprocess
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COMFY_INPUT = Path("/home/sean/projects/ComfyUI/input")
COMFY_OUTPUT = Path("/home/sean/projects/ComfyUI/output")
PYTHON = Path("/home/sean/projects/ComfyUI/venv/bin/python")
RUNNER = ROOT / "tools/krea2_identity_edit_runner.py"


def main():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    args = parser.parse_args()
    manifest_path = args.manifest.resolve()
    data = json.loads(manifest_path.read_text())
    prompt = data["prompt"]
    batch_id = manifest_path.parent.name
    output_dir = manifest_path.parent / "outputs"
    output_dir.mkdir(parents=True, exist_ok=True)

    completed = {
        item["id"] for item in data.get("results", [])
        if item.get("status") == "success"
    }
    for case in data["cases"]:
        if case["id"] in completed:
            print(f"SKIP {case['id']}: already successful", flush=True)
            continue
        source = Path(case["source"])
        if not source.is_file():
            raise SystemExit(f"missing input anchor: {source}")
        staged = COMFY_INPUT / f"sean_{batch_id}_{case['id']}_front.png"
        shutil.copy2(source, staged)
        prefix = f"sean_{batch_id}/{case['id']}/threeview"
        command = [
            str(PYTHON), str(RUNNER), "--reference", str(staged),
            "--mode", "front_reference", "--model-lora", data["parameters"]["lora"],
            "--prompt-override", prompt,
            "--positive-grounding-px", str(data["parameters"]["positive_grounding_px"]),
            "--grounding-px", str(data["parameters"]["grounding_px"]),
            "--width", str(data["parameters"]["width"]),
            "--height", str(data["parameters"]["height"]),
            "--steps", str(data["parameters"]["steps"]),
            "--cfg", str(data["parameters"]["cfg"]),
            "--ref-boost", str(data["parameters"]["ref_boost"]),
            "--sampler", data["parameters"]["sampler"],
            "--scheduler", data["parameters"]["scheduler"],
            "--seed", str(case["seed"]), "--prefix", prefix, "--timeout", "1200",
        ]
        print(f"RUN {case['id']} seed={case['seed']}", flush=True)
        started = time.monotonic()
        proc = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
        elapsed = round(time.monotonic() - started, 2)
        if proc.stdout:
            print(proc.stdout.rstrip(), flush=True)
        if proc.stderr:
            print(proc.stderr.rstrip(), flush=True)
        record = {"id": case["id"], "seed": case["seed"], "seconds": elapsed,
                  "status": "failed", "prompt_id": None, "output": None}
        for line in reversed(proc.stdout.splitlines()):
            try:
                item = json.loads(line)
            except json.JSONDecodeError:
                continue
            if "prompt_id" in item:
                record["prompt_id"] = item["prompt_id"]
            if item.get("status"):
                record["status"] = item["status"]
                images = item.get("outputs", {}).get("save", {}).get("images", [])
                if images:
                    image = images[0]
                    original = COMFY_OUTPUT / image.get("subfolder", "") / image["filename"]
                    saved = output_dir / f"sean_{case['id']}_threeview_seed{case['seed']}.png"
                    shutil.copy2(original, saved)
                    record["output"] = str(saved.relative_to(manifest_path.parent))
                break
        data["results"].append(record)
        data["status"] = "running" if record["status"] == "success" else "failed"
        manifest_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")
        with (manifest_path.parent / "run.log").open("a") as log:
            log.write(json.dumps(record, ensure_ascii=False) + "\n")
        print(json.dumps(record, ensure_ascii=False), flush=True)
        if proc.returncode or record["status"] != "success":
            raise SystemExit(f"generation failed: {case['id']}")
        completed.add(case["id"])

    data["status"] = "awaiting_visual_qc"
    manifest_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")
    print("BATCH_COMPLETE awaiting_visual_qc", flush=True)


if __name__ == "__main__":
    main()
