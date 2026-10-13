# Sean — Continuum 1×5 秒 Sage 基线

owner: Sean
date: 2026-09-25

## 配置

- Continuum V3.4，1 chunk × 5 秒
- 1024×576，Native Masked，Strong 39 frames（单 chunk 时无跨 chunk 作用）
- PDD Ref2VA Acc 8-step
- Sage Attention + KJ Low-Mem Attention/FFN
- 新版 INT8 VAE，`--fast fp16_accumulation`
- 不接 Plus 二采，先测 Continuum 第一采

## 结果

- 成功
- 输出：120 帧 / 4.998 秒 / 1024×576
- 峰值显存：约 23060 MiB
- 执行时间：约 39.98 秒
- 输出：[sean_continuum_sage_1x5_1024_00001_.mp4](../comfyui_output_archive_20260928.md)

## 结论

单个 5 秒 chunk 在当前 4090 上稳定运行，显存约 23.1 GiB。下一步测试 2×5 秒，验证 Native Masked 的实际跨 chunk 连续性和 assemble 行为。
