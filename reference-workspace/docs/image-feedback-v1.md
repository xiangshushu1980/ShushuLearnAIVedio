# 图片检验与步骤修订衔接 v1

Owner: Sean。2026-10-04。

## 使用

1. 在项目图片工作流或实验批次中选择最多 8 张结果，交给项目助手检验。助手应读取实体、关系、变体变化、对应步骤保持项，并逐张调用看图工具。
2. 保存的图片报告显示观察范围与一致／冲突／证据不足。问题可以指向具体已检查图片；报告不是人工确认。
3. 点击报告中的「按报告讨论修订 · 步骤名」，填写下一轮讨论要求及已检查选图。没有自动发送，没有生成授权。多步骤报告分别修订各逻辑步骤。
4. 助手读取完整报告和目标步骤，提出保留原实体的步骤修订。工作区与对话中显示报告摘要、依据图片和原步骤版本。
5. 比较后人工采用，再建立新的实验批次并明确开始。旧结果、报告和版本继续保留，修改提示词不等于已改善图像。

助手可以在同一轮完成报告与关联修订，但对话完整成功结束前不能人工采用。原步骤已明确选择的参考图可以保留；新增引用仍须由用户本轮选定。有问题的输出不会自动成为新的生成参考。

## 来源与兼容

图片报告的 `workflowSources` 由服务生成，包含 assetId、entityId、contentHash、runId，以及实际 run 的 authoring 来源对应的 stepId/rootStepId/version/stepHash/role/label/batchId/fullStepRead。只信任已保存 Reference run 对应的步骤与来源修订；图片备注中的 authoring 字段不能伪造生成来源。没有来源的导入图片仍可检验，workflow=null。

报告问题新增可选 `assetIds`，必须是报告已经实际观察的图片。`conflicts` 结论必须有具体冲突；有冲突不能宣称 consistent。未完整读取的实体/步骤明确显示覆盖范围，不把索引摘要当作完整审核。

修订请求新增可选 `feedback`：

```json
{
  "reviewId":"<报告 UUID>",
  "expectedReviewHash":"<报告 SHA256>",
  "assetIds":["<此步骤已检查结果 UUID>"]
}
```

反馈依据写入现有不可变 `entity_workflow_step_revisions.basis.feedback`，不改实体模型、不新增确认状态。记录报告 ID/hash/结论/摘要与原图步骤来源；运行快照另带 authoring.feedback 的报告 ID/hash。历史报告不会补写或重算来源：旧报告需重新检验后才能建立反馈关联。原来不带 feedback 的人工修订兼容。

保存和首次采用检查报告范围、完整运行状态、当前项目上下文、所检查图片实际字节哈希以及同一实体/同一逻辑步骤。错误图片400，未知/其他项目报告404，哈希或资料变化409。恢复已经采用过的历史版本沿用原版本选择规则；恢复历史不重新声称旧报告有效。

## API 与 Agent 工具

- `GET /api/authoring/:projectId/image-reviews/:reviewId`：只读完整报告、来源、runStatus 和当前 stale。继承本机访问限制，不提供任意磁盘读取。
- 原 `POST /api/authoring/:projectId/steps/:stepId/revisions` 支持 feedback；其余必填字段见[步骤版本说明](workflow-step-revisions-v1.md)。
- Agent 新增 `get_image_consistency_review`，关联修订前必须实际读取报告，并按既有规则读取完整步骤。
- `propose_image_consistency_review` 支持问题 assetIds；`propose_image_step_revision` 支持 feedback，仍只有提案权限。

## 验证边界

42 项测试和 Vite build 通过。`npm test` 包含 6 项新增隔离测试：报告→关联修订→人工采用→明确启动模拟新批次；来源范围/版本；证据或项目变化；错误问题引用与结论；保留原明确引用/拒绝偷偷新增；上传备注不能伪造工作流来源。合法真实生成快照以 previewPrepared 检查报告来源链，不调用生成服务。

PC 隔离模拟验证：报告入口只填文字（后台仍只有原一轮、0修订）→主动发送→保存待审阅v2→刷新后对话和报告关联仍在。控制台0错误、无横向溢出。证据位于 experiments/sean_reference_authoring_goal_20261004/feedback-{revision-pc.png,ui-session.json,ui-review.json}，色块和模拟报告均明确标记，不代表实际模型效果。

复现：在 reference-workspace 中先 `npm run build`，再 `REFERENCE_FEEDBACK_FIXTURE=1 node scripts/scene-images-ui-fixture.mjs`，打开输出 workflowUrl →「与项目助手讨论」。该可选入口使用真实 API 与模拟 Agent、临时数据库，不读取凭据，不调用模型或 ComfyUI。普通隔离场景 fixture 不启用模拟 Agent。

完整目标仍需要真实人物/场景图像质量、一致性反馈效果及再生成实验验证。V3与声音已有手工流程，后续编排还需继续实现。

## 图文对照读取范围（2026-10-04）

Owner: Sean。新报告增加服务端计算的 `comparisonCoverage`，包含 entityIds、missingEntityIds、stepIds、unreadStepIds、untrackedAssetIds、status 和 scope。范围仅覆盖 reviewedAssetIds 对应实体及其已登记生成步骤，不递归要求读取全项目。

`consistent` 要求本轮完整读取图片所属实体，且读取每个可溯源生成步骤；否则工具返回 400、字段级 conclusion 错误和缺失范围，助手需补读或保存 inconclusive。冲突或证据不足的观察仍可保存，界面显示读取缺口。无生成步骤的导入图可以对照实体文字，但来源明确标记为空，不虚构步骤。旧报告不补写不可变内容，界面提示重新检验补齐范围。

此范围只是访问证据，不是视觉正确性证明，也不意味着人工确认、全项目审核或已检验所有关系。

验证：76 项测试及构建通过。新增 3 项隔离测试覆盖未读所属实体、未读生成步骤、多视图步骤分别读取、导入图无来源。原观察工具测试补全实体读取。模拟 PC 报告显示范围，无横向溢出，控制台 0 错误；本地截图 experiments/sean_reference_authoring_goal_20261004/review-comparison-coverage-pc.png。没有真实模型调用或 ComfyUI 生成。
