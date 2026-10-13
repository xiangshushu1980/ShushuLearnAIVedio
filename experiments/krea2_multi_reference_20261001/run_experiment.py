#!/usr/bin/env python3
"""[Sean] Reproducible Krea 2 multi-reference experiment runner."""

import argparse
import json
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parent
PROJECT = ROOT.parents[1]
API = "http://127.0.0.1:8188"
MANIFEST = ROOT / "manifest.json"
OUTPUTS = ROOT / "outputs"
WORKFLOWS = ROOT / "api_workflows"
CHAR1 = PROJECT / "experiments/krea2_quadview_stability_20260928/role_anchors/outputs/sean_eastern_swordswoman_role_front_seed4803001.png"
CHAR2 = PROJECT / "experiments/krea2_quadview_stability_20260928/role_anchors/outputs/sean_red_mage_role_front_seed4803002.png"


def api(path, payload=None, data=None, headers=None, timeout=30):
    if payload is not None:
        data = json.dumps(payload).encode()
        headers = {**(headers or {}), "Content-Type": "application/json"}
    req = urllib.request.Request(API + path, data=data, headers=headers or {})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            return response.read()
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"ComfyUI HTTP {exc.code}: {detail}") from exc


def upload(path: Path, remote_name: str) -> str:
    boundary = "----CodexKrea2MultiRefBoundary"
    raw = path.read_bytes()
    chunks = [
        f"--{boundary}\r\nContent-Disposition: form-data; name=\"image\"; filename=\"{remote_name}\"\r\nContent-Type: image/png\r\n\r\n".encode(),
        raw,
        f"\r\n--{boundary}\r\nContent-Disposition: form-data; name=\"type\"\r\n\r\ninput\r\n--{boundary}\r\nContent-Disposition: form-data; name=\"overwrite\"\r\n\r\ntrue\r\n--{boundary}--\r\n".encode(),
    ]
    result = json.loads(api("/upload/image", data=b"".join(chunks), headers={"Content-Type": f"multipart/form-data; boundary={boundary}"}))
    return result["name"]


def submit(graph: dict, name: str, lease_id: str | None = None) -> dict:
    WORKFLOWS.mkdir(parents=True, exist_ok=True)
    (WORKFLOWS / f"{name}.json").write_text(json.dumps(graph, indent=2, ensure_ascii=False) + "\n")
    response = json.loads(api("/prompt", {"prompt": graph, "client_id": "sean-krea2-multiref-20261001"}))
    prompt_id = response["prompt_id"]
    start = time.time()
    last_heartbeat = start
    while time.time() - start < 1200:
        history = json.loads(api(f"/history/{prompt_id}"))
        item = history.get(prompt_id)
        if item and item.get("outputs"):
            found = []
            for node_out in item["outputs"].values():
                found.extend(node_out.get("images", []))
            if found:
                saved = []
                OUTPUTS.mkdir(parents=True, exist_ok=True)
                for i, image in enumerate(found):
                    query = urllib.parse.urlencode({"filename": image["filename"], "subfolder": image.get("subfolder", ""), "type": image.get("type", "output")})
                    raw = api(f"/view?{query}")
                    local = OUTPUTS / f"{name}_{i + 1:02d}.png"
                    local.write_bytes(raw)
                    saved.append(str(local.relative_to(ROOT)))
                return {"prompt_id": prompt_id, "seconds": round(time.time() - start, 2), "outputs": saved, "comfy_images": found}
        if lease_id and time.time() - last_heartbeat > 50:
            import subprocess
            subprocess.run(["hive-resource", "lease", "heartbeat", lease_id, "--ttl", "600000"], check=True, capture_output=True, text=True)
            last_heartbeat = time.time()
        time.sleep(2)
    raise TimeoutError(f"ComfyUI job {prompt_id} exceeded 1200 seconds")


