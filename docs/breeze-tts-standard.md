# Breeze TTS 当前标准流程

## 默认入口

用户提出“用 Breeze 制作声音/配音”时，默认使用：

**ComfyUI-Breeze-TTS-2 节点流程**

原因：当前任务需要多人对白，ComfyUI 节点提供 `BreezeTTS2Speaker` + `BreezeTTS2MultiSpeaker`，可以为每个角色独立设计/克隆声音，并直接按角色脚本生成，不需要手工拼接音频。

## 默认配置

- 模型：`bf16 (best quality)`
- device：`auto` / CUDA
- attention：优先 `sdpa`；ComfyUI 环境成功安装 `flash_attn` 后再测试 `flash_attention`
- decode：`cuda_graphs`
- 多人：`BreezeTTS2Speaker` + `BreezeTTS2MultiSpeaker`
- 输出：24kHz、单声道，优先 FLAC；需要兼容时使用 WAV
- 连续任务：一次加载模型，连续生成后再停止/重启 ComfyUI 释放显存

## 三套环境的定位

### ComfyUI 节点：正式默认流程

路径：`/home/sean/projects/ComfyUI/custom_nodes/ComfyUI-Breeze-TTS-2`

适用于：多人对白、角色声音设计、批量配音、与 ComfyUI 视频流程衔接。

### 官方 Breeze CLI/venv：备用流程

路径：`/home/sean/projects/comfy-ops/.venv-breeze-tts`

适用于：单人语音、官方 CLI/API 对照测试和故障回退。不作为多人短剧的默认入口。

### Docker：隔离和性能实验环境

目标镜像：`comfy-ops/breeze-tts:cu128`

适用于：固定 CUDA 12.8 编译环境、安装/测试 `flash-attn`、复现实验。Docker 构建完成并验证前，不替代 ComfyUI 默认流程。

## 模型位置

ComfyUI 节点使用：

`/home/sean/projects/ComfyUI/models/breezetts2/drbaph_Breeze-TTS-2-comfyui/Breeze-TTS-2-bf16.safetensors`

官方 CLI/Docker 使用：

`/home/sean/projects/comfy-ops/models/breeze-tts-2/`

## 读取规则

新 Breeze TTS 任务只需读取本文件和 ComfyUI 节点的 `SKILL.md`；不需要扫描历史 Breeze 任务。只有任务明确涉及 Docker 构建或 Flash Attention 时，才读取 Docker 任务进度。
