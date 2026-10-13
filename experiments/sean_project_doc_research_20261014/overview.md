---
owner: Sean
observed_at: 2026-10-14
scope: project-doc-system skill 开源方案总览
status: overview-complete; source-deep-dives-pending
---

# 项目文档系统：开源方案总览

## 结论与筛选依据

优化对象是 agent 的写入、定位、维护协议，最有价值的是组合三组机制：按读者需求组织内容与保留决策演进；用显式依赖与审阅指纹发现失效；用按需校验保证链接和字段可读。网站发布只作为可选出口。筛选依据是解决现有 skill 的具体缺口、机制能否以 Markdown 轻量实现、源码/文档是否可核验，未以 stars 排名。

当前 skill 已有分层、单一正文、摘要密度、Git 边界和增量定位纪律。待修正项（本报告判断）：

- 存储层级与内容类型混在一起。边界/摘要/细节/历史回答“权威正文在哪”，教程/操作/参考/解释回答“读者要做什么”，应视为两个维度。
- “文档声称 < 源码确认 < 静态推断 < 本地实测”不是通用可靠性等级。静态推断不天然优于源码确认，局部实测不天然覆盖全局行为。拆分证据类型、适用版本/环境、验证覆盖、限制与来源锚点。
- “当前状态只在摘要层维护”须限于文档/技术结论的有效性；任务进度由 Task Center 维护，索引只链接或注明投影时间。
- 没有明确 supersedes、过期触发、来源依赖、审阅结果和失效处置。
- “摘要层可整读”与“禁止整读摘要层”冲突；按体积与问题范围选择读入口、局部表或全文，避免绝对化。
- 生成索引/参考页不应成为另一份人工维护真源；需标出输入与生成方式。

## 候选 10 方案

