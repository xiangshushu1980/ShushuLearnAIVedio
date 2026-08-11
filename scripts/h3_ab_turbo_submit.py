#!/usr/bin/env python3
"""H3 A/B Turbo 批提交：t2v + TurboLoRA(ema_ckt850) + TurboSampler 4 步。
独立于 h3_turbo_runner.py（该 runner 的 t2v 分支有 bug：未建节点 6 却引用）。
用法：python3 scripts/h3_ab_turbo_submit.py /tmp/h3_ab_turbo_cases.json
"""
import json
import sys
import time
import urllib.request

HOST = "http://127.0.0.1:8188"
CLIP = "qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors"


def api(path, data=None, timeout=30):
    url = f"{HOST}{path}"
    if data is not None:
        req = urllib.request.Request(url, data=json.dumps(data).encode(),
                                     headers={"Content-Type": "application/json"})
    else:
        req = urllib.request.Request(url)
    return json.load(urllib.request.urlopen(req, timeout=timeout))


def build_wf(c):
    wf = {
        "1": {"class_type": "UNETLoader", "inputs": {"unet_name": c.get("unet", "minimax_h3_fl2va_pruned_fp8_scaled.safetensors"), "weight_dtype": "default"}},
        "2": {"class_type": "CLIPLoader", "inputs": {"clip_name": CLIP, "type": "minimax", "device": "default"}},
        "3": {"class_type": "VAELoader", "inputs": {"vae_name": "minimax_h3_video_vae_fp16.safetensors"}},
        "4": {"class_type": "VAELoader", "inputs": {"vae_name": "minimax_h3_audio_vae_fp32.safetensors"}},
        # t2v：MiniMaxH3ImageToVideo 不带 first_frame 即文生视频模式
        "6": {"class_type": "MiniMaxH3ImageToVideo", "inputs": {
            "clip": ["2", 0], "vae": ["3", 0],
            "prompt": c["prompt"], "width": c.get("width", 960), "height": c.get("height", 544),
            "length": c.get("length", 240)}},
    }
    model_ref = "1"
    sampler_node = "7"
    if c.get("lora"):
        wf["90"] = {"class_type": "MiniMaxH3TurboLoRA", "inputs": {
            "model": ["1", 0], "lora_name": c["lora"],
            "strength": c.get("lora_strength", 1.0), "low_vram": False}}
        model_ref = "90"
        wf["7"] = {"class_type": "MiniMaxH3TurboSampler", "inputs": {}}
    else:
        wf["7"] = {"class_type": "KSamplerSelect", "inputs": {"sampler_name": "res_multistep"}}
    wf["8"] = {"class_type": "BasicScheduler", "inputs": {"model": [model_ref, 0], "scheduler": "simple", "steps": c.get("steps", 4), "denoise": 1}}
    wf["9"] = {"class_type": "BasicGuider", "inputs": {"model": [model_ref, 0], "conditioning": ["6", 0]}}
    wf["10"] = {"class_type": "RandomNoise", "inputs": {"noise_seed": c.get("seed", 20260808)}}
    wf["11"] = {"class_type": "SamplerCustomAdvanced", "inputs": {"noise": ["10", 0], "guider": ["9", 0], "sampler": [sampler_node, 0], "sigmas": ["8", 0], "latent_image": ["6", 1]}}
    wf["12"] = {"class_type": "VAEDecode", "inputs": {"samples": ["11", 0], "vae": ["3", 0]}}
    wf["13"] = {"class_type": "VAEDecodeAudio", "inputs": {"samples": ["11", 0], "vae": ["4", 0]}}
    wf["14"] = {"class_type": "CreateVideo", "inputs": {"images": ["12", 0], "fps": 24, "audio": ["13", 0], "bit_depth": 8}}
    wf["15"] = {"class_type": "SaveVideo", "inputs": {"video": ["14", 0], "filename_prefix": c["prefix"], "format": "mp4", "codec": "auto"}}
    return wf


def main():
    cases = json.load(open(sys.argv[1]))
    results = []
    for c in cases:
        t0 = time.time()
        try:
            pid = api("/prompt", {"prompt": build_wf(c)})["prompt_id"]
        except urllib.error.HTTPError as e:
            msg = e.read().decode()[:300]
            print(f"[{c['name']}] ❌ 提交失败: {msg}", flush=True)
            results.append({"name": c["name"], "error": msg})
            continue
        print(f"[{c['name']}] 已入队 -> {pid}", flush=True)
        # 等待本条完成（队列串行，轮询 history）
        while True:
            time.sleep(10)
            h = api("/history")
            if pid in h and h[pid]["status"].get("completed"):
                secs = time.time() - t0
                print(f"[{c['name']}] 完成 {secs:.0f}s", flush=True)
                results.append({"name": c["name"], "secs": round(secs)})
                break
    print("结果:", json.dumps(results, ensure_ascii=False))
    json.dump(results, open(sys.argv[1] + ".results.json", "w"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
