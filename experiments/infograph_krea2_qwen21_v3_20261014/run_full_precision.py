#!/usr/bin/env python3
"""Owner: Sean. Reproducible full-precision multi-seed v3 runner."""
from __future__ import annotations

import json
import os
import sys
import shutil
import subprocess
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

import requests
from PIL import Image

ROOT = Path(__file__).resolve().parent
COMFY = Path("/home/sean/projects/ComfyUI")
BASE = "http://127.0.0.1:8188"
LEASE = os.environ["HIVE_RESOURCE_LEASE_ID"]
TTL = "600000"
TEMP_OUT = COMFY / "output" / "infograph-bench-v3-full"
IMAGE_DIR = ROOT / "images" / "full_precision"
WORKFLOW_DIR = ROOT / "workflows" / "full_precision"
RUN_DIR = ROOT / "runs" / "full_precision"
PROMPT_DIR = ROOT / "prompts"
SEEDS = (42, 1337, 2026)

for directory in (TEMP_OUT, IMAGE_DIR, WORKFLOW_DIR, RUN_DIR):
    directory.mkdir(parents=True, exist_ok=True)

session = requests.Session()
session.headers["User-Agent"] = "infograph-research-v3-full-precision/1.0"
processes = subprocess.check_output(["ps", "-eo", "pid=,args="], text=True).splitlines()
main_pid = next((int(p.strip().split(None, 1)[0]) for p in processes
                 if "python3 main.py --enable-assets" in p), None)
if main_pid is None:
    raise RuntimeError("Could not identify the managed ComfyUI Python process")
last_heartbeat = time.monotonic()
lease_lost = False


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def read(name: str) -> str:
    return (PROMPT_DIR / name).read_text(encoding="utf-8").strip()


QWEN = {"zh": read("qwen21_bf16_zh_pe_output.txt"), "en": read("qwen21_bf16_en_pe_output.txt")}
KREA = {"zh": read("krea2_raw_zh.txt"), "en": read("krea2_raw_en.txt")}
FLUX = {"zh": read("flux2_klein_zh.txt"), "en": read("flux2_klein_en.txt")}


def graph_for(model: str, lang: str, seed: int, job: str) -> tuple[dict, str]:
    prompt = {"qwen21": QWEN, "krea2": KREA, "flux2": FLUX}[model][lang]
    if model == "qwen21":
        graph = {
            "1": {"class_type": "UNETLoader", "inputs": {"unet_name": "qwen_image_2.1_bf16.safetensors", "weight_dtype": "default"}},
            "2": {"class_type": "CLIPLoader", "inputs": {"clip_name": "qwen3vl_8b_bf16.safetensors", "type": "qwen_image"}},
            "3": {"class_type": "VAELoader", "inputs": {"vae_name": "qwen_image_2.1_vae_bf16.safetensors"}},
            "4": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["2", 0], "text": prompt}},
            "5": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["2", 0], "text": ""}},
            "6": {"class_type": "EmptyLatentImage", "inputs": {"width": 1536, "height": 1024, "batch_size": 1}},
            "7": {"class_type": "KSampler", "inputs": {"model": ["1", 0], "positive": ["4", 0], "negative": ["5", 0], "latent_image": ["6", 0], "seed": seed, "steps": 40, "cfg": 1.0, "sampler_name": "euler", "scheduler": "simple", "denoise": 1.0}},
            "8": {"class_type": "VAEDecode", "inputs": {"samples": ["7", 0], "vae": ["3", 0]}},
            "9": {"class_type": "SaveImage", "inputs": {"images": ["8", 0], "filename_prefix": f"infograph-bench-v3-full/{job}"}},
        }
    elif model == "krea2":
        graph = {
            "1": {"class_type": "UNETLoader", "inputs": {"unet_name": "krea2_raw_bf16.safetensors", "weight_dtype": "default"}},
            "2": {"class_type": "CLIPLoader", "inputs": {"clip_name": "qwen3vl_4b_bf16.safetensors", "type": "krea2"}},
            "3": {"class_type": "VAELoader", "inputs": {"vae_name": "qwen_image_vae.safetensors"}},
            "4": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["2", 0], "text": prompt}},
            "5": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["2", 0], "text": "text, watermark, logo, collage, blurry, low detail"}},
            "6": {"class_type": "EmptySD3LatentImage", "inputs": {"width": 1536, "height": 1024, "batch_size": 1}},
            "7": {"class_type": "KSampler", "inputs": {"model": ["1", 0], "positive": ["4", 0], "negative": ["5", 0], "latent_image": ["6", 0], "seed": seed, "steps": 52, "cfg": 3.5, "sampler_name": "euler", "scheduler": "simple", "denoise": 1.0}},
            "8": {"class_type": "VAEDecode", "inputs": {"samples": ["7", 0], "vae": ["3", 0]}},
            "9": {"class_type": "SaveImage", "inputs": {"images": ["8", 0], "filename_prefix": f"infograph-bench-v3-full/{job}"}},
        }
    else:
        graph = {
            "1": {"class_type": "UNETLoader", "inputs": {"unet_name": "flux-2-klein-9b.safetensors", "weight_dtype": "default"}},
            "2": {"class_type": "CLIPLoader", "inputs": {"clip_name": "qwen_3_8b.safetensors", "type": "flux2"}},
            "3": {"class_type": "VAELoader", "inputs": {"vae_name": "flux2-vae.safetensors"}},
            "4": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["2", 0], "text": prompt}},
            "5": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["2", 0], "text": ""}},
            "6": {"class_type": "EmptyFlux2LatentImage", "inputs": {"width": 1536, "height": 1024, "batch_size": 1}},
            "7": {"class_type": "Flux2Scheduler", "inputs": {"steps": 50, "width": 1536, "height": 1024}},
            "8": {"class_type": "CFGGuider", "inputs": {"model": ["1", 0], "positive": ["4", 0], "negative": ["5", 0], "cfg": 3.5}},
            "9": {"class_type": "RandomNoise", "inputs": {"noise_seed": seed}},
            "10": {"class_type": "KSamplerSelect", "inputs": {"sampler_name": "euler"}},
            "11": {"class_type": "SamplerCustomAdvanced", "inputs": {"noise": ["9", 0], "guider": ["8", 0], "sampler": ["10", 0], "sigmas": ["7", 0], "latent_image": ["6", 0]}},
            "12": {"class_type": "VAEDecode", "inputs": {"samples": ["11", 0], "vae": ["3", 0]}},
            "13": {"class_type": "SaveImage", "inputs": {"images": ["12", 0], "filename_prefix": f"infograph-bench-v3-full/{job}"}},
        }
    return graph, prompt


