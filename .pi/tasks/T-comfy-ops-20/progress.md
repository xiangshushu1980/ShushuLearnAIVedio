# T-comfy-ops-20 认知架构落地：ledger+incdoc+mentor(refs)+mem0 四件套（v3 最简版）

任务线：comfy-ops_ledger ｜ 开始：2026-08-22

## 目标

按 docs/dev/cognition-architecture-v3.md 实施 v3 最简版：零新增基础设施，只加 refs 指针 + 两条纪律。

## 实施清单（v3 §五）

- [x] ① AGENTS 两条纪律
  - 收尾四步 → 五步：改 multi-agent-collab skill 权威定义（①定论 append ledger ②经验 retain ③progress ④[STATE] ⑤finish；finish 防漏校验改验 ③④）
  - retain 打标转 ledger：mem0 skill 会话纪律补"实测定论 retain 打标 [定论候选] → 转项目 .pi/ledger/"
  - 项目 AGENTS.md 内容落盘补强制点（指向上述两 skill）
- [x] ② mentor concepts.json 加 refs 字段试点 3 条（h3 域）：
  - H3 VAE 选型 → refs [{kind:ledger, query:"VAE"}]
  - nvfp4 量化 → refs [{kind:ledger, query:"nvfp4"}]
  - Hybrid 融合模式 → refs [{kind:ledger, query:"Hybrid"}]
  - mentor-mode skill 同步补 refs 用法说明（复习前 incdoc grep .pi/ledger/ 取现行值）
- [x] ③ 试点验证：mentor 复习 → refs → incdoc grep → 取 ledger 现行值
  - VAE → h3-speed.md C-20260816-07 现行值（#15446 VAE 优化无明显提速）
  - nvfp4 → h3-speed.md C-20260816-02 现行值（TE 冷 11s 含 nvfp4 反量化）
  - Hybrid → h3-models.md C-20260816-20（🟡待验证状态可见）
  - incdoc grep 对 ledger 全文件逐文件可命中，条目级输出 ✓

## 关键决策

- 收尾四步权威定义在 multi-agent-collab skill（用户级），直接改权威源，不另在项目 AGENTS 复制（项目 AGENTS 只放指向+强制点）
- refs 只存 kind+query（不存文件路径）：复习时对 .pi/ledger/ 全文件 incdoc grep（文件少、毫秒级），与 v3"薄指针"一致；试点 3 条 query 均经实测验证可命中

## 收尾（五步）

- [x] ① 定论 append ledger：本任务为架构落地（无实测参数/加速比类定论），不入 ledger；后续任务按新纪律走
- [x] ② 经验 retain：用户级文件修改通告已 retain global（pi-agent-config 3d9a06b + 项目 94fc015）；误存 comfy-ops 池的 5 条已删
- [x] ③ progress 归档（本文件）
- [x] ④ [STATE] 更新
- [x] ⑤ hive-todo finish

## commit

- pi-agent-config 3d9a06b：multi-agent-collab/mem0/mentor-mode skill + mentor/concepts.json（用户级，scoped）
- comfy-ops 94fc015：AGENTS.md（项目级，scoped）
