# 项目文档 skill 调研

Owner: Sean
日期：2026-10-14
目标：研究现有开源方案，优化用户级 `project-doc-system`；规范源是 `/home/sean/.pi/agent/skills/project-doc-system`，Codex 软链共用。

## 阅读入口

- [现有 skill 审计](baseline-audit.md)：文本审查发现的问题。
- [方案总览](overview.md)：10 个候选与一手来源、渠道覆盖和限制。
- [信息架构与决策记录](architecture-decisions.md)：Diátaxis、MADR、adr-tools 固定源码研究。
- [证据追溯与变更复核](traceability.md)：Doorstop、StrictDoc、Sphinx-Needs 固定源码研究。
- [轻量质量检查](quality-gates.md)：lychee、Vale、MkDocs 固定源码研究。
- [综合取舍与改造](synthesis.md)：主 agent 的分析、采纳决策与最终交付。
- [仓库版本清单](repository-manifest.json)：9 个实际下载仓库的 URL、commit、许可证文件与本地位置。
- [独立文本行为审查](skill-review.md)：三个请求场景的审查及轻量修订建议。

下载仓库存于 `/home/sean/research/sean-project-doc-research-20261014/`，只用于静态研究，不作为交付依赖；各报告记录 commit 与上游永久链接。

任务状态与控制权以 Task Center 为准；本页仅为研究材料导航。此次执行前已查询 Task Center，未找到对应任务；用户未要求立项，因此未新建远程任务。
