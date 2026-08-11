#!/usr/bin/env python3
"""双轨盲区补测 runner（2026-08-09 h3-prompt-agent 任务线，独立文件）

测什么：快车道（fl2va i2v/firstlast + turbo lora）与慢车道（ref2va 多图）在最终
定档配置下的 速度/显存/兼容性——纯客观参数，无目测。

显存纪律（用户 2026-08-09）：
- 跑批前估算（见 cases 注释），串行一次一个任务
- 轮询时监控 vram_used，>23.6GB 打印警告
- 错误含 out of memory → abort 剩余 case（爆显存任务不会自己继续）

用法: python3 h3_gap_runner.py <cases.json> [--interval 10]
case 字段:
  name, mode: t2v|i2v|firstlast|ref2va
  unet(默认 fl2va fp8), lora(可选), lora_strength, steps(默认20), sampler(auto)
  width/height/length, seed, prompt(内联或 @文件)
  images: [相对 input/ 的路径...]  -> mode 决定语义:
    i2v: [first]; firstlast: [first, last]; ref2va: [ref1, ref2...]
  prefix: SaveVideo 前缀（子目录直接带）
  chain_from: {"case": "A2", "frame": "last"} —— 本 case 首帧用 A2 产物末帧
输出: <cases.json>.results.json（耗时/错误/产物路径/显存峰值）
"""
import json, os, re, subprocess, sys, time, urllib.request

HOST = "http://127.0.0.1:8188"
INPUT_DIR = "/home/sean/projects/ComfyUI/input"
OUTPUT_DIR = "/home/sean/projects/ComfyUI/output"
CHAIN_DIR = os.path.join(INPUT_DIR, "start", "gap_chain")
VRAM_WARN = 23.6 * 1024**3

TURBO_LORA = "minimax_h3_turbo_v4_step600_ema.safetensors"
FL2VA_FP8 = "minimax_h3_fl2va_pruned_fp8_scaled.safetensors"
REF2VA_INT8 = "minimax_h3_ref2va_pruned_int8_convrot.safetensors"
CLIP = "qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors"


def api(path, data=None, timeout=30):
    url = f"{HOST}{path}"
    if data is not None:
        req = urllib.request.Request(url, data=json.dumps(data).encode(),
            headers={"Content-Type": "application/json"})
    else:
        req = urllib.request.Request(url)
    return json.load(urllib.request.urlopen(req, timeout=timeout))


def vram_used_gb():
    try:
        st = api("/system_stats")
        d = st["devices"][0]
        if "vram_used" in d:
            return d["vram_used"] / 1024**3
        return (d["vram_total"] - d["vram_free"]) / 1024**3
    except Exception:
        return -1


def add_image(wf, node_id, rel_path):
    wf[str(node_id)] = {"class_type": "LoadImage", "inputs": {"image": rel_path}}
    return [str(node_id), 0]


