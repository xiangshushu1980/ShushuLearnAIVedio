# 历史归档

这里保存已经完成研究、被当前主线替代，或不再作为默认运行入口的资料。

## 使用规则

- 主区只保留当前主线、稳定备用能力和可直接运行的入口。
- 归档不等于删除：需要追溯实验细节时，先按下表定位，再读取对应目录或 Git 历史。
- 新的结论应先提炼到现行文档或 `.pi/ledger/`；不要把归档原始样本重新当作现行参数。

## 归档索引

| 主题 | 位置 | 结论摘要 | 检索词 |
|---|---|---|---|
| 认知架构旧稿 | `dev/cognition-architecture-design.md`、`dev/cognition-architecture-v2.md` | 已由 v3 定稿替代；v3 采用 ledger + incdoc + mentor refs + mem0 的最简结构 | `cognition architecture v1 v2` |
| Git 历史导出 | `project/git-history-handoff.md` | 历史提交、旧路径和交接时点的完整快照 | `git history handoff` |
| H3 旧加速对比 | `../../scripts/archive/historical/` | Sol-Attn 无速度优势且高动态更差；EasyCache 不作为默认档；旧 Turbo/V1/Sage runner 仅保留复盘用途 | `Sol-Attn EasyCache H3 Turbo` |
| LongCat / Sol-Attn 工作流 | `../../workflows/archive/historical/` | LongCat 本机产能不达标；Sol-Attn 已弃用 | `LongCat Sol-Attn` |
| Seedance 适用性实验 | `../../experiments/archive/seedance_verify/` | 仅保留“哪些提示词经验适用于 H3”的研究证据，不能视作 Seedance 生产方案 | `Seedance H3` |
| Promptor 对比样本 | `../../experiments/archive/promptor_compare/` | 结论已吸收到 `docs/11`、`docs/16`、`docs/17`；原始样本用于追溯 | `promptor T8` |
| 已完成任务进度 | `../../.pi/tasks/archive/` | 仅保留任务过程和证据链；结论以 docs、ledger 和 Mem0 为准 | `h3 turbo speech video ledger backfill` |

## 当前相关话题的查找顺序

先查 `docs/INDEX.md`、`.pi/ledger/` 和 Mem0；若需要原始证据，再查本页对应归档目录，最后查 Git 历史。
