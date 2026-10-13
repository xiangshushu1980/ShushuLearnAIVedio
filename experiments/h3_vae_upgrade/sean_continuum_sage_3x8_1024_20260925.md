# Sean — Continuum 3×8 秒长视频与资源测试

owner: Sean
date: 2026-09-25

## 配置

- Continuum V3.4，3 chunks × 8 秒
- 1024×576，Native Masked，Strong 39 frames
- PDD Ref2VA Acc 8-step
- Sage Attention + KJ Low-Mem Attention/FFN
- 新版 INT8 VAE，`--fast fp16_accumulation`
- 不接 Plus 二采

## 结果

- 成功
- 输出：576 帧 / 23.999 秒 / 1024×576
- 峰值显存采样：约 23092 MiB / 24564 MiB（约 94%）
- 主机内存采样峰值：约 51690 MiB；最低可用约 7569 MiB
- Swap：生成后观测到约 224 MiB，未见持续换页迹象；该值不是全过程峰值
- 执行时间：约 261.8 秒
- 输出：[sean_continuum_sage_3x8_1024_00001_.mp4](../comfyui_output_archive_20260928.md)
- 边界帧：8 秒和 16 秒附近抽帧检查，未见明显断帧或亮度跳变
- 音频：8 秒和 16 秒附近波形未见硬静音断点；听感上的音色/环境变化仍可能来自 chunk 音频续接

## 结论

3×8 秒在本机 RTX 4090 上可运行，实际拼接约 24 秒。显存峰值与 2×10 秒基本相同，说明当前瓶颈不是 chunk 数量线性增加的显存占用；主要压力在主机内存，约 51.7 GiB，最低可用约 7.6 GiB。相较 2×10 秒（约 223.2 秒），3×8 秒约 261.8 秒，增加一个 chunk 后耗时上升但仍稳定。

音频接缝不能直接归因于“显存接近满”：显存压力会决定能否运行、是否需要分批/卸载，但不会主动生成音效切换。当前更像是 Continuum 每个 chunk 独立生成后由 Assemble Seam 续接，Native Masked 主要锁定视频/音频 latent 尾部（Strong 39 frames），并不能保证后续新生成音频的环境声完全一致。
