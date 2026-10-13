# Sean — PDD 单次长视频阶段 2

owner: Sean
date: 2026-09-25

## 配置

- PDD：Ref2VA Acc 8-step
- 模式：单次完整时间轴采样，不使用 Continuum，不使用时间 chunk
- 分辨率：1024×576
- 请求时长：20 秒
- KJ Low-Mem Attention：head_chunks=4
- KJ Chunk FeedForward：chunks=4，seq_threshold=4096
- VAE：新版 INT8 H3 VAE
- 启动参数：`--fast fp16_accumulation`

## 结果

- 成功
- 实际输出：481 帧 / 20.040 秒 / 1024×576
- 峰值显存：约 23108 MiB
- 执行时间：约 585.4 秒（9.76 分钟）
- 输出：[sean_pdd_onepass_1024x576_20s_00001_.mp4](../comfyui_output_archive_20260928.md)
- 中间帧目视检查：正常生成，无明显执行损坏

## 阶段结论

在当前 RTX 4090 24GB 上，PDD + KJ Low-Mem + 新版 INT8 VAE 已实现 1024×576、20 秒一次性生成。没有时间 chunk，也没有 Continuum 拼接。相对 832×480，显存基本不变，但耗时从约 294 秒增加到约 585 秒。
