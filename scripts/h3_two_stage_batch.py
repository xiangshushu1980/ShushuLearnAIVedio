#!/usr/bin/env python3
"""H3 两阶段批处理（cond-cache-node 任务线 第二步，2026-08-16）

形态 = 批处理脚本（非常驻守护进程），走 ComfyUI API 编排，复用已建节点：
  阶段1（TE 班）：一个工作流 = 1×CLIPLoader 喂 N×MiniMaxH3ImageToVideo → N×MiniMaxH3CondSaver
                  （TE 只载一次，编 N 个 cond 落盘）
  阶段2（DiT 班）：一个工作流 = 1×UNETLoader + PathchSageAttentionKJ 喂 N 条采样分支
                  （DiT 只载一次，逐个 cond 读盘→采样→decode→出片）

收益（实测模型）：省 (N-1)×~22s（冷加载）；真瓶颈采样不碰。

任务从 JSON 文件读（--tasks），每任务：prompt/seed/width/height/length/steps/prefix。
用法（标准库 python3）：
  python3 scripts/h3_two_stage_batch.py --tasks experiments/h3_batch_tasks.json
  python3 scripts/h3_two_stage_batch.py --prompts "p1" "p2" "p3" --steps 8 --width 1024 --height 576
"""
import argparse, hashlib, json, os, sys, time, urllib.request, urllib.error

HOST = "http://127.0.0.1:8188"
CLIP = "qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors"
VIDEO_VAE = "minimax_h3_video_vae_fp16.safetensors"
AUDIO_VAE = "minimax_h3_audio_vae_fp32.safetensors"
UNET = "minimax_h3_fl2va_pruned_int8_convrot.safetensors"
LORA = "minimax_h3_turbo_v4_step600_ema.safetensors"
COND_DIR = "/home/sean/projects/ComfyUI/output/conditioning"


