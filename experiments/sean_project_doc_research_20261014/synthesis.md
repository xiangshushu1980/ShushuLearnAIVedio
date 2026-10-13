# 综合取舍与 skill 改造

Owner: Sean
日期：2026-10-14
目标：把开源方案中最有价值的机制转化为用户级 `project-doc-system` 的实际工作协议。

## 结论

采用“问题导航 + 分类权威正文 + 可定位证据 + 变化触发复核”的轻量组合。主要成果是 skill v2.0 与模板/按需参考，不是安装一个文档门户或需求管理平台。

三个研究方向互补：Diátaxis/MADR 改善找哪页与为什么选择；Doorstop/StrictDoc/Sphinx-Needs 提供身份、依赖与版本变化模型；lychee/Vale/MkDocs 说明结构检查能力及其盲区。事实真实性、决定采纳、任务验收仍需分别判断。

## 研究过程与材料

先由一个 agent 形成[总览](overview.md)，首轮推荐后启动两组深研，总览 agent 再研究第三组。主 agent 审计原 skill、对照本地契约、汇总三组报告，并独立阅读 Doorstop `reviewed/cleared/stamp/review` 与 MkDocs 默认校验级别源码。没有安装或执行候选工具。

- 10 个候选，9 个仓库浅克隆；TechDocs 仅查官方文档，不克隆大型门户仓库。
- 信息架构与决定：[architecture-decisions.md](architecture-decisions.md)。
- 证据追溯与变化：[traceability.md](traceability.md)。
- 质量工具与覆盖：[quality-gates.md](quality-gates.md)。
- 本地原版本问题：[baseline-audit.md](baseline-audit.md)。
- 仓库实际 URL、commit、许可证文件与长期本地位置：[repository-manifest.json](repository-manifest.json)。

覆盖 Exa、Tavily、GitHub API/官方仓库和官方正文；搜索摘要只用于定位。未做社区口碑、安装性能、工具运行或发布版兼容实测。旧 OpenFastTrace 路径未核验成功，不作为采用依据。具体失败与未覆盖信息见总览。

## 取舍表

| 来源机制 | 本地问题 | 最小采纳 | 没有采纳的部分 |
|---|---|---|---|
| Diátaxis 用途分类与渐进方法 | 存储分层不能回答读者要找哪页 | 按查规则/执行/理解/学习设置入口，一页一个主要用途 | 四套空目录、全库搬迁 |
| MADR 问题、候选、选择理由、后果 | 当前基线缺少选择依据 | 重要选择才记录理由与代价，确认方式链接证据 | 每次编辑写 ADR、全模板必填 |
| adr-tools 双向替代关系 | 旧入口可能继续指向历史结论 | 新旧记录互相说明替代关系，沿用已有 ID/ledger | CLI 与另一套流水号 |
| Doorstop 本项与依赖分开复核 | 只看日期，缺乏变化影响判断 | 精确来源版本，变化→待复核→人工判断 | 默认 hash/自动盖章当验收 |
| StrictDoc 稳定身份与图检查 | 改名拆分后证据关系可能丢失 | 长期跨文档引用时显式稳定 ID，迁移留指针 | 全库专用格式与所有引用无环 |
| Sphinx-Needs 关系/字段约束 | 复杂关系可能需要机器校验 | 已有 Sphinx 等满足条件时再评估 | 默认装栈或宣称新快照能力可生产使用 |
| lychee local/network 及 fragment 范围 | 链接成功被误当证据有效 | 分清目标缺失、网络未确认、锚点覆盖 | 默认全网扫描、吞超时使检查通过 |
| Vale 规则作用域 | 风格约定可能批量维护 | 已有规则或真实批量需求时选用 | 英文规则直接作为中文事实门禁 |
| MkDocs strict 依赖告警级别 | 构建成功被误当完整检查 | 发布视图派生，报告实际配置/覆盖 | 为 Markdown 文档强制建网站 |
| TechDocs 输入与生成物分离 | 生成索引被当第二份权威 | 指明输入和生成方式 | 单人 skill 引入门户栈 |

