#!/usr/bin/env python3
"""[Sean] Test whether Krea2 can keep two characters in matching uniform/equipment."""

import json
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PROJECT = ROOT.parents[1]
API = "http://127.0.0.1:8188"
OUT, FLOWS = ROOT / "outputs", ROOT / "api_workflows"
FACE1 = PROJECT / "experiments/krea2_quadview_stability_20260928/role_anchors/outputs/sean_eastern_swordswoman_role_front_seed4803001.png"
FACE2 = PROJECT / "experiments/krea2_quadview_stability_20260928/role_anchors/outputs/sean_red_mage_role_front_seed4803002.png"
MANIFEST = ROOT / "manifest.json"


def api(path, payload=None, data=None, headers=None, timeout=30):
    if payload is not None:
        data = json.dumps(payload).encode()
        headers = {**(headers or {}), "Content-Type": "application/json"}
    request = urllib.request.Request(API + path, data=data, headers=headers or {})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return response.read()


def upload(path, remote_name):
    boundary = "----SeanSharedOutfitWeaponBoundary"
    raw = path.read_bytes()
    body = b"".join([
        f"--{boundary}\r\nContent-Disposition: form-data; name=\"image\"; filename=\"{remote_name}\"\r\nContent-Type: image/png\r\n\r\n".encode(), raw,
        f"\r\n--{boundary}\r\nContent-Disposition: form-data; name=\"type\"\r\n\r\ninput\r\n--{boundary}\r\nContent-Disposition: form-data; name=\"overwrite\"\r\n\r\ntrue\r\n--{boundary}--\r\n".encode(),
    ])
    result = json.loads(api("/upload/image", data=body, headers={"Content-Type": f"multipart/form-data; boundary={boundary}"}))
    return result["name"]


def submit(graph, job, lease_id):
    (FLOWS / f"{job}.json").write_text(json.dumps(graph, indent=2, ensure_ascii=False) + "\n")
    prompt_id = json.loads(api("/prompt", {"prompt": graph, "client_id": "sean-krea2-shared-uniform-20261002"}))["prompt_id"]
    start, heartbeat = time.time(), time.time()
    while time.time() - start < 1200:
        item = json.loads(api(f"/history/{prompt_id}")).get(prompt_id, {})
        images = [image for node in item.get("outputs", {}).values() for image in node.get("images", [])]
        if images:
            image = images[0]
            query = urllib.parse.urlencode({"filename": image["filename"], "subfolder": image.get("subfolder", ""), "type": image.get("type", "output")})
            local = OUT / f"{job}.png"
            local.write_bytes(api(f"/view?{query}"))
            return {"id": job, "prompt_id": prompt_id, "seed": graph["sample"]["inputs"]["seed"], "seconds": round(time.time()-start, 2), "output": str(local.relative_to(ROOT)), "comfy_image": image}
        if time.time() - heartbeat > 50:
            import subprocess
            subprocess.run(["hive-resource", "lease", "heartbeat", lease_id, "--ttl", "600000"], check=True, capture_output=True)
            heartbeat = time.time()
        time.sleep(2)
    raise TimeoutError(prompt_id)


def graph(prompt, seed, prefix, refs=None, text_only=False, width=1280, height=832):
    graph = {
        "unet": {"class_type": "UNETLoader", "inputs": {"unet_name": "krea2_turbo_fp8.safetensors", "weight_dtype": "default"}},
        "clip": {"class_type": "CLIPLoader", "inputs": {"clip_name": "qwen3vl_4b_fp8_scaled.safetensors" if text_only else "qwen3vl_4b_bf16.safetensors", "type": "krea2", "device": "default"}},
        "vae": {"class_type": "VAELoader", "inputs": {"vae_name": "qwen_image_vae.safetensors"}},
        "negative": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["clip", 0], "text": ""}},
        "latent": {"class_type": "EmptySD3LatentImage", "inputs": {"width": width, "height": height, "batch_size": 1}},
        "sample": {"class_type": "KSampler", "inputs": {"model": ["model", 0], "positive": ["positive", 0], "negative": ["negative", 0], "latent_image": ["latent", 0], "seed": seed, "control_after_generate": "fixed", "steps": 8, "cfg": 1.0, "sampler_name": "er_sde", "scheduler": "simple", "denoise": 1.0}},
        "decode": {"class_type": "VAEDecode", "inputs": {"samples": ["sample", 0], "vae": ["vae", 0]}},
        "save": {"class_type": "SaveImage", "inputs": {"images": ["decode", 0], "filename_prefix": prefix}},
    }
    if text_only:
        graph["model"] = {"class_type": "LoraLoaderModelOnly", "inputs": {"model": ["unet", 0], "lora_name": "Jibs_Krea_2_Midjourney_Fantasy_Style_V1.safetensors", "strength_model": 0.8}}
        graph["positive"] = {"class_type": "CLIPTextEncode", "inputs": {"clip": ["clip", 0], "text": prompt}}
    else:
        graph["model"] = {"class_type": "Krea2ReferenceLoraLoader", "inputs": {"model": ["unet", 0], "lora_name": "krea2_style_reference.safetensors", "strength_text_fusion": 1.0, "strength_dit_body": 0.0}}
        graph["positive"] = {"class_type": "TextEncodeKrea2Reference", "inputs": {"clip": ["clip", 0], "prompt": prompt, "layout_split": 0.25}}
        for slot, ref in enumerate(refs or [], 1):
            node = f"ref_{slot}"
            graph[node] = {"class_type": "LoadImage", "inputs": {"image": ref["name"]}}
            source = [node, 0]
            if ref.get("crop"):
                c = ref["crop"]
                graph[f"crop_{slot}"] = {"class_type": "ImageCrop", "inputs": {"image": source, **c}}
                source = [f"crop_{slot}", 0]
            graph["positive"]["inputs"][f"image{slot}"] = source
            graph["positive"]["inputs"][f"image{slot}_detail"] = ref.get("detail", "high")
    return graph


