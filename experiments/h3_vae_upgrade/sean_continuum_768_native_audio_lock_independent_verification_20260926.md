# Sean Continuum 768 一采 + 二采 + NativeAudioLock 独立验收

owner: Sean
date: 2026-09-26
type: independent artifact verification

## 结论

Continuum V3.4 的 4×8 秒双角色流程已经有可复用的 768×448 一采结果；接入 Continuum Plus 的 `refine_state` 和 `MinimaxH3LatentUpscaler3DRefineHandoff` 后，二采成功输出 1376×800、约 32 秒视频。NativeAudioLock 的外部对白音频保持在最终媒体中，视频条件随音频生成；本次验收不执行 FaceRefine。

本记录是对已完成产物的独立验收，不重复提交 32 秒生成任务：共享 ComfyUI 当时空闲，但上一轮已显示二采阶段主机内存最低约 326 MB，重复运行会增加共享实例风险。

## 工作流与参数

一采 graph：

```text
5 张 reference picture
  → Continuum V3.4 Timeline，4 chunks × 8 s
  → MiniMax H3 Ref2VA
  → Native Masked Strong 39 frames
  → PDD Ref2VA Acc 8-step + Sage Attention
  → INT8 VAE decode / chunk assemble
```

一采参数：

- 768×448，24 fps，768 帧，实际 31.998 s
- Continuum Timeline headers：`[0-8s]`、`[8-16s]`、`[16-24s]`、`[24-32s]`
- PDD Acc 8 steps；Sage Attention；INT8 VAE
- 双角色：银发精灵弓手 + 红发女性；单弓、单罗盘、单条青色 ribbon
- 外部中文对白经 NativeAudioLock 写入 AV latent；prompt 不重复编写未经核对的台词

二采 graph：

```text
Continuum chunk refine_state
  → MinimaxH3LatentUpscaler3DRefineHandoff
  → BF16 latent refine，lock_audio=true
  → VAE decode / audio decode / SaveVideo
```

二采参数：目标 1344×768，节点按 32 对齐；实际输出 1376×800，BF16，PDD denoise 0.25，`lock_audio=true`。二采没有使用 FaceRefine、ROI refine 或身份检测。

## 产物与资源

| 阶段 | 产物 | 结果 | 耗时/资源 |
|---|---|---|---|
| 一采 | [`sean_ref2va_continuum_4x8_1024_00001_.mp4`](../comfyui_output_archive_20260928.md) | 1024×576，768 帧，31.998 s | 约 399.6 s；峰值显存约 23,110 MiB；最低可用内存约 5 GiB |
| 二采 | [`sean_ref2va_continuum_dialogue_4x8_1344_00001_.mp4`](../comfyui_output_archive_20260928.md) | 1376×800，768 帧，31.998 s | 676.69 s；峰值显存 23,574/24,564 MiB；最低可用内存 326 MB |

二采音频探针：32 kHz、2 声道、AAC、31.999 s、1001 个音频帧。源片与二采片的音视频时长均在 1 ms 级别内对齐；二采没有裁掉或重新拼接对白轨。

## 视觉与口型验收

- 抽查帧：0、约 8、16、24、32 秒边界，以及 15–25 秒每 0.5 秒序列。
- 双角色、观测台拱窗/石台、弓的位置和青色 ribbon 的连续生长均保留；二采没有把角色重置成单人或改变左右关系。
- 15–25 秒序列中，角色面部和头部运动持续存在，未见静帧式“贴脸”或二采造成的明显口型冻结。
- NativeAudioLock 的音频轨持续存在且时长精确覆盖 32 秒；据此确认音频锁定链路工作。仅凭静态抽帧不能给出逐音素同步率，因此本次口型结论为“定性通过、未量化百分比”，不是 85%/100% 等数值定论。

## 失败与边界

- 32 秒整段 FaceRefine 因主机内存压力主动中止；这不是显存 OOM。本流程因此明确排除 FaceRefine。
- 二采请求 1344×768，实际得到 1376×800；后续比较必须使用实际尺寸，不能把它标记成严格 1344×768。
- 二采峰值显存接近 24 GB，主机内存更危险；不建议在同一实例上并行或直接叠加 32 秒 FaceRefine。
- 双人后处理若使用 `fast-detect face-index=1`，可能错误选中红发角色；本流程不做身份 refine，后续若启用必须改用坐标/ROI 或 analysis manifest，并保留目标框证据。
- Continuum Plus 的 `refine_state` 是运行时 chunk 状态，不能从结束后 MP4 或普通 latent 精确恢复；正式二采应在同一运行期间按 chunk 传递状态。

## 证据来源

- 一采/二采详细实测：[`sean_ref2va_continuum_dialogue_4x8_1344_face_20260926.md`](sean_ref2va_continuum_dialogue_4x8_1344_face_20260926.md)
- Timeline prompt：[`sean_ref2va_continuum_4x8_chunked_prompt_v2_20260925.txt`](sean_ref2va_continuum_4x8_chunked_prompt_v2_20260925.txt)
- H3 工程约束：[`docs/33_h3_mc_engineering.md`](../../docs/33_h3_mc_engineering.md)
- NativeAudioLock 机制：[`docs/h3-digital-human-research/06_native_audio_lock_motion_context.md`](../../docs/h3-digital-human-research/06_native_audio_lock_motion_context.md)
