# Comfy-ops 项目约定（所有会话自动加载）

## 新会话开场（每会话自动执行）

0. **路由：判断会话类型**（首消息是否 `[任务锚点 v1]` 锚点）
   - 是 → **任务会话**（已接上执行线）：读对应 `.pi/tasks/<任务>/progress.md`，走 1-4
   - 否 → **自由对话**：读 docs/INDEX.md 等上下文直接工作；**不声明任务线**、不自接
1. 读 `docs/INDEX.md`（导航，按需读）
2. 按需加载 skill / 读 references 分册（要哪段读哪段，不整读大文件）
3. 完成后直接开始任务

> 开场 recall [STATE] + TODO 对账已上升为全局规则（全局 AGENTS 会话纪律 + multi-agent-collab skill 开场清单），不再在本项目重复定义；池名 = comfy-ops（默认规则自动生效）

## 内容落盘

**判定树权威源：用户级 AGENTS.md + mem0 skill；此处只记项目专属执行要点：**
- 可查参考（模型清单/工作流结构/参数表/安装要点）→ `docs/` + `.pi/skills/comfyui/`（手册，按需读）
- **定论（实测得出的参数值/加速比/可行性/选型结论）→ 现行值写 `docs/`；演进史/覆盖链/证据锚写 `.pi/ledger/`**（结论谱系，append-only，规则见 `.pi/ledger/README.md`）
- 动态经验、踩坑、偏好 → Mem0：项目专属 → 池 `comfy-ops`；跨界 → `global`；**agent_id=任务名**
- **共享状态（焦点/活跃决策/全局待办）→ Mem0 `[STATE]`**（comfy-ops 池，agent_id=任务名）：每任务线一条，收尾 memory_update 维护，不重复 retain；**格式与维护细节见 multi-agent-collab skill**
- **私有进度 → `.pi/tasks/<任务>/progress.md`**：做什么/做到哪/卡点/负责文件；阶段收尾必更新
- 拿不准 → 问用户

> 手册 vs 经验：可执行参考进文档/SKILL（单一写者）；经验进 Mem0（retain 零协调）。文档越写越大时先问：经验还是手册？经验 → Mem0

### Skill 划分纪律（多 skill 维护）

- 三层：**共享层**（跨所有 skill 的稳定契约，只写一份用引用不复制）/ **核心能力 skill**（框架层：安装+理解+节点+通用工作流）/ **特定用例 skill**（业务层：组装核心）
- **经验永远不进共享库**：经验→Mem0（按池隔离），只有验证稳定跨场景通用才蒸馏进 skill 参数表
- 建 skill 前先读 `docs/14_skill_governance.md` 决定建哪种/经验放哪，再调 skill-creator 写文件

## 多 PI Agent 协作纪律

完整细则（任务分区认领/scoped commit/共享资源占坑/收尾两更新/不整树操作/[STATE] 维护）→ **加载 `multi-agent-collab` skill**（全局，所有项目通用）。核心速查：只 `git add <自己的文件>` 禁止 `git add -A`；跑批前 [STATE] 声明队列；收尾 progress + [STATE] 两更新缺一不可。
