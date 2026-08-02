---
name: mem0
description: 多 Agent 共享记忆系统（Mem0）操作手册 — MCP 工具（memory_retain/recall/list/delete/update）用法、记忆池设计、内容分类决策树、迁移与运维。需要跨会话共享经验、检索历史实测数据/踩坑/用户偏好，或决定"内容该放文档还是记忆"时加载。
---

# Mem0 共享记忆操作手册

## 是什么

本地自托管的 agent 记忆系统，解决多 Agent 跨会话经验共享：
- **LLM**: DeepSeek API（提取/去重/总结，费用≈0）；已配置 **custom_instructions 中文提取**（保留技术术语原文）
- **Embedder**: bge-m3 本地 + **BM25 稀疏检索**（fastembed，术语精确命中）
- ⚠️ **显存（实测 2025-08-02）**：sentence-transformers 加载 bge-m3 时默认探测 CUDA 并把模型放 GPU（**占 ~2.6GB 显存**，WSL2 下 nvidia-smi per-process 显示 N/A 测不出，需用总显存差值法）；已在 `mem0_mcp.py` embedder 配置 `model_kwargs: {"device": "cpu"}` 强制 CPU 推理，显存占用归零（代价：embedding 慢一点，毫秒~百毫秒级，可忽略）
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

## 内容分类决策树

> 规则唯一权威源在项目根 `AGENTS.md`（每个会话自动加载）。摘要：

```
稳定可执行参考（模型/工作流/参数/安装）→ 文档/SKILL（手册）
动态经验/踩坑/实测/偏好 → Mem0（本手册，retain 零协调）
会话进度 → handoff（短期）
```

- 经验类**别写进文档**（文档膨胀的根因）；实测数字、踩坑实例、提炼认知 → retain
- 手册类**别塞进记忆**（语义检索不如文档精确，且记忆不该是权威源）
- 会话进度**别进 Mem0**（短期、结构化、需要人看 → handoff）

## 多 Agent 使用原则（推荐）

1. **写经验 = 直接 retain，零协调**：append-only 无冲突，LLM 自动去重合并；不需要“先读后写/互相等待”（那是文档的规则）
2. **读经验 = recall 随时并行**：只读无副作用
3. **命名空间**：`user_id=comfy-ops` 共享池（项目级共写共读）；`agent_id` 私有/任务级（中间态不污染共享池）
4. **权威边界**：经验/事实进 Mem0（写自由、可覆盖）；手册/权威参考进文档（单一写者、低频更新）
5. **矛盾结论**：新结论 retain 带日期/条件，必要时 update 旧条目，检索以最近/明确者为准
6. **会话进度不进 Mem0**：仍是 handoff

## 运维

- Server: `scripts/mem0_mcp.py`（conda env `mem0`，python 3.11）
- **HTTP 常驻模式**（streamable-http）：`scripts/start_mem0.sh` 启动，监听 `http://127.0.0.1:8899/mcp`；**单实例服务所有 pi 会话**（消除 stdio 多进程撞锁）
- `.mcp.json` 配置：`"mem0": {"url": "http://127.0.0.1:8899/mcp"}`（url 模式，非 command）
- Key：`~/.config/mem0_deepseek_key`（600 权限，不入 git；server 启动时自动读）或环境变量 `MEM0_DEEPSEEK_API_KEY`
- 重启 server：`pkill -f mem0_mcp.py && ./scripts/start_mem0.sh`（首次启动需加载 bge-m3 ~30s）
- 数据: `.mem0/`（gitignored）

## 已知坑（mem0ai 2.x）

- QdrantConfig `embedding_model_dims` 默认 1536（OpenAI 维度），本地 bge-m3 必须显式 1024，否则 add/search 维度错
- API 不一致：`add()` 用 `user_id=`；`search()`/`get_all()` 用 `filters={"user_id": ...}`；`delete(memory_id)` 只收 id（不带 user_id）
- mcp SDK 需 1.x（`pip install "mcp>=1.12,<2"`）；mcp 2.0 移除 FastMCP
- `.mcp.json` 新增 server 后需重启 pi 生效
- 中文提取：MemoryConfig `custom_instructions` 加“记忆条目必须使用简体中文输出，保留关键技术术语原文”（已配在 mem0_mcp.py）
- BM25 需要 `pip install "mem0ai[extras]"`（fastembed），首次使用自动下载稀疏模型
- **Qdrant 嵌入式单实例锁**：`.mem0/qdrant` 同一时刻只允许一个进程访问（独占锁）；多进程会报 "already accessed by another instance"。**HTTP 常驻模式已从架构上消除**（单 server 进程串行访问）——不要回退到 stdio 多实例模式
- **stdio 模式淘汰**：mcp 2.0 移除 FastMCP（需 1.x）；HTTP 模式用 `transport="streamable-http"`（不是 "http"）
- **启动注意**：`start_mem0.sh` 前台跑时 curl 探测会挂起 ~30s（等 bge-m3 加载）；用 `setsid nohup ... &` 脱离进程组，避免 shell 超时把 server 一起杀掉
- **WSL2 显存测量坑**：nvidia-smi per-process 对 GPU 内存显示 N/A（加载了 libnvdxgdmal 但不显示数字）；判断某进程是否占显存要用总显存差值法（`nvidia-smi --query-gpu=memory.used` 停前/停后对比）
