# 已有实体的自然语言文字修改 v1

Owner: Sean。2026-10-04。

## PC 使用

在当前项目的创作助手中说明需要修改哪个人物或场景、改哪些内容。助手读取完整实体后，通过 propose_entity_update 保存提案。网页显示提案时的原字段与建议字段，人工点击「接受并应用实体修改」才写入。提案未接受不改变实体；对话必须完整成功结束。

可修改名称、实体介绍、固定外观、声音描述。只写入明确提出的字段，其余文字、flags/type、关系、素材、声音选择、形象选择与生成历史保留。剧情作用仍属于项目，当前站位/移动属于拍摄本；空间布局仍使用空间助手，关系仍使用关系界面或创作方案。

实体是全局共用资料，修改影响所有引用它的项目，网页会明确提示。文本变更通过已有修订机制使相关图片步骤显示 stale；已确认场景空间/图片组按原证据机制提示重新核对，不自动确认、不自动改提示词或提交生成。之后可让助手讨论步骤修订并显式安排新实验。

## 数据与接口

不可变表 agent_entity_proposals 保存项目/实体/session/run、summary、before、changes、basis、contentHash、createdAt；应用后只写 applied_entity_revision。basis 同时固定项目完整内容哈希和实体来源修订。before 的文字来自实际存储字段，不把声音样本的派生说明偷偷写回实体。

- Agent 工具 propose_entity_update：entityId、summary、changes。必须先 get_project_entity 完整读取目标，本轮依据仍新鲜；只保存候选。
- GET /api/agents/sessions/:sessionId：新增 entityProposals，包含应用状态与 stale，旧消息和提案兼容。
- POST /api/agents/entity-proposals/:proposalId/apply：expectedContentHash、acknowledgeUpdate:true，响应 entityId、revision、alreadyApplied，以及首次应用的 generationSubmitted:false。

请求示例：

```json
{"expectedContentHash":"<提案 SHA256>","acknowledgeUpdate":true}
```

只读提案中的 changes 示例：

```json
{"appearance":"灰色长外套；手套改为深蓝色。"}
```

校验和应用是同一事务。项目/实体变化或对话未成功409；格式/不支持字段400，未知提案404。重复应用返回原应用记录，不重新覆盖新文字。沿用本机 Host/Origin 边界，没有 Agent 应用工具，也没有文件路径输入。

## 验证与复现

51 项测试及 Vite build 通过。新增4项隔离验证覆盖：未读取完整资料拒绝、人工应用门槛、字段/原始扩展数据保留、未指定缺省字段保持缺省、过期依据与未成功对话拒绝、未知字段/跨项目读取、图片步骤失效、不可变提案/重复应用，以及应用记录失败时实体修改一并回滚。

PC 临时库及模拟 Agent 验证：字段差异预览→接受前实体不变→点击接受→仅指定描述变化→刷新保留已应用，控制台0错误、无横向溢出。证据 experiments/sean_reference_authoring_goal_20261004/entity-change-{preview-pc.png,ui-before.json,ui-after.json,ui-session.json}。模型语义质量和真实生成未在本轮验证。

复现：在 reference-workspace 中 `npm run build`，然后 `REFERENCE_ENTITY_CHANGE_FIXTURE=1 node scripts/scene-images-ui-fixture.mjs`，打开输出 workflowUrl → 与项目助手讨论。此模式使用模拟运行时和临时数据库，不读取凭据、不调用模型或 ComfyUI。关闭进程清理临时库。普通 fixture 与图片检验 fixture 继续可用。
