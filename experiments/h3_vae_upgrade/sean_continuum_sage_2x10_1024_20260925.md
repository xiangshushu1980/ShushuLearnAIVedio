# Sean — Continuum 2×10 秒拼接与内存测试

owner: Sean
date: 2026-09-25

## 配置

- Continuum V3.4，2 chunks × 10 秒
- 1024×576，Native Masked，Strong 39 frames
- PDD Ref2VA Acc 8-step
- Sage Attention + KJ Low-Mem Attention/FFN
- 新版 INT8 VAE，`--fast fp16_accumulation`
- 不接 Plus 二采

## 结果

- 成功
- 输出：480 帧 / 19.998 秒 / 1024×576
- 峰值显存：约 23108 MiB
- 主机内存峰值：约 51500 MiB
- 主机可用内存最低：约 7760 MiB
- Swap：0 MiB
- 执行时间：约 223.2 秒
- 输出：[sean_continuum_sage_2x10_1024_00001_.mp4](../comfyui_output_archive_20260928.md)
- 10 秒 chunk 边界附近帧：已目视检查，未见明显断帧或亮度跳变

## 结论

10 秒 chunk 在本机 4090 上可运行，GPU 显存没有明显超过 5 秒 chunk；主要增加的是主机内存驻留，约 51.5 GiB，最低可用约 7.8 GiB。2×10 秒已具备超过单 chunk 15 秒上限的实际路线，但系统内存余量已经明显变小。
