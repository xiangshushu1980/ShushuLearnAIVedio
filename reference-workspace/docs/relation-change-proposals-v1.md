# 已有关系修订提案 v1

Owner: Sean

项目创作助手新增 propose_relation_update。先读取最新项目和两个端点实体，再提供 relationId、scope（entity-setting/project-story）、summary 和 changes（type/description 至少一个）。新关系继续由创作方案或现有编辑入口建立，本接口只修订已有关系文本，保留 ID、两端和分类。历史未分配剧情关系不在可修改范围；派生来源不可修改。

session 响应新增 relationProposals，包含提案时 before、changes、basis.contextHash/relationHash、contentHash、stale 与 appliedReceipt。网页展示提案前后差异和影响范围：设定关系影响共用实体库，剧情关系仅当前项目。对话成功结束后，人工可接受。

`POST /api/agents/relation-proposals/:proposalId/apply`：请求 `{expectedContentHash:"<SHA256>",acknowledgeUpdate:true}`。返回 relationId、scope、sourceRevision、alreadyApplied、generationSubmitted=false。未知提案404，格式/非法范围400，内容或来源变化/对话未成功结束409。

新增 SQLite agent_relation_proposals 保存不可变提案及一次接受记录；提案主体由触发器保护。接受在同一个事务中调用既有关系编辑规则并保存记录，失败全部回滚，重复接受返回原记录。现有编辑服务增加内部 inTransaction 选项，普通调用保持原事务边界。项目或任一实体/关系变化都会要求重新讨论。无图片、素材确认或生成副作用；原有报告/图片步骤按来源变化提示重新检查。

验证：86项测试和 Vite build 通过。5个新增隔离测试覆盖两种范围、两端读取、无变化/非法字段/错误范围、对话结束前拒绝、来源/哈希变化、不可变主体、重复接受、接受记录失败时回滚。PC模拟剧情提案差异→接受→刷新持久化通过，API核对 ID/两端不变；没有真实模型或 ComfyUI 调用。

复现 PC：`REFERENCE_PROJECT_REVIEW_FIXTURE=1 REFERENCE_RELATION_UPDATE_FIXTURE=1 node scripts/scene-images-ui-fixture.mjs`，打开 workflowUrl，进入项目助手。使用临时库与模拟模型，无凭据访问。截图本地 experiments/sean_reference_authoring_goal_20261004/relation-update-proposal-pc.png。

## 真实 Pi 工具验证

Owner: Sean。`REFERENCE_VERIFY_RELATION_UPDATE=1 node scripts/verify-authoring-scenarios.mjs` 只运行两轮真实关系说明修订，在同一临时项目与同一 session 使用应用已配置的 deepseek/deepseek-flash。测试分别给出固定设定关系和项目剧情关系的具体 ID、scope 及目标 description。

实测两轮均完整读取最新资料及两端实体，调用 propose_relation_update，只生成指定 description 提案，文字与请求逐字一致；提案期间没有改资料。脚本随后调用与网页相同的接受接口，模拟人工接受，逐项核对：ID、类型、分类、两端、全部实体原始数据库文字、worldRules 不变，另一个范围关系不变，0生成运行。第二轮重新读取后识别第一轮已被接受，不把尚待处理的电子腕表规则冲突说成已解决。

本地证据：experiments/sean_reference_authoring_goal_20261004/real-authoring-scenarios-1791110380987.json。临时数据库和应用凭据副本已清理；没有改生产项目、没有调用 ComfyUI。脚本记录每轮 relationProposals 与实际接受记录，按 runId 区分历史轮次。

这验证的是明确指定关系与文字的受控修改，尚不证明模型能够独立提出正确的关系语义修正、完整处理大型项目或完成图片逻辑检验。
