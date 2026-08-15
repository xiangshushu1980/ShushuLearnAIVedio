# ComfyUI-MiniMax-H3-CondCache

MiniMax H3 两阶段流水线的 cond 缓存节点（docs/10 批量优化落地第一步）。

- **MiniMaxH3CondSaver**（Save MiniMax H3 Cond）：把 H3 conditioning 落盘成 `.pt`
  （Qwen3VL hidden states + `minimax_token_tags` + `minimax_keyframes`/`minimax_refs` 的 latent）。
  输出绝对路径 STRING，可直接接 Loader。
- **MiniMaxH3CondLoader**（Load MiniMax H3 Cond）：读盘 `.pt` → CONDITIONING，
  采样全程**不需要 TE（Qwen3VL）**。

## 用法（两阶段）

```
阶段1（TE 班）: CLIPLoader(minimax) ─┐
                VAELoader ───────────┼─ MiniMaxH3ImageToVideo ─ MiniMaxH3CondSaver ─ path
                prompt/尺寸/时长 ─────┘

阶段2（DiT 班）: MiniMaxH3CondLoader(path) ─ BasicGuider
                UNETLoader(fl2va/ref2va) ──┬─ BasicScheduler/KSampler ─ SamplerCustomAdvanced ─ VAEDecode ─ SaveVideo
                EmptyMiniMaxH3LatentAV ────┘（latent_image）
```

## cond 结构（2026-08-16 实测验证，逐位无损）

```python
[(embeds (1, seq, 5120), {"pooled_output": None, "minimax_token_tags": (seq,)}), ...]
# fl2va/ref2va 时 attrs 再挂 minimax_keyframes / minimax_refs（含 VAE latent）
```

标准 ComfyUI conditioning list，`torch.save`/`torch.load` 直通；节点保存前统一搬到 CPU
（可移植），加载时搬回 `intermediate_device()`（对齐 sd1_clip 编码输出设备），逐位一致。

## 验证

`comfy-ops/scripts/h3_condcache_verify.py`：阶段1 TE 编码落盘 → 阶段2 读盘采样，
服务端日志窗口内 0 次 TE 加载（免 TE 重载坐实），出片成功。

## 安装

源码真相在 `comfy-ops/custom_nodes/`，ComfyUI `custom_nodes/` 下是软链指向它。
