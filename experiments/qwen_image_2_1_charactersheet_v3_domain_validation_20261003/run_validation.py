#!/usr/bin/env python3
"""[Sean] Run a fixed-reference, multi-seed validation of Qwen Character Sheet V3."""
import json
import os
import subprocess
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PROJECT = ROOT.parents[1]
BASE = PROJECT / "experiments/qwen_image_2_1_civitai_character_sheet_20261002"
COMFY_OUTPUT = Path("/home/sean/projects/ComfyUI/output")
COMFY_INPUT = Path("/home/sean/projects/ComfyUI/input")
API = "http://127.0.0.1:8188"
PREFIX = "sean_qwen_v3_domain_validation_20261003"
LEASE = os.environ["HIVE_LEASE_ID"]
CLIENT = "sean-qwen-v3-domain-validation-20261003"
MANIFEST_PATH = ROOT / "manifest.json"
UPLOADED = []

CASES = [
    {"id": "character", "source": BASE / "inputs/qwen_generated_fullbody.png", "prompt": "character_face_threeview.txt", "source_seed": None, "seed_base": 2026100300},
    {"id": "prop_katana", "source_prompt": "source_katana.txt", "prompt": "prop_katana.txt", "source_seed": 2026100311, "seed_base": 2026100320},
    {"id": "object_lantern", "source_prompt": "source_lantern.txt", "prompt": "object_lantern.txt", "source_seed": 2026100331, "seed_base": 2026100340},
    {"id": "scene_shrine", "source_prompt": "source_shrine.txt", "prompt": "scene_shrine.txt", "source_seed": 2026100351, "seed_base": 2026100360},
]

def request(path, payload=None, data=None, headers=None):
    if payload is not None:
        data = json.dumps(payload).encode()
        headers = {**(headers or {}), "Content-Type": "application/json"}
    req = urllib.request.Request(API + path, data=data, headers=headers or {})
    return urllib.request.urlopen(req, timeout=90).read()

def queue_empty():
    queue = json.loads(request("/queue"))
    if queue.get("queue_running") or queue.get("queue_pending"):
        raise RuntimeError("Shared ComfyUI queue became busy; stopping this batch")

def heartbeat():
    subprocess.run(["hive-resource", "lease", "heartbeat", LEASE, "--ttl", "600000"], check=True, capture_output=True, text=True)

def upload(source, remote):
    boundary = "----SeanQwenV3DomainValidation20261003"
    fields = [
        ("image", remote, "image/png", source.read_bytes()),
        ("type", None, None, b"input"),
        ("overwrite", None, None, b"true"),
    ]
    chunks = []
    for name, filename, mime, content in fields:
        head = f"--{boundary}\r\nContent-Disposition: form-data; name=\"{name}\""
        if filename:
            head += f"; filename=\"{filename}\"\r\nContent-Type: {mime}"
        chunks.extend([head.encode() + b"\r\n\r\n", content, b"\r\n"])
    chunks.append(f"--{boundary}--\r\n".encode())
    request("/upload/image", data=b"".join(chunks), headers={"Content-Type": f"multipart/form-data; boundary={boundary}"})
    UPLOADED.append(remote)

def wait_image(prompt_id, output_path, start_time):
    last_heartbeat = start_time
    while time.time() - start_time < 1200:
        hist = json.loads(request("/history/" + prompt_id)).get(prompt_id, {})
        status = hist.get("status", {})
        if status.get("status_str") == "error":
            raise RuntimeError(json.dumps(status, ensure_ascii=False))
        images = [im for node in hist.get("outputs", {}).values() for im in node.get("images", [])]
        if images:
            im = images[0]
            query = urllib.parse.urlencode({"filename": im["filename"], "subfolder": im.get("subfolder", ""), "type": im.get("type", "output")})
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_bytes(request("/view?" + query))
            subfolder = Path(im.get("subfolder", ""))
            if not str(subfolder).startswith(PREFIX):
                raise RuntimeError(f"Unexpected ComfyUI output subfolder: {subfolder}")
            temp = COMFY_OUTPUT / subfolder / im["filename"]
            if temp.is_file():
                temp.unlink()
            return {"prompt_id": prompt_id, "seconds": round(time.time() - start_time, 2), "output": str(output_path.relative_to(ROOT)), "comfy_image": im}
        if time.time() - last_heartbeat > 40:
            heartbeat()
            last_heartbeat = time.time()
        time.sleep(2)
    raise TimeoutError(prompt_id)

