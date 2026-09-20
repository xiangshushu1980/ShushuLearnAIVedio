# 协作机制结论谱系（Collaboration Governance Ledger）

> 定位：多 Agent 协作机制、任务系统行为、用户级治理约定的「定论谱系」（跨项目通用）。
> 与 h3-*.md（comfy-ops 技术参数）分开，避免污染技术谱系。
> 规则与模板沿用 `README.md`：append-only、C-ID、状态机、来源任务、证据锚、独立 commit。

---

## 〇、条目索引

| C-ID | 主题 | 状态 | 所在文件 |
|---|---|---|---|
| C-20260822-01 | 协作三时点分层（建任务体检 / 自由对话轻检 / 锚点注入） | ✅现行 | collab-governance.md |
| C-20260907-01 | Conductor Worker 失败回报与重试契约 | ✅现行 | T-32 验证 |

---

### C-20260822-01 | 协作三时点分层
- 状态：✅现行（valid_from 2026-08-22）
- 现行值：多 Agent 协作的任务系统查询/建任务行为按三时点分层——①自由对话**默认不查任务系统**，仅信号触发一次轻量 search（命中才提示、无命中静默，触发原因可审计）；②**建任务前强制「决策点体检」**：查四层（TODO search / [STATE] list / done 归档 / mem0+docs）补充依赖·权限·验收，输出五分类结论（重复/冲突/依赖/已否决/可立项）+ 依据，**只建议不阻止**，用户拍板后才 add/claim；③任务会话锚点注入保持现状不变。触发信号为可观测规则（显式历史指代/执行承诺/共享资源写操作/跨项目/任务 ID，时机锚点=准备调用工具或改文件前）。
- 时间线：
  - 2026-08-22 提出并拍板：用户提议「全询问式（不自动建任务/不主动查询）」→ 讨论修正为三时点分层 → Codex（gpt-5.6-terra）评审修正（补执行承诺漏检、体检五分类结构化、信号可观测化+审计、ledger 元数据）→ 拍板「只建议不阻止 + 指标靠审计日志」；来源：自由对话讨论 + Codex 评审（无任务 T-ID）
  - 2026-08-22 落地：AGENTS.md 新增建任务决策点体检 + 自由对话默认不查（commit 879fc90）；multi-agent-collab skill 同步 + Codex 优化重写 206→191 行压缩 45%（commit 72582fc，独立会话实测 16 机制点全保留）
- 证据锚：~/.pi/agent/AGENTS.md（创建与启动节/查询与跨项目节）/ ~/.pi/agent/skills/multi-agent-collab/SKILL.md / git pi-agent-config 879fc90, 72582fc / mem0 global「用户级文件修改纪律」通告


### C-20260907-01 | Conductor Worker 失败回报与重试契约
- 状态：✅现行（valid_from 2026-09-07，09-08 复测）
- 现行值：**Worker 失败必须显式回报 FAILED 并由 Conductor 重试，不静默吞掉**——不存在 Source 文件触发 `FileNotFoundError` 时，Run `d71e4c11-5bec-4c16-ae3d-7d43e7bbf5f8` 由 Worker 回报 FAILED，Conductor 按契约重试该 Source 并保留失败轨迹。
- 时间线：
  - 2026-09-07 提出：T-comfy-ops-32 首次验证 Worker 失败回报与重试机制（来源任务 T-comfy-ops-32）
  - 2026-09-08 复测：同场景再次验证一致（来源任务 T-comfy-ops-32）
- 证据锚：.pi/tasks/T-comfy-ops-32/progress.md / mem0 b0b33c26
