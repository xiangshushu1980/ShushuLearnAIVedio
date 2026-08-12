#!/usr/bin/env python3
"""Motion Context 跨段连续性验证 runner（2026-08-12 mc-test 任务线，独立文件）

测什么：H3 Motion Context 节点（NikoDemon80/ComfyUI-H3-Motion-Context）能否解决
跨段衔接——两段链式（MC）vs 现有静态锚基线（agreement_v2 已验收产物）。

用法: python3 h3_mc_runner.py <cases.json> [--interval 10]
case 字段（继承 h3_gap_runner 约定）:
  name, mode: ref2va
  unet(默认 ref2va int8), steps(默认20), width/height/length, seed, prompt(@file)
  images: [相对 input/ 的路径...], audios: [..]
  prefix: SaveVideo 前缀
  save_latent: {"filename_prefix": "h3_context/clip", "clip_index": 1}  # 采样后存 AV latent
  mc: {"context_length": "22", "audio_context_length": 24,
       "latent_path": "h3_context", "clip_index": 1}  # 段2 加 MC 节点（从 clip_index 继续）

参考: /home/sean/projects/ComfyUI/custom_nodes/ComfyUI-H3-Motion-Context/
  README + example_workflows（节点连接与参数默认值）
显存纪律：串行一次一个任务；轮询监控 vram_used；>23.6GB 警告；OOM abort。
"""
import json, os, subprocess, sys, time, urllib.request

HOST = "http://127.0.0.1:8188"
INPUT_DIR = "/home/sean/projects/ComfyUI/input"
OUTPUT_DIR = "/home/sean/projects/ComfyUI/output"
VRAM_WARN = 23.6 * 1024**3

REF2VA_INT8 = "minimax_h3_ref2va_pruned_int8_convrot.safetensors"
CLIP = "qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors"
VIDEO_VAE = "minimax_h3_video_vae_fp16.safetensors"
AUDIO_VAE = "minimax_h3_audio_vae_fp32.safetensors"


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


def glob(pattern):
    import glob as _g
    return _g.glob(pattern)


def find_output(prefix):
    base = os.path.join(OUTPUT_DIR, prefix)
    cands = sorted(glob(base + "*.mp4"))
    return cands[-1] if cands else None


