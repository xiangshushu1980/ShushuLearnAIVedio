# Comfy-ops 项目约定（所有会话自动加载）

## 新会话开场（每个会话自动执行，无需用户提示）

1. 读 `docs/INDEX.md`（导航）→ `docs/05_session_handoff.md`（交接/待办）恢复上下文
2. `memory_recall` 检索相关经验（关键词：任务相关术语，如 Bernini/超分/踩坑）
3. 按需加载 skill / 读 references 分册（需要哪段读哪段，不整读大文件）
4. 以上完成后直接开始任务

## 内容落盘决策树（写任何内容前套用）

```
这条信息是？
├─ 稳定、可执行、需要查的参考（模型清单/工作流结构/参数表/安装要点）→ docs/ + .pi/skills/comfyui/（手册）
├─ 动态经验、踩坑、实测数据、对比结论、用户偏好 → Mem0 共享记忆（memory_retain）
│   ├─ 所有项目都需要（网络/机器/工具方法论）→ user_id="global"（跨项目通用池）
│   ├─ 本项目专属（Bernini/Wan2.2/ComfyUI 细节）→ user_id=comfy-ops（项目池）
│   └─ 说不清/可能跨界 → 默认 global（检索是命中式不是强制加载，放宽不易丢）
├─ 会话级进度（正在做什么/交接下一步）→ docs/05_session_handoff.md（短期，收尾归档）
└─ 拿不准 → 问用户
```

> recall 默认双池合并检索（global + comfy-ops 按分数排序），Agent 无需指定池；
> 显式传 user_id 则只查指定池（高级用法）。
> **手册 vs 经验**：可执行参考进文档/SKILL（单一写者）；经验性内容进 Mem0（retain 零协调）——别都堆进文档，文档越写越大时先问：这算经验还是手册？经验 → Mem0

## 写协作纪律（多 Agent）

- 写共享文件（SKILL/docs/工作流）前先 read 最新版，基于最新增量改
- SKILL.md / docs 单一写者；要并行写就开独立文件
- 每会话结束 git commit（改动可回滚）
