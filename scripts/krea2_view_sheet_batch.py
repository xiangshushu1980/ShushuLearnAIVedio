#!/usr/bin/env python3
"""[Sean] Run one fixed QuadView sheet layout against matched role anchors."""

import hashlib
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


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    args = parser.parse_args()
    manifest_path = args.manifest.resolve()
    data = json.loads(manifest_path.read_text())
    output_dir = manifest_path.parent / "outputs"
    output_dir.mkdir(parents=True, exist_ok=True)
    completed = {r["id"] for r in data.get("results", []) if r.get("status") == "success"}
    prompt = data["prompt"]
    params = data["parameters"]

    for case in data["cases"]:
        if case["id"] in completed:
            print(f"SKIP {case['id']}: already successful", flush=True)
            continue
        source = (manifest_path.parent / case["source"]).resolve()
        if not source.is_file():
            raise SystemExit(f"missing approved role anchor: {source}")
        staged = COMFY_INPUT / f"sean_{data['batch_id']}_{case['id']}_front.png"
        if staged.exists():
            raise SystemExit(f"refusing to overwrite staged ComfyUI input: {staged}")
        shutil.copy2(source, staged)
        prefix = f"sean_{data['batch_id']}/{case['id']}/sheet"
        command = [
            str(PYTHON), str(RUNNER), "--reference", str(staged),
            "--mode", "front_reference", "--model-lora", params["lora"],
            "--prompt-override", prompt,
            "--positive-grounding-px", str(params["positive_grounding_px"]),
            "--grounding-px", str(params["grounding_px"]),
            "--width", str(params["width"]), "--height", str(params["height"]),
            "--steps", str(params["steps"]), "--cfg", str(params["cfg"]),
            "--ref-boost", str(params["ref_boost"]),
            "--sampler", params["sampler"], "--scheduler", params["scheduler"],
            "--seed", str(case["seed"]), "--prefix", prefix, "--timeout", "1200",
        ]
        started = time.monotonic()
        proc = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
        if proc.stdout:
            print(proc.stdout.rstrip(), flush=True)
        if proc.stderr:
            print(proc.stderr.rstrip(), flush=True)
        record = {
            "id": case["id"], "seed": case["seed"], "source_sha256": digest(source),
            "status": "failed", "prompt_id": None, "output": None,
            "seconds": round(time.monotonic() - started, 2),
        }
        output_payload = None
        for line in proc.stdout.splitlines():
            try:
                item = json.loads(line)
            except json.JSONDecodeError:
                continue
            if item.get("prompt_id"):
                record["prompt_id"] = item["prompt_id"]
            if item.get("status") in ("success", "error", "timeout"):
                record["status"] = item["status"]
                output_payload = item.get("outputs", {}).get("save", {}).get("images", [])
        if record["status"] == "success" and output_payload:
            image = output_payload[0]
            original = COMFY_OUTPUT / image.get("subfolder", "") / image["filename"]
            saved = output_dir / f"sean_{case['id']}_{data['view_count']}view_seed{case['seed']}.png"
            shutil.copy2(original, saved)
            record["output"] = str(saved.relative_to(manifest_path.parent))
            original.unlink()
        elif record["status"] == "success":
            record["status"] = "failed"
        staged.unlink(missing_ok=True)
        data.setdefault("results", []).append(record)
        data["status"] = "running" if record["status"] == "success" else "failed"
        manifest_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")
        with (manifest_path.parent / "run.log").open("a") as log:
            log.write(json.dumps(record, ensure_ascii=False) + "\n")
        print(json.dumps(record, ensure_ascii=False), flush=True)
        if proc.returncode or record["status"] != "success":
            raise SystemExit(f"generation failed: {case['id']}")

    data["status"] = "awaiting_visual_qc"
    manifest_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")
    print("BATCH_COMPLETE awaiting_visual_qc", flush=True)


if __name__ == "__main__":
    main()
