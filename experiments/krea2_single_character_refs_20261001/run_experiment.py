#!/usr/bin/env python3
"""[Sean] Controlled Krea 2 single-character reference-role experiment."""

import json
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parent
PROJECT = ROOT.parents[1]
API = "http://127.0.0.1:8188"
SOURCE = PROJECT / "experiments/krea2_quadview_stability_20260928/role_anchors/outputs/sean_eastern_swordswoman_role_front_seed4803001.png"
SCENE = PROJECT / "experiments/krea2_multi_reference_20261001/outputs/scene_ref_01.png"
OUT = ROOT / "outputs"
FLOWS = ROOT / "api_workflows"
MANIFEST = ROOT / "manifest.json"


def api(path, payload=None, data=None, headers=None, timeout=30):
    if payload is not None:
        data = json.dumps(payload).encode()
        headers = {**(headers or {}), "Content-Type": "application/json"}
    req = urllib.request.Request(API + path, data=data, headers=headers or {})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            return response.read()
    except urllib.error.HTTPError as exc:
        raise RuntimeError(f"ComfyUI HTTP {exc.code}: {exc.read().decode(errors='replace')}") from exc


def upload(path: Path, name: str) -> str:
    boundary = "----SeanSingleCharacterRefsBoundary"
    raw = path.read_bytes()
    body = b"".join([
        f"--{boundary}\r\nContent-Disposition: form-data; name=\"image\"; filename=\"{name}\"\r\nContent-Type: image/png\r\n\r\n".encode(), raw,
        f"\r\n--{boundary}\r\nContent-Disposition: form-data; name=\"type\"\r\n\r\ninput\r\n--{boundary}\r\nContent-Disposition: form-data; name=\"overwrite\"\r\n\r\ntrue\r\n--{boundary}--\r\n".encode(),
    ])
    result = json.loads(api("/upload/image", data=body, headers={"Content-Type": f"multipart/form-data; boundary={boundary}"}))
    return result["name"]


def prompt(roles: list[str]) -> str:
    scene_slot = roles.index("scene") + 1 if "scene" in roles else None
    place = f"the moonlit courtyard shown in reference image {scene_slot}" if scene_slot else "a moonlit stone courtyard with a ruined archway, worn flagstones and scattered red autumn leaves"
    bindings = [
        f"Reference image {i} is the {role} reference; use it specifically to preserve that feature on this one character."
        for i, role in enumerate(roles, 1)
    ]
    return (
        "Create one coherent square fantasy game concept-art illustration in the exact same painterly rendering style as the reference images. "
        + " ".join(bindings) + " "
        "Show exactly one adult East Asian swordswoman, full body from head to boots, standing naturally in a three-quarter view, face clearly visible. "
        "Preserve her recognizable face: softly tapered oval face, almond-shaped dark-brown eyes, straight brows, small nose, calm confident expression, "
        "black hair in a high ponytail tied with a red silk cord, two cheek-length locks. "
        "She wears the same ivory wrapped tunic, deep navy split riding coat with red lining, lacquered black shoulder guard, red waist sash, dark trousers and black boots. "
        "A single long katana in a black lacquer scabbard hangs at her left hip; preserve its dark grip, restrained bronze fittings and curved silhouette. "
        f"Place her naturally within {place}; the environment surrounds her as one continuous space, with architecture visible behind her. "
        "Keep the face, hair, clothing, armor and katana belonging to this one same character. "
        "One image, no extra people, no duplicate weapons, no inset panels, no reference board, no borders, no labels, no text, no watermark. "
        "Consistent painterly edges, rich but restrained colors, detailed fantasy game illustration, unified night lighting and perspective."
    )


