# [Sean] H3 Reference 工作台重新设计

> Owner: Sean  
> 状态：产品设计草案 v0.4（2026-09-28）；首轮产品范围、画布界面方向、角色三视图/声音范围已确认，插件实现边界待评审。  
> 任务：`remote-c1320849-4f64-4781-9929-c7922a9d1ae5`

## 1. 目标与边界

工作台管理“可被 H3 使用的参考对象及其资产”，把对象设定、资产版本、审核、引用和固定工作流运行记录连在一起。当前方向是以 ComfyUI 插件形态提供项目资产栏、Reference 语义节点和固定工作流；复用 ComfyUI 原生无限画布与执行队列，不另造执行器，也不改成 ComfyUI 核心分支。Python 自定义节点执行 Krea2/Breeze 等工作流；前端扩展管理资产并提供画布交互。

第一阶段聚焦 Reference 的创建、审核和整理，必须包含形象设定、定稿三视图、对象资料/提示词、项目对象管理，以及角色人声生成。图像能力固定为 Krea2；角色语音固定由 ComfyUI 的 Breeze TTS 2 节点生成；后续视频能力固定为 H3。提示词由 Codex 在能力适配时生成，或调用 DeepSeek API。生产流程只能从已登记、带版本的工作流模板运行，不开放任意 Agent 自主规划或任意节点画布。首版声音范围限于人声；音乐和音效暂不生成，后续接入合适的开源方案。

保留现有 H3 Reference 生成流程和文档。当前正式生产基线见 [`docs/45_ref_asset_handbook.md`](45_ref_asset_handbook.md)，Krea2 主图能力见 [`docs/40_krea2_prompt_and_identity_pipeline.md`](40_krea2_prompt_and_identity_pipeline.md)。实验性 Krea2 三视图不能自动成为正式资产链；只有明确标成候选并走审核，才可在工作台中试用。旧拍摄本 Web 工具不作为页面或数据模型的起点。

### 暂不做

- 不做通用媒体编辑器、无限画布或 ComfyUI 节点编辑器。
- 不做 Agent 自动选流程、自动批准资产或自动升级 canonical。
- 不在本阶段实现 H3 视频生成、脚本/分镜生产、镜头选包自动规划。
- 不覆盖或迁移现有实验目录；工作台记录 Artifact 引用和来源即可。

## 2. 用户任务与产品对象

用户主要完成五件事：

1. 创建或导入一个参考对象，记录它是什么、服务什么 H3 用途。
2. 从固定模板生成主图/视图候选，查看提示词、参数、输入和运行结果。
3. 逐项审核资产，批准、拒绝或标为有条件可用。
4. 按用途查看对象当前有哪些可用资产、缺少什么、哪些版本被引用。
5. 为后续 H3 任务选取并导出一组有明确职责和来源的参考资产。

对象类型采用开放枚举，内置 `character`（角色）、`building`（建筑）、`ecosystem`（生态/环境）、`prop`（物品/道具）；可扩展但不得让类型专属字段污染所有对象。对象可包含叙事/世界观描述、外观或结构设定、生成提示词、故事线信息、变体和用途约束。角色三视图固定为三个职责面板：脸部特写、正面、背面；建筑、生态和物品按各自用途配置视觉参考，不强套角色三视图。首版对象库属于单个项目；模型保留后期共享库扩展空间，当前不做跨项目共享、引用或同步。

“对象”与“资产”分开：对象表达语义真值；资产是图像、音频、视频、文本或组合板等具体版本。一个对象可以有多个变体，每个变体有自己的设定覆盖和资产集合；不能把变体误认为新生成的随机版本。

## 3. 画布主界面与交互

主界面只有当前项目的无限画布和左侧资产栏；不设独立对象列表页、详情页或固定右侧属性栏。画布使用 ComfyUI 主图；对象与流程节点沿画布组织。左侧资产栏按“对象/描述与故事线/提示词/形象与三视图/声音/工作流模板”分组，支持搜索、对象类型和审核状态筛选。

资产栏中的对象资料、图片、提示词和声音都可以拖到画布上，创建对应的语义输入节点。用户再把它们接入固定的 Krea2 主形象、角色三视图、Breeze 声音等工作流节点/子图；运行后输出 candidate 资产节点，审核通过后保存为项目资产，并可从左侧再次拖入其他流程。

