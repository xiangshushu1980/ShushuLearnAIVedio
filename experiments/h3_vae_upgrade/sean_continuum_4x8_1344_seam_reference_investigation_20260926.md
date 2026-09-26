# Sean Continuum 4×8 1344 接缝与双角色 reference 调查

owner: Sean
date: 2026-09-26

## 调查对象

目标输出：`/home/sean/projects/ComfyUI/output/video/sean_ref2va_continuum_dialogue_4x8_1344_00001_.mp4`

实际媒体为 31.999 秒、1376×800、24 fps、768 视频帧、32000 Hz 双声道 AAC。工作流元数据确认：768×448 一采、4×8 秒、Native Masked exact continuation、Strong 39 frames、5 张 reference、`audio_continuity=true`，然后接 `MinimaxH3LatentUpscaler3DRefineHandoff` 做 2× latent 二采，目标 1344×768，因 32 对齐实际变成 1376×800。

## 接缝证据

我逐帧检查了三个 Continuum 边界的前后各一帧：7.958/8.000/8.042 秒、15.958/16.000/16.042 秒、23.958/24.000/24.042 秒；同时检查了每个边界前后约 1 秒的 0.25 秒网格。

- 没有发现建筑拱窗、中央柱、圆形地面或石台在边界处发生硬切式位移、重复或断裂。
- Native Masked 的边界是连续的：8 秒附近从红发角色单人状态继续，16 秒附近保持双人状态，24 秒附近保持同一法术状态。
- 画面内存在缓慢推近/构图变化，不能把人物进入、法术开始和相机重构本身误判为 seam deformation。
- 因此当前证据不支持“4×8 拼接是建筑接缝变形的主因”。如果用户看到的是更细的纹理弯曲，优先怀疑二采阶段的 learned 3D latent upscaler，而不是 Assemble/Native Audio。

## 归因排序

1. **最可疑：1344 latent 二采。** 它对整段 32 秒 latent 做时空重建；基础 768×448 一采没有同等的二采变形风险。目标尺寸实际被对齐到 1376×800，亦增加了观察难度。
2. **次可疑：scene reference 的视角不匹配。** `sean_t2_scene_observatory.png` 是干净的 1:1 场景图，而目标视频是 16:9、带中央前景柱和横向拱窗构图。它能约束风格/空间类别，但不足以锁定当前镜头的建筑几何。
3. **较低可疑：prompt/latent 状态。** 每段都显式写了上一段的 exact final state，且边界抽查稳定；提示词更可能影响“角色/法术何时出现”，不是造成边界处建筑硬变形。
4. **较低可疑：NativeAudio。** 接缝画面连续，音频是独立的 AAC/Native continuation 链路；没有证据表明音频锁定会把建筑几何拉变。

## 已测试的 reference 对照

- 简化双角色/场景 baseline：`sean_ref2va_continuum_4x8_1024_00001_.mp4`，2 张 reference，31.999 秒，1024×576。
- 职责型完整 reference：`sean_ref2va_chunked_prompt_v2_4x8_00001_.mp4`，角色 A、角色 B、场景、法术、道具共 5 张，31.999 秒，1024×576。
- 同一职责型 4×8 结构再接 1344 latent 二采：目标输出即本报告调查对象。

这三组对照支持：增加 scene/character/object reference 没有把接缝变成硬切；真正新增的变量是 1344 latent 二采。因此下一轮应先做“同一 768×448 一采、只比较不二采 vs 1344 二采”的局部 8 秒对照，并保留相同 seed、prompt、reference 和 Continuum 状态。

## 采用的改进

1. 已建立 `sean_dual_character_reference_v1/manifest.json`：角色 A、角色 B、scene、spell、prop 各自独立；默认双人中景只选 A identity + B identity + scene。
2. 不再把 A character board、total board 或混合 pair board 当作默认双角色 identity 输入；它们只作辅助/负对照。
3. 角色 B 当前只有一张 identity 图，近景/侧背暴露时标记为 coverage gap；不要用 A 的 face/board 补 B。
4. scene reference 下一版优先补一张干净的 16:9 observatory establishing view，镜头布局应接近实际视频中的中央柱、三拱窗和两石台；这比继续增加角色图更直接地针对建筑漂移。
5. 诊断顺序固定为：先验收 768×448 一采边界，再单独比较 1344 latent 二采；不要在同一次实验里同时改 reference、prompt、NativeAudio 和 upscale。

## 当前结论

当前证据：**4×8 Native Masked/Assemble 不是主要接缝故障源；目标视频的边界画面连续。1344 latent 二采与 1:1 scene reference 到 16:9 镜头的几何约束不足，是更合理的风险假设。** 标准双角色 reference 已落盘，可直接用于下一次控制变量实验。

## 未执行项

本轮没有重新提交 ComfyUI 生成任务；结论基于现有成功输出、工作流元数据和逐帧检查。后续若执行新 smoke，应只跑一个 8 秒 chunk，先比较 768×448 原片与同 chunk 的 1376×800 二采结果，避免再次把完整 32 秒二采作为诊断样本。
