# H3 开源实现事实

## 1. 官方和核心运行入口

- [MiniMaxAI/MiniMax-H3](https://huggingface.co/MiniMaxAI/MiniMax-H3)：官方权重、模型卡和提示词文档。
- [ComfyUI 官方 H3 教程](https://docs.comfy.org/tutorials/video/minimax/minimax-h3)：ComfyUI 原生运行入口。
- [MiniMax-AI/awesome-minimax-h3-integration](https://github.com/MiniMax-AI/awesome-minimax-h3-integration)：官方集成资源索引，包含 ComfyUI、Diffusers、SGLang、vLLM 和 LightX2V。

H3 已经进入 ComfyUI 的核心支持路线。不同版本对量化、token、PackedLayout、Turbo sampler 和帧网格的支持可能不同，因此工作流必须和版本一起保存。

## 2. NativeAudioLock

[MiniMax-H3-NativeAudio-MusicVideo-Workflow](https://github.com/Shrek3OnVH5/MiniMax-H3-NativeAudio-MusicVideo-Workflow) 提供社区自定义节点和示例工作流。

仓库 README 说明：

- 将 source audio 锁入 H3 audio latent；
- 返回该音频用于最终视频保存；
- NativeAudioLock 应放在 H3 视频条件节点之后；
- 非人声时间段需要明确提示嘴部保持闭合；
- 每个新场景使用角色参考图；
- 片段续接使用上一段真实最终帧。

它是把外部 vocals 约束加入 H3 的工程扩展，不是 H3 官方基础 Ref2VA 的同义名称。

## 3. H3 FaceRefine

[ComfyUI-H3-FaceRefine](https://github.com/Carasibana/ComfyUI-H3-FaceRefine) 的设计目标是改善 H3 视频中的小脸和远景脸，使用：

```text
人脸检测/身份 embedding
→ 每帧脸部跟踪和裁剪
→ H3 局部重绘
→ 回贴到原视频
```

它依赖 YOLO、InsightFace、VideoHelperSuite 等组件，并在示例工作流中与 NativeAudioLock 配合。它解决的是脸部质量、身份和局部稳定，不是独立的口型算法。

## 4. 长视频开源扩展

社区出现了多个 H3 长视频方向：

- [ComfyUI-MiniMax-H3-LongMedia](https://github.com/vizart-vj/ComfyUI-MiniMax-H3-LongMedia)：多段生成、隐藏重叠、视频/音频连续性、lip-sync 和 VRAM 管理；
- [H3 Promptor](https://github.com/1038lab/ComfyUI-MiniMax-H3-Promptor)：提示词、L2VA、音频同步和多段时间线；
- [H3 Motion Context / T8 系列](https://github.com/T8mars)：将上一段的尾部 context 或 latent 带入下一段；
- [H3 Infinite Continuation Suite](https://github.com/HerrgottMargott/Herrgotts-H3-Infinite-Continuation-Suite)：围绕 FL2VA 首尾帧和长时续写；
- [H3 工作流集合](https://github.com/mdkberry/comfyui_workflows/tree/main/workflows_by_model/Minimax-H3)：包含远景脸修复和 H3 工作流变体。

这些项目大多是工作流层扩展，不是重新训练的 H3 长视频基础模型。共同点是保存并传递 video/audio latent 或 context，而不是独立生成 mp4 后直接拼接。

## 5. InfiniteTalk 的开源事实

[MeiGen-AI/InfiniteTalk](https://github.com/MeiGen-AI/InfiniteTalk) 是 Apache-2.0 的开源项目，目标是音频驱动的稀疏帧视频配音。

官方代码提供：

- image-to-video 和 video-to-video；
- single / multi-person；
- `clip` 和 `streaming` 模式；
- 480p 和 720p；
- `motion_frame`；
- `sample_audio_guide_scale`；
- TeaCache、低显存和量化入口。

代码中默认 `frame_num=81`，要求符合 4n+1 规则；默认 `max_frame_num=1000`，并提供 `motion_frame=9` 的长视频参数。I2V 官方说明约 1 分钟后更容易出现颜色变化，V2V 因为有原始视频的运动与机位参考而更适合长视频。

## 6. 开源组件职责

```text
H3 FL2VA / Ref2VA → 整体画面、动作、镜头、环境声
NativeAudioLock   → 外部 vocals 的 audio latent 约束
FaceRefine        → 人脸局部质量、远景脸、身份检查
Motion Context    → 跨片段 video/audio latent 或 context
InfiniteTalk      → 长时音频驱动和 sparse-frame streaming 参照
```
