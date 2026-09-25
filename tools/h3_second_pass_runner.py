#!/usr/bin/env python3
"""Run a low-denoise H3 img2img second pass on an existing video."""

from __future__ import annotations

import argparse
import json
import time
import urllib.error
import urllib.request


API = "http://127.0.0.1:8188"


def api(path: str, payload: dict | None = None):
    request = urllib.request.Request(API + path)
    if payload is not None:
        request = urllib.request.Request(
            API + path,
            data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json"},
        )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.load(response)
    except urllib.error.HTTPError as error:
        raise RuntimeError(error.read().decode("utf-8", errors="replace")) from error


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--video", required=True)
    p.add_argument("--prompt", required=True)
    p.add_argument("--identity", required=True)
    p.add_argument("--scene", required=True)
    p.add_argument("--outfit")
    p.add_argument("--out-prefix", default="face_solution/second_pass")
    p.add_argument("--width", type=int, default=1024)
    p.add_argument("--height", type=int, default=576)
    p.add_argument("--denoise", type=float, default=0.20)
    p.add_argument("--steps", type=int, default=20)
    p.add_argument("--seed", type=int, default=20260920)
    p.add_argument("--timeout", type=int, default=1200)
    args = p.parse_args()

    prompt = open(args.prompt, encoding="utf-8").read()
    graph = {
        "u": {"class_type": "UNETLoader", "inputs": {
            "unet_name": "minimax_h3_ref2va_pruned_int8_convrot.safetensors",
            "weight_dtype": "default",
        }},
        "c": {"class_type": "CLIPLoader", "inputs": {
            "clip_name": "qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors",
            "type": "minimax", "device": "default",
        }},
        "v": {"class_type": "VAELoader", "inputs": {
            "vae_name": "minimax_h3_video_vae_fp16.safetensors",
        }},
        "av": {"class_type": "VAELoader", "inputs": {
            "vae_name": "minimax_h3_audio_vae_fp32.safetensors",
        }},
        "vid": {"class_type": "VHS_LoadVideoPath", "inputs": {
            "video": args.video, "force_rate": 24.0,
            "custom_width": args.width, "custom_height": args.height,
            "frame_load_cap": 124, "skip_first_frames": 0,
            "select_every_nth": 1, "format": "H3",
        }},
        "id": {"class_type": "LoadImage", "inputs": {"image": args.identity}},
        "scene": {"class_type": "LoadImage", "inputs": {"image": args.scene}},
        "cond": {"class_type": "MiniMaxH3ReferenceToVideo", "inputs": {
            "clip": ["c", 0], "vae": ["v", 0], "audio_vae": ["av", 0],
            "prompt": prompt, "width": args.width, "height": args.height,
            "length": 124, "ref_image_size": "max",
            "ref_images.ref_image_0": ["id", 0],
            "ref_images.ref_image_1": ["scene", 0],
        }},
        "inject": {"class_type": "H3InjectVideoLatent", "inputs": {
            "av_latent": ["cond", 1], "images": ["vid", 0], "vae": ["v", 0],
        }},
        "sampler": {"class_type": "KSamplerSelect", "inputs": {
            "sampler_name": "res_multistep",
        }},
        "sched": {"class_type": "BasicScheduler", "inputs": {
            "model": ["u", 0], "scheduler": "simple",
            "steps": args.steps, "denoise": args.denoise,
        }},
        "guide": {"class_type": "BasicGuider", "inputs": {
            "model": ["u", 0], "conditioning": ["cond", 0],
        }},
        "noise": {"class_type": "RandomNoise", "inputs": {"noise_seed": args.seed}},
        "sample": {"class_type": "SamplerCustomAdvanced", "inputs": {
            "noise": ["noise", 0], "guider": ["guide", 0],
            "sampler": ["sampler", 0], "sigmas": ["sched", 0],
            "latent_image": ["inject", 0],
        }},
        "decode": {"class_type": "VAEDecode", "inputs": {
            "samples": ["sample", 0], "vae": ["v", 0],
        }},
        "video": {"class_type": "CreateVideo", "inputs": {
            "images": ["decode", 0], "fps": 24.0,
            "audio": ["vid", 2], "bit_depth": 8, "codec": "none",
        }},
        "save": {"class_type": "SaveVideo", "inputs": {
            "video": ["video", 0], "filename_prefix": args.out_prefix,
            "format": "mp4", "codec": "auto",
        }},
    }
    if args.outfit:
        graph["outfit"] = {"class_type": "LoadImage", "inputs": {"image": args.outfit}}
        graph["cond"]["inputs"]["ref_images.ref_image_2"] = ["outfit", 0]
    queued = api("/prompt", {"prompt": graph, "client_id": "h3-second-pass"})
    prompt_id = queued["prompt_id"]
    print(json.dumps({"prompt_id": prompt_id, "denoise": args.denoise,
                      "steps": args.steps, "size": [args.width, args.height]}), flush=True)
    started = time.time()
    while time.time() - started < args.timeout:
        time.sleep(5)
        history = api("/history/" + prompt_id)
        if prompt_id not in history:
            continue
        record = history[prompt_id]
        status = record.get("status", {})
        print(json.dumps({"prompt_id": prompt_id,
                          "status": status.get("status_str"),
                          "elapsed_s": round(time.time() - started, 1),
                          "outputs": record.get("outputs", {})}, ensure_ascii=False), flush=True)
        return 0 if status.get("status_str") != "error" else 1
    print(json.dumps({"prompt_id": prompt_id, "status": "timeout"}), flush=True)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
