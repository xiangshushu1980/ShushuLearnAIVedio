# Comfy-ops 项目约定（所有会话自动加载）

## 新会话开场（每个会话自动执行，无需用户提示）

1. 读 `docs/INDEX.md`（导航）→ `docs/05_session_handoff.md`（交接/待办，结构按 `docs/05_TEMPLATE.md` activeContext 模板：焦点/环境/变更/活跃决策/模式偏好/待办）恢复上下文
2. `memory_recall` 检索相关经验（关键词：任务相关术语，如 Bernini/超分/踩坑）
3. 按需加载 skill / 读 references 分册（需要哪段读哪段，不整读大文件）
4. 以上完成后直接开始任务

## 内容落盘

**权威判定树在用户级 AGENTS.md（注入）+ mem0 skill（按需查），此处只记项目专属执行要点：**
- 可查参考（模型清单/工作流结构/参数表/安装要点）→ `docs/` + `.pi/skills/comfyui/`（手册，按需读）
- 动态经验、踩坑、实测数据、对比结论、偏好 → Mem0：项目专属（Bernini/Wan2.2/ComfyUI 细节）→ 项目池 `comfy-ops`；说不清/跨界 → `global`
- 会话级进度 → `docs/05_session_handoff.md`（按 `docs/05_TEMPLATE.md` 模板更新，活跃决策/模式偏好板块勿丢；收尾归档）
- 拿不准 → 问用户

> 手册 vs 经验：可执行参考进文档/SKILL（单一写者）；经验性内容进 Mem0（retain 零协调）——别都堆进文档。文档越写越大时先问：这算经验还是手册？经验 → Mem0

## 写协作纪律（多 Agent）

- 写共享文件（SKILL/docs/工作流）前先 read 最新版，基于最新增量改
- SKILL.md / docs 单一写者；要并行写就开独立文件
- 每会话结束 git commit（改动可回滚）