def gpu_sample() -> dict:
    raw = subprocess.check_output(["nvidia-smi", "--query-gpu=memory.used,utilization.gpu,temperature.gpu", "--format=csv,noheader,nounits"], text=True).strip().split(",")
    rss = subprocess.check_output(["ps", "-o", "rss=", "-p", str(main_pid)], text=True).strip()
    mem = {}
    for line in Path("/proc/meminfo").read_text().splitlines():
        if line.startswith(("MemAvailable:", "MemTotal:")):
            key, value, _ = line.split()
            mem[key.rstrip(":").lower() + "_mb"] = round(int(value) / 1024)
    return {"time": now(), "vram_used_mb": int(raw[0]), "gpu_util_pct": int(raw[1]), "temperature_c": int(raw[2]), "comfy_rss_mb": round(int(rss or 0) / 1024), **mem}


def heartbeat(force: bool = False) -> None:
    global last_heartbeat, lease_lost
    if lease_lost:
        raise RuntimeError("GPU lease heartbeat previously failed")
    if force or time.monotonic() - last_heartbeat >= 90:
        p = subprocess.run(["hive-resource", "lease", "heartbeat", LEASE, "--ttl", TTL], text=True, capture_output=True)
        if p.returncode:
            lease_lost = True
            raise RuntimeError(p.stderr or p.stdout)
        last_heartbeat = time.monotonic()