def build_wf(c):
    wf = {
        "1": {"class_type": "UNETLoader", "inputs": {"unet_name": c.get("unet", FL2VA_FP8), "weight_dtype": "default"}},
        "2": {"class_type": "CLIPLoader", "inputs": {"clip_name": CLIP, "type": "minimax", "device": "default"}},
        "3": {"class_type": "VAELoader", "inputs": {"vae_name": "minimax_h3_video_vae_fp16.safetensors"}},
        "4": {"class_type": "VAELoader", "inputs": {"vae_name": "minimax_h3_audio_vae_fp32.safetensors"}},
    }
    prompt = c["prompt"]
    if prompt.startswith("@"):
        prompt = open(prompt[1:]).read()

    img_refs = {}  # LoadImage node_id -> rel path
    n = 50  # 主节点 1-15 区，图像节点从 50 起（firstlast 双图曾与主节点 6 冲突）
    for i, p in enumerate(c.get("images", [])):
        img_refs[i] = (n, p)
        wf[str(n)] = {"class_type": "LoadImage", "inputs": {"image": p}}
        n += 1

    aud_refs = {}  # LoadAudio node_id -> rel path
    for i, p in enumerate(c.get("audios", [])):
        aud_refs[i] = (n, p)
        wf[str(n)] = {"class_type": "LoadAudio", "inputs": {"audio": p}}
        n += 1

    mode = c["mode"]
    if mode in ("t2v", "i2v", "firstlast"):
        inp = {"clip": ["2", 0], "vae": ["3", 0], "prompt": prompt,
               "width": c["width"], "height": c["height"], "length": c["length"]}
        if mode in ("i2v", "firstlast") and 0 in img_refs:
            inp["first_frame"] = [str(img_refs[0][0]), 0]
        if mode == "firstlast":
            inp["last_frame"] = [str(img_refs[1][0]), 0]
        wf["6"] = {"class_type": "MiniMaxH3ImageToVideo", "inputs": inp}
    else:  # ref2va
        inp = {"clip": ["2", 0], "vae": ["3", 0], "audio_vae": ["4", 0],
               "prompt": prompt, "width": c["width"], "height": c["height"],
               "length": c["length"], "ref_image_size": c.get("ref_image_size", "match")}
        for i, (node_id, _) in img_refs.items():
            inp[f"ref_images.ref_image_{i}"] = [str(node_id), 0]
        for i, (node_id, _) in aud_refs.items():
            inp[f"ref_audios.ref_audio_{i}"] = [str(node_id), 0]
        wf["6"] = {"class_type": "MiniMaxH3ReferenceToVideo", "inputs": inp}

    # sampler / lora
    model_ref, sampler_node = "1", "7"
    lora = c.get("lora")
    if lora:
        wf["90"] = {"class_type": "MiniMaxH3TurboLoRA",
                    "inputs": {"model": ["1", 0], "lora_name": lora,
                               "strength": c.get("lora_strength", 1.0), "low_vram": False}}
        model_ref = "90"
        wf["7"] = {"class_type": "MiniMaxH3TurboSampler", "inputs": {}}
    else:
        wf["7"] = {"class_type": "KSamplerSelect", "inputs": {"sampler_name": "res_multistep"}}
    wf["8"] = {"class_type": "BasicScheduler", "inputs": {
        "model": [model_ref, 0], "scheduler": "simple",
        "steps": c.get("steps", 20), "denoise": 1.0}}
    wf["9"] = {"class_type": "BasicGuider", "inputs": {"model": [model_ref, 0], "conditioning": ["6", 0]}}
    wf["10"] = {"class_type": "RandomNoise", "inputs": {"noise_seed": c.get("seed", 20260809)}}
    wf["11"] = {"class_type": "SamplerCustomAdvanced", "inputs": {
        "noise": ["10", 0], "guider": ["9", 0], "sampler": [sampler_node, 0],
        "sigmas": ["8", 0], "latent_image": ["6", 1]}}
    wf["12"] = {"class_type": "VAEDecode", "inputs": {"samples": ["11", 0], "vae": ["3", 0]}}
    wf["13"] = {"class_type": "VAEDecodeAudio", "inputs": {"samples": ["11", 0], "vae": ["4", 0]}}
    wf["14"] = {"class_type": "CreateVideo", "inputs": {"images": ["12", 0], "fps": 24, "audio": ["13", 0], "bit_depth": 8}}
    wf["15"] = {"class_type": "SaveVideo", "inputs": {
        "video": ["14", 0], "filename_prefix": c["prefix"], "format": "mp4", "codec": "auto"}}
    return wf


def extract_last_frame(video_path, out_png):
    """提取视频末帧（帧链用）"""
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0",
                        "-count_frames", "-show_entries", "stream=nb_read_frames",
                        "-of", "csv=p=0", video_path], capture_output=True, text=True)
    nframes = int(r.stdout.strip() or 0) or 120
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", video_path,
                    "-vf", f"select=eq(n\\,{nframes-1})", "-frames:v", "1", out_png],
                   capture_output=True)
    return out_png


def find_output(prefix):
    base = os.path.join(OUTPUT_DIR, prefix)
    cands = sorted(glob(base + "*.mp4"))
    return cands[-1] if cands else None


def glob(pattern):
    import glob as _g
    return _g.glob(pattern)


