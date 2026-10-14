#!/usr/bin/env python3
"""Owner: Sean. Reproducible API runner for the infograph baseline task."""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent
COMFY = Path("/home/sean/projects/ComfyUI")
BASE = "http://127.0.0.1:8188"
LEASE = os.environ["HIVE_RESOURCE_LEASE_ID"]
TTL = "600000"
TEMP_OUT = COMFY / "output" / "infograph-bench-v3"
PROMPT_OUT = TEMP_OUT / "prompts"
IMAGE_DIR = ROOT / "images"
WORKFLOW_DIR = ROOT / "workflows"
RUN_DIR = ROOT / "runs"

for directory in (TEMP_OUT, PROMPT_OUT, IMAGE_DIR, WORKFLOW_DIR, RUN_DIR):
    directory.mkdir(parents=True, exist_ok=True)

session = requests.Session()
session.headers["User-Agent"] = "infograph-research-v3/1.0"
main_pid = None
for process in subprocess.check_output(["ps", "-eo", "pid=,args="], text=True).splitlines():
    if "python3 main.py --enable-assets" in process and "/home/sean/projects/ComfyUI" not in process:
        main_pid = int(process.strip().split(None, 1)[0])
        break
if main_pid is None:
    # The service wrapper may run outside the model directory as cwd is enough.
    for process in subprocess.check_output(["ps", "-eo", "pid=,args="], text=True).splitlines():
        if "python3 main.py --enable-assets" in process:
            main_pid = int(process.strip().split(None, 1)[0])
            break
if main_pid is None:
    raise RuntimeError("Could not identify the managed ComfyUI Python process")
last_heartbeat = time.monotonic()
lease_lost = False


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_prompt(name: str) -> str:
    return (ROOT / "prompts" / name).read_text(encoding="utf-8").strip()


ZH_TEXT = load_prompt("qwen21_zh_brief.txt")
EN_TEXT = load_prompt("qwen21_en_brief.txt")
KREA_ZH = load_prompt("krea2_raw_zh.txt")
KREA_EN = load_prompt("krea2_raw_en.txt")


def graph_for(job: str) -> tuple[dict, str | None]:
    if job.startswith("qwen21"):
        lang = "zh" if job.endswith("zh") else "en"
        source = ZH_TEXT if lang == "zh" else EN_TEXT
        graph = {
            "1": {"class_type": "UNETLoader", "inputs": {"unet_name": "qwen_image_2.1_bf16.safetensors", "weight_dtype": "default"}},
            "2": {"class_type": "CLIPLoader", "inputs": {"clip_name": "qwen3vl_8b_bf16.safetensors", "type": "qwen_image"}},
            "3": {"class_type": "VAELoader", "inputs": {"vae_name": "qwen_image_2.1_vae_bf16.safetensors"}},
            "4": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["2", 0], "text": ["10", 0]}},
            "5": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["2", 0], "text": ""}},
            "6": {"class_type": "EmptyLatentImage", "inputs": {"width": 1536, "height": 1024, "batch_size": 1}},
            "7": {"class_type": "KSampler", "inputs": {"model": ["1", 0], "positive": ["4", 0], "negative": ["5", 0], "latent_image": ["6", 0], "seed": 42, "steps": 40, "cfg": 1.0, "sampler_name": "euler", "scheduler": "simple", "denoise": 1.0}},
            "8": {"class_type": "VAEDecode", "inputs": {"samples": ["7", 0], "vae": ["3", 0]}},
            "9": {"class_type": "SaveImage", "inputs": {"images": ["8", 0], "filename_prefix": f"infograph-bench-v3/{job}"}},
            "10": {"class_type": "QwenImage21_T2IPromptRewrite", "inputs": {"clip": ["2", 0], "prompt": source, "temperature": 1.0, "top_p": 0.95, "top_k": 20, "presence_penalty": 1.5, "max_new_tokens": 16256, "seed": 42}},
            "11": {"class_type": "SaveStringKJ", "inputs": {"string": ["10", 0], "filename_prefix": job, "output_folder": "infograph-bench-v3/prompts", "file_extension": ".txt"}},
        }
        return graph, source

    if job.startswith("krea2_raw"):
        lang = "zh" if job.endswith("zh") else "en"
        source = KREA_ZH if lang == "zh" else KREA_EN
        graph = {
            "1": {"class_type": "UNETLoader", "inputs": {"unet_name": "krea2_raw_fp8_scaled.safetensors", "weight_dtype": "default"}},
            "2": {"class_type": "CLIPLoader", "inputs": {"clip_name": "qwen3vl_4b_bf16.safetensors", "type": "krea2"}},
            "3": {"class_type": "VAELoader", "inputs": {"vae_name": "qwen_image_vae.safetensors"}},
            "4": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["2", 0], "text": source}},
            "5": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["2", 0], "text": "text, watermark, logo, collage, blurry, low detail"}},
            "6": {"class_type": "EmptySD3LatentImage", "inputs": {"width": 1536, "height": 1024, "batch_size": 1}},
            "7": {"class_type": "KSampler", "inputs": {"model": ["1", 0], "positive": ["4", 0], "negative": ["5", 0], "latent_image": ["6", 0], "seed": 42, "steps": 52, "cfg": 3.5, "sampler_name": "euler", "scheduler": "simple", "denoise": 1.0}},
            "8": {"class_type": "VAEDecode", "inputs": {"samples": ["7", 0], "vae": ["3", 0]}},
            "9": {"class_type": "SaveImage", "inputs": {"images": ["8", 0], "filename_prefix": f"infograph-bench-v3/{job}"}},
        }
        return graph, source

    if job == "krea2_turbo_zh":
        graph = {
            "1": {"class_type": "UNETLoader", "inputs": {"unet_name": "krea2_turbo_fp8.safetensors", "weight_dtype": "default"}},
            "2": {"class_type": "ModelSamplingFlux", "inputs": {"model": ["1", 0], "max_shift": 1.15, "base_shift": 0.5, "width": 1536, "height": 1024}},
            "3": {"class_type": "CLIPLoader", "inputs": {"clip_name": "qwen3vl_4b_bf16.safetensors", "type": "krea2"}},
            "4": {"class_type": "VAELoader", "inputs": {"vae_name": "qwen_image_vae.safetensors"}},
            "5": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["3", 0], "text": KREA_ZH}},
            "6": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["3", 0], "text": "text, watermark, logo, collage, blurry, low detail"}},
            "7": {"class_type": "EmptySD3LatentImage", "inputs": {"width": 1536, "height": 1024, "batch_size": 1}},
            "8": {"class_type": "KSampler", "inputs": {"model": ["2", 0], "positive": ["5", 0], "negative": ["6", 0], "latent_image": ["7", 0], "seed": 42, "steps": 8, "cfg": 0.0, "sampler_name": "euler", "scheduler": "simple", "denoise": 1.0}},
            "9": {"class_type": "VAEDecode", "inputs": {"samples": ["8", 0], "vae": ["4", 0]}},
            "10": {"class_type": "SaveImage", "inputs": {"images": ["9", 0], "filename_prefix": f"infograph-bench-v3/{job}"}},
        }
        return graph, KREA_ZH

    raise ValueError(f"Unknown job: {job}")


