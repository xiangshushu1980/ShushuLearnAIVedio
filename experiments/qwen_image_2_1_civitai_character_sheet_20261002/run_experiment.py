#!/usr/bin/env python3
"""[Sean] Qwen-only smoke for the Civitai character-sheet workflow."""
import json
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
API = "http://127.0.0.1:8188"
INPUTS = ROOT / "inputs"
OUTPUTS = ROOT / "outputs"
FLOWS = ROOT / "api_workflows"
MANIFEST = ROOT / "manifest.json"
W, H = 1536, 1024


def api(path, payload=None, data=None, headers=None, timeout=60):
    if payload is not None:
        data = json.dumps(payload).encode()
        headers = {**(headers or {}), "Content-Type": "application/json"}
    with urllib.request.urlopen(urllib.request.Request(API + path, data=data, headers=headers or {}), timeout=timeout) as r:
        return r.read()


def upload(path, remote):
    boundary = "----SeanQwenCharacterSheet20261002"
    body = (
        f"--{boundary}\r\nContent-Disposition: form-data; name=\"image\"; filename=\"{remote}\"\r\nContent-Type: image/png\r\n\r\n".encode()
        + path.read_bytes()
        + f"\r\n--{boundary}\r\nContent-Disposition: form-data; name=\"type\"\r\n\r\ninput\r\n--{boundary}\r\nContent-Disposition: form-data; name=\"overwrite\"\r\n\r\ntrue\r\n--{boundary}--\r\n".encode()
    )
    return json.loads(api("/upload/image", data=body, headers={"Content-Type": f"multipart/form-data; boundary={boundary}"}))['name']


def graph(prompt, seed, prefix, reference=None):
    g = {
        "1": {"class_type": "UNETLoader", "inputs": {"unet_name": "qwen_image_2.1_int8_convrot.safetensors", "weight_dtype": "default"}},
        "2": {"class_type": "CLIPLoader", "inputs": {"clip_name": "qwen3vl_8b_int8_convrot.safetensors", "type": "qwen_image", "device": "default"}},
        "3": {"class_type": "VAELoader", "inputs": {"vae_name": "qwen_image_2.1_vae_bf16.safetensors"}},
        "4": {"class_type": "QwenImage21Cache", "inputs": {"model": ["1", 0], "device": "auto", "dtype": "default"}},
        "5": {"class_type": "TextEncodeQwenImage21", "inputs": {"clip": ["2", 0], "prompt": prompt, "negative_prompt": "", "resolution": 1024, "vae": ["3", 0]}},
        "6": {"class_type": "EmptyLatentImage", "inputs": {"width": W, "height": H, "batch_size": 1}},
        "7": {"class_type": "KSampler", "inputs": {"model": ["4", 0], "positive": ["5", 0], "negative": ["5", 1], "latent_image": ["6", 0], "seed": seed, "steps": 25, "cfg": 1.0, "sampler_name": "euler", "scheduler": "simple", "denoise": 1.0}},
        "8": {"class_type": "VAEDecode", "inputs": {"samples": ["7", 0], "vae": ["3", 0]}},
        "9": {"class_type": "SaveImage", "inputs": {"images": ["8", 0], "filename_prefix": prefix}},
    }
    if reference:
        g["5"]["inputs"]["images.image_1"] = ["10", 0]
        g["10"] = {"class_type": "LoadImage", "inputs": {"image": reference}}
    return g


def submit(g, name, lease):
    (FLOWS / f"{name}.json").write_text(json.dumps(g, indent=2, ensure_ascii=False) + "\n")
    pid = json.loads(api("/prompt", {"prompt": g, "client_id": "sean-qwen-character-sheet-20261002"}))['prompt_id']
    start = time.time()
    beat = start
    while time.time() - start < 1800:
        item = json.loads(api(f"/history/{pid}")).get(pid, {})
        images = [im for n in item.get("outputs", {}).values() for im in n.get("images", [])]
        if images:
            im = images[0]
            query = urllib.parse.urlencode({"filename": im["filename"], "subfolder": im.get("subfolder", ""), "type": im.get("type", "output")})
            local = OUTPUTS / f"{name}.png"
            local.write_bytes(api(f"/view?{query}"))
            return {"id": name, "prompt_id": pid, "seconds": round(time.time() - start, 2), "output": str(local.relative_to(ROOT)), "comfy_image": im}
        if time.time() - beat > 45:
            import subprocess
            subprocess.run(["hive-resource", "lease", "heartbeat", lease, "--ttl", "600000"], check=True, capture_output=True)
            beat = time.time()
        time.sleep(3)
    raise TimeoutError(pid)


def main():
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--lease-id", required=True)
    args = p.parse_args()
    INPUTS.mkdir(exist_ok=True)
    OUTPUTS.mkdir(exist_ok=True)
    FLOWS.mkdir(exist_ok=True)
    manifest = json.loads(MANIFEST.read_text())
    manifest["status"] = "active"
    MANIFEST.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")

    source_prompt = (ROOT / "prompts/source_fullbody.txt").read_text().strip()
    source_result = submit(graph(source_prompt, 6200601, "sean_qwen_civitai_character_sheet_20261002/source_fullbody"), "source_fullbody", args.lease_id)
    source_image = INPUTS / "qwen_generated_fullbody.png"
    source_image.write_bytes((ROOT / source_result["output"]).read_bytes())
    source_result["output"] = str(source_image.relative_to(ROOT))
    manifest["source_image"]["result"] = source_result
    MANIFEST.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")

    reference = upload(source_image, "sean_qwen_character_sheet_source_20261002.png")
    sheet_prompt = (ROOT / "prompts/character_sheet.txt").read_text().strip()
    sheet_result = submit(graph(sheet_prompt, 6200602, "sean_qwen_civitai_character_sheet_20261002/design_sheet", reference), "character_design_sheet", args.lease_id)
    manifest["sheet_generation"]["result"] = sheet_result
    manifest["status"] = "review"
    manifest["results"] = [source_result, sheet_result]
    MANIFEST.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps({"source": source_result, "sheet": sheet_result}, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
