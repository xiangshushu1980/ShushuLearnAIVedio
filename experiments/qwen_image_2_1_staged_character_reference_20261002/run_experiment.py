#!/usr/bin/env python3
"""[Sean] Qwen-only staged character and reference-sheet experiment."""
import json
import os
import shutil
import subprocess
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
API = "http://127.0.0.1:8188"
LEASE = os.environ.get("HIVE_LEASE_ID", "LEASE_ID")
W, H = 1536, 1024
PREFIX = "sean_qwen_staged_character_reference_20261002"
ASSETS = {
    "face_identity": "Create a clean photorealistic studio identity reference portrait of one adult East Asian woman, straight-on head and shoulders, neutral expression, looking at camera. Dark brown eyes, oval face, straight black hair tied in a low ponytail with a center part, natural makeup. Plain warm off-white background, soft even studio light, realistic skin texture. No jewelry, no armor, no hat, no text.",
    "uniform_clothing": "Create a clean photorealistic product reference of one complete dark navy military-inspired uniform laid flat, front view, on a plain warm off-white studio background. Tailored high-collar button-front jacket with shoulder epaulettes, two chest pockets, fitted waist, matching straight trousers, and black knee-high boots arranged neatly below. No person, no mannequin, no armor, no belt, no weapons, no text. Show the whole outfit clearly with soft even studio light.",
    "silver_armor_gear": "Create a clean photorealistic product reference of a matching set of silver steel armor accessories arranged separately on a plain warm off-white studio background: two segmented shoulder guards and two articulated forearm guards. Brushed silver metal, understated practical construction, consistent scale, front-facing product view. No person, no clothing, no weapon, no extra objects, no text.",
    "katana_item": "Create a clean photorealistic product reference of exactly one black sheathed katana with a black-and-white wrapped handle, shown horizontally in full length on a plain warm off-white studio background. Include the complete handle, guard, scabbard, and one simple belt loop attachment. No person, no hands, no second weapon, no stand, no text.",
}
COMPOSE = (
    "Create one photorealistic full-body character concept image using the four supplied reference images with fixed roles: "
    "image 1 defines the woman's face, skin, and hairstyle; image 2 defines the navy uniform and boots; "
    "image 3 defines the silver shoulder and forearm armor; image 4 defines the single black sheathed katana. "
    "Show exactly one adult East Asian woman standing upright, front-facing, full figure from head to boots, hands visible and relaxed. "
    "Preserve her identity and ponytail from image 1. Dress her in the exact uniform from image 2, fit the silver guards from image 3, "
    "and attach exactly one sheathed katana at her waist from image 4. Keep all design details simple and readable. "
    "Plain warm off-white studio background, soft consistent lighting, realistic skin and fabric. No extra people, no extra weapons, no text, no labels."
)
SHEET_PROMPTS = {
    "face_front_back": (
        "Create a clean 3:2 landscape character reference sheet using the supplied character image as the sole design source. "
        "Exactly one design shown in three views: a large close-up of the same woman's face and head at left, cropped around shoulders; "
        "at right, exactly two evenly sized complete full-body views side by side, front view and back view. "
        "The two figures have identical height, body proportions, stance, uniform, silver armor, boots, and the same single sheathed katana attached at the waist. "
        "Preserve face, ponytail, clothing cuts, armor shapes, and weapon design. Plain warm off-white studio background, clear whitespace, same neutral lighting. "
        "No side view, extra views, extra people, text, labels, borders, or invented accessories."
    ),
    "face_front_side_back": (
        "Create a clean 3:2 landscape character reference sheet using the supplied character image as the sole design source. "
        "Exactly one design shown in four views: a large close-up of the same woman's face and head at left, cropped around shoulders; "
        "at right, exactly three evenly spaced complete full-body views in one row: front view, strict side profile, and back view. "
        "The three figures have identical height, body proportions, stance, uniform, silver armor, boots, and the same single sheathed katana attached at the waist. "
        "Preserve face, ponytail, clothing cuts, armor shapes, and weapon design. Plain warm off-white studio background, clear whitespace, same neutral lighting. "
        "No extra views, extra people, text, labels, borders, or invented accessories."
    ),
}