## 进一步分析：为什么优先选择 Doorstop 的复核区分

其价值不是哈希本身，而是把“变了什么”与“结论还成立吗”分开。主 agent 对固定源码观察确认：`cleared` 比较父项存档指纹，`reviewed` 比较本项指纹；`stamp` 包含指定字段，外部文件 SHA 取决扩展配置。原生字段本身没有证明人已阅读或语义已变化的能力。[固定实现](https://github.com/doorstop-dev/doorstop/blob/7cec21eca4ea09c243c03b3fcd01ec55d742ebf5/doorstop/core/item.py#L527)

两种常见情况：本项只改措辞，可保留结论并说明范围/依据不变；父项新增无关段落，可保留结论并更新核对版本。若把所有变化直接标为失效，就会增加无效实验；若只刷新日期，又会隐藏真实影响。因此采纳范围明确的复核理由与结果，默认不增加 hash 系统。

最小证据合同：结论与范围、证据精确位置、可解析来源版本、证据方式。稳定 ID、检查日期、复核理由和类型化依赖按实际需要增加；不可变 commit 链接已经包含版本，不再重复填 SHA。

这些是静态研究支持的设计建议，不是已经证明能节省多少成本的本地实测。需要未来真实使用反馈才能量化收益。

## 已实施变化

规范源：`/home/sean/.pi/agent/skills/project-doc-system`；Codex 的对应路径仍为软链。

| 文件 | 作用 |
|---|---|
| SKILL.md | v2.0：按事实类别确定真源，分清导航/研究流水、技术有效性/任务状态，补写入和复核流程 |
| references/maintenance.md | 范围审计、渐进迁移、入链修复、变化处理、检查结果分类 |
| references/design-and-tools.md | 采用机制与固定来源，按问题选工具，列默认检查盲区 |
| assets/index-skeleton.md | 短导航与可拆研究索引，去掉手工任务状态及证据总排序 |
| assets/baseline-record.md | 当前基线的范围、证据、边界与按需复核信息 |
| assets/decision-record.md | 重要决定的理由、代价、确认条件与演进链接 |
| assets/gitignore-template | 按路径/用途选择边界，不默认忽略全部图片、vendor 或 .pi |
| references/case-study.md | 保留原始观察，明确旧节号与特定场景推论的历史性质 |

原始 roughcut 案例仍可作为定位和重复维护问题的证据。图片白名单、数字禁令、固定第一调用等不再推广为所有项目的统一规则。没有改用户全局 settings/AGENTS、其他 skill 或 ComfyUI。

## 验证与交付范围

skill-creator 的 `quick_validate.py` 已通过；它只检查结构和格式，不证明行为质量。另做 skill 内本地引用完整性与变更范围审阅，并由独立 agent 用三种请求做文本行为审查，见 [skill-review.md](skill-review.md)。已按审查结果澄清：已有证据直接复用，仅实质替代/迁移建立后继关系；当前查验版本不覆盖原证据版本；模板占位符需交付前替换。没有执行候选工具、运行模型场景或做 token 成本实测。

本地正文引用检查覆盖 skill 与研究报告的 24 个文件链接，未发现缺失；代码示例、网络目标与章节锚点不在该检查范围。相关路径 `git diff --check` 通过。

下载源码保存在 `/home/sean/research/sean-project-doc-research-20261014/`，仓库外；报告内固定 commit 链接足以在本地副本不可用时重取。此次未创建 Task Center 任务，未改变任务生命周期。

Git 交付：用户级配置仓库 `main` 的 skill scoped commit 为 `561c4bd`。研究报告在 comfy-ops `main` scoped 提交，可用本目录的 Git 历史定位。两个仓库均有其他任务的历史提交尚未推送，因此本轮没有批量推送到 `origin/main`；源码克隆保留本地，不入项目 Git。
