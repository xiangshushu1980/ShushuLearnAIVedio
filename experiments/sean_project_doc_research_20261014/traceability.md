# 项目文档证据追溯与变更复核调研

Owner: Sean  
调研日期：2026-10-14  
研究方式：官方 GitHub 页面核验 → 浅克隆源码 → 定位官方文档、实现与上游测试。未安装依赖、未运行工具或测试。以下“源码确认”只表示静态检查，不表示本地实测。

## 建议结论

最值得借鉴的是 Doorstop 的两种独立问题：本项在最后复核后发生变化（unreviewed changes），与它引用的父项版本变化（suspect link）。两者都意味着重新判断适用性，不能自动判定结论错误。我们应先把这一原则与证据定位合同写入 skill，用 Markdown 记录即可；不默认引入哈希、Sphinx 或需求管理栈。

StrictDoc 适合有明确需求层级、需求到源码覆盖与交换格式需求的项目；Sphinx-Needs 适合已经有 Sphinx 构建且需要关系图、过滤、跨项目导入和规则约束的项目。它们不能替代 Task Center 的任务生命周期，也不能把研究索引提升为项目所有“状态”的唯一真源。

## 固定研究对象

| 工具 | 官方仓库与本次 commit | 许可证 | 下载位置 |
|---|---|---|---|
| Doorstop | https://github.com/doorstop-dev/doorstop/tree/7cec21eca4ea09c243c03b3fcd01ec55d742ebf5 | LGPL-3.0（LICENSE.md，实际文件应以仓库为准） | `/home/sean/research/sean-project-doc-research-20261014/doorstop` |
| StrictDoc | https://github.com/strictdoc-project/strictdoc/tree/cc8be791316a92a708be4940e40a245803e5e88e | Apache-2.0 | `/home/sean/research/sean-project-doc-research-20261014/strictdoc` |
| Sphinx-Needs | https://github.com/useblocks/sphinx-needs/tree/8b7a465824b932516ec7e35a7e69482c8d313773 | MIT | `/home/sean/research/sean-project-doc-research-20261014/sphinx-needs` |

这是按当天默认分支取得的快照，不能用当前 master/main 链接代替本次证据。Sphinx-Needs 已采用 packages monorepo；网络搜索还命中旧根目录布局，因此需要以本次克隆校正。

## Doorstop：复核版本与依赖版本分开

**源码确认。** Item.stamp 默认取 UID、text、ref、references；自己的复核指纹还能包含链接 UID 与配置中的扩展字段。reviewed 比较本项当前指纹与存档指纹；cleared 比较每条父链接存档指纹与父项当前指纹。clear 刷新父链接的已看版本，review 刷新本项复核指纹；执行命令本身不证明人或 Agent 已读证据。

永久证据：