def gpu_sample() -> dict:
    raw = subprocess.check_output([
        "nvidia-smi", "--query-gpu=memory.used,utilization.gpu,temperature.gpu",
        "--format=csv,noheader,nounits",
    ], text=True).strip().split(",")
    rss = subprocess.check_output(["ps", "-o", "rss=", "-p", str(main_pid)], text=True).strip()
    return {"time": now(), "vram_used_mb": int(raw[0]), "gpu_util_pct": int(raw[1]),
            "temperature_c": int(raw[2]), "comfy_rss_mb": round(int(rss or 0) / 1024)}


def ensure_lease(force: bool = False) -> None:
    global last_heartbeat, lease_lost
    if lease_lost:
        raise RuntimeError("GPU lease heartbeat previously failed; refusing another generation")
    if force or time.monotonic() - last_heartbeat >= 90:
        cp = subprocess.run(["hive-resource", "lease", "heartbeat", LEASE, "--ttl", TTL], text=True, capture_output=True)
        if cp.returncode:
            lease_lost = True
            raise RuntimeError(f"GPU lease heartbeat failed: {cp.stderr or cp.stdout}")
        last_heartbeat = time.monotonic()
        print(f"[{now()}] lease heartbeat ok", flush=True)


def queue_is_empty() -> bool:
    data = session.get(f"{BASE}/queue", timeout=10).json()
    return not data.get("queue_running") and not data.get("queue_pending")


