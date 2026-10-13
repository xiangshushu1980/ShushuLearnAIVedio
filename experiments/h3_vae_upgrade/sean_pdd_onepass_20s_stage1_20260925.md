# Sean — PDD 单次长视频阶段 1

owner: Sean
date: 2026-09-25

## 配置

- PDD：Ref2VA Acc 8-step
- 模式：单次完整时间轴采样，不使用 Continuum，不使用时间 chunk
- 分辨率：832×480
- 请求时长：20 秒
- KJ Low-Mem Attention：head_chunks=4
- KJ Chunk FeedForward：chunks=4，seq_threshold=4096
- VAE：INT8
- ComfyUI 启动：`--fast fp16_accumulation`

## 结果

- 成功
- 实际输出：481 帧 / 20.040 秒 / 832×480
- 峰值显存：约 23044 MiB
- 执行时间：约 293.9 秒（4.90 分钟）
- 输出：[sean_pdd_onepass_832x480_20s_00001_.mp4](../comfyui_output_archive_20260928.md)
- 中间帧目视检查：正常生成，无明显执行损坏

## 阶段结论

KJ Low-Mem 方案确实支持完整 20 秒一次性 PDD 采样；它不是分段生成再合并。832×480 已达到单次长视频门槛。下一阶段测试 1024×576、20 秒，保持同一拓扑。
