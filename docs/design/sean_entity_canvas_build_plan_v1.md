# 实体无限画布 + PI：首期施工设计 v1.0（待整体确认）

> Owner: Sean。2026-10-07。用户已确认产品方向、实验规模、独立 Vue/TypeScript 项目及 ComfyUI 前端复用。本文汇总可施工方案；尚未创建施工任务、开发应用或操作模型服务。普通技术选择由 Codex 提议，整体方案确认后创建 queued 开发任务，由用户启动。

## 1. 交付目标

在一个独立应用中，从小说片段开始，多对象与 PI 讨论、采用实体及关系，在无限画布查看真实 ComfyUI 工作流，完成一个人物两轮 Qwen Image 2.1 生成、比较和人工确认，并能刷新恢复。

首期的重点是画布与 Agent 配合，不追求完整实体制作系统。不做视频、剧本编辑、声音、多视图、批量生成、自由流程编辑、多人权限系统或自动无限迭代。PC、本机单用户优先。

### 已确认与本次具体化

| 项目 | 本期决定 |
|---|---|
| 工程 | 新独立仓库，工作名 entity-canvas-studio；不在旧 Reference/Film 应用上继续堆页面 |
| 前端 | 基于官方 ComfyUI_frontend 有限改造，Vue/TypeScript；保留上游结构和版本关系 |
| 数据 | 独立 SQLite 与素材目录，旧应用不双写；讨论和实体多对多 |
| 运行 | 现有共享 ComfyUI 单实例，只提交固定 Qwen 模板；不启动第二实例 |
| PI | 原生 PiWeb 会话 + 独立实体扩展 + Vue 聊天侧栏；沿用视频接入经验 |
| 任务/记忆 | 应用库保存创作目标和恢复资料；远程 Task Center 只管理本次开发，首期不依赖 Mem0 |
| 授权 | 人工采用事实、输入卡单次生成、人工确认主形象，三个动作独立 |
| 体验 | 自动布局、节点连线、平移缩放、选择上下文、流程内进入和返回；无手动接线 |

本文件是施工入口；产品语义详见 [总体设计](sean_entity_canvas_pi_v1.md) 与 [交互契约](sean_entity_canvas_interaction_v1.md)。新技术决策以本文、[前端分析](sean_comfy_frontend_reuse_analysis_v1.md)、[PI 协议](sean_entity_canvas_pi_transport_v1.md) 为准；组件选型文档中 React Flow 部分是历史方案。

## 2. 工程和版本

建议未来代码目录 `/home/sean/projects/entity-canvas-studio`，本轮未创建。前端保留官方源码基线与 GPL-3.0-only 许可；新增业务服务在同仓独立子目录，运行数据在仓库之外。所有新增模块、模板、manifest、文档标 Owner: Sean，外部源文件不为标签做批量修改。

首期候选前端基线为 v1.52.7，远端 tag SHA **1a7a6b82514874545dc5e8203d0bd2188c2d9b18**。这是本项目已有安装记录中的版本，且已核对 tag 源码；不能因此认为当前共享实例仍用此版。另一个历史 checkpoint 记录过 1.53.6，所以施工首次只读核对实际前端/后端和节点版本后选择最终基线。选定时写 manifests/upstream-lock.json；只允许有记录的技术兼容调整，不自动更新共享实例。

