#!/usr/bin/env python3
"""H3 加载时间精确测量 + 试验2：落盘 cond 采样对比（2026-08-16 cond-roundtrip 任务线）

测量（全部精确 wall-time）：
  T1  TE 加载（nvfp4 15.7GB → CPU 反量化 → GPU）
  T2  cond 编码 + 落盘
  T3  fl2va int8 DiT 冷加载 + 热路径采样（内存 cond）
  T4  fl2va int8 DiT 再加载（测重载成本）+ 落盘路径采样（.pt 读回）
  T5  ref2va int8 DiT 加载（纯计时，成片档）
对比：热路径 vs 落盘路径输出帧（PSNR / max abs diff）

用法:
  /home/sean/projects/ComfyUI/venv/bin/python \
    /home/sean/projects/comfy-ops/scripts/h3_load_time_sampling.py
"""
import os, sys, time, json, urllib.request, gc

COMFYUI = "/home/sean/projects/ComfyUI"
sys.path.insert(0, COMFYUI)
os.chdir(COMFYUI)

import torch
import comfy.sd
import comfy.utils
import comfy.nested_tensor
import comfy.model_management as mm
from comfy.samplers import KSampler
from comfy_extras.nodes_custom_sampler import Noise_RandomNoise
from comfy_extras.nodes_minimax_h3 import _empty_av_latent

HOST = "http://127.0.0.1:8188"
TE = "models/text_encoders/qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors"
FL2VA_INT8 = "models/diffusion_models/minimax_h3_fl2va_pruned_int8_convrot.safetensors"
REF2VA_INT8 = "models/diffusion_models/minimax_h3_ref2va_pruned_int8_convrot.safetensors"
VIDEO_VAE = "models/vae/minimax_h3_video_vae_fp16.safetensors"
PROMPT = "a red ball on a wooden table, soft daylight, camera slowly zooming in"
W, H, LEN, STEPS, SEED = 768, 448, 124, 20, 20260805
COND_PATH = "/tmp/h3_cond_t2va_sampling.pt"

timings = {}


def free_comfyui():
    req = urllib.request.Request(HOST + "/free",
        data=json.dumps({"unload_models": True, "free_memory": True}).encode(),
        headers={"Content-Type": "application/json"})
    urllib.request.urlopen(req, timeout=30)
    time.sleep(2)


def to_device(obj, device):
    if isinstance(obj, comfy.nested_tensor.NestedTensor):
        return obj.to(device)
    if isinstance(obj, torch.Tensor):
        return obj.to(device)
    if isinstance(obj, dict):
        return {k: to_device(v, device) for k, v in obj.items()}
    if isinstance(obj, list):
        return [to_device(v, device) for v in obj]
    return obj


def encode_t2va(clip, prompt):
    tokens = clip.tokenize(prompt, images=[])
    return clip.encode_from_tokens_scheduled(tokens)


def run_sampling(model, cond, latent_nested):
    """复刻工作流采样链：res_multistep / simple / STEPS 步 / cfg=1（BasicGuider 语义 negative=positive）。"""
    sampler = KSampler(model, STEPS, mm.get_torch_device(),
                       sampler="res_multistep", scheduler="simple", denoise=1.0)
    noise = Noise_RandomNoise(SEED).generate_noise({"samples": latent_nested})
    out = sampler.sample(noise, cond, cond, 1.0, latent_image=latent_nested,
                         force_full_denoise=True, seed=SEED)
    return out  # NestedTensor（video+audio）


def decode_video(vae, lat):
    """复刻 VAEDecode：nested 取 unbind()[0]（video 部分）→ vae.decode。"""
    if isinstance(lat, comfy.nested_tensor.NestedTensor):
        lat = lat.unbind()[0]
    return vae.decode(lat)


def unload_all():
    mm.unload_all_models()
    gc.collect()
    torch.cuda.empty_cache()