def _post(path, data=None):
    body = None if data is None else json.dumps(data).encode()
    req = urllib.request.Request(HOST + path, data=body,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        raw = r.read()
        return json.loads(raw) if raw else {}


def _get(path):
    with urllib.request.urlopen(HOST + path, timeout=30) as r:
        return json.loads(r.read())


def wait(pid, timeout=7200):
    t0 = time.time()
    while time.time() - t0 < timeout:
        time.sleep(3)
        h = _get(f"/history/{pid}")
        if pid in h:
            st = h[pid].get("status", {})
            if st.get("completed"):
                return h[pid], time.time() - t0
            if st.get("status_str") == "error":
                for m in st.get("messages", []):
                    if m[0] == "execution_error":
                        raise RuntimeError(m[1].get("exception_message", "?"))
                raise RuntimeError(str(st))
    raise TimeoutError("超时")


def next_cond_path(prefix):
    os.makedirs(COND_DIR, exist_ok=True)
    index = 0
    for name in os.listdir(COND_DIR):
        if name.startswith(prefix + "_") and name.endswith(".pt"):
            stem = name[len(prefix) + 1:-3]
            if stem.isdigit():
                index = max(index, int(stem) + 1)
    return os.path.join(COND_DIR, f"{prefix}_{index:05d}.pt")


def build_stage1(tasks):
    """1×TE 编 N cond。节点 ID：loaders=1/2，enc<i>，save<i>。"""
    wf = {
        "1": {"class_type": "CLIPLoader", "inputs": {"clip_name": CLIP, "type": "minimax", "device": "default"}},
        "2": {"class_type": "VAELoader", "inputs": {"vae_name": VIDEO_VAE}},
    }
    for i, t in enumerate(tasks):
        prefix = t["prefix"]
        wf[f"enc{i}"] = {"class_type": "MiniMaxH3ImageToVideo", "inputs": {
            "clip": ["1", 0], "vae": ["2", 0], "prompt": t["prompt"],
            "width": t["width"], "height": t["height"], "length": t["length"]}}
        wf[f"save{i}"] = {"class_type": "MiniMaxH3CondSaver", "inputs": {
            "positive": [f"enc{i}", 0], "filename_prefix": prefix, "subdirectory": "conditioning"}}
    return wf


def build_stage2(tasks, cond_paths, use_sage=True):
    """1×DiT(+sage) 喂 N 分支。节点 ID：model=1/2，其余 per-branch 前缀。"""
    wf = {
        "1": {"class_type": "UNETLoader", "inputs": {"unet_name": UNET, "weight_dtype": "default"}},
        "5": {"class_type": "LoraLoaderModelOnly", "inputs": {"model": ["1", 0], "lora_name": LORA, "strength_model": 1.0}},
        "3": {"class_type": "VAELoader", "inputs": {"vae_name": VIDEO_VAE}},
        "4": {"class_type": "VAELoader", "inputs": {"vae_name": AUDIO_VAE}},
    }
    model_src = ["5", 0]
    if use_sage:
        wf["6"] = {"class_type": "PathchSageAttentionKJ", "inputs": {"model": ["5", 0], "sage_attention": "auto", "allow_compile": False}}
        model_src = ["6", 0]

    for i, t in enumerate(tasks):
        p = f"b{i}"
        wf[f"{p}_ld"] = {"class_type": "MiniMaxH3CondLoader", "inputs": {"filename": cond_paths[i]}}
        wf[f"{p}_lat"] = {"class_type": "EmptyMiniMaxH3LatentAV", "inputs": {
            "width": t["width"], "height": t["height"], "length": t["length"]}}
        wf[f"{p}_ks"] = {"class_type": "KSamplerSelect", "inputs": {"sampler_name": "res_multistep"}}
        wf[f"{p}_sch"] = {"class_type": "BasicScheduler", "inputs": {
            "model": model_src, "scheduler": "simple", "steps": t["steps"], "denoise": 1.0}}
        wf[f"{p}_g"] = {"class_type": "BasicGuider", "inputs": {"model": model_src, "conditioning": [f"{p}_ld", 0]}}
        wf[f"{p}_noise"] = {"class_type": "RandomNoise", "inputs": {"noise_seed": t["seed"]}}
        wf[f"{p}_smpl"] = {"class_type": "SamplerCustomAdvanced", "inputs": {
            "noise": [f"{p}_noise", 0], "guider": [f"{p}_g", 0], "sampler": [f"{p}_ks", 0],
            "sigmas": [f"{p}_sch", 0], "latent_image": [f"{p}_lat", 0]}}
        wf[f"{p}_dec"] = {"class_type": "VAEDecode", "inputs": {"samples": [f"{p}_smpl", 0], "vae": ["3", 0]}}
        wf[f"{p}_deca"] = {"class_type": "VAEDecodeAudio", "inputs": {"samples": [f"{p}_smpl", 0], "vae": ["4", 0]}}
        wf[f"{p}_cv"] = {"class_type": "CreateVideo", "inputs": {
            "images": [f"{p}_dec", 0], "fps": 24.0, "audio": [f"{p}_deca", 0], "bit_depth": 8}}
        wf[f"{p}_save"] = {"class_type": "SaveVideo", "inputs": {
            "video": [f"{p}_cv", 0], "filename_prefix": f"video/{t['prefix']}", "format": "mp4", "codec": "auto"}}
    return wf


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tasks", help="任务 JSON 文件路径")
    ap.add_argument("--prompts", nargs="+", help="内联 prompt 列表")
    ap.add_argument("--steps", type=int, default=8)
    ap.add_argument("--width", type=int, default=1024)
    ap.add_argument("--height", type=int, default=576)
    ap.add_argument("--length", type=int, default=124)
    ap.add_argument("--no-sage", action="store_true")
    args = ap.parse_args()

    if args.tasks:
        with open(args.tasks) as f:
            tasks = json.load(f)
    else:
        prompts = args.prompts or ["a red ball on a wooden table, soft daylight, camera slowly zooming in",
                                   "a blue toy car rolling across a sunny sidewalk, birds chirping",
                                   "a gentle waterfall in a mossy forest, soft mist, ambient birdsong"]
        tasks = [{"prompt": p, "seed": 20260816 + i, "width": args.width, "height": args.height,
                  "length": args.length, "steps": args.steps,
                  "prefix": f"h3_batch_{hashlib.md5(p.encode()).hexdigest()[:8]}"} for i, p in enumerate(prompts)]
    N = len(tasks)
    print(f"== H3 两阶段批处理（N={N}，{'sage 节点' if not args.no_sage else '无 sage'}）==")

    # 阶段1
    print(f"[阶段1] TE 一次编码 {N} 个 cond ...", flush=True)
    _post("/free", {"unload_models": True, "free_memory": True}); time.sleep(3)
    cond_paths = [next_cond_path(t["prefix"]) for t in tasks]
    t0 = time.time()
    pid1 = _post("/prompt", {"prompt": build_stage1(tasks)})["prompt_id"]
    _, dt1 = wait(pid1)
    print(f"  阶段1 完成 {dt1:.1f}s（含 TE 加载一次 + 编码 {N}）")
    for p in cond_paths:
        print(f"    cond: {p} ({os.path.getsize(p)/1e6:.2f}MB)" if os.path.isfile(p) else f"    ⚠️ 缺失 {p}")

    # 阶段2
    print(f"[阶段2] DiT 一次加载，逐个采样 {N} ...", flush=True)
    _post("/free", {"unload_models": True, "free_memory": True}); time.sleep(3)
    t0 = time.time()
    pid2 = _post("/prompt", {"prompt": build_stage2(tasks, cond_paths, use_sage=not args.no_sage)})["prompt_id"]
    entry2, dt2 = wait(pid2)
    print(f"  阶段2 完成 {dt2:.1f}s（含 DiT 加载一次 + 采样 {N}）")

    outs = entry2.get("outputs", {})
    videos = []
    for node in outs.values():
        for it in (node.get("images") or []) + (node.get("videos") or []):
            if isinstance(it, dict) and str(it.get("filename", "")).split(".")[-1] in ("mp4", "webm"):
                videos.append((it.get("subfolder"), it.get("filename")))
    print(f"  出片 {len(videos)}: {videos}")

    print("\n== 汇总 ==")
    total = dt1 + dt2
    single_est = N * 65  # 实测单任务 sage 65s
    print(f"  两阶段总耗时: {total:.1f}s（阶段1 {dt1:.1f} + 阶段2 {dt2:.1f}）")
    print(f"  对比单任务 {N}×65s = {single_est}s，省 ~{single_est - total:.0f}s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
