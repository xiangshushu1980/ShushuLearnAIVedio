# Sean — 标准驱动动画：Shot 边界对齐 Continuum 4×8 秒

owner: Sean
date: 2026-09-25

## 配置

- `prompt_mode=Timeline`
- 四个 8 秒 Shot，边界固定在 00:08、00:16、00:24
- 5 个职责清晰的参考：精灵 A、红发角色 B、观测台、青色法术、黄铜罗盘
- 1024×576，Native Masked，Strong 39 frames
- PDD Ref2VA Acc 8-step
- Sage Attention + KJ Low-Mem Attention/FFN
- 新版 INT8 VAE，`--fast fp16_accumulation`
- 不接 Plus 二采

## 结果

- 成功
- 输出：768 帧 / 31.999 秒 / 1024×576
- 峰值显存采样：约 23062 MiB / 24564 MiB
- 主机内存峰值采样：约 47839 MiB；最低可用约 11419 MiB
- 执行时间：约 508.2 秒
- 输出：[sean_ref2va_standard_shot_boundaries_4x8_00001_.mp4](../comfyui_output_archive_20260928.md)
- 抽帧：观测台、两个人物和青色法术在后半段保持连续；Shot 边界没有形成硬切，而是被 Native Masked 作为连续状态延伸。
- 4 秒间隔时间网格复核：00:04、00:08、00:12、00:16、00:20、00:24、00:28 的人物/罗盘/法术状态没有严格按提示词中的四段线性推进，法术和人物状态在部分 chunk 间反复出现；因此不能把本次 Timeline 结果视为四个 Shot 被准确执行。

## 结论

把 Shot 边界对齐到 Continuum chunk 边界适合作为诊断实验，能够直接观察每次续接的状态保留；它不是生产剪辑的唯一推荐。当前结果表明 Continuum 更像“连续状态续写”，不会自动把每个 Shot 变成干净剪辑段；在本次全局 32 秒 Timeline 中，Shot 的语义顺序也没有被稳定执行。后续应改为每个 chunk 使用一个独立、短的 8 秒 prompt，并由 Native Masked 负责状态续接；不要把 32 秒四段叙事一次性塞进单个全局 Timeline 再假设它会严格按 chunk 分配。
