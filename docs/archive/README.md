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
| 已完成的 T37 / TaoMate 规格 | `../../experiments/archive/completed_specs/` | 已完成评测或仅保留执行规格，当前不作为默认入口 | `T-comfy-ops-37 TaoMate HyperFlow` |
| Krea2 旧探针 | `../../experiments/archive/krea2_probes/` | 独立风格探针和早期 H3 桥接探针，不能替代当前 turnaround 主线 | `Krea2 Jibs magic H3 probe` |
| H3 MC 孤立案例 | `../../experiments/archive/h3_mc_orphan_cases/` | 已被任务记录和 `mc_test`/H3 主线资料取代的单文件案例 | `MC face clothing scene` |
| 已完成任务进度 | `../../.pi/tasks/archive/` | 仅保留任务过程和证据链；结论以 docs、ledger 和 Mem0 为准 | `h3 turbo speech video ledger backfill` |
| 提示词生成器计划 | `research/16_prompt_generator_plan.md` | 目标已由 h3-prompt-writing skill 实现；分层管线设计可作历史参考 | `prompt generator IR 分层管线` |
| IR 样本拆解 | `research/18_ir_sample_teardown.md` | 服务于 16 的学习基准；结构规律已吸收到 17 和 skill | `IR sample teardown 拆解` |
| antirez h3.c 架构研究 | `research/25_h3c_study.md` | 纯 C Metal 推理引擎架构笔记，本机 NVIDIA 不可运行；方法论参考 | `antirez h3.c Metal MLX` |
| DUIX Avatar 评估 | `research/27_DUIX_Avatar_数字人评估.md` | 4090 产能不达标；结论已反映在 h3-digital-human-research/ | `DUIX Avatar 数字人 4090` |
| 数字人在线方案对比 | `research/28_数字人在线方案_对比与价位.md` | 2026-09 时点快照，价格可能已变；仅作历史参考 | `数字人 在线 价格 HeyGen` |
| 每日视频系统设计旧稿 | `research/29_daily_video_system.md` | 被 31 服务架构替代；早期架构讨论记录 | `daily video system 每日话题` |
| 开源工作流 UI 调研 | `research/30_open_source_workflow_ui_research.md` | 调研阶段记录；选型结论在 31/32 | `workflow UI n8n Prefect Dagster` |
| 编排框架评估 | `research/32_orchestrator_framework_evaluation.md` | Conductor 验收完成；详细结果在 experiments/ | `orchestrator Conductor vertical slice` |
| HyperFlow 4090 研究 | `research/37_hyperflow_4090_ref2va_research.md` | 结论：不应写入生产推荐；pruned backbone 实验门槛记录 | `HyperFlow pruned 4090 Ref2VA` |
| SelfLift 4090 研究 | `research/38_h3_selflift_ref2va_4090_research.md` | 结论：Ref2VA+SelfLift 未证明，不值得继续测试 | `SelfLift Ref2VA 4090 latent lift` |

## 当前相关话题的查找顺序

先查 `docs/INDEX.md`、`.pi/ledger/` 和 Mem0；若需要原始证据，再查本页对应归档目录，最后查 Git 历史。