def api(path, payload=None, data=None, headers=None, timeout=60):
    if payload is not None:
        data = json.dumps(payload).encode()
        headers = {**(headers or {}), "Content-Type": "application/json"}
    with urllib.request.urlopen(urllib.request.Request(API + path, data=data, headers=headers or {}), timeout=timeout) as r:
        return r.read()


def upload(path, remote):
    boundary = "----SeanQwenStagedCharacter20261002"
    body = (
        f"--{boundary}\r\nContent-Disposition: form-data; name=\"image\"; filename=\"{remote}\"\r\nContent-Type: image/png\r\n\r\n".encode()
        + path.read_bytes()
        + f"\r\n--{boundary}\r\nContent-Disposition: form-data; name=\"type\"\r\n\r\ninput\r\n--{boundary}\r\nContent-Disposition: form-data; name=\"overwrite\"\r\n\r\ntrue\r\n--{boundary}--\r\n".encode()
    )
    result = json.loads(api("/upload/image", data=body, headers={"Content-Type": f"multipart/form-data; boundary={boundary}"}))
    return result["name"]


def graph(prompt, seed, output_prefix, references=None):
    g = {
        "1": {"class_type": "UNETLoader", "inputs": {"unet_name": "qwen_image_2.1_int8_convrot.safetensors", "weight_dtype": "default"}},
        "2": {"class_type": "CLIPLoader", "inputs": {"clip_name": "qwen3vl_8b_int8_convrot.safetensors", "type": "qwen_image", "device": "default"}},
        "3": {"class_type": "VAELoader", "inputs": {"vae_name": "qwen_image_2.1_vae_bf16.safetensors"}},
        "4": {"class_type": "QwenImage21Cache", "inputs": {"model": ["1", 0], "device": "auto", "dtype": "default"}},
        "5": {"class_type": "TextEncodeQwenImage21", "inputs": {"clip": ["2", 0], "prompt": prompt, "negative_prompt": "", "resolution": 1024, "vae": ["3", 0]}},
        "6": {"class_type": "EmptyLatentImage", "inputs": {"width": W, "height": H, "batch_size": 1}},
        "7": {"class_type": "KSampler", "inputs": {"model": ["4", 0], "positive": ["5", 0], "negative": ["5", 1], "latent_image": ["6", 0], "seed": seed, "steps": 25, "cfg": 1.0, "sampler_name": "euler", "scheduler": "simple", "denoise": 1.0}},
        "8": {"class_type": "VAEDecode", "inputs": {"samples": ["7", 0], "vae": ["3", 0]}},
        "9": {"class_type": "SaveImage", "inputs": {"images": ["8", 0], "filename_prefix": output_prefix}},
    }
    if references:
        for i, filename in enumerate(references, 1):
            node = str(9 + i)
            g["5"]["inputs"][f"images.image_{i}"] = [node, 0]
            g[node] = {"class_type": "LoadImage", "inputs": {"image": filename}}
    return g