```text
左侧项目资产栏                     当前项目无限画布
┌──────────────────┐   ┌────────────────────────────────────────────┐
│ 对象             │   │ [角色对象] ─ [对象描述] ─ [生成提示词]    │
│ ├ 角色 Alya      │   │                         ├───────────────┐  │
│ ├ 服装变体       │   │                         ▼               │  │
│ 资料/故事线      │   │                 [Krea2 主形象模板]      │  │
│ 提示词           │   │                         ▼               │  │
│ 形象 / 三视图    │   │                [主形象候选] → [审核]    │  │
│ 声音             │   │                         ▼               │  │
│ 工作流模板       │   │                 [Krea2 三视图模板]      │  │
└──────────────────┘   │                         ▼               │  │
                       │          [脸部特写 / 正面 / 背面]         │  │
                       │                         ▼               │  │
                       │                 [Breeze 人声模板]        │  │
                       └────────────────────────────────────────────┘
```

新建项目/对象、编辑资料、检查版本、图像放大对比、声音试听和审核通过画布上下文菜单、节点编辑器或短暂浮层完成，不切换到另一套页面。项目选择是轻量顶部控件；画布承担对象间关系、生成链、运行状态和输入输出追踪。

默认操作路径：

```text
创建/选择项目 → 画布上新建对象 → 拖入描述/故事线/提示词
    → 连接 Krea2 主形象模板 → 运行并审核主形象
    → 连接 Krea2 三视图模板 → 审核脸部特写/正面/背面并定稿
    → 连接 Breeze 声音模板 → 试听、审核和定稿 → 资产回到左侧栏
```

生产工作流模板有 `production`、`candidate`、`deprecated` 状态。用户可以在业务层连接模板节点和资产输入输出，但不在日常流程里编辑封装的模型节点细节。运行前能检查对象资料版本、提示词、输入资产和参数；运行后展示阶段状态、失败原因、输出候选和审核决定。

角色三视图面板固定为脸部特写、正面、背面；建筑、生态和物品由类型模板定义相应视图。主形象、每个视图与声音资产均独立版本化，重新生成会追加候选，不覆盖已定稿版本。

## 4. 对象、资产与运行模型

首版以关系型语义建模、JSON 文件/SQLite 的物理存储待架构评审，不让 UI 组件形状决定数据结构。

### 4.1 主要实体

```text
Project
  └─ ReferenceObject (type, name, description, story_context, intended_h3_uses)
       └─ Variant (name, changes, constraints)
            ├─ Asset (kind, role, version, status, usage_conditions)
            │    └─ Artifact (immutable file, hash, media metadata)
            └─ WorkflowRun
                 ├─ WorkflowTemplate@version
                 ├─ PromptRevision / parameters / input asset refs
                 ├─ RunEvents
                 └─ output Asset candidates
```

对象共享字段：`id`、`project_id`、`type`、`name`、`summary`、`description`、`story_context`、`intended_h3_uses[]`、`tags[]`、`created_at`、`updated_at`。类型特有设定放进经 schema 验证的 `type_data`，并带 `schema_version`。

Variant 字段：`id`、`object_id`、`name`、`description`、`change_set`、`constraints[]`、`status`。例如角色服装版、建筑损毁版、季节生态版；必须明确继承哪些基础设定、覆盖哪些字段。

Asset 字段：`id`、`object_id`、`variant_id?`、`kind`、`role`、`version`、`status`、`artifact_ids[]`、`source_refs[]`、`workflow_run_id?`、`prompt_revision_id?`、`intended_h3_uses[]`、`usage_conditions[]`、`review`、`supersedes?`。`role` 是语义职责（如角色 `identity_portrait`、`full_body`、`wardrobe_body`、`front/side/back`；建筑 `exterior_front`、`floorplan`；生态 `wide_establishing`、`species_detail`；声音 `character_voice`、`ambient`、`music`），通过类型 schema 注册，不硬编码成一个全局枚举。

角色声音资产另有可编辑的 `voice_profile`：`mode`（design/clone/direction）、声音文字描述、参考音频与逐字稿（clone/direction 时）、方向指令、Breeze speaker 配置和输出语言。每次试听产物单独登记为 candidate；用户可比较多个候选并把选中版本设为当前批准 voice asset。角色台词与多角色对白属于声音生成运行的输入内容，不应混进稳定的角色声音身份描述。

