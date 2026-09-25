# H3 Ref2VA + NativeAudioLock + Motion Context 工程流程

## 当前标准

当前数字人连续视频使用 `MiniMaxH3ReferenceToVideo`（Ref2VA）作为起始条件，随后接 `MiniMaxH3NativeAudioLock` 固定台词音频，再由 `MiniMaxH3MotionContext` 使用上一段保存的 AV latent 做续接。每个续接段的 `MotionContextTrim` 必须同时裁视频和音频，最终母片只挂载一次原始 Breeze 母带。

## Reference 的组成

- `ref_images.ref_image_0`：当前流程中的人物/场景参考图。它仍会影响每个续接段的生成，不是只锁身份的隔离参考。
- `context_latent`：MC 的主要连续性锚点，包含上一段的视频和音频 latent；这是跨段运动、人物状态和局部背景连续的核心。
- `NativeAudioLock` 的 `audio`：当前段的真实台词驱动音频；它不是普通 audio reference 模仿，而是把当前音频锁进 AV latent。
- `ref_audios`：本标准流程不使用。它属于音频参考/模仿路径，不应和 NativeAudioLock 混作台词锁定。
- `last_frame`：当前标准流程不使用；只有做尾帧参考对照时才单独加入，不能与 MC 的头部锚点混淆。

## 帧长与时间线铁律

H3 的合法视频长度必须满足 `17*k+5`，常用值为 `124、141、243`。禁止使用 `146` 等任意长度做 MC 链，因为 latent 时间网格会改变实际 pin/trim 帧数。

若续接段生成长度为 `N`、实际 MC 输出 `trim_frames=P`，则交付长度是 `N-P`。下一段音频预滚必须使用实际 `P/fps`，不能用配置里的 `context_length` 猜测。生成后必须用媒体探针核对实际帧数和音频时长。

推荐流程：

1. A 段生成并保存 AV latent。
2. B/C/D 每段加载上一段 AV latent；保持同一模型、分辨率、fps、采样器和 steps。
3. MC 使用 `context_length=22`、`audio_context_length=24`，并把 MC 返回的 `trim_frames` 接到 Trim。
4. Trim 同时接 `images` 和解码音频，`match_tail=true`。
5. 逐段记录 `generated_frames / trim_frames / kept_frames / audio_duration`。
6. 用保留帧数建立累计时间线，最后只从原始母带取对应总时长并挂载一次。

## 质量验收

必须分别检查每个接缝的画面 SSIM/跳变、全片人物和背景漂移、音视频时长以及口型同步。画面接缝平滑不代表音画同步；原始母带覆盖只能修复音轨，不能修复生成时的口型偏移。逐段生成音轨直接串联可能带来 AAC padding、重复尾部和点击声，不作为最终母带。

## Runner 防错

`scripts/h3_mc_runner.py` 在提交前拒绝非法 H3 length，要求 MC 段声明 `save_latent`，并在结果中记录输出媒体元数据；已有结果但声明的 latent 文件缺失时会自动重跑，避免 B 无 latent 却被跳过。