def main():
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--lease-id", required=True)
    args = p.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    FLOWS.mkdir(parents=True, exist_ok=True)
    manifest = json.loads(MANIFEST.read_text())
    manifest["status"] = "active"
    MANIFEST.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
    # Clean Krea2-generated single-object references. They are inputs, not scored results.
    helpers = [
        ("uniform_reference", "M1djourneyArtStyle, one complete matching fantasy military field uniform displayed front-facing on an invisible mannequin, no head, no face, no person, ivory high-collar under-tunic, deep navy fitted split coat with restrained red lining, identical red waist sash, dark fitted trousers, black knee boots, one simple lacquered shoulder guard, coherent practical garment set, full outfit visible from collar to boots, centered studio product reference on plain warm gray, painterly high-end fantasy game concept art, clean silhouette, no weapons, no text, no collage", 768, 1024),
        ("weapon_reference", "M1djourneyArtStyle, one complete matching curved katana displayed alone diagonally on a plain warm gray studio background, black lacquer scabbard, dark wrapped grip, restrained bronze crossguard and fittings, full weapon visible tip to pommel, crisp readable silhouette, painterly high-end fantasy game concept art, no person, no hand, no extra objects, no text", 1024, 768),
    ]
    helper_results = []
    for i, (name, text, width, height) in enumerate(helpers):
        result = submit(graph(text, 6200201+i, f"sean_krea2_shared_costume_weapon/{name}", text_only=True, width=width, height=height), name, args.lease_id)
        result.update({"kind": "reference_input", "prompt": text})
        helper_results.append(result)
        manifest["results"].append(result)
        MANIFEST.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
    uploaded = [
        {"name": upload(FACE1, "sean_shared_uniform_face1.png"), "crop": {"x": 256, "y": 0, "width": 512, "height": 512}, "detail": "high"},
        {"name": upload(FACE2, "sean_shared_uniform_face2.png"), "crop": {"x": 256, "y": 0, "width": 512, "height": 512}, "detail": "high"},
    ]
    outfit = {"name": upload(OUT / "uniform_reference.png", "sean_shared_uniform_ref.png"), "detail": "high"}
    weapon = {"name": upload(OUT / "weapon_reference.png", "sean_shared_weapon_ref.png"), "detail": "high"}
    prompt_base = (
        "Create one coherent wide fantasy game concept-art illustration, a single continuous studio scene. Show exactly two adult women, full body head to boots, standing side by side at equal scale with clear space between them. Left woman has the recognizable East Asian face, almond-shaped dark-brown eyes and black high ponytail from reference image 1. Right woman has the recognizable freckled oval face, green-hazel eyes and copper-red braided ponytail from reference image 2. The two faces, hairstyles and identities must remain distinct. Both women wear exactly the same uniform: same ivory high-collar tunic, same deep navy fitted split coat with red lining, same red waist sash, same dark trousers, same black knee boots, same single lacquered shoulder guard; the cut, colors, materials, proportions and details match between them. Each woman carries exactly one identical curved katana with the same black lacquer scabbard, dark wrapped grip and restrained bronze fittings. Put one matching katana in each woman's hand, clearly visible. Simple warm-gray studio backdrop, full silhouettes visible, painterly fantasy game concept art, unified light and perspective. No other people, no extra weapons, no costume variations, no panels, no borders, no labels, no text, no watermark."
    )
    conditions = [
        ("faces_prompt_only", [*uploaded], "Reference image 1 is only the left woman's face identity; reference image 2 is only the right woman's face identity."),
        ("faces_plus_uniform", [*uploaded, outfit], "Reference images 1 and 2 are the left and right face identities. Reference image 3 defines the exact shared uniform; both women wear that same outfit."),
        ("faces_plus_weapon", [*uploaded, weapon], "Reference images 1 and 2 are the left and right face identities. Reference image 3 defines the exact katana; each woman carries an identical copy."),
        ("faces_plus_uniform_weapon", [*uploaded, outfit, weapon], "Reference images 1 and 2 are the left and right face identities. Reference image 3 defines the exact shared uniform worn by both women. Reference image 4 defines the exact katana carried identically by each woman."),
    ]
    for condition, refs, binding in conditions:
        text = binding + " " + prompt_base
        for seed in (6200211, 6200212):
            job = f"{condition}_seed{seed}"
            result = submit(graph(text, seed, f"sean_krea2_shared_costume_weapon/{job}", refs=refs), job, args.lease_id)
            result.update({"kind": "scored_output", "condition": condition, "references": len(refs), "layout_split": 0.25, "prompt": text})
            manifest["results"].append(result)
            MANIFEST.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
            print(json.dumps(result, ensure_ascii=False), flush=True)
    manifest["status"] = "review"
    MANIFEST.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main()