Artifact 是不可变文件引用：`uri`、`sha256`、`media_type`、尺寸/时长/帧率、文件大小、创建时间。Artifact 不承载对象语义；语义与用途属于 Asset。

### 4.2 状态与版本

资产状态建议为 `candidate`、`approved`、`conditional`、`rejected`、`superseded`。审核记录包含审核人、时间、结论、原因、适用条件。工作流产物初始为 candidate；仅人工审核可批准或设条件；新版本不改写旧版本；替代版本通过 `supersedes` 关联。对象设定修订也产生 revision，使生成时使用的设定可还原。

### 4.3 来源链

每个生成资产必须可回答：由哪个对象/变体设定版本、哪些输入资产、哪个模板及版本、哪版提示词、哪些参数和 seed、哪个 Provider/模型生成；由谁在何时审核；后续哪些任务/包引用它。来源关系通过显式 ID 连接，不依赖文件名或共享目录约定。声音克隆需记录参考音频来源及使用授权；Breeze 模型/权重许可和资产允许用途随声音 Artifact 一起登记。当前本地 Breeze TTS 2 节点 README 标注模型权重及自托管输出受 Research and Non-Commercial License 约束，商业使用需另获书面授权。

## 5. 固定工作流契约

工作流模板是版本化、可审核的定义，声明：`workflow_id`、`version`、适用对象类型/用途、输入 schema、允许改动的参数、步骤、Provider 能力、输出资产职责、审核门、失败/重试策略、资源需求和 manifest schema。已运行模板版本只读；修改产生新版本。

首阶段模板建议：

| 模板 | Provider | 输出 | 当前定位 |
|---|---|---|---|
| 角色主形象/身份图 | Krea2 | 角色 portrait candidate | 基于现行 Krea2 三模式；逐张审核 |
| 单对象主图 | Krea2 | 对象主视图 candidate | 角色以外对象需确定各类型提示词模板 |
| 角色三视图 | Krea2 | 脸部特写、正面、背面三个面板组成的可定稿资产 | MVP 必需；首个模板可复用 T48 Krea2 候选流程，模板要经本任务冻结和审核后才能标记 production |
| 角色全视角与派生包 | Krea2 + H3（后续阶段） | 主图、turnaround、抽帧职责图 | 对齐 docs/45 正式手册，不在 MVP 执行 |
| 角色声音设计/克隆/方向控制 | ComfyUI Breeze TTS 2 | 角色试听样本与批准的声音资产 | MVP 必需；支持自然语言声音设计、参考音频克隆及方向控制，支持多说话人合成；按现行 `docs/breeze-tts-standard.md` 走 ComfyUI 节点 |
| 场景环境音 / 专属音乐 / 音效 | 后续确定 | 可被对象引用的声音资产 | 不进入首版生成范围；后续评估开源 Provider 和固定模板，纳入可扩展的音频资产类型 |

工作流执行由 Runner/Provider 对接 ComfyUI 或 Breeze；前端只调用工作台 API。每次运行记录 `run_id`、模板快照、对象/设定 revision、输入 refs、prompt revision、参数、状态事件、资源/耗时、产物与错误。审核 gate 是服务端持久状态，不能仅靠浏览器弹窗控制。

提示词编辑分两类：模板固定结构由系统拼装；用户可编辑的对象描述或可变提示段另存 revision。提示词生成器必须保留原始输入、生成文本、模型/版本和用户修改差异。Codex 仅在宿主可执行且明确适配此能力时作为生成选项；否则走配置的 DeepSeek API。

## 6. MVP 切分

### MVP-0：可评审原型/设计冻结

- 确认对象与变体字段、资产职责注册方式、状态和 provenance。
- 确认总览、对象工作区、运行向导、审核和导出主要流程。
- 确认存储/执行 API 选型与首批可运行模板。

### MVP-1：项目 Reference 与形象/声音生成闭环