def run_one(job: str) -> dict:
    ensure_lease(force=True)
    if not queue_is_empty():
        raise RuntimeError("Shared ComfyUI queue is not empty; not submitting alongside another job")
    graph, actual_input = graph_for(job)
    workflow_path = WORKFLOW_DIR / f"{job}.json"
    workflow_path.write_text(json.dumps({"prompt": graph}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    run = {"job": job, "owner": "Sean", "submitted_at": now(), "workflow": str(workflow_path.relative_to(ROOT)),
           "input_prompt": actual_input, "seed": 42, "resolution": "1536x1024"}
    started = time.monotonic()
    response = session.post(f"{BASE}/prompt", json={"prompt": graph, "client_id": str(uuid.uuid4())}, timeout=60)
    response.raise_for_status()
    reply = response.json()
    if reply.get("node_errors"):
        raise RuntimeError(json.dumps(reply["node_errors"], ensure_ascii=False))
    prompt_id = reply["prompt_id"]
    run["prompt_id"] = prompt_id
    samples = []
    last_sample = 0.0
    last_seen = time.monotonic()
    history = None
    while time.monotonic() - started < 5400:
        ensure_lease()
        current = time.monotonic()
        if current - last_sample >= 3:
            try:
                sample = gpu_sample()
                samples.append(sample)
                with (RUN_DIR / f"{job}_gpu_samples.jsonl").open("a", encoding="utf-8") as f:
                    f.write(json.dumps(sample, ensure_ascii=False) + "\n")
            except Exception as exc:
                print(f"[{now()}] metrics sample error: {exc}", flush=True)
            last_sample = current
        hist_response = session.get(f"{BASE}/history/{prompt_id}", timeout=10)
        hist_response.raise_for_status()
        hist_data = hist_response.json()
        history = hist_data.get(prompt_id)
        if history is not None:
            status = history.get("status", {})
            if status.get("completed"):
                break
            if status.get("status_str") == "error":
                raise RuntimeError(json.dumps(status.get("messages", []), ensure_ascii=False))
        else:
            q = session.get(f"{BASE}/queue", timeout=10).json()
            present = any(str(item[1]) == prompt_id for item in q.get("queue_running", []) + q.get("queue_pending", []))
            if present:
                last_seen = time.monotonic()
            elif time.monotonic() - last_seen > 90:
                raise RuntimeError("Prompt disappeared from queue without a completed history record")
        time.sleep(2)
    else:
        raise TimeoutError("ComfyUI generation exceeded 90 minutes")

    elapsed = time.monotonic() - started
    outputs = history.get("outputs", {})
    save_id = "9" if job.startswith("qwen21") or job.startswith("krea2_raw") else "10"
    images = outputs.get(save_id, {}).get("images", [])
    if not images:
        raise RuntimeError(f"Completed prompt has no SaveImage output: {json.dumps(outputs, ensure_ascii=False)}")
    image = images[0]
    source = COMFY / "output" / image.get("subfolder", "") / image["filename"]
    target = IMAGE_DIR / f"{job}.png"
    shutil.copy2(source, target)
    source.unlink()

    actual_prompt_file = None
    if job.startswith("qwen21"):
        matches = sorted(PROMPT_OUT.glob(f"{job}_*.txt"), key=lambda p: p.stat().st_mtime, reverse=True)
        if matches:
            actual_prompt_file = ROOT / "prompts" / f"{job}_pe_output.txt"
            shutil.copy2(matches[0], actual_prompt_file)
            matches[0].unlink()
        else:
            run["prompt_capture_warning"] = "SaveStringKJ output missing; PE text must be recovered from PNG/workflow metadata if available"

    peak_vram = max((s["vram_used_mb"] for s in samples), default=None)
    peak_rss = max((s["comfy_rss_mb"] for s in samples), default=None)
    run.update({"status": "success", "completed_at": now(), "elapsed_seconds": round(elapsed, 2),
                "image": str(target.relative_to(ROOT)), "image_file": image,
                "actual_prompt_file": str(actual_prompt_file.relative_to(ROOT)) if actual_prompt_file else None,
                "peak_vram_mb_observed": peak_vram, "peak_comfy_rss_mb_observed": peak_rss,
                "peak_temperature_c_observed": max((s["temperature_c"] for s in samples), default=None),
                "peak_gpu_utilization_pct_observed": max((s["gpu_util_pct"] for s in samples), default=None),
                "gpu_samples": len(samples), "comfy_history_status": history.get("status", {})})
    (RUN_DIR / f"{job}.json").write_text(json.dumps(run, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    with (RUN_DIR / "runs.jsonl").open("a", encoding="utf-8") as f:
        f.write(json.dumps(run, ensure_ascii=False) + "\n")
    print(f"[{now()}] {job} complete in {elapsed:.1f}s; peak VRAM observed={peak_vram} MB; image={target}", flush=True)
    return run


jobs = ["qwen21_bf16_zh", "qwen21_bf16_en", "krea2_raw_fp8_zh", "krea2_raw_fp8_en", "krea2_turbo_zh"]
for job in jobs:
    try:
        run_one(job)
    except Exception as exc:
        run = {"job": job, "owner": "Sean", "status": "failed", "failed_at": now(), "error": repr(exc)}
        (RUN_DIR / f"{job}.json").write_text(json.dumps(run, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        with (RUN_DIR / "runs.jsonl").open("a", encoding="utf-8") as f:
            f.write(json.dumps(run, ensure_ascii=False) + "\n")
        print(f"[{now()}] {job} FAILED: {exc}", flush=True)
        if lease_lost:
            break
