# Comfy-ops 项目约定（所有会话自动加载）

## 新会话开场（每会话自动执行）

1. **声明任务名**：延续任务 → 读 `.pi/agents/<任务>/progress.md`；新任务 → 建进度文件（模板 `.pi/agents/PROGRESS_TEMPLATE.md`）
2. 读 `docs/INDEX.md`（导航，按需读）
3. `memory_recall`：项目池 `[STATE]`（其他任务线焦点/待办/热文件）+ 任务相关经验
4. 按需加载 skill / 读 references 分册（要哪段读哪段，不整读大文件）
5. 完成后直接开始任务

## 内容落盘

**判定树权威源：用户级 AGENTS.md + mem0 skill；此处只记项目专属执行要点：**
- 可查参考（模型清单/工作流结构/参数表/安装要点）→ `docs/` + `.pi/skills/comfyui/`（手册，按需读）
- 动态经验、踩坑、实测数据、对比结论、偏好 → Mem0：项目专属 → 池 `comfy-ops`；跨界 → `global`；**agent_id=任务名**
- **共享状态（焦点/活跃决策/全局待办）→ Mem0 `[STATE]`**（comfy-ops 池，格式见下）：每任务线一条，收尾 memory_update 维护，不重复 retain
- **私有进度 → `.pi/agents/<任务>/progress.md`**：做什么/做到哪/卡点/负责文件；阶段收尾必更新
- 拿不准 → 问用户

### [STATE] 条目格式（mem0 comfy-ops 池）

```
content: "[STATE] <YYYY-MM-DD> agent=<任务名> 状态=🟡进行中|⏸暂停|✅完成
焦点=一句话
活跃决策=[...]
全局待办=[T1. ... T2. ...]
热文件=[docs/X.md, workflows/Y.json]"
```

- 收尾 `memory_update` 更新自己的 [STATE]（先 recall 拿条目 id）
- **全局待办编号化（T1/T2...）**：跨 agent 精确引用（"T3 我在做，别动"），不写歧义表述
- **用户决策标记**：用户拍板的重要决策带 `用户决策 YYYY-MM-DD`——溯源是用户定的，recall 到不再重复问
- 开工前 recall `[STATE]`：避免重复劳动、看热文件声明、确认队列占用

> 手册 vs 经验：可执行参考进文档/SKILL（单一写者）；经验进 Mem0（retain 零协调）。文档越写越大时先问：经验还是手册？经验 → Mem0

## 多 PI Agent 协作纪律

- **任务分区**：文件认领制——谁负责谁写，跨线只读；并行写新内容开独立文件
- **写共享文件前**：read 最新版 + `git status` 查他人 WIP
- **scoped commit**：只 `git add <自己的文件>`，**禁止 `git add -A`**；message 带 `[任务名]` 前缀
- **共享资源占坑**：ComfyUI 队列/显存同一时刻只一个任务线跑批；跑批前 [STATE] 声明（含热文件），结束释放
- **收尾两更新**：progress（私有）+ [STATE]（共享）缺一不可；git commit
- **不整树操作**：禁止 `git rebase / reset --hard / checkout . / stash`（会卷走他人 WIP）
- 拿不准的共享决策 → 问用户，不自改共享约定