def submit(name, prompt, seed, refs=None, category="outputs"):
    (ROOT / "prompts").mkdir(exist_ok=True)
    flowdir = ROOT / "api_workflows"
    flowdir.mkdir(exist_ok=True)
    (ROOT / "prompts" / f"{name}.txt").write_text(prompt + "\n")
    out = ROOT / category
    out.mkdir(parents=True, exist_ok=True)
    g = graph(prompt, seed, f"{PREFIX}/{name}", refs)
    (flowdir / f"{name}.json").write_text(json.dumps(g, ensure_ascii=False, indent=2) + "\n")
    queue = json.loads(api("/queue"))
    if queue.get("queue_running") or queue.get("queue_pending"):
        raise RuntimeError("Shared ComfyUI queue became busy; stopping before submission")
    pid = json.loads(api("/prompt", {"prompt": g, "client_id": "sean-qwen-staged-character-20261002"}))["prompt_id"]
    start = time.time()
    beat = start
    while time.time() - start < 1200:
        item = json.loads(api(f"/history/{pid}")).get(pid, {})
        if item.get("status", {}).get("status_str") == "error":
            raise RuntimeError(json.dumps(item.get("status"), ensure_ascii=False))
        images = [im for n in item.get("outputs", {}).values() for im in n.get("images", [])]
        if images:
            im = images[0]
            query = urllib.parse.urlencode({"filename": im["filename"], "subfolder": im.get("subfolder", ""), "type": im.get("type", "output")})
            path = out / f"{name}.png"
            path.write_bytes(api(f"/view?{query}"))
            result = {"id": name, "prompt_id": pid, "seconds": round(time.time() - start, 2), "output": str(path.relative_to(ROOT)), "seed": seed, "comfy_image": im}
            print(json.dumps(result, ensure_ascii=False), flush=True)
            return result
        if time.time() - beat > 45:
            subprocess.run(["hive-resource", "lease", "heartbeat", LEASE, "--ttl", "600000"], check=True, capture_output=True)
            beat = time.time()
        time.sleep(2)
    raise TimeoutError(pid)


def main():
    (ROOT / "inputs/assets").mkdir(parents=True, exist_ok=True)
    manifest = {"owner": "Sean", "experiment": ROOT.name, "status": "active", "purpose": "Test staged Qwen-only generation: isolated face/item/gear/clothing references -> several full-body character candidates -> two reference-sheet compositions per candidate.", "runtime": {"comfyui": API, "unet": "qwen_image_2.1_int8_convrot.safetensors", "clip": "qwen3vl_8b_int8_convrot.safetensors", "vae": "qwen_image_2.1_vae_bf16.safetensors", "lora": None, "krea2_used": False, "output_size": f"{W}x{H}", "steps": 25, "cfg": 1.0, "sampler": "euler", "scheduler": "simple"}, "design_assets": [], "character_candidates": [], "reference_sheets": []}
    (ROOT / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    remote_refs = {}
    for i, (name, prompt) in enumerate(ASSETS.items()):
        result = submit(name, prompt, 6200701 + i, category="inputs/assets")
        result["role"] = name
        manifest["design_assets"].append(result)
        path = ROOT / result["output"]
        remote_refs[name] = upload(path, f"{PREFIX}_{name}.png")
        (ROOT / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    candidate_sources = []
    for i, seed in enumerate((6200711, 6200712, 6200713), 1):
        name = f"character_candidate_{i:02d}"
        result = submit(name, COMPOSE, seed, list(remote_refs.values()))
        manifest["character_candidates"].append(result)
        candidate_sources.append(upload(ROOT / result["output"], f"{PREFIX}_{name}.png"))
        (ROOT / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    seed = 6200720
    for i, reference in enumerate(candidate_sources, 1):
        for style, prompt in SHEET_PROMPTS.items():
            name = f"candidate_{i:02d}_{style}"
            result = submit(name, prompt, seed, [reference])
            seed += 1
            result["candidate"] = i
            result["layout"] = style
            manifest["reference_sheets"].append(result)
            (ROOT / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    manifest["status"] = "review"
    manifest["deviations"] = ["All four design references and all character/sheet images are prompt-generated or Qwen-edited; no Krea2 or LoRA used.", "Three candidate characters share the same four source references; each candidate produces both requested reference-sheet layouts.", "Peak VRAM was not sampled during generation."]
    (ROOT / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"status": "review", "assets": len(manifest["design_assets"]), "characters": len(manifest["character_candidates"]), "sheets": len(manifest["reference_sheets"])}, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
