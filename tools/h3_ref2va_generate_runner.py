#!/usr/bin/env python3
"""Minimal local Ref2VA generation runner for resolution experiments."""
from __future__ import annotations

import argparse
import json
import time
import urllib.error
import urllib.request

API = "http://127.0.0.1:8188"


def api(path: str, payload: dict | None = None):
    req = urllib.request.Request(API + path)
    if payload is not None:
        req = urllib.request.Request(API + path, data=json.dumps(payload).encode(),
                                     headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        raise RuntimeError(e.read().decode("utf-8", errors="replace")) from e


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--prompt", required=True)
    p.add_argument("--ref", action="append", required=True,
                   help="Reference image; repeat in the intended ref_image order")
    p.add_argument("--width", type=int, default=1344)
    p.add_argument("--height", type=int, default=768)
    p.add_argument("--length", type=int, default=124)
    p.add_argument("--steps", type=int, default=4)
    p.add_argument("--seed", type=int, default=2026092020)
    p.add_argument("--out-prefix", required=True)
    p.add_argument("--timeout", type=int, default=1800)
    args = p.parse_args()

    graph = {
        "u": {"class_type": "UNETLoader", "inputs": {
            "unet_name": "minimax_h3_ref2va_pruned_int8_convrot.safetensors",
            "weight_dtype": "default"}},
        "c": {"class_type": "CLIPLoader", "inputs": {
            "clip_name": "qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors",
            "type": "minimax", "device": "default"}},
        "v": {"class_type": "VAELoader", "inputs": {
            "vae_name": "minimax_h3_video_vae_fp16.safetensors"}},
        "av": {"class_type": "VAELoader", "inputs": {
            "vae_name": "minimax_h3_audio_vae_fp32.safetensors"}},
        "cond": {"class_type": "MiniMaxH3ReferenceToVideo", "inputs": {
            "clip": ["c", 0], "vae": ["v", 0], "audio_vae": ["av", 0],
            "prompt": open(args.prompt, encoding="utf-8").read(),
            "width": args.width, "height": args.height, "length": args.length,
            "ref_image_size": "max"}},
        "sampler": {"class_type": "KSamplerSelect", "inputs": {"sampler_name": "res_multistep"}},
        "sched": {"class_type": "BasicScheduler", "inputs": {
            "model": ["u", 0], "scheduler": "simple", "steps": args.steps,
            "denoise": 1.0}},
        "guide": {"class_type": "BasicGuider", "inputs": {
            "model": ["u", 0], "conditioning": ["cond", 0]}},
        "noise": {"class_type": "RandomNoise", "inputs": {"noise_seed": args.seed}},
        "sample": {"class_type": "SamplerCustomAdvanced", "inputs": {
            "noise": ["noise", 0], "guider": ["guide", 0], "sampler": ["sampler", 0],
            "sigmas": ["sched", 0], "latent_image": ["cond", 1]}},
        "decode": {"class_type": "VAEDecode", "inputs": {
            "samples": ["sample", 0], "vae": ["v", 0]}},
        "decode_audio": {"class_type": "VAEDecodeAudio", "inputs": {
            "samples": ["sample", 0], "vae": ["av", 0]}},
        "video": {"class_type": "CreateVideo", "inputs": {
            "images": ["decode", 0], "fps": 24.0, "audio": ["decode_audio", 0],
            "bit_depth": 8, "codec": "none"}},
        "save": {"class_type": "SaveVideo", "inputs": {
            "video": ["video", 0], "filename_prefix": args.out_prefix,
            "format": "mp4", "codec": "auto"}},
    }
    for i, path in enumerate(args.ref):
        graph[f"ref{i}"] = {"class_type": "LoadImage", "inputs": {"image": path}}
        graph["cond"]["inputs"][f"ref_images.ref_image_{i}"] = [f"ref{i}", 0]

    q = api("/prompt", {"prompt": graph, "client_id": "h3-ref2va-resolution"})
    pid = q["prompt_id"]
    print(json.dumps({"prompt_id": pid, "size": [args.width, args.height],
                      "steps": args.steps}), flush=True)
    started = time.time()
    while time.time() - started < args.timeout:
        time.sleep(5)
        h = api("/history/" + pid)
        if pid not in h:
            continue
        rec = h[pid]
        status = rec.get("status", {}).get("status_str")
        print(json.dumps({"prompt_id": pid, "status": status,
                          "elapsed_s": round(time.time() - started, 1),
                          "outputs": rec.get("outputs", {})}, ensure_ascii=False), flush=True)
        return 0 if status != "error" else 1
    print(json.dumps({"prompt_id": pid, "status": "timeout"}), flush=True)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
