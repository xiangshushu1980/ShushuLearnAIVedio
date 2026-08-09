#!/usr/bin/env python3
"""H3 提示词视频验收批：DS-Pro vs IR 同 seed 同参数对比（t8 生产候选档）

6 场景 × 2 版（DS-Pro / IR），t2v 与 i2v 混合。
用法：python3 scripts/h3_prompt_video_ab.py [--dry-run] [--steps 8]
"""
import argparse
import json
import sys
import time
import urllib.request

HOST = "http://127.0.0.1:8188"
CLIP = "qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors"
LORA = "minimax_h3_turbo_4step_ema_ckpt850_pruned_comfyui.safetensors"
IR = "experiments/ir_samples"
DS = "experiments/prompt_compare/pro"
IMGDIR = "/home/sean/projects/ComfyUI/input/start"

SCENES = [
    # name, mode, duration_s, frames, seed, ir_file, ds_file, image(optional)
    ("onsen",       "t2v", 10, 240, 20260810, f"{IR}/ab_A_onsen_10s.txt",       f"{DS}/onsen_deepseek-v4-pro.txt", None),
    ("wow_fight",   "t2v", 10, 240, 20260810, f"{IR}/ab_B_wow_fight_10s.txt",   f"{DS}/wow_fight_deepseek-v4-pro.txt", None),
    ("cyberpunk",   "t2v", 5,  120, 20260810, f"{IR}/t2v_cyberpunk_rainy.txt",  f"{DS}/cyberpunk_rainy_deepseek-v4-pro.txt", None),
    ("streetfood",  "t2v", 5,  120, 20260810, f"{IR}/t2v_doc_streetfood.txt",   f"{DS}/doc_streetfood_deepseek-v4-pro.txt", None),
    ("alya_beach",  "i2v", 5,  120, 20260810, f"{IR}/i2v_alya_beach.txt",       f"{DS}/alya_beach_deepseek-v4-pro.txt", "start/alya_169.png"),
    ("dessert",     "i2v", 5,  120, 20260810, f"{IR}/i2v_dessert.txt",          f"{DS}/dessert_deepseek-v4-pro.txt", "start/dessert_1024.png"),
]


def api(path, data=None, timeout=30):
    url = f"{HOST}{path}"
    if data is not None:
        req = urllib.request.Request(url, data=json.dumps(data).encode(),
                                     headers={"Content-Type": "application/json"})
    else:
        req = urllib.request.Request(url)
    return json.load(urllib.request.urlopen(req, timeout=timeout))


def build_wf(c, version, steps, dry):
    name, mode, _, frames, seed, ir_file, ds_file, image = c
    prompt = open(ds_file if version == "ds" else ir_file).read().strip()
    wf = {
        "1": {"class_type": "UNETLoader", "inputs": {"unet_name": "minimax_h3_fl2va_pruned_fp8_scaled.safetensors", "weight_dtype": "default"}},
        "2": {"class_type": "CLIPLoader", "inputs": {"clip_name": CLIP, "type": "minimax", "device": "default"}},
        "3": {"class_type": "VAELoader", "inputs": {"vae_name": "minimax_h3_video_vae_fp16.safetensors"}},
        "4": {"class_type": "VAELoader", "inputs": {"vae_name": "minimax_h3_audio_vae_fp32.safetensors"}},
    }
    n = 5
    if mode == "i2v":
        wf["5"] = {"class_type": "LoadImage", "inputs": {"image": image}}
        wf["6"] = {"class_type": "MiniMaxH3ImageToVideo", "inputs": {
            "clip": ["2", 0], "vae": ["3", 0],
            "prompt": prompt, "width": 960, "height": 544,
            "length": frames, "first_frame": ["5", 0]}}
    else:
        wf["6"] = {"class_type": "MiniMaxH3ImageToVideo", "inputs": {
            "clip": ["2", 0], "vae": ["3", 0],
            "prompt": prompt, "width": 960, "height": 544,
            "length": frames}}
    wf["90"] = {"class_type": "MiniMaxH3TurboLoRA", "inputs": {
        "model": ["1", 0], "lora_name": LORA, "strength": 1.0, "low_vram": False}}
    wf["7"] = {"class_type": "MiniMaxH3TurboSampler", "inputs": {}}
    wf["8"] = {"class_type": "BasicScheduler", "inputs": {"model": ["90", 0], "scheduler": "simple", "steps": steps, "denoise": 1}}
    wf["9"] = {"class_type": "BasicGuider", "inputs": {"model": ["90", 0], "conditioning": ["6", 0]}}
    wf["10"] = {"class_type": "RandomNoise", "inputs": {"noise_seed": seed}}
    wf["11"] = {"class_type": "SamplerCustomAdvanced", "inputs": {"noise": ["10", 0], "guider": ["9", 0], "sampler": ["7", 0], "sigmas": ["8", 0], "latent_image": ["6", 1]}}
    wf["12"] = {"class_type": "VAEDecode", "inputs": {"samples": ["11", 0], "vae": ["3", 0]}}
    wf["13"] = {"class_type": "VAEDecodeAudio", "inputs": {"samples": ["11", 0], "vae": ["4", 0]}}
    wf["14"] = {"class_type": "CreateVideo", "inputs": {"images": ["12", 0], "fps": 24, "audio": ["13", 0], "bit_depth": 8}}
    wf["15"] = {"class_type": "SaveVideo", "inputs": {"video": ["14", 0], "filename_prefix": f"video/h3_prompt_ab/{name}_{version}", "format": "mp4", "codec": "auto"}}
    return wf


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--steps", type=int, default=8)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--only", help="只跑指定场景名（逗号分隔）")
    args = ap.parse_args()

    cases = []
    for c in SCENES:
        if args.only and c[0] not in args.only.split(","):
            continue
        cases.append((c, "ds"))
        cases.append((c, "ir"))

    if args.dry_run:
        for c, v in cases:
            wf = build_wf(c, v, args.steps, True)
            print(f"[dry] {c[0]}_{v} 镜数工作流节点: {sorted(wf.keys())}")
        return

    results = []
    for c, v in cases:
        t0 = time.time()
        try:
            pid = api("/prompt", {"prompt": build_wf(c, v, args.steps, False)})["prompt_id"]
        except urllib.error.HTTPError as e:
            msg = e.read().decode()[:300]
            print(f"[{c[0]}_{v}] ❌ 提交失败: {msg}", flush=True)
            results.append({"name": f"{c[0]}_{v}", "error": msg})
            continue
        print(f"[{c[0]}_{v}] 已入队 -> {pid}", flush=True)
        while True:
            time.sleep(10)
            h = api("/history")
            if pid in h and h[pid]["status"].get("completed"):
                secs = time.time() - t0
                print(f"[{c[0]}_{v}] 完成 {secs:.0f}s", flush=True)
                results.append({"name": f"{c[0]}_{v}", "secs": round(secs)})
                break
    print("结果:", json.dumps(results, ensure_ascii=False))


if __name__ == "__main__":
    main()