def build_wf(c):
    """ref2va 工作流（对齐 h3_gap_runner 节点布局，1-15 不动），
    16+ 为 MC 专属节点。"""
    wf = {
        "1": {"class_type": "UNETLoader", "inputs": {"unet_name": c.get("unet", REF2VA_INT8), "weight_dtype": "default"}},
        "2": {"class_type": "CLIPLoader", "inputs": {"clip_name": CLIP, "type": "minimax", "device": "default"}},
        "3": {"class_type": "VAELoader", "inputs": {"vae_name": VIDEO_VAE}},
        "4": {"class_type": "VAELoader", "inputs": {"vae_name": AUDIO_VAE}},
    }
    prompt = c["prompt"]
    if prompt.startswith("@"):
        prompt = open(prompt[1:]).read()

    img_refs, aud_refs = {}, {}
    n = 50
    for i, p in enumerate(c.get("images", [])):
        img_refs[i] = (n, p)
        wf[str(n)] = {"class_type": "LoadImage", "inputs": {"image": p}}
        n += 1
    for i, p in enumerate(c.get("audios", [])):
        aud_refs[i] = (n, p)
        wf[str(n)] = {"class_type": "LoadAudio", "inputs": {"audio": p}}
        n += 1

    inp = {"clip": ["2", 0], "vae": ["3", 0], "audio_vae": ["4", 0],
           "prompt": prompt, "width": c["width"], "height": c["height"],
           "length": c["length"], "ref_image_size": c.get("ref_image_size", "match")}
    for i, (node_id, _) in img_refs.items():
        inp[f"ref_images.ref_image_{i}"] = [str(node_id), 0]
    for i, (node_id, _) in aud_refs.items():
        inp[f"ref_audios.ref_audio_{i}"] = [str(node_id), 0]
    wf["6"] = {"class_type": "MiniMaxH3ReferenceToVideo", "inputs": inp}

    wf["7"] = {"class_type": "KSamplerSelect", "inputs": {"sampler_name": "res_multistep"}}
    wf["8"] = {"class_type": "BasicScheduler", "inputs": {
        "model": ["1", 0], "scheduler": "simple",
        "steps": c.get("steps", 20), "denoise": 1.0}}
    wf["9"] = {"class_type": "BasicGuider", "inputs": {"model": ["1", 0], "conditioning": ["6", 0]}}
    wf["10"] = {"class_type": "RandomNoise", "inputs": {"noise_seed": c.get("seed", 20260812)}}
    wf["11"] = {"class_type": "SamplerCustomAdvanced", "inputs": {
        "noise": ["10", 0], "guider": ["9", 0], "sampler": ["7", 0],
        "sigmas": ["8", 0], "latent_image": ["6", 1]}}

    mc = c.get("mc")
    trim = None
    if mc:
        # 16 LoadLatent -> 17 MotionContext -> 9 BasicGuider / 18 Trim
        wf["16"] = {"class_type": "MiniMaxH3MotionContextLoadLatent", "inputs": {
            "latent_path": mc.get("latent_path", "h3_context"),
            "clip_index": mc.get("clip_index", 1)}}
        wf["17"] = {"class_type": "MiniMaxH3MotionContext", "inputs": {
            "conditioning": ["6", 0],
            "vae": ["3", 0],
            "latent": ["6", 1],
            "context_length": mc.get("context_length", "22"),
            "audio_context_length": mc.get("audio_context_length", 24),
            "context_latent": ["16", 0]}}
        wf["9"]["inputs"]["conditioning"] = ["17", 0]
        trim = "18"

    wf["12"] = {"class_type": "VAEDecode", "inputs": {"samples": ["11", 0], "vae": ["3", 0]}}
    wf["13"] = {"class_type": "VAEDecodeAudio", "inputs": {"samples": ["11", 0], "vae": ["4", 0]}}

    if trim:
        # Trim 去掉 pin 头部（trim_frames 从 MC 节点 output1 取），音画同步裁
        wf["18"] = {"class_type": "MiniMaxH3MotionContextTrim", "inputs": {
            "images": ["12", 0], "trim_frames": ["17", 1],
            "audio": ["13", 0], "fps": 24.0, "match_tail": True}}
        wf["14"] = {"class_type": "CreateVideo", "inputs": {
            "images": ["18", 0], "fps": 24, "audio": ["18", 1], "bit_depth": 8}}
    else:
        wf["14"] = {"class_type": "CreateVideo", "inputs": {
            "images": ["12", 0], "fps": 24, "audio": ["13", 0], "bit_depth": 8}}

    wf["15"] = {"class_type": "SaveVideo", "inputs": {
        "video": ["14", 0], "filename_prefix": c["prefix"], "format": "mp4", "codec": "auto"}}

    if trim:
        # seam_probe 需要 trim 前的音频（VAEDecodeAudio 直出，不经过 Trim）
        wf["20"] = {"class_type": "SaveAudioAdvanced", "inputs": {
            "audio": ["13", 0], "filename_prefix": c.get("prefix") + "_untrimmed", "format": "flac"}}

    sl = c.get("save_latent")
    if sl:
        # 采样器 latent -> SaveLatent（段1 存 clip1，段2 存 clip2，供链式续跑）
        wf["19"] = {"class_type": "MiniMaxH3MotionContextSaveLatent", "inputs": {
            "latent": ["11", 0],
            "filename_prefix": sl.get("filename_prefix", "h3_context/clip"),
            "clip_index": sl.get("clip_index", 1)}}
    return wf


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
    results = []
    out = sys.argv[1] + ".results.json"
    done = {r["name"]: r for r in json.load(open(out))} if os.path.exists(out) else {}
    aborted = False

    for c in cases:
        if c["name"] in done:
            prev = done[c["name"]]
            if prev.get("error") and "skipped (OOM abort)" not in prev["error"]:
                print(f"[{c['name']}] 上次失败({prev['error'][:60]}...)，重跑", flush=True)
            else:
                print(f"[{c['name']}] 已存在结果，跳过", flush=True)
                continue
        if aborted:
            print(f"[{c['name']}] ⛔ OOM abort，跳过", flush=True)
            results.append({"name": c["name"], "error": "skipped (OOM abort)"})
            continue

        wf = build_wf(c)
        v0 = vram_used_gb()
        t0 = time.time()
        peak = v0
        try:
            pid = api("/prompt", {"prompt": wf, "client_id": "h3-mc"})["prompt_id"]
        except urllib.error.HTTPError as e:
            msg = e.read().decode()[:300]
            print(f"[{c['name']}] ❌ 提交失败: {msg}", flush=True)
            results.append({"name": c["name"], "error": "submit: " + msg})
            continue
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
        err = errs[0][:300] if errs else None
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

    final = [done[c["name"]] for c in cases if c["name"] in done]
    json.dump(final, open(out, "w"), indent=1, ensure_ascii=False)
    print(f"\n结果: {out}")
    for r in results:
        print(f"  {r['name']}: {r.get('seconds','?')}s vram={r.get('peak_vram_gb')} {'❌ '+r['error'] if r.get('error') else '✅'}")


if __name__ == "__main__":
    main()