- [Item.cleared / reviewed，item.py L527](https://github.com/doorstop-dev/doorstop/blob/7cec21eca4ea09c243c03b3fcd01ec55d742ebf5/doorstop/core/item.py#L527)
- [stamp / clear / review，item.py L864](https://github.com/doorstop-dev/doorstop/blob/7cec21eca4ea09c243c03b3fcd01ec55d742ebf5/doorstop/core/item.py#L864)
- [指纹与链接语义，官方文档 item.md L175](https://github.com/doorstop-dev/doorstop/blob/7cec21eca4ea09c243c03b3fcd01ec55d742ebf5/docs/reference/item.md#L175)（文档声称）
- [validator 报 unreviewed changes，L99](https://github.com/doorstop-dev/doorstop/blob/7cec21eca4ea09c243c03b3fcd01ec55d742ebf5/doorstop/core/validators/item_validator.py#L99)
- [validator 报 suspect link，L175](https://github.com/doorstop-dev/doorstop/blob/7cec21eca4ea09c243c03b3fcd01ec55d742ebf5/doorstop/core/validators/item_validator.py#L175)
- [上游测试：指纹变化报 unreviewed changes，L71](https://github.com/doorstop-dev/doorstop/blob/7cec21eca4ea09c243c03b3fcd01ec55d742ebf5/doorstop/core/tests/test_item_validator.py#L71)（上游测试定义，未运行）

**情景 A：措辞变但语义不变。** 将 text 的“不得复制正文”改为“正文禁止重复保存”，若文本指纹变化，就仍会触发 unreviewed changes。源码只比较内容指纹，不评估语义。复核后保留结论并刷新 reviewed 即可；不需要编造“原结论错误”。

**情景 B：父项变但结论仍适用。** 父需求增加与本子项无关的说明，父指纹变而子项正文不变；suspect link 触发，而子项自己的 reviewed 可以仍成立。检查影响范围后 clear；这是依赖复核，不是必须重写子项。

**重要边界。** ref 是定位字符串，默认不等同于读入目标文件字节。references 的外部文件 SHA 是需启用 item_sha_required 的扩展，见 [哈希实现 L304](https://github.com/doorstop-dev/doorstop/blob/7cec21eca4ea09c243c03b3fcd01ec55d742ebf5/doorstop/core/item.py#L304) 与 [review L891](https://github.com/doorstop-dev/doorstop/blob/7cec21eca4ea09c243c03b3fcd01ec55d742ebf5/doorstop/core/item.py#L891)。默认字段没涵盖的变化不会自动发现；配置还可能自动给新项/链接盖章，因此不可把“盖章”当成验收证据。Doorstop 支持 YAML-frontmatter Markdown，见 [load L291](https://github.com/doorstop-dev/doorstop/blob/7cec21eca4ea09c243c03b3fcd01ec55d742ebf5/doorstop/core/item.py#L291)，但仍要接受工具管理的 item/document/tree 结构，普通 Markdown 链接并不自动得到这些能力。

## StrictDoc：标识、范围与关系一致性

**文档声称 + 源码确认。** UID 用于人可读的跨节点关联，MID 是可选机器身份，用于节点身份持续性。区分“身份”与标题/文件位置有价值，不应把每天改动的标题哈希当稳定 ID。

- [MID 文档，user guide L1302](https://github.com/strictdoc-project/strictdoc/blob/cc8be791316a92a708be4940e40a245803e5e88e/docs/strictdoc_01_user_guide.sdoc#L1302)
- [重复 UID 硬失败，index_builder L554](https://github.com/strictdoc-project/strictdoc/blob/cc8be791316a92a708be4940e40a245803e5e88e/strictdoc/core/traceability_index_builder.py#L554)
- [关系图环检查，L750](https://github.com/strictdoc-project/strictdoc/blob/cc8be791316a92a708be4940e40a245803e5e88e/strictdoc/core/traceability_index_builder.py#L750)
- [上游环测试文件](https://github.com/strictdoc-project/strictdoc/blob/cc8be791316a92a708be4940e40a245803e5e88e/tests/unit/strictdoc/core/test_traceability_index_cycles.py#L1)（上游测试定义，未运行）
- [需求到源码两种连接方式与 source_root_path，L3174](https://github.com/strictdoc-project/strictdoc/blob/cc8be791316a92a708be4940e40a245803e5e88e/docs/strictdoc_01_user_guide.sdoc#L3174)：源码加 marker 或需求加 file relation，可分别或共同使用（文档声称）。
- [diff/changelog 统计 modified/added/removed，L200](https://github.com/strictdoc-project/strictdoc/blob/cc8be791316a92a708be4940e40a245803e5e88e/strictdoc/features/diff_and_changelog/project_diff_analyzer.py#L200)（源码确认）。

本轮没有找到与 Doorstop 同等的原生 reviewed/suspect 自动流程；不能据此断言 StrictDoc 所有扩展都没有，只能说本轮确认的是身份、链接、环校验、源码追溯、变更呈现。diff 展示“modified”仍不是“wrong”。源码覆盖也不能证明实现满足需求，只证明指定的关联存在。

对我们有用：链接应限定项目/组件/版本与范围，需求图的禁止环不能盲目套给所有研究关系——研究资料互相引用可能合法；只有 depends_on 或 supersedes 的特定关系才需要额外约束。

## Sphinx-Needs：图、约束与当前指纹能力

**源码确认。** 手工 ID 可以遵循格式约束；默认自动 ID 来自标题或正文的 SHA-1 片段，改标题可能改 ID，因此长期被引用条目应显式 ID。见 [api/need.py L1535](https://github.com/useblocks/sphinx-needs/blob/8b7a465824b932516ec7e35a7e69482c8d313773/packages/sphinx-needs/src/sphinx_needs/api/need.py#L1535)。

当前版本具有 hash 与 fingerprint 派生规则。hash 只覆盖声明字段；fingerprint 覆盖规则选定的核心、项目字段、链接，排除派生字段、backlinks、位置、渲染配置等。链接条件不进入 link fingerprint，能避免修改固定目标版本条件造成自己的指纹递归变动。它不等于给源文件内容自动计算哈希。

- [序列化与 SHA-256 实现，common.py L1015](https://github.com/useblocks/sphinx-needs/blob/8b7a465824b932516ec7e35a7e69482c8d313773/packages/sphinx-needs/src/sphinx_needs/functions/common.py#L1015)
- [fingerprint 字段边界与默认值规则，configuration.rst L816](https://github.com/useblocks/sphinx-needs/blob/8b7a465824b932516ec7e35a7e69482c8d313773/packages/sphinx-needs/docs/configuration.rst#L816)（文档声称，与实现互证）。尤其“配置默认值变，但依赖默认值的节点指纹未必变化”，说明必须记录运行/配置范围，哈希无法替代 scope。
- [链接条件针对 target，need.rst L141](https://github.com/useblocks/sphinx-needs/blob/8b7a465824b932516ec7e35a7e69482c8d313773/packages/sphinx-needs/docs/directives/need.rst#L141)（文档声称）
- [条件求值失败只报 warning，directives/need.py L550](https://github.com/useblocks/sphinx-needs/blob/8b7a465824b932516ec7e35a7e69482c8d313773/packages/sphinx-needs/src/sphinx_needs/directives/need.py#L550)
- [上游条件测试，test_link_conditions.py L21](https://github.com/useblocks/sphinx-needs/blob/8b7a465824b932516ec7e35a7e69482c8d313773/packages/sphinx-needs/tests/test_link_conditions.py#L21)（上游测试定义，未运行）
- [缺失链接设置两个独立标记，need.py L496](https://github.com/useblocks/sphinx-needs/blob/8b7a465824b932516ec7e35a7e69482c8d313773/packages/sphinx-needs/src/sphinx_needs/directives/need.py#L496)
- [external needs 及 namespace prefix，configuration.rst L2721](https://github.com/useblocks/sphinx-needs/blob/8b7a465824b932516ec7e35a7e69482c8d313773/packages/sphinx-needs/docs/configuration.rst#L2721)（文档声称）。

可用链接条件 pin 目标指纹来构建“依赖版本不一致”警示，这是我们基于已确认机制的方案推断；本轮未运行此组合，不写成本地实测。措辞变更可改指纹，已 pin 的子项会警示，即使语义仍成立。复核并更新 pin 可解除；condition_failed 证明配置条件不满足，不证明业务结论错。

## 最小 Markdown 合同

对象只包括需要长期使用、被其他结论引用或支撑决策的结论/约束；不是每段、每条日志都加字段。现有摘要层维持一句结论与详情链接，以下字段放权威正文，索引不复制它们。

| 字段 | 默认要求 | 理由与成本 |
|---|---|---|
| claim + scope | 必须，用普通正文即可 | 写结论和适用版本/环境/边界；防止局部实验外推。scope 可以是“本次仓库 commit 的静态观察”。 |
| evidence locator | 必须 | 固定 commit URL + 文件/符号/行范围，或实验目录内 manifest/result/QC 的精确链接。只给仓库首页不够。 |
| source version | 必须与 locator 合计可解析到所观察版本 | commit permalink 已携带版本就不重复写 SHA；本地证据用不可变 run ID/manifest。可变网页用抓取日期+版本说明，必要时授权快照。 |
| evidence kind | 必须 | 文档声称、源码观察、静态推断、本地/在线实测等是类别而非固定可信度排序；上游测试未执行要明确。 |
| stable ID | 被跨文档引用/会重命名拆分时必须；短期局部项可不用 | `claim_id: DOC-TRACE-001` 或持久显式锚点，ID 不含状态、标题哈希；重命名保留 ID/重定向，禁止复用旧 ID。 |
| verified_at | 活跃、易变、要求周期复核时用 | 日期说明最后核对时间，不说明核对版本；不能单独替代 source version。静态不可变快照无需为每条重复日期。 |
| review_reason | 变化待复核或复核后保留旧结论时用 | 写“父项 v2 新增音频约束，需检查视频链路影响”或“仅重排章节，原结论仍适用”；常态无需空字段。 |
| supersedes / depends_on | 实际存在覆盖或依赖时用 | 一条有类型关系即可；不用建立全量图。覆盖时指新权威位置并保留旧证据。 |

建议正文：

```markdown
### 本地单实例入口 {#DOC-TRACE-001}
结论：共享实例通过指定 wrapper 管理。
适用：comfy-ops；wrapper 的已核对 commit；单实例运行方式。
证据：[实现 permalink](...)；类别：源码观察。
复核：2026-10-14；父约束：[...]。
```

上面 `{#...}` 是示意显式锚点；采用时必须遵循当前 Markdown 渲染器支持的语法（例如显式 HTML anchor），不能假设所有渲染器都支持该扩展。更通用方式是正文 `ID: DOC-TRACE-001` 加文件链接。

变更处理：先列被影响的明确关联项，标“待复核”并写理由；检查相关范围；结果为保留/缩小范围/修订/被覆盖。只在有反证时标“不成立”。纯编辑改动可简短记“措辞调整，范围与证据不变”。父项增加无关内容可记“父版本更新，所依赖段落未变”。不要自动修改 Task Center 生命周期，也不要强制每次拼写更正重跑实验。

## 哈希能证明什么

哈希或 commit pin 证明所取样的字节/规范化字段是否与某一已记录版本一致（在算法、序列化、输入范围固定的前提下），以及以后定位时是否仍是该快照。它们不证明作者诚实、测量方法有效、证据支持结论、全部依赖纳入、语义变化、部署版本一致或审查已完成。全文 hash 会因无关格式变化产生复核噪声；字段 hash 可能遗漏真正重要的外部变化。

source locator + 固定版本足以应对低频且人工可明确找到依赖的结论。哈希系统仅在“经常漏掉依赖变更且已有可自动解析的关系”时增加；应先定义覆盖字段、规范化方式、基线更新权限和噪声处理，再采用。没有版本化数据或依赖图时，盲加 SHA 只是新增元数据维护。

## 何时升级工具

不按条目数量设置伪精确门槛，按反复发生的成本触发：

- 人工排查重复 ID、断链、版本影响经常漏项，且存在稳定父子需求结构：先评估 Doorstop。收益是版本复核与链接校验；代价是一项一文件、配置、CLI、依赖结构与评审盖章纪律。
- 必须做正式需求到实现/测试的覆盖、跨文档图一致性或需求交换：评估 StrictDoc。收益是显式模型和需求管理能力；代价是 SDoc 语法、导出/服务栈、图迁移，不能直接承诺源码关联就是满足性。
- 已有 Sphinx，发布资料要关系图/过滤表/外部 needs/约束：评估 Sphinx-Needs。收益是在同一构建中复用；代价是 Python 构建配置、ID 设计、派生规则/外部数据管理、上游版本迁移。本次新版能力需先验证所选发布版，不以默认分支特性承诺生产可用。

对当前 project-doc-system 最有价值的改造是：证据类别去除错误的总排序；增加作用域与版本定位；引入“变化→待复核→判断”的小流程；说明 stable ID 条件使用；把研究状态与任务生命周期明确分开。暂不增加全仓图、默认 hash、复杂 schema。

## 检索覆盖与限制

已使用通用网络搜索定位官方仓库、官方项目文档、GitHub 静态源码与测试三个互补证据面；命中三仓库及其文档、实现和上游测试。未搜商业 SaaS/社区口碑，未增加 OpenFastTrace，因为三主仓库已提供身份、链接、范围、变更复核、约束的互补机制，额外仓库不解决本轮核心未知。没有仅凭聚合摘要作机制结论。未验证安装体验、性能、维护工时和运行输出；上述选型触发条件属于本调研的设计建议。
