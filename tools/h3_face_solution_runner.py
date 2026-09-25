#!/usr/bin/env python3
"""Small API runner for the H3 face-solution experiments."""

from __future__ import annotations

import argparse
import json
import shutil
import time
import urllib.request
import urllib.error
from pathlib import Path


API = "http://127.0.0.1:8188"
COMFY_INPUT = Path("/home/sean/projects/ComfyUI/input")


def get_json(path: str):
    with urllib.request.urlopen(API + path, timeout=10) as response:
        return json.load(response)


def post_json(path: str, payload: dict):
    request = urllib.request.Request(
        API + path,
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.load(response)
    except urllib.error.HTTPError as error:
        body = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"ComfyUI HTTP {error.code}: {body}") from error


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--reference", required=True)
    parser.add_argument("--size", type=int, default=512)
    parser.add_argument("--seed", type=int, default=20260920)
    parser.add_argument("--prefix", default="face_solution/contact_sheet")
    parser.add_argument("--timeout", type=int, default=900)
    args = parser.parse_args()

    source = Path(args.reference).resolve()
    staged = COMFY_INPUT / "face_solution_contact_sheet_ref.png"
    shutil.copyfile(source, staged)

    graph = {
        "u": {"class_type": "UNETLoader", "inputs": {
            "unet_name": "minimax_h3_ref2va_pruned_int8_convrot.safetensors",
            "weight_dtype": "default",
        }},
        "lo": {"class_type": "LoraLoaderModelOnly", "inputs": {
            "lora_name": "minimax_h3_five_view_512_s1500.safetensors",
            "strength_model": 1.0,
            "model": ["u", 0],
        }},
        "c": {"class_type": "CLIPLoader", "inputs": {
            "clip_name": "qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors",
            "type": "minimax",
            "device": "default",
        }},
        "v": {"class_type": "VAELoader", "inputs": {
            "vae_name": "minimax_h3_video_vae_fp16.safetensors",
        }},
        "img": {"class_type": "LoadImage", "inputs": {
            "image": staged.name,
        }},
        "cs": {"class_type": "H3ContactSheet", "inputs": {
            "clip": ["c", 0],
            "vae": ["v", 0],
            "prompt": "Generate five coordinated character reference views of the subject in <Picture 1>: front face close-up, front three-quarter view, left profile, right profile, and back view. Preserve the same facial identity, short black hair, ears, facial hair, skin tone, and neutral expression across all views. Use a clean neutral gray studio background and keep the subject centered in every panel.",
            "ref_image": ["img", 0],
            "size": args.size,
        }},
        "g": {"class_type": "BasicGuider", "inputs": {
            "model": ["lo", 0],
            "conditioning": ["cs", 0],
        }},
        "sch": {"class_type": "BasicScheduler", "inputs": {
            "model": ["lo", 0],
            "scheduler": "simple",
            "steps": 28,
            "denoise": 1.0,
        }},
        "ks": {"class_type": "KSamplerSelect", "inputs": {
            "sampler_name": "res_multistep",
        }},
        "n": {"class_type": "RandomNoise", "inputs": {
            "noise_seed": args.seed,
        }},
        "s": {"class_type": "SamplerCustomAdvanced", "inputs": {
            "noise": ["n", 0],
            "guider": ["g", 0],
            "sampler": ["ks", 0],
            "sigmas": ["sch", 0],
            "latent_image": ["cs", 1],
        }},
        "dec": {"class_type": "H3ContactSheetDecode", "inputs": {
            "vae": ["v", 0],
            "samples": ["s", 0],
        }},
        "save_strip": {"class_type": "SaveImage", "inputs": {
            "images": ["dec", 1],
            "filename_prefix": args.prefix + "_strip",
        }},
        "save_views": {"class_type": "SaveImage", "inputs": {
            "images": ["dec", 0],
            "filename_prefix": args.prefix + "_views",
        }},
    }

    queued = post_json("/prompt", {"prompt": graph, "client_id": "h3-face-solution"})
    prompt_id = queued["prompt_id"]
    print(json.dumps({"prompt_id": prompt_id, "size": args.size, "seed": args.seed}))
    started = time.time()
    while time.time() - started < args.timeout:
        time.sleep(5)
        history = get_json("/history/" + prompt_id)
        if prompt_id not in history:
            continue
        record = history[prompt_id]
        status = record.get("status", {})
        result = {
            "prompt_id": prompt_id,
            "status": status.get("status_str"),
            "elapsed_s": round(time.time() - started, 1),
            "outputs": record.get("outputs", {}),
        }
        print(json.dumps(result, ensure_ascii=False))
        return 0 if status.get("status_str") != "error" else 1
    print(json.dumps({"prompt_id": prompt_id, "status": "timeout"}))
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
