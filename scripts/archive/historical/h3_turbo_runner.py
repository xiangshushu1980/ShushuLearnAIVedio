#!/usr/bin/env python3
"""H3 Turbo LoRA 测试 runner（2026-08-07 h3-turbo-pilot 任务线，独立文件不碰 h3_batch_runner.py）
用法: python3 h3_turbo_runner.py <cases.json> [--interval 15]
case 字段（在 h3_batch_runner 基础上）:
  lora: turbo lora 文件名（如 minimax_h3_turbo_4step_ema_ckpt850_pruned_comfyui.safetensors）
  lora_strength: 默认 1.0
  steps: 采样步数（turbo 档 4/6/8）
  unet: 默认 fl2va pruned fp8（快速档基线模型）
输出: <cases.json>.results.json（含每条耗时/错误）+ stdout 汇总
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
    }
    if c.get("clipproj"):  # ClipProj 分支：4B TE + 线性/MLP 投影（TE 瘦身 POC）
        wf["2"] = {"class_type": "ClipProjLoader", "inputs": {
            "clip_name": c.get("clip_name", "qwen3vl_4b_fp8_scaled.safetensors"),
            "type": "auto",
            "projection": c.get("projection", "mmh3-4b-ClipProj-celeb-mlp.safetensors"),
            "device": "cuda:0", "mode": "resident"}}
    if c.get("image"):  # fl2va I2V
        wf["5"] = {"class_type": "LoadImage", "inputs": {"image": c["image"]}}
        wf["6"] = {"class_type": "MiniMaxH3ImageToVideo", "inputs": {
            "clip": ["2",0], "vae": ["3",0],
            "prompt": c["prompt"], "width": c.get("width",768), "height": c.get("height",448),
            "length": c.get("length",124), "first_frame": ["5",0]}}
    # lora 分支：默认 Larryvrh 节点；loader=native 时走原生 LoraLoaderModelOnly + er_sde（lightx2v v0.1 官方蒸馏版，无需自定义节点）
    model_ref = "1"
    sampler_node = "7"
    if c.get("lora"):
        if c.get("loader") == "native":
            wf["90"] = {"class_type": "LoraLoaderModelOnly", "inputs": {
                "model": ["1",0], "lora_name": c["lora"], "strength_model": c.get("lora_strength", 0.75)}}
            model_ref = "90"
            wf["7"] = {"class_type": "KSamplerSelect", "inputs": {"sampler_name": c.get("sampler", "er_sde")}}
        else:
            wf["90"] = {"class_type": "MiniMaxH3TurboLoRA", "inputs": {
                "model": ["1",0], "lora_name": c["lora"],
                "strength": c.get("lora_strength", 1.0), "low_vram": False}}
            model_ref = "90"
            wf["7"] = {"class_type": "MiniMaxH3TurboSampler", "inputs": {}}
    else:
        wf["7"] = {"class_type": "KSamplerSelect", "inputs": {"sampler_name": "res_multistep"}}
    wf["8"] = {"class_type": "BasicScheduler", "inputs": {"model": [model_ref,0], "scheduler": "simple", "steps": c.get("steps",14), "denoise": 1}}
    wf["9"] = {"class_type": "BasicGuider", "inputs": {"model": [model_ref,0], "conditioning": ["6",0]}}
    wf["10"] = {"class_type": "RandomNoise", "inputs": {"noise_seed": c.get("seed",20260807)}}
    wf["11"] = {"class_type": "SamplerCustomAdvanced", "inputs": {"noise": ["10",0], "guider": ["9",0], "sampler": [sampler_node,0], "sigmas": ["8",0], "latent_image": ["6",1]}}
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
        print(f"❌ ComfyUI 不可用: {e}"); sys.exit(1)

    results = []
    for c in cases:
        t0 = time.time()
        try:
            pid = api("/prompt", {"prompt": build_wf(c), "client_id": "h3-turbo"})["prompt_id"]
        except urllib.error.HTTPError as e:
            print(f"[{c['name']}] ❌ 提交失败: {e.read().decode()[:200]}", flush=True)
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
            print(f"[{c['name']}] ⚠️ 提交后 100s 未见队列/历史，跳过", flush=True)
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
        print(f"[{c['name']}] {t1-t0:.0f}s {'❌ '+errs[0][:120] if errs else '✅'}", flush=True)
        results.append({"name": c["name"], "seconds": round(t1-t0), "error": errs[0] if errs else None})

    out = sys.argv[1] + ".results.json"
    json.dump(results, open(out, "w"), indent=1, ensure_ascii=False)
    print(f"\n结果: {out}")

if __name__ == "__main__":
    main()