def build_graph(refs, scene_condition, seed, name, layout_split=0.0):
    roles = [r["role"] for r in refs]
    text = prompt(roles)
    graph = {
        "unet": {"class_type": "UNETLoader", "inputs": {"unet_name": "krea2_turbo_fp8.safetensors", "weight_dtype": "default"}},
        "clip": {"class_type": "CLIPLoader", "inputs": {"clip_name": "qwen3vl_4b_bf16.safetensors", "type": "krea2", "device": "default"}},
        "vae": {"class_type": "VAELoader", "inputs": {"vae_name": "qwen_image_vae.safetensors"}},
        "model": {"class_type": "Krea2ReferenceLoraLoader", "inputs": {"model": ["unet", 0], "lora_name": "krea2_style_reference.safetensors", "strength_text_fusion": 1.0, "strength_dit_body": 0.0}},
        "positive": {"class_type": "TextEncodeKrea2Reference", "inputs": {"clip": ["clip", 0], "prompt": text, "layout_split": layout_split}},
        "negative": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["clip", 0], "text": ""}},
        "latent": {"class_type": "EmptySD3LatentImage", "inputs": {"width": 1024, "height": 1024, "batch_size": 1}},
        "sample": {"class_type": "KSampler", "inputs": {"model": ["model", 0], "positive": ["positive", 0], "negative": ["negative", 0], "latent_image": ["latent", 0], "seed": seed, "control_after_generate": "fixed", "steps": 8, "cfg": 1.0, "sampler_name": "er_sde", "scheduler": "simple", "denoise": 1.0}},
        "decode": {"class_type": "VAEDecode", "inputs": {"samples": ["sample", 0], "vae": ["vae", 0]}},
        "save": {"class_type": "SaveImage", "inputs": {"images": ["decode", 0], "filename_prefix": f"sean_krea2_single_refs/{name}"}},
    }
    for slot, ref in enumerate(refs, 1):
        load = f"ref_{slot}"
        graph[load] = {"class_type": "LoadImage", "inputs": {"image": ref["name"]}}
        source = [load, 0]
        if "crop" in ref:
            crop = f"crop_{slot}"
            c = ref["crop"]
            graph[crop] = {"class_type": "ImageCrop", "inputs": {"image": source, **c}}
            source = [crop, 0]
        graph["positive"]["inputs"][f"image{slot}"] = source
        graph["positive"]["inputs"][f"image{slot}_detail"] = ref.get("detail", "high")
    return graph


def run(graph, name, lease_id):
    FLOWS.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)
    (FLOWS / f"{name}.json").write_text(json.dumps(graph, indent=2, ensure_ascii=False) + "\n")
    response = json.loads(api("/prompt", {"prompt": graph, "client_id": "sean-krea2-single-refs-20261001"}))
    pid = response["prompt_id"]
    start, heartbeat = time.time(), time.time()
    while time.time() - start < 1200:
        item = json.loads(api(f"/history/{pid}")).get(pid, {})
        found = [image for node in item.get("outputs", {}).values() for image in node.get("images", [])]
        if found:
            image = found[0]
            query = urllib.parse.urlencode({"filename": image["filename"], "subfolder": image.get("subfolder", ""), "type": image.get("type", "output")})
            local = OUT / f"{name}_01.png"
            local.write_bytes(api(f"/view?{query}"))
            return {"id": name, "prompt_id": pid, "seed": graph["sample"]["inputs"]["seed"], "seconds": round(time.time()-start, 2), "output": str(local.relative_to(ROOT)), "comfy_image": image}
        if time.time() - heartbeat >= 50:
            import subprocess
            subprocess.run(["hive-resource", "lease", "heartbeat", lease_id, "--ttl", "600000"], check=True, capture_output=True)
            heartbeat = time.time()
        time.sleep(2)
    raise TimeoutError(pid)


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--lease-id", required=True)
    parser.add_argument("--conditions", nargs="+", default=None)
    parser.add_argument("--layout-split", type=float, default=0.0)
    args = parser.parse_args()
    source_name = upload(SOURCE, "sean_single_ref_source.png")
    scene_name = upload(SCENE, "sean_single_ref_scene.png")
    # All crops come from the same full-body anchor, keeping their rendering style identical.
    base = {"name": source_name, "detail": "high"}
    refs = {
        "face": {**base, "role": "face", "crop": {"x": 256, "y": 0, "width": 512, "height": 512}},
        "clothing": {**base, "role": "clothing", "crop": {"x": 120, "y": 320, "width": 760, "height": 760}},
        "equipment": {**base, "role": "equipment", "crop": {"x": 500, "y": 420, "width": 480, "height": 820}},
        "scene": {"name": scene_name, "role": "scene", "detail": "normal"},
    }
    cases = [
        ("face_only", ["face"], False),
        ("face_clothing", ["face", "clothing"], False),
        ("face_equipment", ["face", "equipment"], False),
        ("face_scene", ["face", "scene"], True),
        ("all_references", ["face", "clothing", "equipment", "scene"], True),
    ]
    if args.conditions:
        cases = [case for case in cases if case[0] in args.conditions]
        missing = set(args.conditions) - {case[0] for case in cases}
        if missing:
            raise ValueError(f"Unknown conditions: {sorted(missing)}")
    manifest = json.loads(MANIFEST.read_text())
    manifest["status"] = "active"
    MANIFEST.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
    for condition, names, scene_condition in cases:
        for seed in (6200101, 6200102):
            layout_split = args.layout_split
            name = f"{condition}" + (f"_split{layout_split:g}" if layout_split else "") + f"_seed{seed}"
            result = run(build_graph([refs[n] for n in names], scene_condition, seed, name, layout_split), name, args.lease_id)
            result.update({"condition": condition, "references": names, "layout_split": layout_split, "prompt": prompt(names)})
            manifest["results"].append(result)
            MANIFEST.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
            print(json.dumps(result, ensure_ascii=False), flush=True)
    manifest["status"] = "review"
    MANIFEST.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main()
