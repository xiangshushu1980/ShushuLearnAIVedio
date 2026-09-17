---
name: comfyui
description: 在 comfy-ops 中操作 ComfyUI 环境、节点、API、图像或视频工作流时使用。提供本机入口、验证边界和按任务读取的分册索引。
---

# ComfyUI 核心 skill

本 skill 只负责 ComfyUI 的通用入口、运行边界和文档路由。详细内容按任务读取：

- 总入口：[INDEX.md](INDEX.md)
- 通用基础：[references/core/](references/core/)
- 图像生成：[references/image/](references/image/)
- 视频生成：[references/video/](references/video/)
- 工作流索引：[references/workflows/](references/workflows/)
- 排错索引：[references/troubleshooting/](references/troubleshooting/)

## 使用纪律

1. 先读 `INDEX.md`，按“任务目的”选择分册。
2. 只读取当前任务需要的 references；不要默认全文读取旧版综合档案。
3. 第一次使用的新节点必须先查源码/官方用法，再做最小验证。
4. 原始实验进入 `experiments/`；当前有效基线进入 docs 或对应分册；历史演进进入 `.pi/ledger/`；动态踩坑进入 Mem0。
5. 不把未实跑的社区工作流写成当前基线。
6. 涉及 H3 视频测试、生成或提示词时，先读 [h3-prompt-writing/SKILL.md](../h3-prompt-writing/SKILL.md) 及其模式参考，并读 [docs/17_h3_prompt_writing_rules.md](../../../docs/17_h3_prompt_writing_rules.md)；ComfyUI 分册负责运行和工作流，不能代替提示词格式契约。

## 环境摘要

- ComfyUI 本体：`/home/sean/projects/ComfyUI`
- 项目工作区：`/home/sean/projects/comfy-ops`
- 服务：`http://127.0.0.1:8188`
- 启动：`cd /home/sean/projects/ComfyUI && ./start.sh`
- Python：`/home/sean/projects/ComfyUI/venv/bin/python`
- 本机基线：WSL2 / RTX 4090 24GB / Python 3.13；版本以运行时探测为准。

模型清单见 [docs/02_models.md](../../../docs/02_models.md)，环境和 API 入口见 [references/core/environment.md](references/core/environment.md)。

## 当前主线摘要

- 视频主线：MiniMax H3，FL2VA/Ref2VA。
- 图像主线：ANIMA、KREA 2、ACE。
- 当前 KREA 2 最小入口：`workflows/krea2_t2i_test.json`。
- 当前正式工作流和研究状态以 `INDEX.md`、对应 references、docs 和 experiments 为准。

## 兼容档案

以下旧版文件暂时保留，作为完整历史档案和旧链接兼容入口：

- `references/nodes.md`
- `references/params.md`
- `references/workflows.md`
- `references/troubleshooting.md`
- `references/learning.md`

新内容优先写入分类分册，确认迁移完成后再收缩或归档旧档案。
