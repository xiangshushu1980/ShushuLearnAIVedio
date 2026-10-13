# Sean — Ref2VA 参考人物+场景 Continuum 4×8 秒

owner: Sean
date: 2026-09-25

## 配置

- 参考人物：`sean_t2_a_character_board.png`
- 参考场景：`sean_t2_scene_observatory.png`
- Continuum V3.4，4 chunks × 8 秒
- 1024×576，Ref2VA，Native Masked，Strong 39 frames
- PDD Ref2VA Acc 8-step
- Sage Attention + KJ Low-Mem Attention/FFN
- 新版 INT8 VAE，`--fast fp16_accumulation`
- 不接 Plus 二采

## 结果

- 成功
- 输出：768 帧 / 31.999 秒 / 1024×576
- 峰值显存采样：约 23110 MiB / 24564 MiB
- 主机内存峰值采样：约 54257 MiB；最低可用约 5001 MiB
- 执行时间：约 399.6 秒
- 输出：[sean_ref2va_continuum_4x8_1024_00001_.mp4](../comfyui_output_archive_20260928.md)

## 结论

4×8 秒（约 32 秒）仍可完成，显存没有明显随 chunk 数增长；主机内存成为主要上限，解码/拼接阶段最低可用约 5 GiB。继续增加段数或同时增加参考图数量时，优先观察 Assemble 阶段的主机内存，而不是显存。
