#!/usr/bin/env python3
"""批量生成分镜图（KREA 扁平插画，16:9）
用法: python gen_scenes.py scenes_test.json [--prefix img_debate2] [--seed N]
读入 scenes JSON（id/s/p），为每个场景调 ComfyUI KREA 生图，存 output/<prefix>/<id>.png
"""
import json, sys, subprocess, time, argparse

API = "http://127.0.0.1:8188"
STYLE = ("flat design, minimalist vector illustration, smooth clean shapes, "
         "muted warm color palette, modern flat illustration style, "
         "16:9 widescreen, no text, no watermark, "
         "human people as debaters, characters are clearly human figures, ")
# 负面提示：明确禁止音响/音箱/扩音设备
NEG = ("loudspeaker, audio speaker, speaker device, loudspeaker on stand, megaphone, "
       "sound system, amplifier, speaker cabinet, no devices, "
       "blurry, low quality, text, watermark, jpeg artifacts, bad anatomy")

def wf(prompt, seed, prefix, sid):
    return {
        "1": {"class_type": "UNETLoader", "inputs": {"unet_name": "krea2_turbo_fp8.safetensors", "weight_dtype": "default"}},
        "2": {"class_type": "CLIPLoader", "inputs": {"clip_name": "qwen3vl_4b_fp8_scaled.safetensors", "type": "krea2", "device": "default"}},
        "3": {"class_type": "VAELoader", "inputs": {"vae_name": "qwen_image_vae.safetensors"}},
        "4": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["2", 0], "text": prompt}},
        "5": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["2", 0], "text": NEG}},
        "6": {"class_type": "EmptyLatentImage", "inputs": {"width": 1024, "height": 576, "batch_size": 1}},
        "7": {"class_type": "KSampler", "inputs": {"model": ["1", 0], "positive": ["4", 0], "negative": ["5", 0],
              "latent_image": ["6", 0], "seed": seed, "steps": 8, "cfg": 1.0, "sampler_name": "er_sde", "scheduler": "simple", "denoise": 1.0}},
        "8": {"class_type": "VAEDecode", "inputs": {"samples": ["7", 0], "vae": ["3", 0]}},
        "9": {"class_type": "SaveImage", "inputs": {"images": ["8", 0], "filename_prefix": f"{prefix}/{sid}"}},
    }

def queue(workflow):
    r = subprocess.run(["curl", "-s", "-X", "POST", f"{API}/prompt",
                        "-H", "Content-Type: application/json",
                        "-d", json.dumps({"prompt": workflow})],
                       capture_output=True, text=True)
    try:
        return json.loads(r.stdout).get("prompt_id")
    except Exception:
        return None

def wait_queue_empty(timeout=900):
    t0 = time.time()
    while time.time() - t0 < timeout:
        r = subprocess.run(["curl", "-s", f"{API}/queue"], capture_output=True, text=True)
        try:
            q = json.loads(r.stdout)
            n = len(q.get("queue_running", [])) + len(q.get("queue_pending", []))
        except Exception:
            n = 1
        if n == 0:
            return True
        time.sleep(3)
    return False

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("scenes", help="scenes JSON")
    ap.add_argument("--prefix", default="img_debate2")
    ap.add_argument("--seed", type=int, default=20260810)
    args = ap.parse_args()

    scenes = json.load(open(args.scenes))
    # 提交所有
    for i, s in enumerate(scenes):
        pid = queue(wf(STYLE + s["p"], args.seed + i, args.prefix, s["id"]))
        print(f"[{s['id']}] 入队: {pid}")
    print("等待生成...")
    ok = wait_queue_empty()
    print("完成" if ok else "超时")

if __name__ == "__main__":
    main()