- 项目内创建/编辑角色、建筑、生态、物品对象与变体；支持对象资料、故事线、可编辑提示词和 H3 用途。
- 注册、预览、筛选、审核、版本比较、导出图片与 manifest。
- 建立主形象并运行固定 Krea2 三视图模板，完成候选对比、逐项审核和定稿；三视图视角按产品决策冻结。
- 运行固定 ComfyUI Breeze TTS 2 声音流程，完成声音设计或克隆、试听候选、选择/拒绝、批准和角色资产关联。
- 首版声音只包含角色人声，不生成音乐、音效或环境音；数据模型保留后续扩展到这些音频资产的空间。
- 所有生成只追加新 Artifact 和版本；支持失败重试及从现有输入另起新运行。
- 历史 H3 Reference 流程通过外部链接/导入 manifest 保留和可追溯。

### 后续

接入 docs/45 所定义的 H3 视角生成与下游使用；再评估 Reference 包自动检查、H3 任务选包和跨对象场景组合。只有固定流程无法满足明确用例后，才评估 Agent。

## 7. 非功能与验收条件

- 可复现：已完成运行保留模板快照、提示词、参数和输入来源。
- 可审阅：待审核资产、审核原因和条件可查询，审核不依赖本地 UI 状态。
- 不丢数据：重新生成/编辑不覆盖此前对象设定、Artifact 或审核记录。
- 可移植：导出的 manifest 能定位原始文件并验证 hash；不绑定 ComfyUI 内部数据库，并携带来源授权/用途限制。
- 类型安全：对象类型扩展有 schema 版本和兼容策略；资产职责由类型扩展注册。
- 执行安全：提交生产运行前显示实际模板版本、Provider、输入、提示词、成本/资源提示和输出职责；共享 ComfyUI 资源遵守项目单实例与资源 lease 规则。

MVP 验收演示：在一个项目内创建角色及一个服装变体，编辑对象资料/提示词，运行固定 Krea2 工作流建立主形象并定稿三视图；运行 Breeze TTS 2 生成角色声音候选并批准一个；查看完整来源和参数；重新生成后旧版本仍可追溯；导出当前批准图像/声音资产及 manifest；再创建一个非角色对象，证明共享核心模型未绑定角色专属字段。

## 8. 已确认决策与待细化

### 已确认

1. 首版必须生成声音，角色语音固定走 ComfyUI Breeze 节点。
2. 对象库按单项目隔离；未来可扩展共享库。
3. 第一版包括形象设定、三视图定稿、对象资料与提示词、项目对象管理。
4. 图像生成使用 Krea2；后续视频生成使用 H3；生产步骤基于固定可复用工作流模板。

### 待细化

1. 对象资料的必填字段及不同对象类型（角色/建筑/生态/物品）的专属字段。
2. 提示词编辑交互：对象资料生成的提示词是可直接编辑、由模板只读合成，还是保留两类字段；运行前是否每次都人工确认。
3. 定稿审核粒度：整组三视图一次批准，还是按主形象/每个视图/声音资产分别审核。

## 9. ComfyUI 插件可行性初查

### 9.1 分层实现方式

- **Python 自定义节点**：实现 Reference 业务输入/输出与生成步骤，和已有 Krea2/Breeze/H3 节点组合成固定 workflow；提供可复用模板，不把用户带进模型细节。
- **JavaScript 前端扩展**：注册 Reference 资产栏/侧栏页签；展示当前项目对象、图片、提示词、声音与审核状态；将选中资产拖到原生图画布时创建对应的加载/语义节点。
- **项目资源存储**：对象、变体、Asset ID、状态、审核决定、来源链和 H3 用途存项目级 manifest/资源目录；workflow JSON 保存节点连接、模板与运行参数，并引用资源 ID。workflow JSON 不单独承担资产库、审核账本或跨版本 lineage。
- **资产与执行的区分**：资产节点是已登记的输入/输出引用；生成/变换节点是固定操作。输出通过保存/登记步骤成为新 candidate Asset，经审核后才成为 approved/conditional 资产。

建议的高层模板包括 Krea2 主形象、角色三视图、Breeze 角色声音设计/克隆。每个模板在底层可以包含复杂节点链；用户日常只连接对象/描述/提示词/参考图等高层节点，不应为了重复使用资产而手工重搭 Krea2 或 Breeze 子图。

### 9.2 与 ComfyUI 原生界面的边界

