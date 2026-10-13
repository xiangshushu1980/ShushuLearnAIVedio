# Sean — Continuum + PDD 独立 smoke 基线

owner: Sean
date: 2026-09-25

## 目的

验证新版 H3 Continuum producer、PDD Acc 和 Plus `refine_state` handoff 是否能在当前 RTX 4090 / 24 GB 环境独立跑通。旧版 `pdd_video_upscale_long.json` 未修改。

## A：Continuum + PDD

- 分辨率：832×480
- chunk：1 × 4 秒
- 帧率：24 fps，96 帧
- PDD：Ref2VA Acc 8-step
- VAE：INT8
- 结果：成功，3.998 秒，输出 `video/sean_continuum_pdd_smoke_4s_00001_.mp4`
- 峰值显存：约 23096 MiB
- 执行时间：约 52 秒

## B：Continuum + PDD + Plus refine_state

- Continuum：1 × 4 秒，832×480 latent
- Plus refine：target dimensions，目标 1024×576，BF16，`offload_after_upscale=True`
- PDD：Ref2VA Acc 8-step；精修 sigma 使用 denoise 0.25
- VAE：INT8
- refine_state：已从 `H3ContinuumSamplerV34` 输出并接入 `MinimaxH3LatentUpscaler3DRefineHandoff`
- 结果：成功，3.998 秒，输出 `video/sean_continuum_pdd_refine_4s_00001_.mp4`
- 实际输出尺寸：1056×608（节点对齐到 32 的结果）
- 峰值显存：约 23076 MiB
- 执行时间：约 44 秒

## 结论

新版 Continuum chunk list 和 Plus `refine_state` 接口已经在本机实际打通。下一步可以在同一图上扩展到 2×4 秒、3×5 秒和 4×5 秒；这验证的是新版分块生成/精修链，不等价于旧版源视频 latent 窗口 upscale。
