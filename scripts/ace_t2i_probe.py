#!/usr/bin/env python3
"""ACE 栈（SDXL turbo）t2i 探测：验证生图链路 + 可挂 SDXL 风格 LoRA。
用法: python3 scripts/ace_t2i_probe.py --lora "xxx.safetensors" --lora-strength 0.8 --prompt "..." --prefix ace_test/x
"""
import argparse
import json
import time
import urllib.request

SERVER = "http://127.0.0.1:8188"
LORAS_DIR = "/home/sean/projects/ComfyUI/models/loras"


def build(prompt: str, prefix: str, lora: str | None, strength: float) -> dict:
    nodes = {
        "1": {"class_type": "UNETLoader", "inputs": {"unet_name": "acestep_v1.5_xl_turbo_bf16.safetensors", "weight_dtype": "default"}},
        "2": {"class_type": "DualCLIPLoader", "inputs": {"clip_name1": "qwen_4b_ace15.safetensors", "clip_name2": "qwen_0.6b_ace15.safetensors", "type": "ace", "device": "default"}},
        "3": {"class_type": "VAELoader", "inputs": {"vae_name": "ace_1.5_vae.safetensors"}},
        "5": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["2", 0], "text": prompt}},
        "6": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["2", 0], "text": "worst quality, low quality, blurry, jpeg artifacts, bad anatomy, extra fingers, watermark, signature, text, logo"}},
        "7": {"class_type": "EmptyLatentImage", "inputs": {"width": 1024, "height": 1024, "batch_size": 1}},
        "9": {"class_type": "VAEDecode", "inputs": {"samples": ["8", 0], "vae": ["3", 0]}},
        "10": {"class_type": "SaveImage", "inputs": {"images": ["9", 0], "filename_prefix": prefix}},
    }
    model_ref = ["1", 0]
    clip_ref = ["2", 0]
    if lora:
        lid = "11"
        nodes[lid] = {"class_type": "LoraLoader", "inputs": {
            "model": model_ref, "clip": clip_ref,
            "lora_name": lora, "strength_model": strength, "strength_clip": strength}}
        model_ref = [lid, 0]
        clip_ref = [lid, 1]
    nodes["8"] = {"class_type": "KSampler", "inputs": {
        "model": model_ref, "positive": ["5", 0], "negative": ["6", 0],
        "latent_image": ["7", 0], "seed": 20260818, "steps": 8, "cfg": 2.0,
        "sampler_name": "euler", "scheduler": "simple", "denoise": 1.0}}
    return nodes


def submit(prompt: dict) -> str:
    data = json.dumps({"prompt": prompt}).encode()
    req = urllib.request.Request(f"{SERVER}/prompt", data=data,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)["prompt_id"]


def wait_queue():
    while True:
        with urllib.request.urlopen(f"{SERVER}/queue", timeout=10) as r:
            q = json.load(r)
        if not q.get("queue_running") and not q.get("queue_pending"):
            return
        time.sleep(3)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--prompt", required=True)
    ap.add_argument("--prefix", default="ace_test/x")
    ap.add_argument("--lora")
    ap.add_argument("--lora-strength", type=float, default=0.8)
    ap.add_argument("--seed", type=int, default=20260818)
    args = ap.parse_args()

    wf = build(args.prompt, args.prefix, args.lora, args.lora_strength)
    if args.lora:
        wf["8"]["inputs"]["seed"] = args.seed
    pid = submit(wf)
    print("submitted", pid)
    wait_queue()
    print("DONE", args.prefix)
