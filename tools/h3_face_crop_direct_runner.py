#!/usr/bin/env python3
"""Run H3FaceTrackCrop directly from a video loader.

This variant is for shots where H3FaceSelect cannot make a reliable pick
(for example a hooded or very small face).  It keeps the source frames and
audio from VHS_LoadVideoPath and lets FaceTrackCrop use a body fallback.
"""
from __future__ import annotations

import argparse
import json
import time
import urllib.request
import urllib.error

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
    p.add_argument("--video", required=True)
    p.add_argument("--identity", required=True)
    p.add_argument("--prompt", required=True)
    p.add_argument("--out-prefix", required=True)
    p.add_argument("--canvas", type=int, default=768)
    p.add_argument("--length", type=int, default=124)
    p.add_argument("--crop-factor", type=float, default=3.0)
    p.add_argument("--confidence", type=float, default=0.10)
    p.add_argument("--fallback-detector", default="segm\\person_yolov8m-seg.pt")
    p.add_argument("--fallback-head-frac", type=float, default=0.5)
    p.add_argument("--x", type=int, default=250)
    p.add_argument("--y", type=int, default=270)
    p.add_argument("--steps", type=int, default=8)
    p.add_argument("--denoise", type=float, default=0.40)
    p.add_argument("--per-frame-denoise", action="store_true")
    p.add_argument("--small-face-mult", type=float, default=1.0)
    p.add_argument("--large-face-mult", type=float, default=0.35)
    p.add_argument("--face-px-small", type=float, default=30.0)
    p.add_argument("--face-px-large", type=float, default=120.0)
    p.add_argument("--denoise-gamma", type=float, default=1.0)
    p.add_argument("--smooth-frames", type=int, default=9)
    p.add_argument("--seed", type=int, default=20260920)
    p.add_argument("--preview", action="store_true")
    p.add_argument("--timeout", type=int, default=1200)
    args = p.parse_args()

    graph = {
        "load": {"class_type": "VHS_LoadVideoPath", "inputs": {
            "video": args.video, "force_rate": 0, "custom_width": 0,
            "custom_height": 0, "frame_load_cap": args.length,
            "skip_first_frames": 0, "select_every_nth": 1, "format": "H3",
        }},
        "id": {"class_type": "LoadImage", "inputs": {"image": args.identity}},
        "crop": {"class_type": "H3FaceTrackCrop", "inputs": {
            "images": ["load", 0], "detector": "face_yolov8m.pt",
            "confidence": args.confidence, "crop_factor": args.crop_factor,
            "canvas_width": args.canvas, "canvas_height": args.canvas,
            "canvas_mode": "manual", "smooth_window": 21,
            "size_smooth_window": 51, "smooth_method": "gaussian",
            "size_mode": "per_frame", "identity_reference": ["id", 0],
            "identity_track": False, "identity_threshold": 0.20,
            "select": "closest_to_xy", "fallback_detector": args.fallback_detector,
            "fallback_head_frac": args.fallback_head_frac,
            "select_index": 0, "identity_model": "insightface",
            "cut_detection": "none", "cut_threshold": 3.0,
            "absent_shots": "off", "X": args.x, "Y": args.y,
            "frame_index": 0,
        }},
    }
    if args.preview:
        graph["video"] = {"class_type": "CreateVideo", "inputs": {
            "images": ["crop", 2], "fps": 24.0, "audio": ["load", 2],
            "bit_depth": 8, "codec": "none",
        }}
    else:
        graph.update({
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
                "width": args.canvas, "height": args.canvas, "length": args.length,
                "ref_image_size": "max", "ref_images.ref_image_0": ["id", 0]}},
            "inject": {"class_type": "H3InjectVideoLatent", "inputs": {
                "av_latent": ["cond", 1], "images": ["crop", 0], "vae": ["v", 0]}},
            "sampler": {"class_type": "KSamplerSelect", "inputs": {"sampler_name": "res_multistep"}},
            "sched": {"class_type": "BasicScheduler", "inputs": {
                "model": ["u", 0], "scheduler": "simple", "steps": args.steps,
                "denoise": args.denoise}},
            "guide": {"class_type": "BasicGuider", "inputs": {"model": ["u", 0], "conditioning": ["cond", 0]}},
            "noise": {"class_type": "RandomNoise", "inputs": {"noise_seed": args.seed}},
            "sample": {"class_type": "SamplerCustomAdvanced", "inputs": {
                "noise": ["noise", 0], "guider": ["guide", 0], "sampler": ["sampler", 0],
                "sigmas": ["sched", 0], "latent_image": ["inject", 0]}},
            "decode": {"class_type": "VAEDecode", "inputs": {"samples": ["sample", 0], "vae": ["v", 0]}},
            "stitch": {"class_type": "H3FaceStitch", "inputs": {
                "base_images": ["load", 0], "refined_crops": ["decode", 0],
                "transform": ["crop", 1], "paste_region": "face_only",
                "mask_dilation": 16, "feather": 6, "colour_match": 1.0,
                "blend": 1.0, "undetected_frames": "fade_out",
                "feather_scales_with_crop": False}},
        })
        if args.per_frame_denoise:
            graph["pf"] = {"class_type": "H3PerFrameDenoise", "inputs": {
                "model": ["u", 0], "av_latent": ["inject", 0],
                "transform": ["crop", 1],
                "denoise_multiplier_small_face": args.small_face_mult,
                "denoise_multiplier_large_face": args.large_face_mult,
                "scale_mode": "absolute_px", "face_px_small": args.face_px_small,
                "face_px_large": args.face_px_large, "gamma": args.denoise_gamma,
                "smooth_frames": args.smooth_frames}}
            graph["sched"]["inputs"]["model"] = ["pf", 2]
            graph["guide"]["inputs"]["model"] = ["pf", 2]
            graph["sample"]["inputs"]["latent_image"] = ["pf", 0]
        graph["video"] = {"class_type": "CreateVideo", "inputs": {
            "images": ["stitch", 0], "fps": 24.0, "audio": ["load", 2],
            "bit_depth": 8, "codec": "none"}}
    graph["save"] = {"class_type": "SaveVideo", "inputs": {
        "video": ["video", 0], "filename_prefix": args.out_prefix,
        "format": "mp4", "codec": "auto"}}

    q = api("/prompt", {"prompt": graph, "client_id": "h3-face-direct"})
    pid = q["prompt_id"]
    print(json.dumps({"prompt_id": pid, "preview": args.preview}), flush=True)
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
