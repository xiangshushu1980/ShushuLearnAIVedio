---
name: mem0
description: 多 Agent 共享记忆系统（Mem0）操作手册 — MCP 工具（memory_retain/recall/list/delete/update）用法、记忆池设计、内容分类决策树、迁移与运维。需要跨会话共享经验、检索历史实测数据/踩坑/用户偏好，或决定"内容该放文档还是记忆"时加载。
---

# Mem0 共享记忆操作手册

## 是什么

本地自托管的 agent 记忆系统，解决多 Agent 跨会话经验共享：
- **LLM**: DeepSeek API（提取/去重/总结，费用≈0）；已配置 **custom_instructions 中文提取**（保留技术术语原文）
- **Embedder**: bge-m3 本地（CPU 推理，**不占生视频 GPU**）+ **BM25 稀疏检索**（fastembed，术语精确命中）
- **存储**: Qdrant 本地（`.mem0/qdrant`，bge-m3 维度 1024）
- **接入**: MCP server（stdio）→ pi / Codex / Cursor 通用

## MCP 工具

| 工具 | 作用 | 示例 |
|---|---|---|
| `memory_retain(content, user_id?, agent_id?)` | 存一条经验/事实 | `memory_retain("Bernini 图像编辑用 res_multistep 采样器，LoRA 3.0/1.5")` |
| `memory_recall(query, user_id?, agent_id?, limit?)` | 语义检索（带分数） | `memory_recall("Bernini 用什么采样器")` |
| `memory_list(user_id?, agent_id?)` | 列出全部记忆（带 id） | 审查/人可读 |
| `memory_delete(memory_id, user_id?)` | 删一条（id 来自 list） | 清错记 |
| `memory_update(memory_id, content, user_id?)` | 改一条 | 修正过时经验 |

- **默认 user_id=comfy-ops**（项目共享池），所有 agent 读写同一池；agent_id 可选区分来源
- 记忆是人可读明文条目（LLM 提取），随时可看可改可删

## 内容分类决策树（与 AGENTS.md 一致）

```
├─ 稳定可执行参考（模型/工作流/参数/安装）→ 文档/SKILL（手册）
├─ 动态经验/踩坑/实测/偏好 → Mem0（本手册）
└─ 会话进度 → handoff
```

- 经验类**别写进文档**（文档膨胀的根因）；实测数字、踩坑实例、提炼认知 → retain
- 手册类**别塞进记忆**（语义检索不如文档精确，且记忆不该是权威源）

## 运维

- Server: `scripts/mem0_mcp.py`（conda env `mem0`，python 3.11）
- 启动: 由 MCP 客户端（pi）按需拉起，无需常驻；数据在 `.mem0/`
- 环境: `DEEPSEEK_API_KEY` 必须（依赖 pi 进程 env 或显式传）；`HF_ENDPOINT=hf-mirror.com` 已在脚本内默认
- 迁移脚本: `scripts/mem0_migrate.py`（批量 retain 用）
- 诊断: `Memory.from_config` 打印 `embedding_model.config.embedding_dims`（必须 1024，不是 1536 默认！）

## 已知坑（mem0ai 2.x）

- QdrantConfig `embedding_model_dims` 默认 1536（OpenAI 维度），本地 bge-m3 必须显式 1024，否则 add/search 维度错
- API 不一致：`add()` 用 `user_id=`；`search()`/`get_all()` 用 `filters={"user_id": ...}`；`delete(memory_id)` 只收 id（不带 user_id）
- mcp SDK 需 1.x（`pip install "mcp>=1.12,<2"`）；mcp 2.0 移除 FastMCP
- `.mcp.json` 新增 server 后需重启 pi 生效
- 中文提取：MemoryConfig `custom_instructions` 加“记忆条目必须使用简体中文输出，保留关键技术术语原文”（已配在 mem0_mcp.py）
- BM25 需要 `pip install "mem0ai[extras]"`（fastembed），首次使用自动下载稀疏模型
