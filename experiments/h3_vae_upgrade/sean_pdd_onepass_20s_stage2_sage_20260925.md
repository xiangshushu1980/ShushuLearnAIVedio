# Sean — PDD 单次长视频阶段 2 Sage 校正

owner: Sean
date: 2026-09-25

## 配置

- 与 Stage 2 完全相同：1024×576、481 帧、PDD Ref2VA Acc 8-step、INT8 VAE、`--fast fp16_accumulation`
- KJ Low-Mem Attention：head_chunks=4
- KJ Chunk FeedForward：chunks=4，seq_threshold=4096
- 新增：`MiniMaxH3MemoryEfficientSageAttentionPatch`
- 模式：一次性完整时间轴，不使用 Continuum，不使用时间 chunk

## 结果

- 成功
- 实际输出：481 帧 / 20.040 秒 / 1024×576
- 峰值显存：约 23116 MiB
- 执行时间：约 277.4 秒（4.62 分钟）
- 输出：[sean_pdd_onepass_1024x576_20s_sage_00001_.mp4](../comfyui_output_archive_20260928.md)

## A/B 结论

| 配置 | 耗时 |
|---|---:|
| KJ Low-Mem，无 Sage | 585.4 s |
| KJ Low-Mem + Sage | 277.4 s |

同一拓扑下 Sage 约 2.11× 加速，显存峰值基本不变。因此后续 H3 长视频测试固定启用 Sage。
