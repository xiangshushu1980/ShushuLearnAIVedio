# 自然语言实体创作工作流 v1

Owner: Sean。2026-10-04。此阶段推进“人物/场景完整创作、变体实验、生成与一致性检验”持续目标，不代表整个目标已完成。

## 用户流程

1. 在项目工作区确定项目介绍、世界规则和故事，加入已有基础实体或从零讨论。
2. 在下方「实体创作工作流」用自然语言描述要创建的人物/场景、关联衣服/装备、实验变体和图片用途，点击「交给创作助手」。
3. 在项目助手选择模型、新建或恢复对话、发送要求。助手读取最新项目资料及工作流 catalog，通过 `propose_entity_workflow` 保存结构化方案。工具只保存候选，不创建实体或生成图片。
4. 返回工作区审阅候选：实体介绍、外观、声音描述、项目剧情作用、变体变化、关系，以及各张图的提示词、模型/风格、参考图、保持不变量、待补充。
5. 「调整方案」修改文字/关系说明/图片提示词与风格/引用等，保存新的不可变方案版本。旧版本保留。接受新设计后应用方案，一次事务建立独立实体、项目角色、设定/剧情关系、派生来源与图片步骤。
6. 「查看工作流」使用现有服务器模板编译预览；图片节点使用稳定素材 ID 占位，预览不上传图片或提交生成。
7. 「载入生成输入」将该步骤准备到原概念图界面，跨实体的明确选图按稳定来源复制为本实体引用，防止任意路径读取；草稿版本比较避免覆盖另一页面修改。检查后在原界面生成。
8. 结果保留步骤来源：原运行快照与输出 metadata.authoring 记录 stepId/planId/图片用途/不变量/未知项。工作流区刷新后可看到关联运行与图片。
9. 勾选最多 8 张结果，点击「检验所选图片」，在项目助手发起对比；实际逐张调用观察工具后才能保存视觉报告。一致、冲突、证据不足分开，不代表人工确认。

人物：概念图直接选为主形象，再接原 V3 多视图。场景：同实体的总览、反向角度、区域或细节图片组，后续图可依赖先选定主图，不强制人物三视图。无明确参考图的人物变体自动依赖基础实体主图（useBaseAppearance）；未选定时阻止准备工作流。固定空间仍由空间助手建立并人工确认，不从镜头透视直接猜完整平面结构。

## 数据与来源

- `entity_authoring_plans`：项目范围的不可变 title/summary/candidates/relations/questions、来源 basis 与参考图字节哈希、Agent session/run 来源、人工应用结果。
- `entity_workflow_steps`：应用后各实体的不可变图片步骤及 source hash。实验变体是独立实体，`entity_derivations` 记录基础来源和变化说明；本阶段不自动复制形象、声音或既有关系。复用声音仍用原派生功能，工作流集成待后续。
- `entity_authoring_draft_links`：步骤到当前生成输入的来源指针。只有草稿时间与生成输入完全对应时，运行归入该步骤；脱离方案的手工修改不会冒充原方案执行。
- 新设计由用户显式接受；不能标为已核实图片或已确认空间。未知项保留在候选/实体 authoring provenance、图片步骤与输出来源中。
- 方案使用当前项目实体、明确用户选图和现有模型参数。拒绝循环派生、未知候选引用、项目外关系目标、重复 key、模型输入不支持的引用组合、主图依赖与指定图并用。
- 项目或参考图变化后，未应用的旧方案无法直接应用；需重新讨论。应用后实体变化，图片步骤显示需要复核。
- 数据库批量应用是原子的，不调用生成服务。复制参考图只读取登记 assetId，不支持路径输入。

## Agent 方法与权限

项目创作模式共享项目核心提示词，增加 `entity-workflow` 方法。复用原 Pi 登录与模型，不引入另一个 Agent 服务。

| 工具 | 能力 |
|---|---|
| get_entity_workflow_catalog | 当前模型、风格、参数与人物/场景流程约束 |
| get_entity_workflow_plans | 最近方案和步骤来源，帮助继续讨论或检验 |
| propose_entity_workflow | 保存实体、关系、实验变体和图像工作流的候选方案 |
| propose_image_consistency_review | 保存实际已看图的视觉对比报告 |

