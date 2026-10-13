# T47-1 8 秒二采控制实验准备记录

owner: Sean
date: 2026-09-26

## 已完成的静态核验

- `sean_dual_character_reference_v1/manifest.json` 中的 A、B、scene、spell、prop canonical 路径全部存在。
- 现有 32 秒目标片和一采片均为 768 帧、24 fps、31.999 s；二采片实际尺寸为 1376×800。
- 两条已有片的首 8 秒已经导出到 `/home/sean/projects/ComfyUI/output/video/t47_1_static_compare_20260926/`，包括左右对照和 7.75 s 抽帧。

## 重要限制

现有一采基线 `sean_ref2va_continuum_4x8_1024_00001_.mp4` 使用简化 reference，现有二采目标 `sean_ref2va_continuum_dialogue_4x8_1344_00001_.mp4` 使用五张职责型 reference；两者不是同一 seed/reference 条件。静态对照中角色状态也不同，因此不能用来归因 latent 二采造成的接缝或建筑变形。

## 下一步控制变量

从二采 MP4 内嵌 prompt metadata 恢复原 workflow。使用同一组五张 reference、同一 prompt、`base_seed=2026092601`、768×448、单个 8 秒 chunk，分别生成：

1. 仅一采输出；
2. 同一 chunk 接 `MinimaxH3LatentUpscaler3DRefineHandoff`，目标 1344×768，实际按 32 对齐记录尺寸。

两次只改变是否二采；本轮不做 FaceRefine，不改 reference、prompt、Continuum 状态或 seed。完成后再检查 0–8 秒内部建筑几何、角色绑定和边界条件；单 chunk 不作为 seam 结论，只作为二采归因对照。

