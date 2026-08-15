#!/usr/bin/env python3
"""H3 两阶段流水线前置验证 · 试验1：cond 序列化往返（2026-08-16 cond-roundtrip 任务线）

验证链（对应 docs/10 前置验证点）：
  case A: t2va（无 keyframes）—— cond 含 NestedTensor embeds + minimax_token_tags
  case B: fl2va（带首帧 keyframes）—— cond 再挂 minimax_keyframes（VideoVAE latent）
  每个 case：torch.save → torch.load(map_location='cpu') → 递归逐位对比所有 tensor
  设备搬运：读回 CPU 版 .to(cuda) 后再对比（模拟采样前搬运路径）

用法（在 ComfyUI venv 里）：
  /home/sean/projects/ComfyUI/venv/bin/python \
    /home/sean/projects/comfy-ops/scripts/h3_cond_roundtrip.py
"""
import os, sys

COMFYUI = "/home/sean/projects/ComfyUI"
sys.path.insert(0, COMFYUI)
os.chdir(COMFYUI)

import torch
import comfy.sd
import comfy.utils
import comfy.nested_tensor
import comfy.model_management as mm
import node_helpers
from comfy_extras.nodes_minimax_h3 import _resize

TE_PATH = "models/text_encoders/qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors"
VAE_PATH = "models/vae/minimax_h3_video_vae_fp16.safetensors"
PROMPT = "a red ball on a wooden table, soft daylight, camera slowly zooming in"
W, H, LEN = 768, 448, 124


def walk_tensors(obj, path="cond"):
    """递归收集 (路径, tensor) 列表，NestedTensor 拆成 .tensors 逐项。"""
    hits = []
    if isinstance(obj, comfy.nested_tensor.NestedTensor):
        for i, t in enumerate(obj.tensors):
            hits.append((f"{path}.tensors[{i}]", t))
    elif isinstance(obj, torch.Tensor):
        hits.append((path, obj))
    elif isinstance(obj, dict):
        for k, v in obj.items():
            hits.extend(walk_tensors(v, f"{path}.{k}"))
    elif isinstance(obj, (list, tuple)):
        for i, v in enumerate(obj):
            hits.extend(walk_tensors(v, f"{path}[{i}]"))
    return hits


def compare_cond(tag, orig, rt):
    """递归逐位对比 orig vs rt，返回 (ok, 明细)。"""
    o = walk_tensors(orig)
    r = walk_tensors(rt)
    if len(o) != len(r):
        return False, f"tensor count mismatch: {len(o)} vs {len(r)}"
    ok, lines = True, []
    for (po, to), (pr, tr) in zip(o, r):
        if po != pr:
            return False, f"structure mismatch at {po} vs {pr}"
        if isinstance(to, comfy.nested_tensor.NestedTensor):
            same = all(torch.equal(x.cpu(), y.cpu()) for x, y in zip(to.tensors, tr.tensors))
        else:
            same = torch.equal(to.cpu(), tr.cpu())
        line = f"  {tag} {po}: equal={same} shape={tuple(to.shape)} dtype={to.dtype}"
        if to.device.type == "cuda":
            line += f" orig_dev=cuda rt_dev={tr.device.type}"
        lines.append(line)
        ok &= same
    return ok, "\n".join(lines)


def to_device(obj, device):
    """递归搬运到 device（处理 NestedTensor/tensor/dict/list）。"""
    if isinstance(obj, comfy.nested_tensor.NestedTensor):
        return obj.to(device)
    if isinstance(obj, torch.Tensor):
        return obj.to(device)
    if isinstance(obj, dict):
        return {k: to_device(v, device) for k, v in obj.items()}
    if isinstance(obj, list):
        return [to_device(v, device) for v in obj]
    return obj


def main():
    mm.unload_all_models()
    print(f"[1] loading TE {os.path.basename(TE_PATH)} ...", flush=True)
    clip = comfy.sd.load_clip([TE_PATH])
    print(f"    clip type: {type(clip).__name__}, ok", flush=True)

    # ---- case A: t2va（无 keyframes）----
    print("\n=== case A: t2va ===", flush=True)
    tokens = clip.tokenize(PROMPT, images=[])
    cond_a = clip.encode_from_tokens_scheduled(tokens)
    print("    cond keys:", list(cond_a.keys()) if isinstance(cond_a, dict) else type(cond_a))
    pa = "/tmp/h3_cond_t2va.pt"
    torch.save(cond_a, pa)
    rt_a = torch.load(pa, map_location="cpu", weights_only=False)
    ok_a, det_a = compare_cond("A", cond_a, rt_a)
    print(det_a)
    print(f"    case A 往返: {'PASS' if ok_a else 'FAIL'}")

    # 设备搬运验证：读回 CPU 版 → GPU，与原件(GPU)对比
    rt_a_gpu = to_device(rt_a, mm.get_torch_device())
    ok_a_gpu = all(torch.equal(a.cpu(), b.cpu())
                   for (_, a), (_, b) in zip(walk_tensors(cond_a), walk_tensors(rt_a_gpu)))
    print(f"    case A 搬运到GPU后对比: {'PASS' if ok_a_gpu else 'FAIL'}")

    # ---- case B: fl2va（带首帧 keyframes）----
    print("\n=== case B: fl2va (first_frame) ===", flush=True)
    vae = comfy.sd.VAE(sd=comfy.utils.load_torch_file(VAE_PATH))
    fake_img = torch.rand(1, H, W, 3)  # [B,H,W,C] 假首帧（0-1 float）
    img = _resize(fake_img[:1], W, H, "disabled")
    tokens_b = clip.tokenize(PROMPT, images=[img])
    cond_b = clip.encode_from_tokens_scheduled(tokens_b)
    kf = {"resolved_frame_index": 0, "latent": vae.encode(img)}
    cond_b = node_helpers.conditioning_set_values(cond_b, {"minimax_keyframes": [kf]})
    print("    cond keys:", list(cond_b.keys()) if isinstance(cond_b, dict) else type(cond_b))
    pb = "/tmp/h3_cond_fl2va.pt"
    torch.save(cond_b, pb)
    rt_b = torch.load(pb, map_location="cpu", weights_only=False)
    ok_b, det_b = compare_cond("B", cond_b, rt_b)
    print(det_b)
    print(f"    case B 往返: {'PASS' if ok_b else 'FAIL'}")

    # keyframes 专项：确认 latent 往返一致 + 搬运可运行
    if isinstance(cond_b, dict) and "minimax_keyframes" in rt_b:
        kf_rt = rt_b["minimax_keyframes"][0]["latent"]
        kf_orig = cond_b["minimax_keyframes"][0]["latent"]
        same = torch.equal(kf_orig.cpu(), kf_rt.cpu())
        print(f"    keyframe latent 往返: equal={same} shape={tuple(kf_orig.shape)} (读回device={kf_rt.device.type})")
        kf_rt_gpu = kf_rt.to(mm.get_torch_device())
        print(f"    keyframe latent .to(cuda): ok, equal={torch.equal(kf_orig.cpu(), kf_rt_gpu.cpu())}")

    ok = ok_a and ok_a_gpu and ok_b
    print(f"\n===== 试验1 总结果: {'PASS' if ok else 'FAIL'} =====")
    mm.unload_all_models()
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
