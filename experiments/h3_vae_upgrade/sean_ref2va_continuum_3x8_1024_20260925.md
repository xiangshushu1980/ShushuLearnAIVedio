# Sean — Ref2VA 参考人物+场景 Continuum 3×8 秒

owner: Sean
date: 2026-09-25

## 配置

- 参考人物：`sean_t2_a_character_board.png`
- 参考场景：`sean_t2_scene_observatory.png`
- Continuum V3.4，3 chunks × 8 秒
- 1024×576，Ref2VA，Native Masked，Strong 39 frames
- PDD Ref2VA Acc 8-step
- Sage Attention + KJ Low-Mem Attention/FFN
- 新版 INT8 VAE，`--fast fp16_accumulation`
- 不接 Plus 二采

## 结果

- 成功
- 输出：576 帧 / 23.999 秒 / 1024×576
- 峰值显存采样：约 23078 MiB / 24564 MiB
- 主机内存采样峰值：约 52074 MiB；最低可用约 7184 MiB
- 执行时间：约 293.3 秒
- 输出：[sean_ref2va_continuum_3x8_1024_00001_.mp4](../comfyui_output_archive_20260928.md)
- 人物/场景抽帧检查：银发精灵弓手、深青斗篷、弓、石质圆形观测台、拱窗、石台和蓝色月光在 24 秒内保持一致；8 秒和 16 秒边界未见明显视觉跳变

## 结论

参考人物和场景没有明显改变显存峰值，主要增加的是参考条件处理与少量耗时；本机仍能稳定完成 3×8 秒。相较纯文本 3×8 秒，Ref2VA 执行时间约增加到 293 秒，主机内存最低可用约 7.2 GiB，已经进入需要谨慎扩展 chunk 数的区间。