| 方案 | 已核验一手机制 | 可吸收能力 | 限制/深研价值 |
|---|---|---|---|
| [Diátaxis](https://diataxis.fr/) / [源码](https://github.com/evildmp/diataxis-documentation-framework) | 按 tutorial/how-to/reference/explanation 四种用户需求组织；无实现工具限制 | 内容分类与“哪类文档解决哪种问题”的分流 | 是方法而非状态数据库；高价值深研 |
| [MADR](https://adr.github.io/madr/) / [源码](https://github.com/adr/madr) | Markdown 决策模板含 context/options/outcome/consequences/confirmation；status 可 superseded | 决策缘由、确认标准、替代链、最小模板 | 完整模板可能冗长；高价值深研；官网部分工具说明与最新模板不一致，应固定源码 commit |
| [adr-tools](https://github.com/npryce/adr-tools) | `adr new -s` 创建替代决策并更新旧决策的状态与链接 | 双向替代链一致性、索引自动生成 | 壳脚本机制简单；2024 后 push 较少不等于不可用；高价值深研 |
| [Doorstop](https://doorstop.readthedocs.io/en/latest/) / [源码](https://github.com/doorstop-dev/doorstop) | 一条需求一个 YAML，文档组成树，可检查需求/测试的链接完整性 | review 指纹、suspect link、变更后重新审阅机制（需源码确认细节） | 文件粒度和术语较重；机制价值高于整套安装；高价值深研 |
| [StrictDoc](https://strictdoc-project.github.io/features/) / [源码](https://github.com/strictdoc-project/strictdoc) | SDoc 与 Markdown 参与追溯图；需求关联代码/测试；覆盖与变更视图 | 稳定 ID、缺失引用、来源覆盖、结构化关系 | 专用格式与整套系统对本 skill 可能偏重；高价值对照 |
| [Sphinx-Needs](https://sphinx-needs.readthedocs.io/en/latest/) / [源码](https://github.com/useblocks/sphinx-needs) | 在 Sphinx 文档中管理 needs/requirements | 将结构化项嵌入正文，关系校验与导出 | 依赖 Sphinx；本轮正文入口核验，详细配置留源码深研 |
| [Vale](https://docs.vale.sh/) / [源码](https://github.com/vale-cli/vale) | 根据文档 markup 作用域执行可配置规则，代码和 URL 可跳过 | 人可读写作约定与机器规则的分工；按需格式/术语校验 | 不会验证结论真实性；中文能力须实测；高价值轻量对照 |
| [lychee](https://lychee.cli.rs/) / [源码](https://github.com/lycheeverse/lychee) | 从 Markdown/HTML 等抽链接并检查目标 | 链接校验、局部文件存在检查与外网检查分离 | HTTP 失败不等于文档内容过期；须处理本地路径/锚点/离线选项；高价值深研 |
| [MkDocs](https://www.mkdocs.org/user-guide/configuration/) / [源码](https://github.com/mkdocs/mkdocs) | Markdown 导航与 strict 配置 | 索引/导航完整性与生成视图作为派生物 | 发布器本身不管理事实有效性；可选、不能变强制依赖 |
| [Backstage TechDocs](https://backstage.io/docs/features/techdocs/) / [源码](https://github.com/backstage/backstage) | 文档靠近代码，catalog 中 owner/lifecycle/ref 描述文档，MkDocs 产物独立存储 | 权威输入与发布派生物分离，入口登记与归属信息 | 对单人 agent skill 过重，取契约思路；暂不克隆巨仓 |

所有候选的判断来自官方文档/仓库说明；上表写“需源码确认”的项目仍属于待核验假设。本轮未运行候选工具，也没有本地实测结论。

## 推荐深研三组与 clone 清单

### A. 信息架构与决策生命周期（优先）

Clone：

- https://github.com/evildmp/diataxis-documentation-framework.git
- https://github.com/adr/madr.git
- https://github.com/npryce/adr-tools.git

源码问题：Diátaxis 如何避免一次性全目录大搬迁；MADR minimal/bare 模板保留哪些必须字段；Confirmation 是否能用证据链接替代详述；adr-tools 更新 supersedes 的文件边界、索引行为、并行编号冲突如何处理；哪些概念可写入 skill 主体，哪些只应提供按需模板。重点输出“内容类型 × 权威层级”的二维映射、替代记录与现行正文的关系。

### B. 依赖、审阅与漂移（优先）

Clone：

- https://github.com/doorstop-dev/doorstop.git
- https://github.com/strictdoc-project/strictdoc.git
- https://github.com/useblocks/sphinx-needs.git（仅对照；先读前两者）

源码问题：Doorstop review/cleared/suspect 的哈希输入是否含正文、属性、链接；父项变更如何传播失效、再次审阅如何解除；StrictDoc 图如何检测不存在/重复 ID 与关系环，Markdown 集成如何定位粒度；是否区分“变更提示待审阅”与“已证伪/已过期”。提炼无需安装依赖的 Markdown 元数据协议，避免强制全项目建图。

### C. 轻量按需质量检查（后续）

Clone：

- https://github.com/lycheeverse/lychee.git
- https://github.com/vale-cli/vale.git
- https://github.com/mkdocs/mkdocs.git（可选对照）

源码问题：lychee 本地文件/锚点与外部网络失败的区别，ignore/重试/缓存是否掩盖失效；Vale 的 Markdown 排除作用域和机器输出；strict 如何区分导航丢失与断链接。最终是可选检查菜单或简短人工检查流程，不默认 CI、不默认安装新工具、不把风格问题当事实问题。

Clone 统一落 /tmp/sean-project-doc-research-20261014/；每个深研记录 git HEAD、观察日期、许可证原文、源码路径和结论适用条件，不执行仓库安装脚本。

## 覆盖、失败与未覆盖

观察日期：2026-10-14。采用 Sources 深/核验档。

1. Exa 语义搜索：两组问题式检索，命中 Diátaxis、ADR、Doorstop、StrictDoc 一手链接；摘要仅用于线索。
2. Tavily 网页搜索：两组检索，命中 MADR/adr-tools 及漂移检测线索；Swimm 查询得到的商业/聚合介绍不能充当开源源码证据，已排除。
3. GitHub REST API 与仓库正文：核查 10 个仓库的归属、默认分支、archived、pushed_at；未使用 stars 排序。
4. 官方文档正文：读取 Diátaxis、MADR、Doorstop、StrictDoc、Sphinx-Needs、Vale、lychee、MkDocs 与 TechDocs 的正文/入口。

失败：`exasol/openfasttrace` 在 GitHub API 和网页均 404，不能继续沿旧名称判断项目不存在，留作未核验候选而不列入推荐；Vale 旧地址 `errata-ai/vale` 已重定向 `vale-cli/vale`，clone 使用新归属。GitHub 对部分 license 字段返回 NOASSERTION，不能当无许可证，深研必须读取 LICENSE 原文。

未覆盖：没有社区评论/运行性能/用户部署体验调研，没有安装执行与跨版本兼容实测，没有检索整个现有项目历史。商业 SaaS 的自动同步宣称和新兴 agent 原生仓库未作为基线。OpenFastTrace 候选旧路径未核验。上述限制不影响方法组合总览，但不支持宣布某个工具已适合本项目实装。

## 深研后的决策标准

只吸收能回答具体动作的规则：新事实写哪、何时重审、旧事实怎么退出、索引怎么找到现行正文、证据怎样标范围。每条候选改造记录“来源机制 → 本地问题 → 最小采纳版本 → 何时不用”；不把工具的功能列表改写成 skill。
