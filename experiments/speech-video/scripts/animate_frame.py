#!/usr/bin/env python3
"""用 Wan2.2 I2V Lightning 把分镜图按上下文动画成视频
用法: python3 animate_frame.py <img> <motion_prompt> <out_prefix> [--w 832] [--h 480] [--len 73]
生成 SaveVideo filename_prefix=video/<out_prefix> 到 ComfyUI output
"""
import json, sys, subprocess, time, argparse, os, urllib.request

API = "http://127.0.0.1:8188"

def upload(image_path):
    import requests
    with open(image_path, "rb") as f:
        r = requests.post(f"{API}/upload/image", files={"image": f}, data={"overwrite": "true"})
        return r.json()["name"]

def build_wf(img_name, motion, w, h, length, seed, prefix):
    neg = "色调艳丽，过曝，静态，细节模糊不清，字幕，风格，作品，画作，画面，静止，整体发灰，最差质量，低质量"
    return {
      "1":{"class_type":"UnetLoaderGGUF","inputs":{"unet_name":"Wan2.2-I2V-A14B-HighNoise-Q4_K_S.gguf","weight_dtype":"default"}},
      "2":{"class_type":"ModelSamplingSD3","inputs":{"model":["1",0],"shift":5.0}},
      "3":{"class_type":"LoraLoaderModelOnly","inputs":{"model":["2",0],"lora_name":"wan2.2_i2v_lightx2v_4steps_lora_v1_high_noise.safetensors","strength_model":1.0}},
      "4":{"class_type":"UnetLoaderGGUF","inputs":{"unet_name":"Wan2.2-I2V-A14B-LowNoise-Q4_K_S.gguf","weight_dtype":"default"}},
      "5":{"class_type":"ModelSamplingSD3","inputs":{"model":["4",0],"shift":5.0}},
      "6":{"class_type":"LoraLoaderModelOnly","inputs":{"model":["5",0],"lora_name":"wan2.2_i2v_lightx2v_4steps_lora_v1_low_noise.safetensors","strength_model":1.0}},
      "7":{"class_type":"CLIPLoaderGGUF","inputs":{"clip_name":"umt5-xxl-encoder-Q5_K_S.gguf","type":"wan","device":"default"}},
      "8":{"class_type":"CLIPTextEncode","inputs":{"clip":["7",0],"text":motion}},
      "9":{"class_type":"CLIPTextEncode","inputs":{"clip":["7",0],"text":neg}},
      "10":{"class_type":"VAELoader","inputs":{"vae_name":"wan_2.1_vae.safetensors"}},
      "11":{"class_type":"LoadImage","inputs":{"image":img_name}},
      "12":{"class_type":"WanImageToVideo","inputs":{"width":w,"height":h,"length":length,"batch_size":1,"positive":["8",0],"negative":["9",0],"vae":["10",0],"start_image":["11",0]}},
      "13":{"class_type":"KSamplerAdvanced","inputs":{"model":["3",0],"positive":["12",0],"negative":["12",1],"latent_image":["12",2],"add_noise":"enable","noise_seed":seed,"steps":6,"cfg":1.0,"sampler_name":"euler","scheduler":"simple","start_at_step":0,"end_at_step":3,"return_with_leftover_noise":"enable"}},
      "14":{"class_type":"KSamplerAdvanced","inputs":{"model":["6",0],"positive":["12",0],"negative":["12",1],"latent_image":["13",0],"add_noise":"disable","noise_seed":seed,"steps":6,"cfg":1.0,"sampler_name":"euler","scheduler":"simple","start_at_step":3,"end_at_step":6,"return_with_leftover_noise":"disable"}},
      "15":{"class_type":"VAEDecode","inputs":{"samples":["14",0],"vae":["10",0]}},
      "16":{"class_type":"CreateVideo","inputs":{"images":["15",0],"fps":16}},
      "17":{"class_type":"SaveVideo","inputs":{"video":["16",0],"filename_prefix":f"video/{prefix}","format":"auto","codec":"auto"}},
    }

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("img"); ap.add_argument("motion"); ap.add_argument("prefix")
    ap.add_argument("--w", type=int, default=832); ap.add_argument("--h", type=int, default=480)
    ap.add_argument("--len", type=int, default=73); ap.add_argument("--seed", type=int, default=20260801)
    args = ap.parse_args()
    img_name = upload(args.img)
    wf = build_wf(img_name, args.motion, args.w, args.h, args.len, args.seed, args.prefix)
    req = urllib.request.Request(f"{API}/prompt", data=json.dumps({"prompt": wf}).encode(), headers={"Content-Type":"application/json"})
    pid = json.loads(urllib.request.urlopen(req).read())["prompt_id"]
    print("enqueued", pid, "| img", img_name)
    # 等待
    start=time.time()
    while time.time()-start < 1800:
        time.sleep(5)
        try:
            hist = json.loads(urllib.request.urlopen(f"{API}/history/{pid}").read())
            if pid in hist:
                print("done in", round(time.time()-start,1),"s")
                return
        except Exception: pass
    print("timeout")

if __name__ == "__main__":
    main()
