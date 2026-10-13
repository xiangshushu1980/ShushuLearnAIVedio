# Sean H3 Continuum 4×8 中文台词、1344 二采与人脸 refine 实测

owner: Sean
date: 2026-09-26

## 目标

在当前 ComfyUI 共享实例上验证：4 个 8 秒 Continuum chunk、中文 `<d>` 台词、768×448 一采、1344 级 latent 二采，以及随后的人脸局部 refine。全程使用 Sage Attention、INT8 VAE、PDD Acc8 和 Native Masked Strong39；不重启服务。

## 一采与二采

- Prompt：`sean_ref2va_continuum_4x8_chunked_prompt_v2_20260925.txt`
- 一采：4×8 秒，768×448，五张参考图，Native Masked Strong39，PDD Acc8。
- 二采：`MinimaxH3LatentUpscaler3DRefineHandoff`，BF16，目标 1344×768；节点按 32 对齐，实际输出为 1376×800。
- 输出：`/home/sean/projects/ComfyUI/output/video/sean_ref2va_continuum_dialogue_4x8_1344_00001_.mp4`
- 实际媒体：31.999 秒，1376×800，768 视频帧，音频 1001 帧。
- 总耗时：676.69 秒，约 11 分 16.7 秒；监控墙钟约 670.7 秒。
- 峰值显存：23574 / 24564 MiB，约 23.0 / 24.0 GiB。
- 主机可用内存最低：326 MB；未发生 OOM，任务成功，但已接近主机内存上限。

## 人脸 refine

使用 `tools/h3_face_crop_refine_runner.py`，每次只处理 192 帧（8 秒），768×768 crop canvas、crop factor 3、denoise 0.40、8 steps、逐帧 denoise、face_only 回贴。

- 红发角色 c1：成功，275.1 秒。输出：`video/sean_dialogue_4x8_red_face_c1_fast_00001_.mp4`。
- 红发角色 c2：成功，228.2 秒；跟踪预览确认绿色框锁定红发角色。输出：`video/sean_dialogue_4x8_red_face_c2_fast_00001_.mp4`。
- 精灵 c2 尝试：任务成功但目标选择错误，290.2 秒；`face-index=1` 仍锁定红发角色，不能作为精灵 refine 结果。输出：`video/sean_dialogue_4x8_elf_face_c2_fast_00001_.mp4` 不纳入有效结果。
- 之前整段 32 秒 face refine 在开始采样前因主机内存压力主动中止；不是显存 OOM。
- 身份匹配模式在该生成视频上多次返回“没有可 refine 的 subject”；fast-detect 可以工作，但远景双人画面不能可靠按身份选择第二个人物。

## 与此前速度对比

本次 8 秒窗口单脸为 228.2–275.1 秒，约 28.5–34.4 秒/输出视频秒。此前 4090 上的 FaceRefine 记录约 145.2 秒（短窗口/不同源片），以及一次 120 秒仍在运行的跟踪预览；因此本次属于同一数量级，但明显更慢。主要差异是本次源视频为 1376×800、每窗口 192 帧，且包含 768×768 局部 H3 采样与逐帧 denoise；不能直接把不同帧数的秒数作一比一比较。

结论更新：FaceRefine 保留为慢车道，仅对近景或明确需要修脸的片段启用；不作为 32 秒全片默认步骤。后续加速方向包括减少采样步数、降低 crop canvas、减少处理帧数后做时序传播，以及使用 ROI/manifest 避免失败的身份搜索，但必须单独做质量对照。

## 结论

1344 latent 二采在 4090 上可完成，但主机内存是瓶颈，最低仅剩 326 MB；不适合把 32 秒视频一次性交给 face refine。人脸 refine 应固定为 8 秒窗口，并使用坐标/ROI 或预生成 manifest 锁定角色。当前已验证红发角色两个分段的 refine；精灵尚未形成有效 refine 结果，不应把错误跟踪输出拼回成品。

资源观测：`9da53a4b-2e69-4ee2-a61d-8564e56a7cc5`（主生成）、`f81aaf82-083f-42e4-99cd-c76c611c697a`（分段 face refine）。
