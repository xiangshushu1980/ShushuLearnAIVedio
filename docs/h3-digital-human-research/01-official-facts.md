# H3 官方事实

## 1. 模型和任务分支

官方模型卡将 H3 描述为支持视频和音频联合生成的多模态模型，并公开两类主要任务 checkpoint：

| 分支 | 官方含义 | 数字人用途 |
|---|---|---|
| FL2VA | First/Last-Frame-to-Audio-Video | 用首尾姿态约束动作路径 |
| Ref2VA | Reference-to-Audio-Video | 用人物图、视频、音频建立身份和表演参考 |

官方还列出 T2VA、I2VA、FL2VA、Ref2VA 等任务形式。公开权重包含 transformer、processor、tokenizer、visual VAE 和 audio VAE。[H3 官方模型卡](https://huggingface.co/MiniMaxAI/MiniMax-H3/blob/main/README.md)

H3 的关键特征不是传统“先生成视频、再单独配音”，而是视频和音频在联合音视频 latent 中共同生成。这解释了它为什么能同时产生人物动作、环境声、动作声和说话表现，也解释了为什么固定外部音频会比普通后期配音更复杂。

## 2. 官方提示词事实

基础提示词需要三个核心字段：

```text
integrated_multimodal_description
overall_soundscape
non_diegetic_music
```

其中：

- `integrated_multimodal_description`：镜头、角色、动作、表情、说话人、台词和场景内声音；
- `overall_soundscape`：环境声、脚步、衣物、呼吸和动作声；
- `non_diegetic_music`：只有观众听到的背景音乐。

说话人使用稳定 ID，例如 `(S1)`、`(S2)`；实际台词放在 `<d>[语言] 原文</d>` 中，官方要求保留用户原始台词和标点，不要改写。[官方基础提示词指南](https://huggingface.co/MiniMaxAI/MiniMax-H3/blob/main/docs/VIDEO_PROMPT_WRITING_GUIDE_base_en.md)

全参考模式增加 `subject_definitions`、`summary`、`retention_analysis` 等字段，用来区分人物、场景、服装、动作、视频参考、图片参考和音频参考。[官方 Ref2VA 提示词指南](https://huggingface.co/MiniMaxAI/MiniMax-H3/blob/main/docs/VIDEO_PROMPT_WRITING_GUIDE_ref_en.md)

官方相机动作词也有明确结构：运动类型、幅度和速度，例如 `push in with small amplitude at slow speed`。

## 3. 参考素材和时长事实

公开 ComfyUI R2V 接口支持：

- 最多 9 张参考图；
- 最多 3 个参考视频；
- 最多 3 个参考视频音轨；
- 最多 3 个独立参考音频。

参考视频通常以 24fps 帧序列输入，公开说明的参考视频范围为 2–15 秒。[ComfyUI R2V 接口说明](https://github.com/TheTerrasque/minimax-h3-frontend/blob/main/resources/COMFYUI_API_GUIDE.md)

ComfyUI 工作流会把秒数转换成 H3 需要的帧数网格，而不是直接接受任意帧数。官方本地质量目标以 768p 为主；官方描述的 2K 流程，是本地 H3 生成后再调用 H3-Context-IR 和 H3-Regenerate-2K API。[官方 2K 流程说明](https://huggingface.co/MiniMaxAI/MiniMax-H3/blob/main/README.md)

## 4. 官方资料没有承诺的内容

以下能力不能从“支持音视频联合生成”直接推导出来：

- 外部播音母带逐字、逐音素原样保留；
- 多个角色的音频永远不会串到其他角色；
- 单张角色图能在长时间内零漂移；
- 一次采样可以持续生成分钟级主持人视频；
- 低步数 Turbo 一定同时保持视频和音频质量。

这些内容需要社区实现或本地验证。

## 5. 许可证

模型使用 H3 Community License Agreement，而不是普通 Apache-2.0 模型许可证。当前许可证页面需要单独核对 Applicable Territory 和商业使用条件。[官方许可证](https://huggingface.co/MiniMaxAI/MiniMax-H3/blob/main/LICENSE)

## 6. NVIDIA H3 Super Acceleration 与本地 PDD 的区别（2026-09-02）

NVIDIA 的 H3 Super Acceleration 不是 H3 原生的“草稿+精修”结构，而是额外搭建的两模型流水线：H3 以 4-step LightX2V 生成低分辨率草稿，再由 LTX-2.5 进行 3-step latent refinement，最后复用 H3 音频。[NVIDIA 官方说明](https://nvlabs.github.io/Sana/Sol-Engine/H3-Super-Acceleration/)

PDD Acc 8-step 则是单个 H3 模型内的采样加速：使用 PDD head bank 和专用 SIGMA/Euler，直接输出最终 H3 视频，不包含 LTX 精修。两者的“4 步”不可直接等价比较。
