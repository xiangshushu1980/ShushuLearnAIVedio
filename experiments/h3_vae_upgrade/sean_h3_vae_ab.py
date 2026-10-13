#!/usr/bin/env python3
# Owner: Sean
"""Isolated MiniMax H3 video-VAE encode/decode A/B benchmark."""

import argparse
import gc
import json
import os
import subprocess
import sys
import time
from pathlib import Path


ROOT = Path("/home/sean/projects/ComfyUI")
DEFAULT_VIDEO = ROOT / "output/face_solution/sylvanas_hero_pullback_1344_final8_00001_.mp4"
VAE_DIR = ROOT / "models/vae"


def run_child(vae_path: Path, video_path: Path, out_dir: Path, width: int, height: int, frames: int) -> dict:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT)
    cmd = [
        sys.executable,
        __file__,
        "--child",
        "--vae",
        str(vae_path),
        "--video",
        str(video_path),
        "--out-dir",
        str(out_dir),
        "--width",
        str(width),
        "--height",
        str(height),
        "--frames",
        str(frames),
    ]
    started = time.perf_counter()
    proc = subprocess.run(cmd, env=env, text=True, capture_output=True)
    elapsed = time.perf_counter() - started
    if proc.returncode != 0:
        raise RuntimeError(f"{vae_path.name} failed ({proc.returncode}):\n{proc.stdout}\n{proc.stderr}")
    result = json.loads(proc.stdout.strip().splitlines()[-1])
    result["process_wall_seconds"] = elapsed
    return result


def read_video(path: Path, width: int, height: int, frame_count: int):
    import av
    import numpy as np
    import torch

    container = av.open(str(path))
    frame_list = []
    for frame in container.decode(video=0):
        frame_list.append(frame.to_ndarray(format="rgb24"))
    container.close()
    array = np.stack(frame_list[:frame_count]).astype(np.float32) / 255.0
    pixels = torch.from_numpy(array)
    if tuple(pixels.shape[1:3]) != (height, width):
        pixels = torch.nn.functional.interpolate(
            pixels.permute(0, 3, 1, 2), size=(height, width), mode="bilinear", align_corners=False
        ).permute(0, 2, 3, 1).contiguous()
    return pixels


def child(args):
    import torch

    sys.argv = [sys.argv[0], "--fast", "fp16_accumulation", "--fp16-vae"]
    sys.path.insert(0, str(ROOT))
    import comfy.model_management as model_management
    import comfy.sd as sd
    import comfy.utils as utils

    pixels = read_video(Path(args.video), args.width, args.height, args.frames)
    if pixels.shape[0] != args.frames or tuple(pixels.shape[1:3]) != (args.height, args.width):
        raise ValueError(f"unexpected input shape: {tuple(pixels.shape)}")

    torch.cuda.empty_cache()
    torch.cuda.reset_peak_memory_stats()
    load_started = time.perf_counter()
    state_dict, metadata = utils.load_torch_file(args.vae, safe_load=True, return_metadata=True)
    vae = sd.VAE(sd=state_dict, metadata=metadata)
    load_seconds = time.perf_counter() - load_started

    def timed(fn):
        torch.cuda.synchronize()
        start = time.perf_counter()
        value = fn()
        torch.cuda.synchronize()
        return value, time.perf_counter() - start

    latent, encode_seconds = timed(lambda: vae.encode(pixels))
    decoded, decode_seconds = timed(lambda: vae.decode(latent))
    finite = bool(torch.isfinite(decoded).all().item())
    result = {
        "vae": Path(args.vae).name,
        "input_shape": list(pixels.shape),
        "latent_shape": list(latent.shape),
        "decoded_shape": list(decoded.shape),
        "load_seconds": load_seconds,
        "encode_seconds": encode_seconds,
        "decode_seconds": decode_seconds,
        "roundtrip_seconds": encode_seconds + decode_seconds,
        "finite_output": finite,
        "decoded_min": float(decoded.min().item()),
        "decoded_max": float(decoded.max().item()),
        "peak_vram_mb": torch.cuda.max_memory_allocated() / 1024**2,
    }
    del decoded, latent, vae, state_dict
    gc.collect()
    model_management.soft_empty_cache()
    print(json.dumps(result))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--child", action="store_true")
    parser.add_argument("--vae")
    parser.add_argument("--video", default=str(DEFAULT_VIDEO))
    parser.add_argument("--out-dir", default="/tmp/sean_h3_vae_ab")
    parser.add_argument("--width", type=int, default=1344)
    parser.add_argument("--height", type=int, default=768)
    parser.add_argument("--frames", type=int, default=124)
    args = parser.parse_args()
    if args.child:
        child(args)
        return

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    vaes = [
        VAE_DIR / "minimax_h3_video_vae_fp16.safetensors",
        VAE_DIR / "minimax_h3_video_vae_int8_convrot.safetensors",
    ]
    results = []
    for vae in vaes:
        if not vae.is_file():
            raise FileNotFoundError(vae)
        results.append(run_child(vae, Path(args.video), out_dir, args.width, args.height, args.frames))
    payload = {
        "owner": "Sean",
        "test": "MiniMax H3 video VAE A/B",
        "input_video": str(DEFAULT_VIDEO),
        "input_contract": f"{args.width}x{args.height}, {args.frames} frames, 24 fps; H3 valid local grid",
        "fast": ["fp16_accumulation"],
        "vae_dtype": "fp16",
        "results": results,
    }
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
