# Sean — Continuum 2×5 秒拼接测试

owner: Sean
date: 2026-09-25

## 配置

- Continuum V3.4，2 chunks × 5 秒
- 1024×576，Native Masked，Strong 39 frames
- PDD Ref2VA Acc 8-step
- Sage Attention + KJ Low-Mem Attention/FFN
- 新版 INT8 VAE，`--fast fp16_accumulation`
- 不接 Plus 二采

## 结果

- 成功
- 输出：240 帧 / 9.998 秒 / 1024×576
- 峰值显存：约 23060 MiB
- 执行时间：约 94.96 秒
- 输出：[sean_continuum_sage_2x5_1024_00001_.mp4](../comfyui_output_archive_20260928.md)
- 边界帧：已抽取 chunk 交界附近 8 帧目视检查，未见明显断帧或亮度跳变

## 结论

2×5 秒 Native Masked 拼接在当前 4090 上稳定运行，显存与单 chunk 基本相同；实际输出接近 10 秒。下一阶段可测试 3×5 秒，但当前 1024×20 秒 PDD 一次性路线仍更快、更直接。
