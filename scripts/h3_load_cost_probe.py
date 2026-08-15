#!/usr/bin/env python3
"""T2 受控复测：TE/DiT 加载成本 冷/热 分解（cond-cache-node 任务线，2026-08-16）

背景：cond-roundtrip 直接库脚本测得 TE 冷 112s/热 24s、DiT 冷 171s/热 14-34s；
但 API 工作流（ComfyUI 0.33 dynamic VRAM loading）实测 TE ~7-10s、DiT ~8s。
本脚本用 posix_fadvise(POSIX_FADV_DONTNEED) 逐文件逐出页缓存（无需 root），
把「load_clip 惰性加载 / 首次前向 nvfp4 反量化 / 热前向」三阶段分开计时，
并对比 DiT 冷/热，用于定性 112s/171s 的真实构成（磁盘 I/O vs CPU 反量化 vs 动态 VRAM 差异）。

用法（先确认 ComfyUI 队列空闲，脚本内部会 POST /free）：
  /home/sean/projects/ComfyUI/venv/bin/python \
    /home/sean/projects/comfy-ops/scripts/h3_load_cost_probe.py
"""
import os, sys, time, json, gc, urllib.request

COMFYUI = "/home/sean/projects/ComfyUI"
sys.path.insert(0, COMFYUI)
os.chdir(COMFYUI)

import torch
import comfy.sd
import comfy.model_management as mm

HOST = "http://127.0.0.1:8188"
TE = "models/text_encoders/qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors"
FL2VA_INT8 = "models/diffusion_models/minimax_h3_fl2va_pruned_int8_convrot.safetensors"
PROMPT_A = "a red ball on a wooden table, soft daylight, camera slowly zooming in"
PROMPT_B = "a blue toy car rolling across a sunny sidewalk, birds chirping in the distance"


def free_comfyui():
    req = urllib.request.Request(HOST + "/free",
        data=json.dumps({"unload_models": True, "free_memory": True}).encode(),
        headers={"Content-Type": "application/json"})
    urllib.request.urlopen(req, timeout=30)
    time.sleep(3)


def fadvise_drop(path):
    """逐出指定文件在页缓存中的页面（无需 root 的冷载控制）。"""
    try:
        fd = os.open(path, os.O_RDONLY)
        try:
            os.posix_fadvise(fd, 0, 0, os.POSIX_FADV_DONTNEED)
        finally:
            os.close(fd)
        return True
    except OSError as e:
        return f"skip({e})"


def fsize_mb(path):
    return os.path.getsize(path) / 1e6


def encode(clip, prompt):
    tokens = clip.tokenize(prompt, images=[])
    return clip.encode_from_tokens_scheduled(tokens)


def unload():
    mm.unload_all_models()
    gc.collect()
    torch.cuda.empty_cache()


def main():
    print("== 清场 ==")
    free_comfyui()

    print(f"\n== TE（nvfp4 {fsize_mb(TE):.0f}MB）直接库路径 阶段分解 ==")
    # --- 冷：逐出页缓存后 load_clip + 首次前向 ---
    print(f"  [冷] fadvise drop: {fadvise_drop(TE)}")
    t0 = time.time(); clip = comfy.sd.load_clip([TE]); t1 = time.time()
    print(f"  [冷] load_clip（惰性）: {t1-t0:.1f}s")
    cond_a = encode(clip, PROMPT_A); t2 = time.time()
    print(f"  [冷] 首次前向(编码A，含 nvfp4 反量化): {t2-t1:.1f}s")
    cond_b = encode(clip, PROMPT_B); t3 = time.time()
    print(f"  [热] 二次前向(编码B，权重已反量化): {t3-t2:.1f}s")

    # --- 热：unload 后重新 load_clip + 首次前向（页缓存热） ---
    del cond_a, cond_b, clip
    unload()
    t0 = time.time(); clip2 = comfy.sd.load_clip([TE]); t1 = time.time()
    print(f"\n  [热] load_clip: {t1-t0:.1f}s")
    cond_c = encode(clip2, PROMPT_A); t2 = time.time()
    print(f"  [热] 首次前向(权重已在页缓存/已反量化): {t2-t1:.1f}s")
    del cond_c, clip2
    unload()

    print(f"\n== fl2va int8 DiT（{fsize_mb(FL2VA_INT8):.0f}MB）直接库路径 ==")
    mm.vram_state = mm.VRAMState.LOW_VRAM
    print(f"  [冷] fadvise drop: {fadvise_drop(FL2VA_INT8)}")
    t0 = time.time()
    model = comfy.sd.load_diffusion_model(FL2VA_INT8)
    mm.load_model_gpu(model)
    t1 = time.time()
    print(f"  [冷] DiT load_diffusion_model + load_model_gpu: {t1-t0:.1f}s")
    del model; unload()
    t0 = time.time()
    model2 = comfy.sd.load_diffusion_model(FL2VA_INT8)
    mm.load_model_gpu(model2)
    t1 = time.time()
    print(f"  [热] DiT 再加载: {t1-t0:.1f}s")
    del model2; unload()

    print("\n== 结论速览 ==")
    print("  若 冷/热 差大 → 磁盘 I/O（页缓存）主导；若 冷≈热 且都小 → 动态 VRAM/惰性路径已非全量反量化")
    return 0


if __name__ == "__main__":
    sys.exit(main())
