# 任务进度：docs-audit-0816（文档 + mem0 + TODO 全面审计清理）

> 项目级私有进度（只有本任务线读写）。

## 任务
- 目标：① docs 过时/错误信息清理 + 优化合并 ② 同步更正 mem0（错误数字/纯重复/过时快照）③ TODO.md 任务合并优化
- 当前状态：🟡 进行中
- 我负责的文件区：docs/（仅错误修正，不跨线合并）、mem0 comfy-ops 池（update/delete）、~/.pi/agent/todo/TODO.md（comfy-ops 条目）

## 进度日志（append-only）

### 2026-08-16
- 全量审计：16 docs + INDEX、comfy-ops 池 ~200 条、global 池、TODO 全量、22 progress 文件
- docs 修正点：INDEX 日期+80s 描述、docs/10 §六"未实现"→已实现、docs/06 Bernini 模型缺失矛盾、docs/01 停止命令
- mem0 错误：4 条含"80s/112s/171s"swap 污染数据待 update
- mem0 重复/快照：~50 条纯重复/全局待办/热文件快照待 delete

### 2026-08-16（执行完成 ✅）
- docs：修正 4 处（INDEX 日期与 80s 描述、10 §六已实现、06 Bernini 缺失注、01 停止命令），docs_check.sh 全绿
- mem0：update 2 条（2527b3ed/52f750b1 的 80s→~22s）+ delete 84 条（4 污染数据 + ~22 纯重复 + ~58 快照）全部成功
- TODO：链 B 三调研收口（T1 实测完成/T3 Qwen3-TTS/T2 被 Regenerate-2K 取代）；发现并解决 T-20260812-06 撞号（AudioSep 关闭释放编号）
- 遗留提示：①07c87b4c0 含 "80s" 字样（vLLM 解析上下文，低优先）②params.md/nodes.md 仍在 git WIP（他线未提交，勿动）③更激进合并（如 docs/19 首帧节与 21 重复、06/02 Bernini 详情重复）可后续再做
