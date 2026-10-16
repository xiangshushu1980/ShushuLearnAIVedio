#!/usr/bin/env python3
"""[Sean] Same-seed Qwen Image 2.1 cache and TextEncode reference smoke test."""
import json
import os
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
API = "http://127.0.0.1:8188"
LEASE = os.environ["HIVE_LEASE_ID"]
SOURCE = Path(__file__).resolve().parents[1] / "qwen_image_2_1_staged_character_reference_20261002/inputs/assets"
REFS = ["face_identity.png", "uniform_clothing.png", "silver_armor_gear.png", "katana_item.png"]
PROMPT = ("Create one photorealistic full-body character concept image using four reference images in order: "
          "image 1 defines identity and hairstyle; image 2 defines the navy uniform; image 3 defines silver armor; "
          "image 4 defines one sheathed katana. Show one adult East Asian woman standing front-facing, full figure, "
          "plain warm off-white studio background, soft light. Preserve the reference roles and keep the design readable. "
          "No extra people, weapons, text, labels, or invented accessories.")


def api(path, payload=None, data=None, headers=None, timeout=60):
    if payload is not None:
        data = json.dumps(payload).encode()
        headers = {**(headers or {}), "Content-Type": "application/json"}
    with urllib.request.urlopen(urllib.request.Request(API + path, data=data, headers=headers or {}), timeout=timeout) as r:
        return r.read()


def upload(path):
    boundary = "----SeanQwen21CacheTest20261016"
    body = (f"--{boundary}\r\nContent-Disposition: form-data; name=\"image\"; filename=\"{path.name}\"\r\n"
            "Content-Type: image/png\r\n\r\n").encode() + path.read_bytes() + (
            f"\r\n--{boundary}\r\nContent-Disposition: form-data; name=\"type\"\r\n\r\ninput\r\n"
            f"--{boundary}\r\nContent-Disposition: form-data; name=\"overwrite\"\r\n\r\ntrue\r\n--{boundary}--\r\n").encode()
    result = json.loads(api("/upload/image", data=body, headers={"Content-Type": f"multipart/form-data; boundary={boundary}"}))
    return result["name"]


def graph(cache_device, cache_dtype, uploaded):
    g = {
        "1": {"class_type": "UNETLoader", "inputs": {"unet_name": "qwen_image_2.1_turbo_int8_convrot.safetensors", "weight_dtype": "default"}},
        "2": {"class_type": "CLIPLoader", "inputs": {"clip_name": "qwen3vl_8b_int8_convrot.safetensors", "type": "qwen_image", "device": "default"}},
        "3": {"class_type": "VAELoader", "inputs": {"vae_name": "qwen_image_2.1_vae_bf16.safetensors"}},
        "4": {"class_type": "QwenImage21Cache", "inputs": {"model": ["1", 0], "device": cache_device, "dtype": cache_dtype}},
        "5": {"class_type": "TextEncodeQwenImage21", "inputs": {"clip": ["2", 0], "prompt": PROMPT, "negative_prompt": "", "resolution": 1024, "vae": ["3", 0]}},
        "6": {"class_type": "EmptyLatentImage", "inputs": {"width": 1024, "height": 1024, "batch_size": 1}},
        "7": {"class_type": "ModelPreviewOverrideKJ", "inputs": {"model": ["4", 0], "max_resolution": 512, "jpeg_quality": 80, "suppress_default_preview": True, "preview_frames": 1, "preview_fps": 12, "tiny_vae": "taeqi2_1_decoder.pth"}},
        "8": {"class_type": "KSampler", "inputs": {"model": ["7", 0], "positive": ["5", 0], "negative": ["5", 1], "latent_image": ["6", 0], "seed": 421016, "steps": 8, "cfg": 1.0, "sampler_name": "euler", "scheduler": "simple", "denoise": 1.0}},
        "9": {"class_type": "VAEDecode", "inputs": {"samples": ["8", 0], "vae": ["3", 0]}},
        "10": {"class_type": "SaveImage", "inputs": {"images": ["9", 0], "filename_prefix": f"sean_qwen21_cache_textencode_20261016/{cache_device}_{cache_dtype}"}},
    }
    for i, filename in enumerate(uploaded, 1):
        node = str(10 + i)
        g["5"]["inputs"][f"images.image_{i}"] = [node, 0]
        g[node] = {"class_type": "LoadImage", "inputs": {"image": filename}}
    return g


def main():
    uploaded = [upload(SOURCE / f) for f in REFS]
    results = []
    for device, dtype in [("auto", "default"), ("off", "default"), ("auto", "int8")]:
        q = json.loads(api("/queue"))
        if q.get("queue_running") or q.get("queue_pending"):
            raise RuntimeError("Shared ComfyUI queue is no longer empty; aborting submissions")
        name = f"{device}_{dtype}"
        g = graph(device, dtype, uploaded)
        (ROOT / f"workflow_{name}.json").write_text(json.dumps(g, ensure_ascii=False, indent=2) + "\n")
        pid = json.loads(api("/prompt", {"prompt": g, "client_id": "sean-qwen21-cache-textencode-20261016"}))["prompt_id"]
        start = time.time()
        beat = start
        while time.time() - start < 600:
            item = json.loads(api(f"/history/{pid}")).get(pid, {})
            status = item.get("status", {}).get("status_str")
            if status == "error":
                raise RuntimeError(json.dumps(item.get("status"), ensure_ascii=False))
            images = [im for n in item.get("outputs", {}).values() for im in n.get("images", [])]
            if images:
                im = images[0]
                query = urllib.parse.urlencode({"filename": im["filename"], "subfolder": im.get("subfolder", ""), "type": im.get("type", "output")})
                dest = ROOT / f"{name}.png"
                dest.write_bytes(api(f"/view?{query}"))
                result = {"variant": name, "prompt_id": pid, "elapsed_s": round(time.time() - start, 2), "output": dest.name, "seed": 421016, "cache": {"device": device, "dtype": dtype}, "preview_tiny_vae": "taeqi2_1_decoder.pth", "references": REFS, "comfy_image": im}
                results.append(result)
                (ROOT / "results.json").write_text(json.dumps(results, ensure_ascii=False, indent=2) + "\n")
                print(json.dumps(result, ensure_ascii=False), flush=True)
                break
            if time.time() - beat >= 45:
                os.system(f"hive-resource lease heartbeat {LEASE} --ttl 600000 >/dev/null")
                beat = time.time()
            time.sleep(2)
        else:
            raise TimeoutError(pid)
    return results


if __name__ == "__main__":
    main()
