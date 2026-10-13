# Sean — Continuum 3×8 二采链路测试（低分辨率）

- owner: Sean
- date: 2026-09-25
- route: H3 Ref2VA → Continuum V3.4 → per-chunk `refine_state` → `MinimaxH3LatentUpscaler3DRefineHandoff`
- hardware: RTX 4090 24GB
- first pass: 768×448，3×8s，Timeline，Native Masked Strong 39，PDD Acc 8-step，Sage，INT8 VAE
- second pass: 每个 chunk 使用 Continuum 输出的 `refine_state`，BF16 latent upscaler/refine，PDD denoise 0.25，`lock_audio=true`，目标 768×448
- references: 与 4×8 基线相同的 5 张职责型参考图

## 结果

- 状态：success
- 输出：23.999s，768×448，576 帧，音频 751 帧
- 执行耗时：287.038s，约 4 分 47.0 秒（execution start/success 时间戳）
- 显存峰值采样：约 23142 MiB / 24564 MiB
- 主机内存最低可用采样：约 11331 MB
- 无 OOM；GPU lease 已释放
- 输出：[sean_ref2va_continuum_refine_3x8_768x448_00001_.mp4](../comfyui_output_archive_20260928.md)
- 边界抽帧：[boundaries.png](sean_ref2va_continuum_refine_3x8_768x448/boundaries.png)

## 初步视觉检查

边界抽帧显示：三段仍保持同一观测台空间、人物逐步进入、罗盘/青色法术状态逐步建立；二采没有造成明显的段间重置或音视频时长错位。该抽帧只验证链路和大状态连续性，不替代逐帧画质验收。

## 结论与边界

1. Continuum 的 `refine_state` → `MinimaxH3LatentUpscaler3DRefineHandoff` 在 3×8 长视频上已实际打通。
2. 二采应按 chunk 顺序处理，`refine_state` 会让前一段二采后的尾部成为后续 Native Masked 续接的状态；不是把 24 秒作为一个全局 latent 一次二采。
3. 在当前 4090 上，低分辨率 3×8 二采链路可行；显存仍接近满载，降低分辨率主要降低耗时和主机内存压力，并没有改变“约 23 GiB 显存常驻峰值”的模型加载边界。
4. 下一步可以做 3×8 的一采/二采画质 A/B，或者把二采目标提高到 1024×576；暂不把完整 32 秒高分辨率二采作为默认路线。

## 时间与 Timeline 语义补充

- Coordinator/ComfyUI 记录的全流程 execution：287.038s。
- 日志没有输出独立节点的精确计时；按日志阶段只能估算：一采（含 reference/文本编码、3 个 chunk 的主采样和模型切换准备）约 3 分 40 秒；二采采样 + 解码/组装约 1 分钟左右。两者不是节点级精确拆分，不能当作严格 benchmark。
- `[0-8s]`、`[8-16s]`、`[16-24s]` 是 Continuum Timeline 的逻辑路由范围；应与 `chunks × chunk_seconds` 的 authored 时间网格对齐。
- 运行时 Native Masked 会加入前一段的精确尾部上下文，因此物理编译日志中的 global frame interval 会比单纯的 8 秒范围更长；这是续接上下文，不代表 prompt 变成了超长 chunk。
- chunk 内的 `[Shot N] At 00:...` 是 H3 内容/镜头节奏提示，属于软约束；想要帧级精确切镜，仍应拆 chunk 或在后期剪辑。
