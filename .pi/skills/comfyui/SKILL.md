---
name: comfyui
description: comfy-ops 的 ComfyUI 研究与维护入口；跨项目图片操作使用用户级共享 comfyui skill。
---

# ComfyUI 项目研究与维护入口

Owner: Sean。

日常图片生成、参考图编辑、Qwen 三视图操作的唯一当前手册是用户级 [`comfyui`](/home/sean/.pi/agent/skills/comfyui/SKILL.md)（本机路径 `/home/sean/.pi/agent/skills/comfyui/SKILL.md`，Codex 软链引用）。直接由当前 Agent 加载，不需要启动另一个 comfy-ops Agent。

共享命令：`pi-skill-run comfyui qwen_image.py --request /absolute/request.json --output-dir /absolute/new-run`。默认离线规划；具体请求与执行规则只在共享 skill 维护。

本目录保留 [INDEX.md](INDEX.md) 和现有分册，作为节点、模型、视频、运维与历史研究的导航。按需进入，不默认整读。项目 AGENTS 只适用于本仓库工作；运行生成时遵循共享服务与资源规则。

模型/节点现状以运行时和对应实验为准；未实跑的社区工作流不得标为生产基线。H3 相关工作仍先读项目 `h3-prompt-writing` skill 及模式参考。
