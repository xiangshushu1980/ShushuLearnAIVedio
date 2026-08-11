#!/usr/bin/env python3
"""H3 Turbo LoRA v1.0 测试 runner（2026-08-11 h3-today-testing 任务线，独立文件）
用法: python3 h3_v1_test_runner.py <cases.json> [--interval 15]
case 字段:
  name / lora / lora_strength(默认1.0) / steps / unet(默认 fp8) /
  sampler: "turbo"(MiniMaxH3TurboSampler, 内置12/3双调度兼容) | "res" (res_multistep)
  shift_video / shift_audio: 设置时插入 MiniMaxH3SigmaShift 节点（res 模式用）
  image / prompt / width / height / length / seed / prefix
输出: <cases.json>.results.json（耗时/错误）
"""
import json, sys, time, urllib.request, urllib.error

HOST = "http://127.0.0.1:8188"
DEFAULT_UNET = "minimax_h3_fl2va_pruned_fp8_scaled.safetensors"
CLIP = "qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors"

def api(path, data=None, timeout=30):
    url = f"{HOST}{path}"
    if data is not None:
        req = urllib.request.Request(url, data=json.dumps(data).encode(),
            headers={"Content-Type": "application/json"})
    else:
        req = urllib.request.Request(url)
    return json.load(urllib.request.urlopen(req, timeout=timeout))

def queue_pids():
    q = api("/queue")
    return ([x[1] for x in q["queue_running"]], [x[1] for x in q["queue_pending"]])

def build_wf(c):
    wf = {
        "1": {"class_type": "UNETLoader", "inputs": {"unet_name": c.get("unet", DEFAULT_UNET), "weight_dtype": "default"}},
        "2": {"class_type": "CLIPLoader", "inputs": {"clip_name": CLIP, "type": "minimax", "device": "default"}},
        "3": {"class_type": "VAELoader", "inputs": {"vae_name": "minimax_h3_video_vae_fp16.safetensors"}},
        "4": {"class_type": "VAELoader", "inputs": {"vae_name": "minimax_h3_audio_vae_fp32.safetensors"}},
        "5": {"class_type": "LoadImage", "inputs": {"image": c["image"]}},
        "6": {"class_type": "MiniMaxH3ImageToVideo", "inputs": {
            "clip": ["2",0], "vae": ["3",0],
            "prompt": c["prompt"], "width": c.get("width",768), "height": c.get("height",448),
            "length": c.get("length",192), "first_frame": ["5",0]}},
    }
    model_ref = "1"
    if c.get("lora"):
        wf["90"] = {"class_type": "MiniMaxH3TurboLoRA", "inputs": {
            "model": ["1",0], "lora_name": c["lora"],
            "strength": c.get("lora_strength", 1.0), "low_vram": False}}
        model_ref = "90"
    if c.get("shift_video") is not None:
        wf["91"] = {"class_type": "MiniMaxH3SigmaShift", "inputs": {
            "model": [model_ref,0],
            "shift_video": c["shift_video"], "shift_audio": c.get("shift_audio", 3.0)}}
        model_ref = "91"
    if c.get("sampler") == "turbo":
        wf["7"] = {"class_type": "MiniMaxH3TurboSampler", "inputs": {}}
    else:
        wf["7"] = {"class_type": "KSamplerSelect", "inputs": {"sampler_name": "res_multistep"}}
    wf["8"] = {"class_type": "BasicScheduler", "inputs": {"model": [model_ref,0], "scheduler": "simple", "steps": c.get("steps",8), "denoise": 1}}
    wf["9"] = {"class_type": "BasicGuider", "inputs": {"model": [model_ref,0], "conditioning": ["6",0]}}
    wf["10"] = {"class_type": "RandomNoise", "inputs": {"noise_seed": c.get("seed",20260811)}}
    wf["11"] = {"class_type": "SamplerCustomAdvanced", "inputs": {"noise": ["10",0], "guider": ["9",0], "sampler": ["7",0], "sigmas": ["8",0], "latent_image": ["6",1]}}
    wf["12"] = {"class_type": "VAEDecode", "inputs": {"samples": ["11",0], "vae": ["3",0]}}
    wf["13"] = {"class_type": "VAEDecodeAudio", "inputs": {"samples": ["11",0], "vae": ["4",0]}}
    wf["14"] = {"class_type": "CreateVideo", "inputs": {"images": ["12",0], "fps": 24, "audio": ["13",0], "bit_depth": 8}}
    wf["15"] = {"class_type": "SaveVideo", "inputs": {"video": ["14",0], "filename_prefix": c["prefix"], "format": "mp4", "codec": "auto"}}
    return wf

def main():
    cases = json.load(open(sys.argv[1]))
    interval = 15
    if "--interval" in sys.argv:
        interval = int(sys.argv[sys.argv.index("--interval")+1])
    try:
        st = api("/system_stats")
        print(f"ComfyUI 就绪: {st['devices'][0]['name']}", flush=True)
    except Exception as e:
        print(f"ComfyUI 不可用: {e}"); sys.exit(1)

    results = []
    for c in cases:
        t0 = time.time()
        try:
            pid = api("/prompt", {"prompt": build_wf(c), "client_id": "h3-v1"})["prompt_id"]
        except urllib.error.HTTPError as e:
            print(f"[{c['name']}] 提交失败: {e.read().decode()[:200]}", flush=True)
            results.append({"name": c["name"], "error": "submit failed"}); continue
        seen = False
        for _ in range(20):
            time.sleep(5)
            run, pend = queue_pids()
            if pid in run or pid in pend:
                seen = True; break
            h = api(f"/history/{pid}")
            if pid in h:
                seen = True; break
        if not seen:
            print(f"[{c['name']}] 提交后 100s 未见队列/历史", flush=True)
            results.append({"name": c["name"], "error": "not seen in queue"}); continue
        while True:
            time.sleep(interval)
            run, pend = queue_pids()
            if pid not in run and pid not in pend:
                break
        t1 = time.time()
        h = api(f"/history/{pid}")
        msgs = h.get(pid, {}).get("status", {}).get("messages", [])
        errs = [m[1].get("exception_message","") for m in msgs if m[0]=="execution_error"]
        ok = not errs
        print(f"[{c['name']}] {t1-t0:.0f}s {'ERROR '+errs[0][:150] if errs else 'OK'}", flush=True)
        results.append({"name": c["name"], "seconds": round(t1-t0), "error": errs[0] if errs else None})

    out = sys.argv[1] + ".results.json"
    json.dump(results, open(out, "w"), indent=1, ensure_ascii=False)
    print(f"\n结果: {out}")

if __name__ == "__main__":
    main()
