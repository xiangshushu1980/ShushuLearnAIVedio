---
owner: Sean
observed_at: 2026-10-14
evidence: official-docs-and-source-inspection
execution: no-install-no-runtime-tests
---

# 轻量文档质量检查源码调研

## 建议

skill 采用按变更触发的检查菜单：改名/移动后查入口与入链；更新结论后核证据/版本/替代链；修改网站配置后才考虑发布构建；批量术语治理时才使用 prose lint。检查对象默认本次变更文件及其直接引用范围。全库网络扫描、CI、依赖安装均由项目明确选择，不进入默认工作流。

检查结果至少区分：确定结构错误、待人工复核的可达性问题、风格建议、未覆盖项。可达链接与合法模板均不能证明技术结论有效；工具告警须与证据审阅分开。

## 下载与许可证

均于 2026-10-14 shallow clone 至 `/home/sean/research/sean-project-doc-research-20261014/`，仅阅读文件，无安装、构建或执行测试。

| 仓库 | HEAD | 许可证正文 | 角色 |
|---|---|---|---|
| [lycheeverse/lychee](https://github.com/lycheeverse/lychee) | `54f8bf47ffbd35973b8eb016ccbc67221c75ba5f` | LICENSE-APACHE + LICENSE-MIT；各 crate Cargo.toml 指明 Apache-2.0 OR MIT | 可选链接工具 |
| [vale-cli/vale](https://github.com/vale-cli/vale) | `cfb21a4ce87238bcfb44b90e8e0db9e0e91d6c09` | LICENSE：MIT | 可选写作规则工具 |
| [mkdocs/mkdocs](https://github.com/mkdocs/mkdocs) | `2862536793b3c67d9d83c33e0dd6d50a791928f8` | LICENSE：BSD 2-Clause 文本 | 已有网站项目的可选发布校验 |

源码链接以下均锁定这些 commit，避免浮动版本。

## lychee：链接失效与检查失败的区别

- [`lychee-bin/src/client.rs#L24`](https://github.com/lycheeverse/lychee/blob/54f8bf47ffbd35973b8eb016ccbc67221c75ba5f/lychee-bin/src/client.rs#L24)：offline 将协议过滤范围设为 file。可将本地路径检查与外部网络检查分开；离线通过不代表外链已检查。
- [`lychee-lib/src/checker/file.rs#L17`](https://github.com/lycheeverse/lychee/blob/54f8bf47ffbd35973b8eb016ccbc67221c75ba5f/lychee-lib/src/checker/file.rs#L17)：本地 checker 可用 fallback_extensions/index_files/wikilink 等解析规则。其 `resolve_local_path` 区分不存在、其他 IO 错误、目录、正常文件。因此不能将权限或读取失败全部写成“断链”。
- [`lychee-bin/src/config/mod.rs#L903`](https://github.com/lycheeverse/lychee/blob/54f8bf47ffbd35973b8eb016ccbc67221c75ba5f/lychee-bin/src/config/mod.rs#L903)：fragment 默认 `None`。**只运行默认链接检查不保证锚点被检查。** 纳入检查前要匹配项目 Markdown/HTML 的实际渲染规则，中文标题、自动 slug 与其他平台格式应人工核对。
- [`lychee-bin/src/commands/check.rs#L171`](https://github.com/lycheeverse/lychee/blob/54f8bf47ffbd35973b8eb016ccbc67221c75ba5f/lychee-bin/src/commands/check.rs#L171)：accept_timeouts 可让超时不影响成功退出。配置意味着验收范围被放宽，不意味着超时链接被证实有效。
- [`lychee.example.toml#L32`](https://github.com/lycheeverse/lychee/blob/54f8bf47ffbd35973b8eb016ccbc67221c75ba5f/lychee.example.toml#L32)：示例开启 cache、设置 max_cache_age。旧缓存可能延后变化发现；审阅证据引用时记录查验时间，关键外链应看原文而不只依赖缓存状态。
- 同一示例接受 429（L91）、accept_timeouts（L206）并非本研究推荐的验收配置；不要直接整份复制示例。401/403/429/网络错误应记“未确认”，避免为让 CI 绿而声称有效。

可吸收协议：本地目标缺失→修复正文或引用；目标存在但锚点不能确认→人工核对对应渲染规则；外网失败→保留错误类别和查验时间，回到官方正文；来源已撤销/被替代→更新技术结论有效性，而不是仅换一个可访问 URL。

## Vale：写作约定可以执行，事实不能由 lint 保证

- [`internal/lint/ast.go#L78`](https://github.com/vale-cli/vale/blob/cfb21a4ce87238bcfb44b90e8e0db9e0e91d6c09/internal/lint/ast.go#L78)：SkippedScopes 可替换跳过标签列表；IgnoredScopes 默认略过 tt/code/kbd/samp，用户自定义列表会替换默认值。不要随意配置后假定代码仍被保护。
- [`internal/core/ini.go#L321`](https://github.com/vale-cli/vale/blob/cfb21a4ce87238bcfb44b90e8e0db9e0e91d6c09/internal/core/ini.go#L321)：BlockIgnores/TokenIgnores 与警告级别等配置可让规则按作用域执行。忽略范围过大也会造成漏报。
- [`cmd/vale/json.go#L10`](https://github.com/vale-cli/vale/blob/cfb21a4ce87238bcfb44b90e8e0db9e0e91d6c09/cmd/vale/json.go#L10)：JSON 告警按文件输出，便于 agent 对具体位置逐条处理；JSON 成功输出只是一种结果格式。
- [官方说明](https://github.com/vale-cli/vale)：规则本身由配置提供，并非内置项目事实校验器。

适合批量治理术语、约定字词和特定正文作用域；不适合判断“同一事实只有一份权威正文”、任务状态真源、实验结论的适用范围。中文语法规则可用性本轮未实测，不能直接采用英文风格包作为全项目门禁。

建议 skill 先列人工可读的质量问题；已有 Vale 项目可用现有规则处理变更文件。若需要新规则，先由真实反例证明必要，再按项目范围启用，不自动安装或修改用户级配置。

## MkDocs strict：发布视图的严格度并非全部默认严格

- [`mkdocs/config/defaults.py#L169`](https://github.com/mkdocs/mkdocs/blob/2862536793b3c67d9d83c33e0dd6d50a791928f8/mkdocs/config/defaults.py#L169)：导航遗漏默认 info、导航不存在目标默认 warn；正文缺失相对路径默认 warn，但 anchors 默认 info。`strict` 不自动将所有问题升级为 warning。
- [`mkdocs/commands/build.py#L253`](https://github.com/mkdocs/mkdocs/blob/2862536793b3c67d9d83c33e0dd6d50a791928f8/mkdocs/commands/build.py#L253)：strict 挂入警告计数器；L341 根据 anchors 的配置级别查锚点；L345 执行 post_build 插件事件后才在告警计数非零时终止。
- 因此“strict 构建通过”必须伴随配置解释；默认 info 级锚点/遗漏不会自动变成失败。构建还会执行项目插件，不是只读的纯 Markdown 检查。

已有 MkDocs 项目可以考虑将本项目确实要求的 links.anchors/nav.omitted_files 级别明确配置。普通 agent 文档项目无需建立站点来检查文件存在，实验正文或增量 ledger 也不必为了导航告警进入网站目录。

## 采用与不采用

| 借鉴机制 | skill 最小实现 | 何时启用工具 |
|---|---|---|
| 明确检查范围 | 收尾列本次变更入口、证据、替代记录与未覆盖项 | 大量链接变动且项目已有工具 |
| local/network 两步 | 文件与引用先查；关键一手外链按需复核 | lychee 已安装或项目明确选择 |
| 作用域/严重级别 | 结构错误与风格建议分别处理 | 已有 Vale 规则或批量治理 |
| 发布派生物 | 输入正文为真源、网站为生成视图 | 已有 MkDocs 站点的配置/正文变更 |
| 可重复机器输出 | 保存必要的结论与覆盖摘要，不长存噪声日志 | 检查确实需要回溯 |

建议新增 skill reference，而非把这些工具参数灌进主文件。默认收尾的三件事足够：入口能定位现行正文；关键结论有范围明确的证据落点；被替代正文有新去向且无活跃入口误导。

本项目额外适配：既有 `.pi/ledger` 已承载实测结论与 superseded 链，决策记录与实测记录分工；不用 adr-tools CLI，不新建第二套记录重复同一结论。工具部署、CI 改造和运行时表现均留为未验证，不作为本次 skill 改造的强制要求。
