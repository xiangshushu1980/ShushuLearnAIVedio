#!/usr/bin/env python3
"""H3 两阶段流水线 · cond 缓存自定义节点 API 验证（cond-cache-node 任务线，2026-08-16）

验证目标（docs/10 两阶段流水线第一步落地）：
  阶段1（TE 班）：CLIPLoader(minimax) → MiniMaxH3ImageToVideo → MiniMaxH3CondSaver 落盘 cond
  阶段2（DiT 班）：MiniMaxH3CondLoader 读盘 cond → 采样（**无 CLIPLoader / 无 TE**）→ 出片

判定：
  1. 阶段1 产出 .pt，阶段2 读回成功采样出片
  2. 阶段2 服务端日志窗口内不出现 MiniMaxH3TEModel（TE）加载 → 免 TE 重载坐实
  3. 计时对比：阶段1 含 TE 冷载（~112s），阶段2 无 TE（DiT 冷载 + 采样）

用法（任意 python3，仅标准库）：
  python3 /home/sean/projects/comfy-ops/scripts/h3_condcache_verify.py
"""
import json, os, sys, time, urllib.request, urllib.error

HOST = "http://127.0.0.1:8188"
CLIP = "qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors"
VIDEO_VAE = "minimax_h3_video_vae_fp16.safetensors"
AUDIO_VAE = "minimax_h3_audio_vae_fp32.safetensors"
UNET = "minimax_h3_fl2va_pruned_int8_convrot.safetensors"
PROMPT = "a red ball on a wooden table, soft daylight, camera slowly zooming in"
W, H, LEN, STEPS, SEED = 768, 448, 124, 20, 20260816
PREFIX = "h3_condcache"


