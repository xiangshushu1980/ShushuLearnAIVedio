#!/usr/bin/env python3
"""Spectrum 采样加速 A/B 实测 runner（T-comfy-ops-11 spectrum-ab 任务线）

对比：同 seed 同 prompt 下 native vs Spectrum(v0.2.20 默认参数)。
矩阵（对齐 params.md 现行三档 + std 慢车道，场景 wave=低动态 / dance=高动态）：
  s8   成片档   int8_convrot + v4-600EMA + sage + 8步 res_multistep @1024×576（wave+dance）
  f4   极速抽卡 fp8 + v4-600EMA + sage + 4步 res_multistep @768×448（dance）
  f8   快速抽卡 fp8 + v4-600EMA + sage + 8步 res_multistep @768×448（dance）
  t20  std慢车道 int8 无LoRA + sage + 20步 res_multistep @1024×576（dance）

度量：总耗时(wait) + 采样段(进度条) + Spectrum 日志（actual/forecast 决策数）
基线模板：workflows/attn3way_{wave,dance}_sage.json（= 成片档现行配置）

用法（标准库 python3）：
  python3 scripts/h3_spectrum_ab_runner.py [--seed 20260814] [--group s8|f4|f8|t20|all]
"""
import json, re, sys, time, urllib.request

HOST = "http://127.0.0.1:8188"
LOG = "/tmp/comfyui_start.log"
BASE = "/home/sean/projects/comfy-ops/workflows"

INT8 = "minimax_h3_fl2va_pruned_int8_convrot.safetensors"
FP8 = "minimax_h3_fl2va_pruned_fp8_scaled.safetensors"
V4 = "minimax_h3_turbo_v4_step600_ema.safetensors"

# (tag, scene, unet, lora, steps, width, height)
GROUPS = {
    "s8": [
        ("s8_wave_native", "wave", INT8, V4, 8, 1024, 576),
        ("s8_wave_spectrum", "wave", INT8, V4, 8, 1024, 576),
        ("s8_dance_native", "dance", INT8, V4, 8, 1024, 576),
        ("s8_dance_spectrum", "dance", INT8, V4, 8, 1024, 576),
    ],
    "f4": [
        ("f4_dance_native", "dance", FP8, V4, 4, 768, 448),
        ("f4_dance_spectrum", "dance", FP8, V4, 4, 768, 448),
    ],
    "f8": [
        ("f8_dance_native", "dance", FP8, V4, 8, 768, 448),
        ("f8_dance_spectrum", "dance", FP8, V4, 8, 768, 448),
    ],
    "t20": [
        ("t20_dance_native", "dance", INT8, None, 20, 1024, 576),
        ("t20_dance_spectrum", "dance", INT8, None, 20, 1024, 576),
    ],
}

SP_INPUTS = {
    "enabled": True, "blend_weight": 0.5, "degree": 1, "ridge_lambda": 0.1,
    "window_size": 2.0, "flex_window": 0.75, "warmup_steps": 1,
    "tail_actual_steps": 1, "max_history": 8, "debug": True,
    "history_storage": "system_ram", "bootstrap_first_forecast": True,
    "offline_smoothing_replay": True, "audio_blend_weight": 0.0,
    "offline_archive_storage": "system_ram", "model_aware_mode": "off",
}


