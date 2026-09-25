# Breeze TTS Docker 构建进度

更新时间：2026-09-14

## 当前状态

- 状态：进行中
- Docker 构建进程：PID 343456，已运行约 1 小时 49 分钟
- 镜像目标：`comfy-ops/breeze-tts:cu128`
- Dockerfile：`tools/breeze-tts/Dockerfile`
- Compose 配置：`tools/breeze-tts/docker-compose.yml`
- 当前阶段：CUDA 12.8 基础镜像和 PyTorch 2.9.1+cu128 已下载，正在安装依赖/编译 `flash-attn`
- 最终镜像尚未生成

## 已完成

- Docker、Docker Compose、NVIDIA Container Toolkit 可用
- 确认 Breeze venv 使用 PyTorch 2.9.1+cu128
- 确认 ComfyUI 使用 PyTorch 2.13.0+cu130
- 确认直接在 ComfyUI venv 编译 flash-attn 会因 CUDA 13.0 与 PyTorch CUDA 版本不匹配失败
- 创建 CUDA 12.8 + Python 3.12 + Python 开发头文件的 Dockerfile
- Docker 构建已完成基础 CUDA 镜像拉取和大部分 Python/CUDA 包下载

## 运行中的正式流程

- ComfyUI Breeze 节点已安装并正常加载
- BF16 模型已下载到 `ComfyUI/models/breezetts2/drbaph_Breeze-TTS-2-comfyui/`
- Multi-Speaker + BF16 + SDPA + CUDA Graphs 已成功测试
- 当前多人测试流程不依赖 Docker

## 后续 TTS 标准流程（已确认）

> **跨 Agent 规则：用户后续要求制作声音/配音时，默认使用此 ComfyUI Breeze 流程；除非用户明确指定其他 TTS。新 Agent 必须先读取本节。**

- 宿主：ComfyUI
- 节点：`ComfyUI-Breeze-TTS-2`
- 模型：`bf16 (best quality)`
- Attention：`sdpa`（Flash Attention 尚未在 ComfyUI CUDA 13 环境安装）
- Decode：`cuda_graphs`
- 对话：`BreezeTTS2Speaker` + `BreezeTTS2MultiSpeaker`
- 输出：24kHz、单声道 FLAC/WAV
- 连续任务完成后停止/重启 ComfyUI 释放显存
- Docker 仅作为后台构建和后续 Flash Attention 实验环境

## 后续待办

1. 等待 Docker 构建结束并记录成功/失败日志。
2. 如果 `flash-attn` 编译成功，运行容器内最小 TTS smoke test。
3. 对比 ComfyUI 节点 SDPA、Flash Attention 和 Docker 官方 CLI 的耗时。
4. 验证 Docker 停止后显存完全释放。
5. Docker 验证通过后，再决定是否切换为正式 Breeze 流程。

## 重要说明

- 不删除现有 `.venv-breeze-tts`。
- Docker 模型通过宿主机目录挂载，模型更新不需要重新构建镜像。
- Breeze 原生输出保持 24kHz、单声道。
