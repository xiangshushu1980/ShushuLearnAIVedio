# Reference Agent 接入经验记录

Owner: Sean。独立保存 Agent 接入的演进和证据；稳定操作入口：[应用内 Agent 接入手册](../../reference-workspace/docs/agent-integration-v1.md)。后续追加条目，通过 incdoc 检索，不全量重读。

## 2026-10-03 · Pi SDK 0.86.0 初次接入

任务：remote-2ce27201-5559-4f60-9bfd-0a4fc402dac7。用例：Reference 场景空间布局对话。来源：本机已安装 SDK docs/sdk.md、dist/core/*.d.ts 与对应实现；应用构建输出。此记录区分源码核对、构建结果和待运行验证，不把未调用的模型结果记为实测结论。

- 源码核对：实际包名是 `@earendil-works/pi-coding-agent`，版本 0.86.0；不能按早期 `@mariozechner/...` 的示例直接复制接入代码。模型/凭据由 ModelRuntime 管理，自定义工具支持普通 JSON Schema。
- 源码核对：默认 ResourceLoader 会发现用户及项目的扩展、skill、AGENTS 和设置。网页业务助手使用应用独立目录、SettingsManager.inMemory 和关闭自动发现；系统提示词通过 systemPromptOverride，工具同时设置 noTools=builtin 和显式 allowlist。避免业务助手继承开发 Agent 的 shell/编辑能力。
- 源码核对：`cacheWarming` 在本版本是字符串枚举 off/streaming/idle。错误填写 `{enabled:false}` 会被 SDK 判为无效并回退 streaming。必须使用 `cacheWarming:'off'`，防止业务网页产生不期望的预热请求。提供方 retry 和 Agent retry 分别设置，不只关其中一个。
- 源码核对：SessionManager.inMemory 支持恢复保存的 header+entries；原始 entries 不提供给网页。SDK 在 message_end 通知订阅者后才 appendMessage，因此不能直接在该回调中保存“已完成消息”的 entries。应用在完整 turn_end 后和运行 finally 保存，重启时保留中断标记，不自动重发。
- 设计选择：共用上下文是工程资料+实体修订+明确决定，讨论记录按工程/实体/用途分别保存。送入模型的是当前场景全文与其他成员摘要；数据源版本在运行时捕获。候选提案与权威空间版本分别存储，并使用来源比较拒绝过期写回。
- 设计选择：模型实际查看过的图才可作为 image 来源。图像缩放仅供观察，不推断真实尺度；用户补充使用用户消息 ID。候选来源引用校验无法替代语义核对，正式确认仍由用户点击。
- 已构建：新增三列 PC 页面（工程/选图、对话、提案）；npm run build 通过。静态 node --check 通过。未运行测试、浏览器或真实模型推理；质量与运行边界仍待验收。
- 依赖注意：SDK 自带 npm-shrinkwrap，初次安装锁定 brace-expansion 5.0.9。npm update / audit fix / 根 overrides 未自动改掉嵌套版本。安全补丁处理及最终安装/扫描结果在后续条目记录，不能只看 package.json 声明。

后续扩展：新增用途先定义提示词/方法包版本、只读资料工具、候选输出 schema、人工应用边界和上下文装配范围，再复用 runtime/session/event 基础设施；不要让新增 skill 隐式获得新工具权限。

## 2026-10-03 · 凭据复用与依赖补丁收尾

- 用户明确选择复用本机 Pi 模型与登录。只复制所需 auth/models/模型缓存到 Reference 私有数据目录，从设置提取默认模型 ID；不复制全局扩展、skill、提示词、聊天或整份设置，不修改原用户文件。能力接口返回 200、两个已配置看图模型、无配置缺失说明；此项是配置读取结果，尚未调用真实推理。
- 安装观察：手动将根 lock 的嵌套 brace-expansion 改为 5.0.12 后，npm ci 仍按照 SDK 自带 shrinkwrap 安装 5.0.9。最终采用根直接固定 5.0.12，加版本受限的应用 postinstall 将嵌套包替换为相同兼容补丁并更新 node_modules 安装库存。根 lock 保持 5.0.12，实际 npm ls 确认嵌套补丁；随后 npm audit 返回零已知漏洞。此方法只针对 SDK 0.86.0，升级须重新评估。
- 新增安全边界：受控工具把业务字段错误返回模型以便修订，非业务异常只返回通用错误，避免文件/提供方异常携带绝对路径或凭据。没有把错误原文放入聊天、事件或日志。
- 服务已启动 4188。构建、静态语法和依赖扫描通过；未进行自动化测试、浏览器操作、真实看图/工具调用、生成或 ComfyUI 操作。待用户实际讨论验收后追加质量与失败恢复结果，不能提前记为已验证。

## 2026-10-03 — 项目工作区与共用上下文 v2

Owner: Sean。任务 remote-8ac0f653-9980-494d-ba73-42ac4e97b71a。

- 把工程资料从场景助手对话窗提升为独立项目入口，沿用 agent_projects ID 与旧 brief。项目剧情作用和剧情关系按 project_id 保存；旧全局 story 不自动归属。
- 应用是资料真源，Pi 的会话/压缩摘要只是讨论历史。每轮自动注入项目设置与实体索引，用只读工具按 ID 取完整实体，来源 hash 变化使提案失效；不能只靠模型“记住”最新世界设定。
- 项目级会话需要真实 nullable entity_id，不用虚构场景占位。SQLite 重建会话表时 foreign_keys 只在迁移外暂时关闭，保留子表 FK 指向原表名，事务复制/替换并恢复检查。新旧服务不能同时写共享库。
- 场景是 purpose/方法/工具的一种专项模式，共用 core prompt/runtime/SSE/持久化。项目资料建议需网页逐字段接受；空间布局另行应用并人工图文确认，两者不混同。
- 一致性报告记录完整读取实体覆盖范围；默认摘要不视作完整审阅。保存实体只改变索引/修订，不自动触发模型；人工触发检查再收费。
- 导出 projectId 是可选适配；projectContext + projectRole + 项目剧情关系进入不可变 manifest，不递归加入其他实体，不重写旧快照。下游必须显式消费新增字段。
- 本阶段证据：PC Vite build、7 个服务模块 node --check、scoped diff 检查通过。未运行测试或 LLM、ComfyUI，不声称模型质量/完整交互已验收。已用 VACUUM INTO 备份本机 Reference 数据库，原服务无活跃 Agent/生成任务，Reference 服务按同端口更新启动。
- 当前契约正文：reference-workspace/docs/project-workspace-v2.md；共用接入手册 reference-workspace/docs/agent-integration-v1.md。

## 2026-10-04 — 自然语言实体创作工作流阶段推进

Owner: Sean。持续 goal 为人物/场景的完整创作与变体实验，不标记目标完成。

- 开始按 Task Center 查询当前任务与设计/外部 skill 任务：未发现同范围活跃代码实现；未修改其他任务生命周期，也未为未授权立项的新阶段自动建任务。
- Agent 只保存不可变结构化方案，人工接受后一次事务建立实体/角色/关系/变体来源/图片步骤。流程输出独立持久化，聊天不作事实真源。
- 图片步骤由现有 catalog/template 编译，参考图使用稳定 ID，并按来源复制到目标实体。工作流预览不等于真实执行；运行与输出记录步骤 provenance。手工生成输入如果脱离所载入的步骤，不冒充原方案执行。
- 视觉报告 reviewedAssetIds 必须是观察工具本轮实际看过的图，coverage 保存实际范围；不能把结构约束测试当模型质量或图文一致性证据。
- 验证证据：Vite build、新隔离测试 6 项、全部测试 18 项通过。使用临时数据库、模拟 Pi runtime、极小纯色测试 fixture，无真实提供方/ComfyUI/GPU调用。
- 缺口：真实 NL 对话与浏览器验证、自动批次执行/依赖恢复/反馈修订、步骤独立修订、三视图与声音编排、场景多图确认导出、实际生成视觉质量。权威正文 reference-workspace/docs/entity-authoring-workflow-v1.md。

### 2026-10-04 实体创作真实对话复核（Owner: Sean）

两次隔离 Pi deepseek-flash 对话均持久化并应用 3 候选、5 图片步骤，生成运行为 0。首轮发现相邻/连通被推为 between，人物变体仅凭文字保持身份；强化不推断空间规则并加入基础实体主图依赖后，第二轮明确保留排列/方向/尺寸未知，变体等待基础主图。证据：experiments/sean_reference_authoring_goal_20261004/conversation-{evidence,after-source-fix}.json。仅此测试请求有效，不代表图片一致性质量已验证；整体 Goal 保持 active。

### 2026-10-04 场景图片组确认与导出（Owner: Sean）

新增不可变场景图片组与人工确认，以文字/主图/空间修订/真实图像哈希为依据；默认导出排除 draft/needs_review。三种 scene_* 角色及现有主图请求兼容，明确素材选择不扩大；图片组不确认为空间事实。24 测试/build通过，隔离PC三图选择/保存/确认/放大/刷新操作通过，0控制台错误。证据 experiments/sean_reference_authoring_goal_20261004/scene-image-set-{pc.png,manifest.json}，权威说明 reference-workspace/docs/scene-images-v1.md。色块测试只验证数据和界面，不证明真实生成质量；完整 Goal 保持 active。

### 2026-10-04 图片步骤独立修订与人工反馈（Owner: Sean）

新稳定stepId对应不可变版本；逻辑root保持实体/key/方案，人工采用/恢复使用CAS，原输出和运行保留。Agent必须本轮读取完整步骤才能提出修订，新引用仅明确选图；旧绑定草稿在版本切换后生成入队前409拒绝。28测试/build、隔离PC修订/采用2/刷新/恢复1通过，0console错误。仅验证版本链路和模拟Agent，不代表真实生成或模型反馈效果。权威 reference-workspace/docs/workflow-step-revisions-v1.md，证据 experiments/sean_reference_authoring_goal_20261004/step-revision-*。完整Goal仍active。

### 2026-10-04 图片批次与依赖恢复（Owner: Sean）

持久化固定步骤/项目/实体/引用事实与模板，串行调用既有生成服务；主图缺失等待，选定后由用户恢复。准备输入不覆盖人工草稿，requestKey与runId恢复避免新建重复Reference run；暂停/取消不全局中断共享ComfyUI，重启不自动提交新步骤。36测试/build、隔离2步PC保存/模拟总览/等待/选图/恢复细节/刷新完成/勾选比较通过，0console错误。实际生成桥接正向纯预览和篡改拒绝验证，未调用ComfyUI/真实模型。权威 reference-workspace/docs/authoring-batches-v1.md，证据 experiments/sean_reference_authoring_goal_20261004/batch-*。整体Goal仍active，真实图像与反馈质量、V3/声音编排待做。

### 2026-10-04 Owner Sean：图片报告关联步骤修订

报告由服务记录真实 run/步骤/hash 来源，修订 basis 保留反馈依据；校验项目/逻辑步骤/字节/对话状态。隔离工具测试及 PC 模拟证明报告→待审阅版本→人工采用→明确新批次的衔接；未调用模型或 ComfyUI，不证明图像质量。接口权威正文 reference-workspace/docs/image-feedback-v1.md；浏览器证据 experiments/sean_reference_authoring_goal_20261004/feedback-*。

本阶段最终验证：42/42 测试、Vite build 通过；模拟 PC 对话刷新保留v2及报告依据，控制台0错误、无横向溢出。完整目标未完成。

### 2026-10-04 Owner Sean：场景变体基础参考与空间草稿

新增场景变体依赖基础主图，可沿用空间草稿；全部待核对、不继承确认和核对图，sourceSpatialVersionId 持久化。旧方案基于规则版本保留原行为。47项测试/build与隔离PC/API验证通过，默认导出未确认事实为空。来源 scene-variants-v1.md 与 experiments/sean_reference_authoring_goal_20261004/scene-variant-*。未调用模型或ComfyUI，真实质量仍未证明。

### 2026-10-04 Owner Sean：已有实体文字提案

Agent必须完整读取当前项目实体后提案，人工接受以事务更新明确字段并保存应用修订；不覆盖未指定字段，不把声音样本派生说明写回文字。51测试/build及隔离PC验证通过，步骤stale、重复应用/过期拒绝/事务回滚有证据。手册 reference-workspace/docs/entity-change-proposals-v1.md；模拟PC产物 experiments/sean_reference_authoring_goal_20261004/entity-change-*。未调用模型或ComfyUI，不证明真实语义质量。

2026-10-04 Owner: Sean — V3 三种多视图布局新增 three_view 创作步骤，概念图/变体与本实体主图依赖、实验批次、逐张检验衔接。56 tests/build 与临时库 PC 三布局等待→人工选图→恢复→3/3 模拟输出通过；零真实生成/模型调用。文档 reference-workspace/docs/authoring-multiview-v1.md。持续目标 active，声音编排及真实图片质量仍待完成。

2026-10-04 Owner: Sean — 已有项目实体图片接续：Agent读取完整实体后规划，网页只读字段+可改图片，接受保留原实体ID/主图/文字/空间/声音。混合新旧候选可明确新增关系，重复key/自身关系/旧关系拒绝。63tests/build及隔离PC调整→接受→刷新验证通过，前后entity detail与project context完全一致、createdEntityIds=[]。未调用模型或ComfyUI；持续目标active。说明 reference-workspace/docs/existing-entity-image-plans-v1.md。

2026-10-04 Owner: Sean — 完成 deepseek/deepseek-flash 三真实对话（已有实体/V3接续、腕伤+绷带关系、世界规则审阅），临时库5步骤、零图片生成。发现未知几何被写成否定、无伤断言等来源问题；收紧方法后单次接续重测人物改进，但场景仍自行指定未知材质/照明，语义质量未通过。文字报告新增本轮完整读取引用约束与partial/complete/unreviewed IDs，67tests/build与PC部分范围显示通过。详见 reference-workspace/docs/authoring-real-dialogue-verification.md；完整目标active。

## 2026-10-04 已有场景来源编译（Owner: Sean）

已有场景 Agent 方案使用 sceneIntent，由服务端替换自由提示词。只引用登记原文、确认空间和项目规则，源变更阻断旧步骤准备和提交。73 测试通过，PC 保存应用刷新通过，真实 Pi 单次目标选择通过；未运行图像生成，不能推断图像一致性。规范见 reference-workspace/docs/scene-prompt-compilation-v1.md。

## 2026-10-04 图片对照依据范围（Owner: Sean）

consistent 报告要求完整读取所观察图片所属实体和每个已登记生成步骤；inconclusive/conflicts 保留观察入口，服务端记录 comparisonCoverage，PC 显示缺口。导入图明确无步骤来源，旧不可变报告不重写。76 测试与 build、模拟 PC 通过。只是读取证据，实际图像质量仍未验证。正文见 reference-workspace/docs/image-feedback-v1.md。

## 2026-10-04 关系检验证据（Owner: Sean）

报告问题可引用 relationIds，先完整读取项目内两个端点；服务端保存 actual relationSources 并区分 entity-setting/project-story/legacy-unassigned-story。修改关系后旧报告保持来源内容并过期。78测试/build、隔离PC展开刷新通过；没有真实模型或Comfy调用。规范见 reference-workspace/docs/relation-review-v1.md。
