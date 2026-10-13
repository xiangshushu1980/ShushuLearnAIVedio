#!/usr/bin/env python3
"""[Sean] Text-to-image role portraits using the fixed Krea2 Jibs style LoRA."""

import json
import time
import urllib.request
from pathlib import Path

API = "http://127.0.0.1:8188"
COMFY_OUTPUT = Path("/home/sean/projects/ComfyUI/output")


def api(path, payload=None):
    data = None if payload is None else json.dumps(payload).encode()
    req = urllib.request.Request(
        API + path, data=data,
        headers={"Content-Type": "application/json"} if data is not None else {},
    )
    with urllib.request.urlopen(req, timeout=30) as response:
        return json.loads(response.read())


def make_graph(case, parameters, prefix):
    text = (
        f"{parameters['style_trigger']}, {parameters['style_prompt']} "
        f"{case['character_prompt']} {parameters['composition_prompt']}"
    )
    return {
        "unet": {"class_type": "UNETLoader", "inputs": {
            "unet_name": parameters["unet"], "weight_dtype": "default"}},
        "style_lora": {"class_type": "LoraLoaderModelOnly", "inputs": {
            "model": ["unet", 0], "lora_name": parameters["lora"],
            "strength_model": parameters["lora_strength"]}},
        "clip": {"class_type": "CLIPLoader", "inputs": {
            "clip_name": parameters["clip"], "type": "krea2", "device": "default"}},
        "vae": {"class_type": "VAELoader", "inputs": {
            "vae_name": parameters["vae"]}},
        "text": {"class_type": "CLIPTextEncode", "inputs": {
            "clip": ["clip", 0], "text": text}},
        "latent": {"class_type": "EmptyLatentImage", "inputs": {
            "width": parameters["width"], "height": parameters["height"], "batch_size": 1}},
        "sample": {"class_type": "KSampler", "inputs": {
            "model": ["style_lora", 0], "positive": ["text", 0],
            "negative": ["text", 0], "latent_image": ["latent", 0],
            "seed": case["seed"], "steps": parameters["steps"],
            "cfg": parameters["cfg"], "sampler_name": parameters["sampler"],
            "scheduler": parameters["scheduler"], "denoise": 1.0}},
        "decode": {"class_type": "VAEDecode", "inputs": {
            "samples": ["sample", 0], "vae": ["vae", 0]}},
        "save": {"class_type": "SaveImage", "inputs": {
            "images": ["decode", 0], "filename_prefix": prefix}},
    }


def main():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    args = parser.parse_args()
    path = args.manifest.resolve()
    data = json.loads(path.read_text())
    output_dir = path.parent / "outputs"
    output_dir.mkdir(parents=True, exist_ok=True)
    completed = {r["id"] for r in data.get("results", []) if r.get("status") == "success"}

    for case in data["cases"]:
        if case["id"] in completed:
            print(f"SKIP {case['id']}: already successful", flush=True)
            continue
        prefix = f"sean_{path.parent.name}/{case['id']}/role_front"
        graph = make_graph(case, data["parameters"], prefix)
        started = time.monotonic()
        prompt_id = api("/prompt", {"prompt": graph, "client_id": "sean-role-t2i-jibs"})["prompt_id"]
        print(json.dumps({"id": case["id"], "prompt_id": prompt_id, "status": "submitted"}), flush=True)
        record = {"id": case["id"], "seed": case["seed"], "prompt_id": prompt_id,
                  "status": "running", "seconds": None, "output": None,
                  "character_prompt": case["character_prompt"]}
        while time.monotonic() - started < data["parameters"].get("timeout", 1200):
            history = api("/history/" + prompt_id)
            if prompt_id in history:
                job = history[prompt_id]
                status = job.get("status", {}).get("status_str", "unknown")
                record["status"] = status
                record["seconds"] = round(time.monotonic() - started, 2)
                images = job.get("outputs", {}).get("save", {}).get("images", [])
                if status == "success" and images:
                    image = images[0]
                    original = COMFY_OUTPUT / image.get("subfolder", "") / image["filename"]
                    saved = output_dir / f"sean_{case['id']}_role_front_seed{case['seed']}.png"
                    saved.parent.mkdir(parents=True, exist_ok=True)
                    saved.write_bytes(original.read_bytes())
                    record["output"] = str(saved.relative_to(path.parent))
                break
            time.sleep(3)
        if record["status"] == "running":
            record["status"] = "timeout"
            record["seconds"] = round(time.monotonic() - started, 2)
        data.setdefault("results", []).append(record)
        data["status"] = "running" if record["status"] == "success" else "failed"
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")
        with (path.parent / "run.log").open("a") as log:
            log.write(json.dumps(record, ensure_ascii=False) + "\n")
        print(json.dumps(record, ensure_ascii=False), flush=True)
        if record["status"] != "success":
            raise SystemExit(f"generation failed: {case['id']} ({record['status']})")

    data["status"] = "awaiting_visual_qc"
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")
    print("BATCH_COMPLETE awaiting_visual_qc", flush=True)


if __name__ == "__main__":
    main()