def run_graph(graph, output_path, label):
    queue_empty()
    prompt_id = json.loads(request("/prompt", {"prompt": graph, "client_id": CLIENT})) ["prompt_id"]
    return wait_image(prompt_id, output_path, time.time()) | {"id": label}

def save_manifest(manifest):
    MANIFEST_PATH.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")

def main():
    manifest = {
        "owner": "Sean",
        "experiment": ROOT.name,
        "status": "running",
        "workflow": "Qwen Image 2.1 Character Design Sheet Maker V3 Simple, adapted static prompt",
        "runtime": {"comfyui": API, "unet": "qwen_image_2.1_int8_convrot.safetensors", "clip": "qwen3vl_8b_int8_convrot.safetensors", "vae": "qwen_image_2.1_vae_bf16.safetensors", "lora": None, "output_size": "1536x1024", "steps": 25, "cfg": 1.0, "sampler": "euler", "scheduler": "simple", "reference_resolution": 1024, "decode": "standard VAE; VAEDeGrid unavailable"},
        "results": [],
        "qc": [],
    }
    save_manifest(manifest)
    try:
        for case in CASES:
            case_id = case["id"]
            if case.get("source_prompt"):
                graph = json.loads((BASE / "api_workflows/source_fullbody.json").read_text())
                graph["5"]["inputs"]["prompt"] = (ROOT / "prompts" / case["source_prompt"]).read_text().strip()
                graph["7"]["inputs"]["seed"] = case["source_seed"]
                graph["9"]["inputs"]["filename_prefix"] = f"{PREFIX}/{case_id}/source"
                source = ROOT / "inputs" / f"{case_id}_source.png"
                result = run_graph(graph, source, case_id + "_source")
                manifest["results"].append(result)
                save_manifest(manifest)
            else:
                source = case["source"]
            remote = f"{PREFIX}_{case_id}_reference.png"
            upload(source, remote)
            for offset in range(3):
                graph = json.loads((BASE / "source_workflow_v3/v3_simple_static_adapted_api.json").read_text())
                graph["5"]["inputs"]["prompt"] = (ROOT / "prompts" / case["prompt"]).read_text().strip()
                graph["7"]["inputs"]["seed"] = case["seed_base"] + offset
                graph["9"]["inputs"]["filename_prefix"] = f"{PREFIX}/{case_id}/sheet_{offset + 1}"
                graph["10"]["inputs"]["image"] = remote
                out = ROOT / "outputs" / case_id / f"seed_{case['seed_base'] + offset}.png"
                result = run_graph(graph, out, f"{case_id}_sheet_{offset + 1}")
                result["seed"] = case["seed_base"] + offset
                manifest["results"].append(result)
                save_manifest(manifest)
            remote_path = COMFY_INPUT / remote
            if remote_path.is_file():
                remote_path.unlink()
        manifest["status"] = "generated_qc_pending"
    except Exception as exc:
        manifest["status"] = "partial_error"
        manifest["error"] = repr(exc)
        raise
    finally:
        for remote in UPLOADED:
            remote_path = COMFY_INPUT / remote
            if remote_path.is_file():
                remote_path.unlink()
        save_manifest(manifest)
    print(json.dumps({"status": manifest["status"], "runs": len(manifest["results"]), "manifest": str(MANIFEST_PATH)}, ensure_ascii=False))

if __name__ == "__main__":
    main()