def base_graph(prompt: str, seed: int, prefix: str, width=1280, height=832, refs=None, layout_split=0.0, text_only=False):
    graph = {
        "unet": {"class_type": "UNETLoader", "inputs": {"unet_name": "krea2_turbo_fp8.safetensors", "weight_dtype": "default"}},
        "clip": {"class_type": "CLIPLoader", "inputs": {"clip_name": "qwen3vl_4b_fp8_scaled.safetensors" if text_only else "qwen3vl_4b_bf16.safetensors", "type": "krea2", "device": "default"}},
        "vae": {"class_type": "VAELoader", "inputs": {"vae_name": "qwen_image_vae.safetensors"}},
        "positive": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["clip", 0], "text": prompt}},
        "negative": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["clip", 0], "text": ""}},
        "latent": {"class_type": "EmptySD3LatentImage", "inputs": {"width": width, "height": height, "batch_size": 1}},
        "sample": {"class_type": "KSampler", "inputs": {"model": ["model", 0], "positive": ["positive", 0], "negative": ["negative", 0], "latent_image": ["latent", 0], "seed": seed, "control_after_generate": "fixed", "steps": 8, "cfg": 1.0, "sampler_name": "er_sde", "scheduler": "simple", "denoise": 1.0}},
        "decode": {"class_type": "VAEDecode", "inputs": {"samples": ["sample", 0], "vae": ["vae", 0]}},
        "save": {"class_type": "SaveImage", "inputs": {"images": ["decode", 0], "filename_prefix": prefix}},
    }
    if text_only:
        graph["model"] = {"class_type": "LoraLoaderModelOnly", "inputs": {"model": ["unet", 0], "lora_name": "Jibs_Krea_2_Midjourney_Fantasy_Style_V1.safetensors", "strength_model": 0.8}}
    else:
        graph["model"] = {"class_type": "Krea2ReferenceLoraLoader", "inputs": {"model": ["unet", 0], "lora_name": "krea2_style_reference.safetensors", "strength_text_fusion": 1.0, "strength_dit_body": 0.0}}
        encoder = {"class_type": "TextEncodeKrea2Reference", "inputs": {"clip": ["clip", 0], "prompt": prompt, "layout_split": layout_split}}
        graph["positive"] = encoder
        slots = refs or {}
        for slot, ref in slots.items():
            node = f"ref_{slot}"
            graph[node] = {"class_type": "LoadImage", "inputs": {"image": ref["name"]}}
            source = [node, 0]
            if ref.get("crop"):
                crop = f"crop_{slot}"
                c = ref["crop"]
                graph[crop] = {"class_type": "ImageCrop", "inputs": {"image": source, "x": c["x"], "y": c["y"], "width": c["width"], "height": c["height"]}}
                source = [crop, 0]
            encoder["inputs"][f"image{slot}"] = source
            encoder["inputs"][f"image{slot}_detail"] = ref.get("detail", "high")
    return graph


def make_reference_images(lease_id):
    cases = [
        ("scene_ref", "M1djourneyArtStyle, a wide empty moonlit fantasy courtyard beside a ruined stone bridge, old weathered pale-gray masonry, worn flagstone path leading toward a distant arched gate, a few red autumn leaves, soft cool-blue night light with a small warm lantern glow, painterly high-end fantasy game concept art, no people, no characters, no weapons, no text, no collage, cinematic 3:2 environment establishing view", 1280, 832),
        ("prop_ref", "M1djourneyArtStyle, a single complete upright wizard staff displayed alone against a clean warm-gray studio background, long dark carved ash-wood shaft with restrained bronze fittings, ornate forked bronze crown holding one luminous cobalt-blue glass orb, full object visible from tip to base, centered product reference, crisp readable silhouette, painterly high-end fantasy game concept art, no person, no hand, no extra objects, no text", 768, 1024),
    ]
    results = []
    for name, prompt, width, height in cases:
        graph = base_graph(prompt, 6100000 + len(results), f"sean_krea2_multiref_inputs/{name}", width, height, text_only=True)
        result = submit(graph, name, lease_id)
        result.update({"id": name, "prompt": prompt})
        results.append(result)
    return results