当前本机 `comfyui-frontend-package` 安装版本为 `1.53.6`（项目更新记录中曾记录 `1.52.7`，以运行环境当前安装为准）。ComfyUI 官方把 Python custom nodes 定位为 server-side execution，把 JavaScript extensions 定位为 frontend enhancements；frontend 当前类型包含可注册的 SidebarTab。适合先复用现有主画布，再加 Reference 资产栏和本项目节点。[Custom node overview](https://docs.comfy.org/zh-CN/custom-nodes/overview) · [Extension development](https://github.com/Comfy-Org/ComfyUI_frontend/blob/main/docs/extensions/development.md) · [Frontend extension types](https://github.com/Comfy-Org/ComfyUI_frontend/blob/main/src/types/extensionTypes.ts)

本机实现参考：

- `ComfyUI-Krea2-Reference`：Python 节点注册 + Krea2 reference 编码/LoRA 节点 + workflow 示例；适合作为后端专用节点起点。
- `ComfyUI-MiniMaxH3-TimelineDirector`：Python 节点配合 JS 扩展，把素材拖放、提示词和时间线编辑集成进专用节点；证明复杂工作流 UI 可以嵌进节点，但不适合把完整对象库塞在单个超大节点里。
- `comfyui-material-gallery`：前端只加入口并跳转单独素材页；可作轻量入口例子，资产库交互仍在 ComfyUI 之外。

### 9.3 技术风险与首选方案

- **首选**：ComfyUI 原生主画布 + 官方扩展接口侧栏资产栏 + 本项目 Python Reference 节点和已版本化 workflow templates。
- **避免**：fork/覆盖 ComfyUI 核心前端，或通过 DOM 选择器/原型劫持重排整套主 UI。ComfyUI 前端仍在迭代，官方扩展文档也区分了受支持扩展钩子与容易随升级失效的内部改写。
- **工作流开发注意**：官方扩展开发说明提到生产构建与 dev server 的 custom-node JS 加载机制不同；开发验证要以当前本机 `1.53.6` 环境确认，不能只凭开发服务器热更新判定插件可用。官方建议优先走提供的扩展 hooks，少依赖内部对象改写。[Extension development caveats](https://github.com/Comfy-Org/ComfyUI_frontend/blob/main/docs/extensions/development.md#why-extensions-dont-load-in-dev-server) · [Core extension practices](https://github.com/Comfy-Org/ComfyUI_frontend/blob/main/docs/extensions/core.md)
- **界面范围边界**：官方扩展 API 支持在现有 ComfyUI 主界面加侧栏，不等于官方承诺可无侵入替换整个画布与应用壳。若用户坚持整屏只有自定义画布、要隐藏 ComfyUI 主菜单/队列/工作流工具，须先做最小可行扩展验证其对核心 DOM 的依赖，再决定是否独立页面或插件主视图。

因此插件方案目前可行，最稳起点是让 ComfyUI 原生图画布承载工作流，Reference 插件负责上层资源语义和工作流入口。资产栏拖入画布时创建有语义的节点；可复用生成模板作为 subgraph/workflow template；输出资产回登记至项目资源库。工作台差异来自项目级 Reference 资产模型、版本/审核/用途和可复用模板，不来自再实现一遍底层推理节点编辑器。

## 10. 现有资料与证据

- 当前 Reference 生产与资产职责：[docs/45_ref_asset_handbook.md](45_ref_asset_handbook.md)
- Krea2 主图和身份编辑：[docs/40_krea2_prompt_and_identity_pipeline.md](40_krea2_prompt_and_identity_pipeline.md)
- 多视图候选研究：[docs/46_multiview_consistency_research.md](46_multiview_consistency_research.md)
- 多视图任务当前阶段 checkpoint：`T-comfy-ops-48`；Krea2 三视图实验过程见 `experiments/krea2_quadview_stability_20260927/threeview_fixed_flow.md` 与 `experiments/krea2_role_reference_20260927/`。
- 用户已确认首版角色三视图为“脸部特写、正面、背面”；其他对象使用各自类型的参考视图。首版声音仅生成人声，音乐和音效留待后续开源方案评估。
- ComfyUI 本机插件实现参考：`/home/sean/projects/ComfyUI/custom_nodes/ComfyUI-Krea2-Reference`、`ComfyUI-MiniMaxH3-TimelineDirector`、`comfyui-material-gallery`；本轮只读，无 ComfyUI 节点/运行时修改。
- H3 生成与节点环境仍按 [docs/INDEX.md](INDEX.md) 的更新资料和本地实测基线处理；本产品草案不宣称更新节点或升级现行工作流。