生成模型、风格、参数由 catalog 校验，模板由现有 `buildComfyWorkflow` 组装；不接受 Agent 任意生成/执行节点 JSON。图片报告的 reviewedAssetIds 必须来自本轮观察工具实际访问记录，不只是用户选图。报告保存实际看图范围和依据；模型语义结论仍需要真实实测与人工核验。

借鉴项目 `reference-entity-authoring` skill 的事实/建议/未知分离与人工版本纪律；该外部 skill 原 Krea2 的一图/两图与单独主形象阶段，不覆盖已确认的 Qwen 现行能力。未修改旧 skill 或已绑定设计任务。

## API

继承 loopback Host/Origin 边界与字段级错误；UUID/字段无效 400、项目范围外/未知 ID 404、版本或依赖冲突 409。

| Endpoint（前缀 /api/authoring） | 用途 |
|---|---|
| GET /:projectId/plans | 方案及其应用/过期状态 |
| POST /:projectId/plans | 保存人工方案；格式与 Agent tool 共用 Zod schema |
| GET /:projectId/plans/:planId | 读取单个方案 |
| POST /:projectId/plans/:planId/revisions | expectedContentHash + plan，保存人工调整版本 |
| POST /:projectId/plans/:planId/apply | expectedContentHash + acknowledgeNewDesign:true |
| GET /:projectId/steps | 实体图片步骤、依赖、运行及输出 |
| GET /:projectId/steps/:stepId/workflow | 固定模板预览，不调用 ComfyUI |
| POST /:projectId/steps/:stepId/load-draft | expectedStepHash、expectedDraftUpdatedAt、acknowledgeReview:true |

机读方案契约在 `server/entity-authoring.mjs` 的 `authoringPlanSchema`；Agent 与 API 共用。单组最多 12 候选，每个最多 12 图片步骤，总方案最大 240 KiB；可分组实验。

## 验证证据与完整目标差距

本阶段：Vite build 通过；新隔离验证 7 项通过，全部测试 19 项通过。自动测试使用隔离数据库和模拟 Agent runtime，覆盖结构/归属/版本/原子性、引用复制、工作流预览、人物基础形象依赖与已观察图片约束。

另通过本机已配置的 deepseek/deepseek-flash 进行了两次真实 Pi 对话，使用临时数据库，不写入用户项目。两次均保存并应用 3 个候选（人物、受伤变体、场景）和 5 个图片步骤，生成运行数为 0。第一次审阅发现模型把相邻/连通推成了“位于两者之间”，且人物变体缺少图像依赖。收紧来源规则并加入基础主图依赖后，第二次方案明确保留朝向/尺度/排列未知，变体等待基础主图，场景后两图等待总览主图。证据：experiments/sean_reference_authoring_goal_20261004/conversation-evidence.json 与 conversation-after-source-fix.json。这只证明一组自然语言方案的链路，不证明真实图片质量。

运行真实对话验证：在 reference-workspace 执行 node scripts/verify-authoring-conversation.mjs，会调用已配置模型并消耗额度，但不调用 ComfyUI；临时数据库和凭据副本结束后清理。

持续目标仍有以下必须完成的部分，不能把本阶段测试当整体完成证据：

- 扩大真实 Pi 对话验证：目前只有一组人物/变体/场景请求，两次对话，不足以证明不同项目的稳定质量。
- PC 浏览器完整操作和错误恢复验证。
- 批次工作流执行器：目前每步载入旧生成界面，尚非 Agent 自动推进/依赖等待/生成后检验与修订的完整循环。
- 已应用实体的图片步骤独立修订与恢复、完整实验分组筛选对比；当前主要调整未应用方案，步骤暂不可独立修订。
- 人物三视图、沿用声音等后续步骤编排；目前接续既有界面。
- 场景多图的独立确认/引用集合和导出角色；目前生成输出仍沿用 concept 登记，附用途 provenance，不能宣称已有完整场景多图确认能力。
- 真实人物与场景多组实验：图片逻辑一致性与关系/信息正确性的质量验证；未提交真实生成或视觉模型调用。

既有生成权限与共享实例规则继续有效：开发 Agent 不自行启动/重启/提交 ComfyUI。后续真实生成验证需明确执行授权及共享队列/资源检查；用户在界面发起生成沿用现有服务。
