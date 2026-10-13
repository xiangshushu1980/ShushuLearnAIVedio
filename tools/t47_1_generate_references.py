#!/usr/bin/env python3
"""Generate the five independent T47-1 canonical reference images via ComfyUI."""
import json
import shutil
import time
import urllib.request
from pathlib import Path

SERVER = "http://127.0.0.1:8188"
ROOT = Path("experiments/h3_reference_pipeline/t47_1_reference_rebuild_20260926")

OBJECTS = [
    ("character_a_silver_elf_archer", "character_a", 1024, 1024, 4701001),
    ("character_b_red_haired_woman", "character_b", 1024, 1024, 4701002),
    ("observatory_scene", "scene", 1344, 768, 4701003),
    ("brass_compass", "prop", 1024, 1024, 4701004),
    ("cyan_ribbon_spell", "spell", 1024, 1024, 4701005),
]

NEGATIVE = (
    "text, watermark, logo, collage, contact sheet, split screen, duplicate subject, "
    "extra person, extra object, deformed geometry, blurry, low detail"
)


def post_json(path, payload):
    req = urllib.request.Request(
        SERVER + path,
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=60) as response:
        return json.loads(response.read())


def workflow(prompt, negative, width, height, seed, prefix):
    return {
        "1": {"class_type": "UNETLoader", "inputs": {"unet_name": "krea2_turbo_fp8.safetensors", "weight_dtype": "default"}},
        "2": {"class_type": "CLIPLoader", "inputs": {"clip_name": "qwen3vl_4b_fp8_scaled.safetensors", "type": "krea2", "device": "default"}},
        "3": {"class_type": "VAELoader", "inputs": {"vae_name": "qwen_image_vae.safetensors"}},
        "4": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["2", 0], "text": prompt}},
        "5": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["2", 0], "text": negative}},
        "6": {"class_type": "EmptyLatentImage", "inputs": {"width": width, "height": height, "batch_size": 1}},
        "7": {"class_type": "KSampler", "inputs": {"model": ["1", 0], "positive": ["4", 0], "negative": ["5", 0], "latent_image": ["6", 0], "seed": seed, "steps": 8, "cfg": 1.0, "sampler_name": "er_sde", "scheduler": "simple", "denoise": 1.0}},
        "8": {"class_type": "VAEDecode", "inputs": {"samples": ["7", 0], "vae": ["3", 0]}},
        "9": {"class_type": "SaveImage", "inputs": {"images": ["8", 0], "filename_prefix": prefix}},
    }


def wait_for(prompt_id):
    while True:
        with urllib.request.urlopen(f"{SERVER}/history/{prompt_id}", timeout=60) as response:
            history = json.loads(response.read())
        item = history.get(prompt_id)
        if item:
            status = item.get("status", {})
            if status.get("completed"):
                return item
            if status.get("status_str") == "error":
                raise RuntimeError(json.dumps(status, ensure_ascii=False))
        time.sleep(3)


def main():
    for object_id, short_name, width, height, seed in OBJECTS:
        prompt_path = ROOT / "prompts" / f"{short_name}.txt"
        prompt = prompt_path.read_text().split("\n\n", 1)[-1].strip()
        prefix = f"t47_1_reference_rebuild_20260926/raw/{short_name}/{object_id}"
        result = post_json("/prompt", {"prompt": workflow(prompt, NEGATIVE, width, height, seed, prefix)})
        prompt_id = result["prompt_id"]
        print(f"submitted {object_id} {prompt_id}", flush=True)
        item = wait_for(prompt_id)
        files = item.get("outputs", {}).get("9", {}).get("images", [])
        if not files:
            raise RuntimeError(f"No image output for {object_id}: {item}")
        filename = files[0]["filename"]
        src = Path("/home/sean/projects/ComfyUI/output") / files[0].get("subfolder", "") / filename
        raw_dir = ROOT / "raw" / short_name
        package_dir = ROOT / "packages" / short_name / "source"
        raw_dir.mkdir(parents=True, exist_ok=True)
        package_dir.mkdir(parents=True, exist_ok=True)
        raw = raw_dir / f"{object_id}_seed{seed}.png"
        shutil.copy2(src, raw)
        shutil.copy2(src, package_dir / "canonical.png")
        print(f"completed {object_id} -> {raw}", flush=True)


if __name__ == "__main__":
    main()