def main():
    cases = json.load(open(sys.argv[1]))
    top_prompt = cases.get("prompt")
    top_seed = cases.get("seed")
    cases = cases["cases"]
    for c in cases:
        c.setdefault("prompt", top_prompt)
        c.setdefault("seed", top_seed)
    interval = 10
    if "--interval" in sys.argv:
        interval = int(sys.argv[sys.argv.index("--interval") + 1])
    os.makedirs(CHAIN_DIR, exist_ok=True)
    results = []
    done = {r["name"]: r for r in json.load(open(sys.argv[1] + ".results.json"))} if os.path.exists(sys.argv[1] + ".results.json") else {}
    aborted = False

    for c in cases:
        if c["name"] in done:
            prev = done[c["name"]]
            if prev.get("error") and "skipped (OOM abort)" not in prev["error"]:
                # 失败/提交失败的 case 重跑（覆盖旧记录）
                print(f"[{c['name']}] 上次失败({prev['error'][:60]}...)，重跑", flush=True)
            else:
                print(f"[{c['name']}] 已存在结果，跳过", flush=True)
                continue
        if aborted:
            print(f"[{c['name']}] ⛔ OOM abort，跳过", flush=True)
            results.append({"name": c["name"], "error": "skipped (OOM abort)"})
            continue

        wf = build_wf(c)
        # 帧链：从已完成的 case 提取末帧作为本 case 首帧
        cf = c.get("chain_from")
        if cf:
            src = done.get(cf["case"]) or next((r for r in results if r["name"] == cf["case"]), None)
            if not src or src.get("error") or not src.get("video"):
                print(f"[{c['name']}] ❌ 帧链依赖 {cf['case']} 不可用，跳过", flush=True)
                results.append({"name": c["name"], "error": f"chain dep {cf['case']} missing"})
                continue
            chain_png = os.path.join(CHAIN_DIR, f"{cf['case']}_last.png")
            extract_last_frame(src["video"], chain_png)
            rel = os.path.relpath(chain_png, INPUT_DIR)
            wf["50"]["inputs"]["image"] = rel  # LoadImage node 50 = first frame（images 从 50 起编号）
            print(f"[{c['name']}] 帧链: {cf['case']} 末帧 -> {rel}", flush=True)

        v0 = vram_used_gb()
        t0 = time.time()
        peak = v0
        try:
            pid = api("/prompt", {"prompt": wf, "client_id": "h3-gap"})["prompt_id"]
        except urllib.error.HTTPError as e:
            msg = e.read().decode()[:300]
            print(f"[{c['name']}] ❌ 提交失败: {msg}", flush=True)
            results.append({"name": c["name"], "error": "submit: " + msg})
            continue
        # 等待完成
        err = None
        while True:
            time.sleep(interval)
            v = vram_used_gb()
            peak = max(peak, v)
            if v > VRAM_WARN:
                print(f"[{c['name']}] ⚠️ 显存 {v:.1f}GB 超阈值 {VRAM_WARN/1024**3:.1f}GB", flush=True)
            run, pend = api("/queue")["queue_running"], api("/queue")["queue_pending"]
            running = [x[1] for x in run] + [x[1] for x in pend]
            if pid not in running:
                break
        t1 = time.time()
        h = api(f"/history/{pid}")
        msgs = h.get(pid, {}).get("status", {}).get("messages", [])
        errs = [m[1].get("exception_message", "") for m in msgs if m[0] == "execution_error"]
        if errs:
            err = errs[0][:300]
        video = None if err else find_output(c["prefix"])
        if err:
            print(f"[{c['name']}] ❌ {t1-t0:.0f}s {err}", flush=True)
        else:
            print(f"[{c['name']}] ✅ {t1-t0:.0f}s 峰值显存 {peak:.1f}GB -> {video}", flush=True)
        rec = {"name": c["name"], "seconds": round(t1 - t0), "peak_vram_gb": round(peak, 1),
               "error": err, "video": video}
        results.append(rec)
        done[c["name"]] = rec
        if err and ("out of memory" in err.lower() or "cuda" in err.lower() and "memory" in err.lower()):
            print("⛔ OOM 检测，abort 剩余 case", flush=True)
            aborted = True

    out = sys.argv[1] + ".results.json"
    final = []
    for c in cases:
        if c["name"] in done:
            final.append(done[c["name"]])
    json.dump(final, open(out, "w"), indent=1, ensure_ascii=False)
    print(f"\n结果: {out}")
    for r in results:
        print(f"  {r['name']}: {r.get('seconds','?')}s vram={r.get('peak_vram_gb')} {'❌ '+r['error'] if r.get('error') else '✅'}")


if __name__ == "__main__":
    main()