def _post(path, data):
    req = urllib.request.Request(HOST + path, data=json.dumps(data).encode(),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        raw = r.read()
        return json.loads(raw) if raw else {}


def _get(path):
    with urllib.request.urlopen(HOST + path, timeout=30) as r:
        return json.loads(r.read())


def wait(pid, timeout=3600):
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


def log_offset():
    with open(LOG, "rb") as f:
        f.seek(0, 2)
        return f.tell()


def read_window(start):
    with open(LOG, "rb") as f:
        f.seek(start)
        return f.read().decode("utf-8", "replace")


def parse_window(text):
    elapsed = []
    for m in re.finditer(r"\[(\d+):(\d+)<", text):
        elapsed.append(int(m.group(1)) * 60 + int(m.group(2)))
    sampling = max(elapsed) if elapsed else None
    actuals, forecasts = [], []
    for m in re.finditer(r"Spectrum H3 step run_id=\d+ step=(\d+) coordinate=\S+ decision=(actual|forecast)", text):
        (actuals if m.group(2) == "actual" else forecasts).append(int(m.group(1)))
    starts = len(re.findall(r"Spectrum H3 run start", text))
    summaries = re.findall(r"run summary phase=(\S+) wall_s=([\d.]+) run_id=\d+ sampler=\S+ steps=(\d+) actual_steps=(\d+) forecast_steps=(\d+)", text)
    m = re.search(r"Prompt executed in ([\d.]+) seconds", text)
    prompt_exec = float(m.group(1)) if m else None
    return {
        "sampling": sampling, "actual": sorted(set(actuals)), "forecast": sorted(set(forecasts)),
        "passes": starts, "prompt_exec": prompt_exec,
        "run_summaries": [{"phase": p, "wall_s": float(w), "steps": int(s),
                           "actual_steps": int(a), "forecast_steps": int(f)}
                          for p, w, s, a, f in summaries],
    }


def build_wf(scene, unet, lora, steps, width, height, spectrum, seed, tag):
    wf = json.load(open(f"{BASE}/attn3way_{scene}_sage.json"))
    wf["1"]["inputs"]["unet_name"] = unet
    if lora is None:  # 去 LoRA：Sage 直接接 UNET
        del wf["5"]
        wf["6"]["inputs"]["model"] = ["1", 0]
    wf["17"]["inputs"]["steps"] = steps
    wf["8"]["inputs"]["width"] = width
    wf["8"]["inputs"]["height"] = height
    wf["10"]["inputs"]["noise_seed"] = seed
    wf["16"]["inputs"]["filename_prefix"] = f"video/spectrum_test/{tag}"
    if spectrum:
        sp_id = "20"
        wf[sp_id] = {"class_type": "SpectrumApplyMiniMaxH3",
                     "inputs": {"model": ["6", 0], **SP_INPUTS}}
        for nid in ("9", "17"):  # guider / scheduler 改接 Spectrum 输出
            if wf[nid]["inputs"].get("model") == ["6", 0]:
                wf[nid]["inputs"]["model"] = [sp_id, 0]
    return wf


def run(tag, wf):
    print(f"\n== {tag} ==", flush=True)
    _post("/free", {"unload_models": True, "free_memory": True})
    time.sleep(3)
    off = log_offset()
    pid = _post("/prompt", {"prompt": wf})["prompt_id"]
    _, dt = wait(pid)
    info = parse_window(read_window(off))
    print(f"  总耗时: {dt:.1f}s | 采样段: {info['sampling']}s | Prompt executed: {info['prompt_exec']}s")
    print(f"  Spectrum passes={info['passes']} actual={info['actual']} forecast={info['forecast']}")
    return dt, info


def main():
    seed = 20260814
    group = "all"
    if "--seed" in sys.argv:
        seed = int(sys.argv[sys.argv.index("--seed") + 1])
    if "--group" in sys.argv:
        group = sys.argv[sys.argv.index("--group") + 1]
    cases = GROUPS[group] if group != "all" else GROUPS["s8"] + GROUPS["t20"] + GROUPS["f4"] + GROUPS["f8"]
    results = {}
    for tag, scene, unet, lora, steps, w, h in cases:
        spectrum = tag.endswith("_spectrum")
        wf = build_wf(scene, unet, lora, steps, w, h, spectrum, seed, tag)
        dt, info = run(tag, wf)
        results[tag] = {"dt": round(dt, 1), **info,
                        "cfg": {"scene": scene, "unet": unet.split("_")[2], "lora": bool(lora),
                                "steps": steps, "res": f"{w}x{h}"}}
    out = f"experiments/spectrum_ab/ab_{group}_{seed}.results.json"
    import os
    os.makedirs(os.path.dirname(out), exist_ok=True)
    json.dump(results, open(out, "w"), indent=1, ensure_ascii=False)
    print(f"\n== 汇总 → {out} ==")
    for tag, r in results.items():
        print(f"  {tag}: 总{r['dt']}s 采样{r['sampling']}s actual={len(r['actual'])} forecast={len(r['forecast'])}")


if __name__ == "__main__":
    main()