def _post(path, data=None):
    body = None if data is None else json.dumps(data).encode()
    req = urllib.request.Request(HOST + path, data=body,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        raw = r.read()
        if not raw:
            return {}
        return json.loads(raw)


def _get(path):
    with urllib.request.urlopen(HOST + path, timeout=30) as r:
        return json.loads(r.read())


def wait(prompt_id, timeout=3600):
    t0 = time.time()
    while time.time() - t0 < timeout:
        time.sleep(3)
        hist = _get(f"/history/{prompt_id}")
        if prompt_id not in hist:
            continue
        status = hist[prompt_id].get("status", {})
        if status.get("completed"):
            return hist[prompt_id], time.time() - t0
        if status.get("status_str") == "error":
            for m in status.get("messages", []):
                if m[0] == "execution_error":
                    raise RuntimeError(m[1].get("exception_message", "未知错误"))
            raise RuntimeError("任务出错: " + str(status))
    raise TimeoutError("任务超时")


def extract_string_output(entry, node_id):
    """从 history outputs 里抽出 STRING 输出的路径（新 API 下 STRING 不进 history，靠确定性路径兑底）。"""
    outs = entry.get("outputs", {}).get(node_id, {})
    for key in ("text", "string", "str"):
        vals = outs.get(key)
        if isinstance(vals, list) and vals and isinstance(vals[0], str):
            return vals[0]
    for v in outs.values():
        if isinstance(v, list) and v and isinstance(v[0], str):
            return v[0]
    return None


def next_cond_path(prefix):
    """确定性复算 Saver 将写入的路径（与 cond_cache.py 的计数器逻辑一致）。"""
    out_dir = "/home/sean/projects/ComfyUI/output/conditioning"
    os.makedirs(out_dir, exist_ok=True)
    index = 0
    for name in os.listdir(out_dir):
        if name.startswith(prefix + "_") and name.endswith(".pt"):
            stem = name[len(prefix) + 1 : -3]
            if stem.isdigit():
                index = max(index, int(stem) + 1)
    return os.path.join(out_dir, f"{prefix}_{index:05d}.pt")


def stage1_workflow():
    return {
        "1": {"class_type": "CLIPLoader", "inputs": {"clip_name": CLIP, "type": "minimax", "device": "default"}},
        "2": {"class_type": "VAELoader", "inputs": {"vae_name": VIDEO_VAE}},
        "3": {"class_type": "MiniMaxH3ImageToVideo", "inputs": {
            "clip": ["1", 0], "vae": ["2", 0], "prompt": PROMPT,
            "width": W, "height": H, "length": LEN}},
        "4": {"class_type": "MiniMaxH3CondSaver", "inputs": {
            "positive": ["3", 0], "filename_prefix": PREFIX, "subdirectory": "conditioning"}},
    }


def stage2_workflow(cond_path):
    return {
        "1": {"class_type": "UNETLoader", "inputs": {"unet_name": UNET, "weight_dtype": "default"}},
        "2": {"class_type": "VAELoader", "inputs": {"vae_name": VIDEO_VAE}},
        "3": {"class_type": "VAELoader", "inputs": {"vae_name": AUDIO_VAE}},
        "4": {"class_type": "MiniMaxH3CondLoader", "inputs": {"filename": cond_path}},
        "5": {"class_type": "EmptyMiniMaxH3LatentAV", "inputs": {"width": W, "height": H, "length": LEN}},
        "6": {"class_type": "KSamplerSelect", "inputs": {"sampler_name": "res_multistep"}},
        "7": {"class_type": "BasicScheduler", "inputs": {"model": ["1", 0], "scheduler": "simple", "steps": STEPS, "denoise": 1.0}},
        "8": {"class_type": "BasicGuider", "inputs": {"model": ["1", 0], "conditioning": ["4", 0]}},
        "9": {"class_type": "RandomNoise", "inputs": {"noise_seed": SEED}},
        "10": {"class_type": "SamplerCustomAdvanced", "inputs": {
            "noise": ["9", 0], "guider": ["8", 0], "sampler": ["6", 0],
            "sigmas": ["7", 0], "latent_image": ["5", 0]}},
        "11": {"class_type": "VAEDecode", "inputs": {"samples": ["10", 0], "vae": ["2", 0]}},
        "12": {"class_type": "VAEDecodeAudio", "inputs": {"samples": ["10", 0], "vae": ["3", 0]}},
        "13": {"class_type": "CreateVideo", "inputs": {"images": ["11", 0], "fps": 24.0, "audio": ["12", 0], "bit_depth": 8}},
        "14": {"class_type": "SaveVideo", "inputs": {
            "video": ["13", 0], "filename_prefix": f"video/{PREFIX}_stage2", "format": "mp4", "codec": "auto"}},
    }


def log_window_markers():
    """返回服务日志当前行数，供阶段2窗口 grep。"""
    log = "/tmp/comfyui_start.log"
    try:
        with open(log, "rb") as f:
            f.seek(0, 2)
            return f.tell()  # byte offset 锚定窗口起点
    except OSError:
        return 0


def read_log_window(start):
    log = "/tmp/comfyui_start.log"
    try:
        with open(log, "rb") as f:
            f.seek(start)
            return f.read().decode("utf-8", "replace")
    except OSError:
        return ""


def main():
    print("== 0. 清场（POST /free）==")
    try:
        _post("/free", {"unload_models": True, "free_memory": True})
        time.sleep(3)
    except urllib.error.URLError as e:
        print(f"  /free 跳过: {e}")

    print("== 阶段1：TE 编码 → 落盘 cond ==")
    cond_path = next_cond_path(PREFIX)
    t0 = time.time()
    pid1 = _post("/prompt", {"prompt": stage1_workflow()})["prompt_id"]
    entry1, dt1 = wait(pid1)
    print(f"  完成 {dt1:.1f}s（含 TE 加载）")
    print(f"  cond 落盘: {cond_path}")
    if not os.path.isfile(cond_path):
        print(f"  ⚠️ 未找到 cond 文件（history outputs: {json.dumps(entry1.get('outputs',{}), ensure_ascii=False)[:500]}）")
    else:
        print(f"  文件大小: {os.path.getsize(cond_path)/1e6:.1f} MB")

    print("\n== 阶段2：读盘 cond → 采样（无 TE）==")
    win_start = log_window_markers()
    t0 = time.time()
    pid2 = _post("/prompt", {"prompt": stage2_workflow(cond_path)})["prompt_id"]
    entry2, dt2 = wait(pid2)
    print(f"  完成 {dt2:.1f}s（DiT 冷载 + 采样，无 TE）")
    outs = entry2.get("outputs", {})
    videos = []
    for node in outs.values():
        for key in ("videos", "images", "gifs"):
            for it in (node.get(key) or []):
                if isinstance(it, dict) and str(it.get("filename", "")).split(".")[-1] in ("mp4", "webm", "gif", "mov", "mkv"):
                    videos.append((it.get("subfolder"), it.get("filename")))
    print(f"  出片: {videos}")

    print("\n== 判定：阶段2 是否加载了 TE ==")
    window = read_log_window(win_start)
    te_hits = window.count("MiniMaxH3TEModel")
    dit_hits = window.count("MiniMaxH3 prepared")
    print(f"  阶段2 日志窗口: MiniMaxH3TEModel(TE) 加载 {te_hits} 次 / MiniMaxH3(DiT) 加载 {dit_hits} 次")
    no_te = te_hits == 0
    print(f"  免 TE 重载: {'PASS（阶段2 全程未加载 Qwen3VL）' if no_te else 'FAIL（阶段2 意外加载了 TE）'}")

    ok = bool(cond_path) and os.path.isfile(cond_path) and bool(videos) and no_te
    print(f"\n===== 验证总结果: {'PASS' if ok else 'FAIL'} =====")
    print(f"  收益: 阶段1 付 1 次 TE 冷载（~{dt1:.0f}s 窗口），阶段2 起每任务完全免 TE；N 个不同 prompt 批编码省 (N-1)×TE 加载")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