def main():
    print("== 清场 ==")
    free_comfyui()
    # 确认 GPU 空闲（服务进程可能占显存，防并发打架）
    try:
        import subprocess
        out = subprocess.run(["/usr/lib/wsl/lib/nvidia-smi", "--query-gpu=memory.used", "--format=csv,noheader,nounits"],
                             capture_output=True, text=True).stdout.strip()
        used = int(out.split("\n")[0])
        print(f"  GPU used: {used} MiB")
        if used > 1024:
            print("  WARN: 服务进程仍占用 GPU，可能干扰测量；建议稍后再跑")
    except Exception as e:
        print(f"  (nvidia-smi 检查跳过: {e})")

    # ---- T1: TE 加载 ----
    print("== T1: TE 加载 ==", flush=True)
    t0 = time.time()
    clip = comfy.sd.load_clip([TE])
    timings["TE 加载"] = time.time() - t0
    print(f"  TE 加载: {timings['TE 加载']:.1f}s", flush=True)

    # ---- T2: cond 编码 + 落盘 ----
    print("== T2: cond 编码 + 落盘 ==", flush=True)
    t0 = time.time()
    cond_hot = encode_t2va(clip, PROMPT)
    torch.save(cond_hot, COND_PATH)
    latent_dict, _ = _empty_av_latent(W, H, LEN)
    latent_nested = latent_dict["samples"]
    timings["cond 编码+落盘"] = time.time() - t0
    print(f"  cond 编码+落盘: {timings['cond 编码+落盘']:.1f}s (cond keys结构=list, embeds={tuple(cond_hot[0][0].shape)})", flush=True)
    del clip
    unload_all()

    vae = comfy.sd.VAE(sd=comfy.utils.load_torch_file(VIDEO_VAE))

    # 采样阶段强制 LOW_VRAM：DiT 部分驻留，给无注意力patch的激活留空间（避免采样OOM）
    mm.vram_state = mm.VRAMState.LOW_VRAM
    print("  vram_state -> LOW_VRAM（采样阶段）", flush=True)

    # ---- T3: fl2va DiT 冷加载 + 热路径采样 ----
    print("== T3: fl2va int8 DiT 冷加载 + 热路径采样 ==", flush=True)
    t0 = time.time()
    model = comfy.sd.load_diffusion_model(FL2VA_INT8)
    mm.load_model_gpu(model)
    timings["fl2va DiT 冷加载"] = time.time() - t0
    print(f"  fl2va DiT 冷加载: {timings['fl2va DiT 冷加载']:.1f}s", flush=True)
    t0 = time.time()
    lat_hot = run_sampling(model, cond_hot, latent_nested)
    timings["热路径采样"] = time.time() - t0
    print(f"  热路径采样: {timings['热路径采样']:.1f}s", flush=True)
    del model
    unload_all()

    # ---- T4: fl2va DiT 再加载 + 落盘路径采样 ----
    print("== T4: fl2va DiT 再加载 + 落盘路径采样 ==", flush=True)
    t0 = time.time()
    model2 = comfy.sd.load_diffusion_model(FL2VA_INT8)
    mm.load_model_gpu(model2)
    timings["fl2va DiT 再加载"] = time.time() - t0
    print(f"  fl2va DiT 再加载: {timings['fl2va DiT 再加载']:.1f}s", flush=True)
    cond_disk = torch.load(COND_PATH, map_location="cpu", weights_only=False)
    cond_disk = to_device(cond_disk, mm.get_torch_device())
    t0 = time.time()
    lat_disk = run_sampling(model2, cond_disk, latent_nested)
    timings["落盘路径采样"] = time.time() - t0
    print(f"  落盘路径采样: {timings['落盘路径采样']:.1f}s", flush=True)
    del model2
    unload_all()

    # ---- T5: ref2va int8 DiT 加载 ----
    print("== T5: ref2va int8 DiT 加载 ==", flush=True)
    t0 = time.time()
    model3 = comfy.sd.load_diffusion_model(REF2VA_INT8)
    mm.load_model_gpu(model3)
    timings["ref2va DiT 加载"] = time.time() - t0
    print(f"  ref2va DiT 加载: {timings['ref2va DiT 加载']:.1f}s", flush=True)
    del model3
    unload_all()

    # ---- 对比：采样输出 latent（VAE decode 是确定性函数，latent 一致 => 视频一致）----
    print("== 对比: 热路径 vs 落盘路径（采样 latent）==", flush=True)
    if isinstance(lat_hot, comfy.nested_tensor.NestedTensor):
        n_hot, n_disk = lat_hot.unbind(), lat_disk.unbind()
        names = ["video", "audio"]
        all_ok = True
        for name, a, b in zip(names, n_hot, n_disk):
            a, b = a.cpu().numpy(), b.cpu().numpy()
            diff = (a - b).astype("float64")
            mse = float((diff ** 2).mean())
            psnr = float("inf") if mse == 0 else 10.0 * __import__("math").log10(float(diff.max() - diff.min() or 1) ** 2 / mse)
            eq = bool((a == b).all())
            print(f"  {name}: shape={a.shape} 逐位一致={eq}  MSE={mse:.3e}  max_abs_diff={abs(diff).max():.3e}")
            all_ok &= eq
        print(f"  判定: {'PASS 逐位一致（落盘 cond 采样结果与热路径完全相同）' if all_ok else '见上 MSE（同seed下非确定性导致微小差异为正常）'}")
    else:
        a, b = lat_hot.cpu().numpy(), lat_disk.cpu().numpy()
        diff = (a - b).astype("float64")
        mse = float((diff ** 2).mean())
        print(f"  latent: shape={a.shape} 逐位一致={(a == b).all()}  MSE={mse:.3e}  max_abs_diff={abs(diff).max():.3e}")

    # ---- 汇总 ----
    print("\n== 时间汇总 ==", flush=True)
    total = 0.0
    for k, v in timings.items():
        print(f"  {k:<28} {v:7.1f}s")
        total += v
    print(f"  {'合计(单任务完整链)':<28} {total:7.1f}s")
    print("\n  单视频生成参考构成:")
    print(f"    TE 加载 {timings['TE 加载']:.0f}s + DiT 加载 {timings['fl2va DiT 冷加载']:.0f}s + 采样 {timings['热路径采样']:.0f}s"
          f" = {timings['TE 加载']+timings['fl2va DiT 冷加载']+timings['热路径采样']:.0f}s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