v1.52.7 自身 package.json 要求 Node >=25 <26、pnpm >=11.3（packageManager 11.13.1）；最新 main 的 Node26 要求不能套在此版。前端按锁定上游工具链独立构建，业务服务可沿用 Node24/Express 和 node:sqlite；不修改用户全局默认 Node。[版本源码](https://github.com/Comfy-Org/ComfyUI_frontend/blob/1a7a6b82514874545dc5e8203d0bd2188c2d9b18/package.json)。

PiWeb 静态协议按本机包 0.10.0/PI1.0.0 分析，源码 commit 见 PI 协议文档；运行实例版本须在施工核对。前端、后端和 PI 服务无需使用同一个 Node 进程或同一个主版本。

```text
entity-canvas-studio/（未来工程）
├── src/                  上游前端，保留主体结构
│   └── sean-studio/      创作画布、导航、上下文托盘、PI侧栏、详情
├── server/               项目领域、版本、提案、媒体、事件、动作与PI桥
├── pi/                   实体扩展与方法注册，非全局用户配置副本
├── templates/qwen/       固定UI图、API模板、字段映射及版本清单
├── manifests/            上游SHA、节点依赖、补丁接缝清单
└── docs/                 使用、恢复、部署与验收证据入口
```

数据默认建议 `~/.local/share/entity-canvas-studio/`，产品项目的 PI 工作目录置于其中 projects/<projectId>/agent-workspace；不在开发 repo 或影片工作区运行创作 PI。具体目录可由服务环境变量指定。凭据保存在工作区外的受控位置；模型 API key 不复制。

## 3. 画布结构

```text
左侧项目树                 中央画布                         右侧PI
项目设定          [原文] → [讨论] → [实体/关系提案]         本轮目标
章节/剧情场景                         ↓ 采用                上下文托盘
实体                        [人物] → [Qwen流程] → [结果]    消息/工具活动
待决定事项                              ↓ 进入              待采用差异
                          真实ComfyUI节点、控件及连线
                          [返回人物设计] 面包屑
```

产品有两种画布模式：studio 创作图和 workflow 执行图。外层由业务对象自动投影；内层来自固定可视工作流。二者分开保存，页面同一时刻只有一个活动浏览区域，PI 侧栏和上下文托盘持续存在。

实现默认采用一个原生 ComfyApp 执行运行环境，加隔离的创作图投影与浏览层。执行图保留上游节点环境；创作图使用同源 LiteGraph/Canvas 与 Vue 内容层，但不改写执行 rootGraph，不将业务节点伪装为后端节点。切换时停用非活动区域的指针/快捷键处理、恢复尺寸与视口。不得同时启动多个 ComfyApp 单例来假装模块化。具体渲染接缝在首个施工检查点核实。

布局采用固定区域与稳定排序：资料 → 讨论/提案 → 实体/输入 → 运行/结果；历史折叠。关系线可形成环，独立于生成依赖；不强行做 DAG 排列。新增节点只扩展所属区域，正文/token/进度刷新不重排。布局和视口有独立版本，不改变业务修订。

图片用缩略图，原图按需打开；长文、参数与关系细节用抽屉。卡片点击只选择，点“加入本轮讨论”才进入 ContextSet。定位引用、采用提案、生成引用各有明确操作，不用选中状态隐式代替。

## 4. Qwen 生成适配

### 本地可参考的已存在实现

- reference-workspace/catalog/qwen-concept.v1.json：九个基础节点的 API 模板。
- reference-workspace/server/catalog.mjs：模型目录、风格、输入校验与固定编译。
- reference-workspace/server/runs.mjs、adapters.mjs：快照、资源租约、上传、提交、状态观察、回收和恢复。
- 模板来源实验目录 experiments/qwen_image_2_1_civitai_character_sheet_20261002，仅定点读取所需模板，不扫描整个 experiments。

现有模型：qwen_image_2.1_int8_convrot、qwen3vl_8b_int8_convrot、qwen_image_2.1_vae_bf16；QwenImage21Cache、TextEncodeQwenImage21。默认 1536×1024、25步、CFG1、Euler/simple、seed42。允许字段沿用现有目录的 size、seed、steps、原始提示词、风格与有序参考。其他节点参数可见但首期只读。节点声明 0–16 图，不将上限解释为一致性质量保证。

### 新项目如何复用

参考旧服务的编译与执行适配代码，迁入新服务内的独立执行模块，并记录来源；不直接 import 旧 store，不通过旧 HTTP 服务建立第二份实体，不动旧业务库。第一期新项目是自身业务真源，旧素材仅在明确导入时按内容 hash 登记。

旧 snapshot 要求参考图属于目标实体，不适合跨实体讨论。新 Asset 属于项目，可可选链接一个或多个实体；生成引用校验同项目、实际 bytes hash、可用图片类型与明确顺序，而非强制属于目标人物。UI 的讨论选图仍不自动成为生成引用。

### 固定结构的边界

“固定”指服务登记的生成算法、节点类型与连接规则固定。参考图从0变1或更多时，允许编译器按模板规则建立 LoadImage 节点10..25，并连接 TextEncodeQwenImage21 的 images.image_1..16；这不属于用户自由改工作流。PI 优化输入与参数，不能首期任意重写采样/模型结构。

现有概念模板只有 API 图，不能直接当完整可视图；来源 CivitAI UI 图还包含分组、其他节点和不同 ID，不能冒充该九节点模板。施工需补专用 UI workflow，保留真实节点及 ID1..9，加载图节点按同一规则增加。通过实际 node definitions 构造控件/端口，保存布局与动态输入元数据。不得凭 API 的输入字典随意猜动态图槽位。

每版模板包括 UI图、API图、bindings、依赖节点清单和hash。每个输入/运行保存两图关联快照。节点5 prompt映射effectivePrompt；节点6尺寸；节点7 seed/steps；节点9为本run系统输出路径，不作为用户自由参数。style后缀与原提示词分别展示。

最终API图由服务编译；UI图导出后规范化比对执行节点与输入。允许忽略已登记的纯展示元数据，不能忽略未知执行节点。两图不一致阻止生成。不是把任意可视图直接提交。

## 5. 最小数据结构

SQLite、事务、外键、版本比较；复杂正文可用结构化JSON，避免为每个画布元素建独立表。以下是建议物理分组，具体字段以迁移文件固化。

| 表/记录组 | 最小字段与约束 |
|---|---|
| projects | id、owner、name、settings、revision |
| chapters / scenes | projectId、parentId、order、name、brief、revision；Scene属于Chapter |
| sources / source_revisions | id、projectId、immutable revision、text/hash、段落anchor；聊天来源另用消息引用 |
| entities / entity_revisions | id、projectId、type、name、headRevision；修订不可变 |
| relations / entity_uses | 关系端点、scope、来源、revision；场景使用固定实体版本与局部状态 |
| discussions / discussion_links | projectId、目标、对象角色及链接；可无章场归属 |
| pi_bindings / pi_turns | discussionId、sessionId、bindingVersion；turnId、ContextSet/hash、receipt、发送/回复状态 |
| proposals / decisions | 候选正文、basis revisions、sources、内容hash、采用/拒绝记录；候选key映射正式ID |
| goals | projectId、可空discussionId、正文、对象、状态、待决定和结果引用 |
| image_inputs / input_revisions | targetEntityId、可空EntityUse、模板版本、提示词/风格/参数、有序assetId/hash |
| actions / runs | intent、inputHash、expiresAt、idempotencyKey、状态、runId；实际API/UI快照、prompt_id、client_id |
| assets / appearance_selections | projectId、hash、媒体类型、相对文件路径、来源run/node；人工选定版本指针 |
| object_read_audit / events | turnId、对象版本/hash、看图范围；projectId内单调seq及事件正文 |
| canvas_views / operations | 视口、折叠、位置投影；幂等请求key、requestHash、结果/未知状态 |

ID用UUID；端点必须同项目；使用实体修订不能悄悄追最新。采用多对象提案事务校验所有基准，关系不能指向未采用候选。已采用正文与decision来源同事务保存，不用聊天总结覆盖事实。

原生前端的settings、workflow/userdata持久化也必须进入本应用私有兼容存储，不能将新产品草案/设置写回共享ComfyUI用户目录。业务输入是现行真源，原生编辑器缓存只是投影；进入历史run时禁用自动保存为当前草案。

媒体先写临时文件并校验hash，原子移入受控素材目录，再登记数据库和业务事件；崩溃遗留文件由对账清理，不能先通知UI再保存资产。历史主形象与run输入引用保留，首期不做永久删除/垃圾回收界面。

## 6. 业务API草案

全部置于 /studio-api/v1，避免与ComfyUI原生 /api 冲突。浏览器不传任意可执行节点JSON或宿主路径；原生图导出仅用于展示一致性校验，不作为生成授权。

| 接口 | 请求重点 / 结果 |
|---|---|
| POST /projects | name、初始settings、requestId → projectId |
| GET /projects/:id/snapshot | 领域对象、待决定、视图投影、latestSeq；首期小项目整体快照 |
| POST /projects/:id/chapters、/scenes、/sources | parentId或原文、requestId；文本限制建议100KB/份，可多份 |
| PATCH /objects/:type/:id | 字段、expectedRevision；同事务写revision与event |
| POST /projects/:id/discussions | goal、links；创建应用Discussion，不必立即调用模型 |
| POST /discussions/:id/pi-session | launchRequestId；服务创建/恢复原生绑定，不发送作品生成 |
| POST /discussions/:id/turns | requestId、text、ContextSet、可空actionId → turnId/状态 |
| GET /discussions/:id/messages、/pi-events | 经过项目授权的历史快照/分页、原生SSE适配 |
| POST /turns/:id/stop | 停PI回复，返回状态；不取消Comfy生成 |
| POST /proposals/:id/adopt、/reject | expectedHash、basis revisions、selected keys；原子采用 |
| POST /entities/:id/image-inputs | 输入草案与expectedRevision，不提交生成 |
| POST /image-inputs/:id/preview | 服务编译提示词/参数/有序ref与双图预览hash |
| GET /image-inputs/:id/workflow、/runs/:id/workflow | 当前草案或历史不可变UI图及关联API图，只读结构 |
| POST /image-inputs/:id/actions | inputRevision/hash、requestId、明确一次授权 → actionId；建立PI执行轮次 |
| GET /actions/:id、/runs/:id | 状态与原动作/执行快照；未知时查询原ID |
| POST /runs/:id/cancel-queued | 只删除本次prompt_id的队列项，运行中拒绝全局中断 |
| POST /entities/:id/appearance | assetId、expectedRevision、requestId；人工确认 |
| GET /assets/:id/content、/thumbnail | 受项目约束的素材，原图不在列表默认加载 |
| PATCH /projects/:id/views/:key | 视口/折叠，独立viewRevision |
| GET /projects/:id/events?after=seq | 业务SSE重放，缺口返回snapshot_required |

所有写操作使用requestId+requestHash；相同key不同正文409。领域冲突409保留草稿；缺输入422；外部服务不可达503；提交未知返回可查询operation/actionId，不引导自动重试。内部PI工具端点使用独立session capability，浏览器不能冒充PI。

## 7. PI与授权时序

完整原生消息、SSE及工具契约见 [PI接入设计](sean_entity_canvas_pi_transport_v1.md)。实体工具操作最小集合为 context/read_source/read_entity/view_image/load_method/propose/preview/submit_action/get_run；不提供 adopted事实直接写入、选主图、shell或任意图提交。

普通讨论保存提案；人工采用动作进入业务服务事务。输入卡“生成这一版”固定inputHash，签发有效期建议10分钟、最多一次的ActionIntent，并发起PI执行轮次。PI只提交此action，不再自行改输入；改变输入后旧intent失效。无需额外“允许PI生成”弹窗，按钮本身就是明确动作。

服务事务消费intent并创建run，随后独立执行；同action重复调用返回原run。停止PI前未消费的intent撤销，已消费的run继续；用户浏览不阻塞。

ActionIntent只授予一次图生成，不能采用事实或确认主形象。新一轮反馈先形成inputRevision，用户看差异后再次点生成。初期不把一句“继续”解释为批量生成。

模型选择来自现有原生配置，并在创建后核验工具/视觉能力。不能用视频端文字默认模型冒充能看图；没有可用模型时保留明确配置阻塞，不擅自换提供方。模型密钥和产品工作区信任配置在施工部署时检查，本轮不改用户级文件。

## 8. 运行、状态与恢复

运行状态建议 prepared → waiting_resource → preparing → submitting → queued → running → collecting → succeeded；失败用 failed，提交不明用 submission_unknown，队列成功取消用 cancelled。连接状态和PI回复状态分别显示。waiting_resource不虚构采样百分比。

本地首期只允许一个活跃生成（服务锁+数据库活跃约束），项目一次一个PI轮次。共享Comfy队列忙时保留本地waiting_resource，可取消；取得资源租约后再检查队列并提交。正常不改共享服务配置、不抢队列头、不独占长驻服务。外部未遵循资源租约的客户端仍可能竞态入队，必须记录限制，不能宣称全局排他保证。

提交前持久保存executionKey、runId、clientId、实际图、输出prefix；将runId写入extra_data，便于不明提交对账。成功响应保存prompt_id。网络/进程在提交边界中断：查询队列和历史按runId/executionKey匹配；找到则接续，未找到且不能证明未接受则保持unknown，禁止自动再投。ComfyUI不提供本应用的强幂等事务，不能保证跨系统恰好一次。

网关中的原生兼容路由遵循明确清单：object_info等只读定义可转发；settings/userdata映射私有兼容存储；prompt写操作进入业务动作适配；queue/history只提供本应用关联运行；view/upload按本项目素材路径映射；free/interrupt/manager等共享管理操作拒绝。WS连接必须绑定本应用client/run并过滤，不能把共享广播直接当项目事件。开发环境也使用同样的兼容层，不让Vite默认代理绕过。

后台服务持久观察原prompt_id，按nodeId记录执行/缓存/进度/错误和受控预览。没有事件时显示已知状态而不是伪造节点完成。图切换不改变run归属；clientId与nodeId映射固定在run，不用当前画布决定事件落点。

输出回收到独立素材库，保存hash、尺寸、run、node及输入来源；回收事务完成后才清理本run受控output前缀文件。恢复只查询旧run，页面/服务重启不自动再调用PI或提交生成。资源lease的申请、续租、观测和释放沿用hive-resource约定；不把lease当Comfy进程锁。

业务事件与事实同事务写outbox；PI消息流使用历史快照恢复。详情见协议文档，不能将两类事件的seq/续传语义混用。

## 9. 实验内容与验收路径

临时小说草案见 [《潮汐站的钥匙》](sean_entity_canvas_experiment_story_v1.md)。只是实验输入，可在施工前替换，不进入现有生产设定。

固定一个项目、两章、每章一个剧情场景；两个人物、一个地点、一件道具。初次讨论与第二章讨论可分别建立Discussion，证明跨讨论共享已采用事实，无需共享全部聊天历史。

验收：导入原文 → PI提出实体/关系及来源 → 人工采用 → 第二章局部状态提案及采用 → 人物基准图第一轮（中性灰背景） → 选图反馈改纯白背景 → 第二轮 → 比较 → 人工选主图 → 刷新/重进恢复。第一轮可零图参考，第二轮明确使用第一轮候选；不以仅选中图片替代生成引用。

两轮以一个人物为目标；第二轮的背景修改是实验设计指令，不能称为原文事实。检查输入变化和视觉结果分别记录，不承诺模型完全保持身份或严格改色。

## 10. 施工顺序与交付物

| 阶段 | 工作 | 可审阅交付 |
|---|---|---|
| A 基线与运行外壳 | 新仓、锁定前端、节点定义/扩展资源、网关、原生图查看、PI协议核对 | 版本manifest、接缝清单；能进入真实Qwen图并返回 |
| B 项目与创作画布 | 最小schema、小说/章场、实体/关系候选、自动投影、选择、采用、视图恢复 | 无模型也能走通数据和浏览；模拟数据明确标注 |
| C 原生PI侧栏 | 会话绑定、上下文快照、方法、工具守卫、历史/SSE、提案回流 | 真实PI多对象讨论、来源、局部状态，开发身份不混入 |
| D 固定Qwen执行 | 双图模板、单次intent、资源租约、run节点状态、回收、反馈输入 | 真实两轮图、前后差异、用户确认及恢复 |
| E 交付 | 安装/运行/恢复说明、边界故障记录、scoped commit与任务checkpoint | 用户可启动使用的PC应用及证据清单 |

先证明原生流程和PI接缝可用，再完善创作页面。工程里保留可替换适配器，不先拆成多个微服务，不引入向量库/复杂调度系统。施工中的运行核验按用户后续授权执行，本轮不添加或运行测试。

## 11. 已知限制与需要用户的最终决定

当前是源码、版本与协议分析，未连接ComfyUI、未核验GPU/队列/节点、未运行模型、未验证构建或图片效果。首期前端有限改造有上游维护成本；模板UI补齐、非后端业务节点渲染和PI工具守卫必须经过首个检查点，不能当现成能力。

没有剩余必须由用户选择的普通技术细节。需要用户审阅并确认本整体方案，才创建开发任务；不因“继续分析”提前施工。名称、建议目录和默认字段可在施工中调整，不影响已确认产品边界。

## 12. 待创建的开发任务草案

标题：`[Sean] 实体无限画布 v1：ComfyUI 前端与原生 PI 协作闭环`。

项目登记建议comfy-ops，执行位置明确为新repo entity-canvas-studio；施工Agent先读新仓AGENTS，并沿用comfy-ops共享ComfyUI与资源纪律。contextRefs包括本文、PI协议、前端分析、交互契约和实验小说；不要只引用某个旧任务的描述。

描述：按本方案新建独立Vue/TypeScript创作应用，基于锁定ComfyUI前端有限改造。实现项目/章场/来源/实体关系、自动无限画布、真实工作流原位进入、原生PI多对象讨论及提案、Qwen Image2.1单人物两轮生成与人工确认、持久恢复。视频/声音/多视图/自由接线不施工。旧应用与数据库保持各自运行，新应用业务独立。

验收：第9节完整路径；实际上下文与引用顺序可核对；真实UI/API图一致；节点进度和结果属于正确run；刷新/重连/未知提交不自动重复；局部状态不污染全局；所有事实采用和主形象确认均可追溯；用户可在应用内完成而非跳外站。

创建前重查Task Center，当前只读查得：remote-c1320849-4f64-4781-9929-c7922a9d1ae5仍running，旧描述为Krea2/暂不引入Agent，虽checkpoint提Comfy画布但不是本方案施工依据；remote-92ecb0d7-d1db-4bd5-8a3e-83732b7404f1仍running，PI能力只作参考。二者有领域重叠，新项目不接管/修改其controller、不改其生命周期、不写其应用文件。用户确认后新建独立queued任务，不claim/start，不自动关闭旧任务。