def main_prompt(use_scene: bool, use_prop: bool, dual_faces: bool) -> str:
    person2 = (
        "the woman from character2" if dual_faces else
        "a second adult woman battle mage with warm freckled skin, green-hazel eyes, copper-red braided ponytail, thin temple braids and loose jaw-length curls"
    )
    scene = "the moonlit stone courtyard shown in image3" if use_scene else "an empty moonlit stone courtyard with a ruined bridge and distant arched gate"
    staff = "the staff design shown in image4" if use_prop else "a long carved ash-wood staff topped with one luminous cobalt-blue glass orb and restrained bronze fittings"
    return (
        "Make one coherent full-color fantasy game illustration, a single wide scene, not a reference board. "
        "Show exactly two adult women together, full body from head to boots, at equal scale, standing side by side with clear space between them. "
        "On the left is the woman swordswoman from character1: preserve her East Asian face, almond-shaped dark-brown eyes, straight brows, black high ponytail tied with a red silk cord and cheek-length locks. "
        "She wears an ivory wrapped tunic, deep-navy split riding coat with red lining, lacquered black shoulder guard, red sash, dark trousers and black boots; a long katana in a black lacquer scabbard hangs at her left hip. "
        f"On the right is {person2}: preserve her oval freckled face, green-hazel eyes, copper-red braided ponytail and jaw-length curls. "
        "She wears an ivory high-collar blouse, burgundy velvet waistcoat, long asymmetrical wine-red coat, charcoal trousers and dark knee boots; she carries " + staff + ". "
        "Keep the two women unmistakably different: black hair and navy-red samurai outfit on the left; copper hair and burgundy mage outfit on the right. "
        f"Place both characters naturally inside {scene}; keep the architecture behind them and visible around their silhouettes. "
        "Eye-level medium-wide camera, natural relaxed stance, faces readable, no overlapping bodies, no duplicate people, no extra panels, no borders, no labels, no text, no watermark. "
        "Detailed painterly fantasy game concept art, coherent lighting and perspective across characters and environment."
    )


def update_manifest(additions):
    manifest = json.loads(MANIFEST.read_text())
    manifest["results"].extend(additions)
    manifest["status"] = "active"
    MANIFEST.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--lease-id", required=True)
    parser.add_argument("--stage", choices=("all", "inputs", "composites"), default="all")
    args = parser.parse_args()
    for path in (CHAR1, CHAR2):
        if not path.exists():
            raise FileNotFoundError(path)
    manifest = json.loads(MANIFEST.read_text())
    manifest["status"] = "active"
    MANIFEST.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")

    if args.stage in ("all", "inputs"):
        generated = make_reference_images(args.lease_id)
        update_manifest(generated)
        if args.stage == "inputs":
            print(f"Generated reference inputs: {OUTPUTS}", flush=True)
            return
    else:
        existing = json.loads(MANIFEST.read_text())["results"]
        generated = [r for r in existing if r.get("id") in ("scene_ref", "prop_ref")]
    generated_by_id = {result["id"]: result for result in generated}
    if not {"scene_ref", "prop_ref"}.issubset(generated_by_id):
        raise RuntimeError("Scene and prop input images are missing; run --stage inputs first")
    scene_path = ROOT / generated_by_id["scene_ref"]["outputs"][0]
    prop_path = ROOT / generated_by_id["prop_ref"]["outputs"][0]
    remote = {
        "character1": {"name": upload(CHAR1, "sean_multiref_character1.png"), "crop": {"x": 256, "y": 0, "width": 512, "height": 512}, "detail": "high"},
        "character2": {"name": upload(CHAR2, "sean_multiref_character2.png"), "crop": {"x": 256, "y": 0, "width": 512, "height": 512}, "detail": "high"},
        "scene": {"name": upload(scene_path, "sean_multiref_scene.png"), "detail": "normal"},
        "prop": {"name": upload(prop_path, "sean_multiref_prop.png"), "detail": "high"},
    }
    conditions = [
        ("one_face", ["character1"], False, False, False, 0.0),
        ("two_faces", ["character1", "character2"], False, False, True, 0.0),
        ("two_faces_scene", ["character1", "character2", "scene"], True, False, True, 0.0),
        ("two_faces_scene_prop", ["character1", "character2", "scene", "prop"], True, True, True, 0.0),
        ("two_faces_scene_prop_split025", ["character1", "character2", "scene", "prop"], True, True, True, 0.25),
    ]
    main_results = []
    for condition, names, use_scene, use_prop, dual, split in conditions:
        refs = {str(i + 1): remote[name] for i, name in enumerate(names)}
        prompt = main_prompt(use_scene, use_prop, dual)
        for seed in (6100101, 6100102):
            job = f"{condition}_seed{seed}"
            graph = base_graph(prompt, seed, f"sean_krea2_multiref/{job}", refs=refs, layout_split=split)
            result = submit(graph, job, args.lease_id)
            result.update({"id": job, "condition": condition, "seed": seed, "references": names, "layout_split": split, "prompt": prompt})
            main_results.append(result)
            update_manifest([result])
            print(json.dumps(result, ensure_ascii=False), flush=True)
    manifest = json.loads(MANIFEST.read_text())
    manifest["status"] = "review"
    manifest["visual_qc_status"] = "pending"
    MANIFEST.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
    print(f"Completed {len(generated) + len(main_results)} jobs; outputs: {OUTPUTS}", flush=True)


if __name__ == "__main__":
    main()