def run_one(model: str, lang: str, seed: int) -> dict:
    job = f"{model}_{lang}_seed{seed}"
    existing = RUN_DIR / f"{job}.json"
    image_path = IMAGE_DIR / f"{job}.png"
    if existing.exists() and image_path.exists():
        prior = json.loads(existing.read_text(encoding="utf-8"))
        if prior.get("status") == "success":
            print(f"[{now()}] {job} already complete; skipping", flush=True)
            return prior
    heartbeat(force=True)
    queue = session.get(f"{BASE}/queue", timeout=10).json()
    if queue.get("queue_running") or queue.get("queue_pending"):
        raise RuntimeError("Shared ComfyUI queue not empty")
    graph, prompt = graph_for(model, lang, seed, job)
    workflow_path = WORKFLOW_DIR / f"{job}.json"
    workflow_path.write_text(json.dumps({"prompt": graph}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    parameters = {"resolution": "1536x1024", "sampler": "euler", "scheduler": "simple" if model != "flux2" else "Flux2Scheduler"}
    if model == "qwen21": parameters.update({"steps": 40, "cfg": 1.0, "diffusion_model": "qwen_image_2.1_bf16.safetensors", "text_encoder": "qwen3vl_8b_bf16.safetensors + Qwen Image 2.1 PE t2i int8_convrot", "vae": "qwen_image_2.1_vae_bf16.safetensors"})
    elif model == "krea2": parameters.update({"steps": 52, "cfg": 3.5, "diffusion_model": "krea2_raw_bf16.safetensors", "text_encoder": "qwen3vl_4b_bf16.safetensors", "vae": "qwen_image_vae.safetensors"})
    else: parameters.update({"steps": 50, "cfg": 3.5, "diffusion_model": "flux-2-klein-9b.safetensors", "text_encoder": "qwen_3_8b.safetensors", "vae": "flux2-vae.safetensors"})
    run = {"job": job, "owner": "Sean", "model": model, "precision": "BF16 diffusion weights; BF16 text encoder except Qwen PE int8_convrot", "language": lang, "seed": seed,
           "parameters": parameters, "resolution": "1536x1024", "input_prompt": prompt, "workflow": str(workflow_path.relative_to(ROOT)),
           "submitted_at": now(), "resource_lease_id": LEASE}
    started = time.monotonic()
    response = session.post(f"{BASE}/prompt", json={"prompt": graph, "client_id": str(uuid.uuid4())}, timeout=60)
    response.raise_for_status()
    reply = response.json()
    if reply.get("node_errors"):
        raise RuntimeError(json.dumps(reply["node_errors"], ensure_ascii=False))
    prompt_id = reply["prompt_id"]
    run["prompt_id"] = prompt_id
    samples, last_sample, last_seen, history = [], 0.0, time.monotonic(), None
    while time.monotonic() - started < 7200:
        heartbeat()
        now_mono = time.monotonic()
        if now_mono - last_sample >= 3:
            sample = gpu_sample()
            samples.append(sample)
            with (RUN_DIR / f"{job}_gpu_samples.jsonl").open("a", encoding="utf-8") as f:
                f.write(json.dumps(sample) + "\n")
            last_sample = now_mono
        history_data = session.get(f"{BASE}/history/{prompt_id}", timeout=10).json()
        history = history_data.get(prompt_id)
        if history and history.get("status", {}).get("completed"):
            break
        if history and history.get("status", {}).get("status_str") == "error":
            raise RuntimeError(json.dumps(history["status"].get("messages", []), ensure_ascii=False))
        if not history:
            q = session.get(f"{BASE}/queue", timeout=10).json()
            present = any(str(item[1]) == prompt_id for item in q.get("queue_running", []) + q.get("queue_pending", []))
            if present:
                last_seen = time.monotonic()
            elif time.monotonic() - last_seen > 90:
                raise RuntimeError("Prompt disappeared without completion")
        time.sleep(2)
    else:
        raise TimeoutError("Generation exceeded two hours")

    elapsed = time.monotonic() - started
    images = history.get("outputs", {}).get("13" if model == "flux2" else "9", {}).get("images", [])
    if not images:
        raise RuntimeError("Completed prompt has no saved image")
    image = images[0]
    source = COMFY / "output" / image.get("subfolder", "") / image["filename"]
    target = IMAGE_DIR / f"{job}.png"
    shutil.copy2(source, target)
    source.unlink()
    with Image.open(target) as output_image:
        output_image.load()
        run["image_dimensions"] = list(output_image.size)
        if output_image.size != (1536, 1024):
            raise RuntimeError(f"Unexpected output dimensions: {output_image.size}")
    run.update({"status": "success", "completed_at": now(), "elapsed_seconds": round(elapsed, 2),
                "image": str(target.relative_to(ROOT)), "image_file": image,
                "peak_vram_mb_observed": max((s["vram_used_mb"] for s in samples), default=None),
                "peak_comfy_rss_mb_observed": max((s["comfy_rss_mb"] for s in samples), default=None),
                "peak_temperature_c_observed": max((s["temperature_c"] for s in samples), default=None),
                "peak_gpu_utilization_pct_observed": max((s["gpu_util_pct"] for s in samples), default=None),
                "gpu_samples": len(samples), "comfy_history_status": history.get("status", {})})
    (RUN_DIR / f"{job}.json").write_text(json.dumps(run, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    with (RUN_DIR / "runs.jsonl").open("a", encoding="utf-8") as f:
        f.write(json.dumps(run, ensure_ascii=False) + "\n")
    print(f"[{now()}] {job} complete in {elapsed:.1f}s; peak VRAM={run['peak_vram_mb_observed']} MB; image={target}", flush=True)
    return run


jobs = [(model, lang, seed) for model in ("qwen21", "krea2", "flux2") for lang in ("zh", "en") for seed in SEEDS]
if len(sys.argv) > 1 and sys.argv[1] == "--pilot":
    jobs = [(model, lang, 42) for model in ("qwen21", "krea2", "flux2") for lang in ("zh", "en")]
for model, lang, seed in jobs:
    try:
        run_one(model, lang, seed)
    except Exception as exc:
        job = f"{model}_{lang}_seed{seed}"
        graph, prompt = graph_for(model, lang, seed, job)
        workflow_path = WORKFLOW_DIR / f"{job}.json"
        workflow_path.write_text(json.dumps({"prompt": graph}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        run = {"job": job, "owner": "Sean", "model": model, "precision": "BF16", "language": lang, "seed": seed,
               "input_prompt": prompt, "workflow": str(workflow_path.relative_to(ROOT)),
               "resolution": "1536x1024", "status": "failed", "failed_at": now(), "error": repr(exc)}
        (RUN_DIR / f"{job}.json").write_text(json.dumps(run, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        with (RUN_DIR / "runs.jsonl").open("a", encoding="utf-8") as f:
            f.write(json.dumps(run, ensure_ascii=False) + "\n")
        print(f"[{now()}] {job} FAILED: {exc}", flush=True)
        if lease_lost:
            break
