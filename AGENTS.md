# Comfy-ops 项目约定（所有会话自动加载）

> 通用纪律（开场 recall/协作状态/TODO 对账、多 Agent 协作、内容落盘判定树）→ **用户级 AGENTS.md + 全局 skill（multi-agent-collab / mem0）**，本项目不再重复定义。此处只记**项目专属**执行要点。

## 新会话开场（每会话自动执行）

1. 读 `docs/INDEX.md`（项目导航，按需读）
2. 按需加载本项目 skill（`.pi/skills/` 下）或 references 分册（要哪段读哪段，不整读大文件）
3. 完成后直接开始任务

> TODO 不全量加载上下文；只用 `hive-todo search <关键词>` 或任务锚点提供的摘要按需检索。

## 内容落盘（项目专属位置）

- 可查参考（模型清单/工作流结构/参数表/安装要点）→ `docs/` + `.pi/skills/comfyui/`（手册，按需读）
- **定论（实测得出的参数值/加速比/可行性/选型结论）→ 现行值写 `docs/`；演进史/覆盖链/证据锚写 `.pi/ledger/`**（结论谱系，append-only，规则见 `.pi/ledger/README.md`）
  - **强制点**：任务收尾走「收尾五步」①定论 append ledger（见 multi-agent-collab skill）；会话结束 retain 时实测定论打标 `[定论候选]` → 统一转 ledger（见 mem0 skill）
- 动态经验、踩坑、偏好 → Mem0 池 `comfy-ops`（跨界 → `global`）

## Skill 划分纪律（多 skill 维护）

- 三层：**共享层**（跨所有 skill 的稳定契约，只写一份用引用不复制）/ **核心能力 skill**（框架层：安装+理解+节点+通用工作流）/ **特定用例 skill**（业务层：组装核心）
- **经验永远不进共享库**：经验→Mem0（按池隔离），只有验证稳定跨场景通用才蒸馏进 skill 参数表
- 建 skill 前先读 `docs/14_skill_governance.md` 决定建哪种/经验放哪，再调 skill-creator 写文件
