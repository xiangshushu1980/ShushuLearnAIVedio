# 图片工作流步骤修订 v1

Owner: Sean。2026-10-04。修正已应用的提示词/图片工作流，不重复创建实体。

## 操作

在项目工作区的「已建立的图片工作流步骤」点击「修订步骤」，调整提示词、用途、模型、风格、参数、参考方式、保持项与未知信息，写明原因后保存候选。新候选与当前版本并列，能展开比较当前提示词；人工点击「采用此版本」后才可预览/载入。保存与采用均不提交生成。

「显示历史步骤版本」可查看以前的提示词、来源与对应运行。资料仍一致时可重新采用旧版本；实体变化时，基于当前资料建立新修订，不能假称旧提示词已经复核。修订保留实体、逻辑步骤 key 和原方案来源，新的稳定 stepId 标识不可变版本。

「与助手讨论修订」进入项目助手。助手必须在本轮实际调用 get_entity_workflow_step 读取完整步骤，才能 propose_image_step_revision。新引用必须来自本轮用户明确选图；主图依赖仍遵循人物身份和场景一致性约束。助手只有保存候选权限，采用与生成由用户决定。

## 数据与并发

- entity_workflow_steps：原有不可变步骤表，每个修订写入新行，保留原 planId/entityId。
- entity_workflow_step_revisions：parent_step_id、root_step_id、version、reason、Agent session/run 来源及当前项目/参考图依据。旧字段不重写。
- entity_workflow_step_heads：当前人工选用版本。旧步骤默认自身为版本 1，兼容原数据。
- entity_workflow_step_selections：人工版本切换记录，恢复不修改历史内容。

修订要求 expectedStepHash、expectedActiveStepId、expectedContextHash；同一逻辑步骤产生多个候选时，版本号继续递增。采用检查当前选择、实体修订、候选项目依据、引用归属与实际哈希、Agent 完整结束状态。版本冲突 409，未知合法 ID 404，字段无效 400。已采用版本的重复请求幂等返回。

未采用或历史版本不能载入生成输入。版本切换之后，仍绑定旧步骤且未经修改的生成输入拒绝执行，要求重新载入；手动修改已脱离方案的输入沿用原普通生成流程。新运行快照保留 stepId/rootStepId/version/sourceRevision，历史运行及输出不改写。

## API

| Endpoint（前缀 /api/authoring/:projectId） | 内容 |
|---|---|
| GET /steps/:stepId | 完整提示词/参数/来源、当前版本、版本状态及关联输出 |
| POST /steps/:stepId/revisions | 保存独立步骤修订候选，返回新 stepId |
| POST /steps/:stepId/adopt | expectedStepHash、expectedActiveStepId、acknowledgeReview:true |

修订请求：

```json
{
  "expectedStepHash":"<原步骤哈希>",
  "expectedActiveStepId":"<当前选用步骤 UUID>",
  "expectedContextHash":"<当前项目 context.contentHash>",
  "reason":"反向角度增加了额外门，保持原门的数量和布局。",
  "image": {
    "key":"overview", "label":"场景总览", "role":"scene_overview",
    "prompt":"Preserve the original doors and layout.", "purpose":"复核固定布局",
    "modelId":"qwen-image-2.1", "styleId":"original", "parameters":{},
    "referenceAssetIds":[], "useMainAppearance":true, "useBaseAppearance":false,
    "invariants":["同一场景固定结构"], "unknowns":["绝对尺寸未知"]
  }
}
```

完整契约沿用 authoringImageSchema；模型/参数由现有 catalog 验证。修订不确认新的场景空间事实，不改变实体关系。

## 证据与限制

28 项自动测试及 Vite build 通过。新测试覆盖独立版本、待采用阻止执行、采用/恢复、并发冲突、项目/实体依据变化，以及模拟 Agent 未读取完整步骤时拒绝提案。旧输入的生成请求验证在入队前拒绝，运行数为 0。

隔离 PC 浏览器完成修改提示词、保存候选、采用版本 2、刷新恢复、查看历史、恢复版本 1；控制台 0 错误，无横向页面溢出。证据 experiments/sean_reference_authoring_goal_20261004/step-revision-{pending-pc.png,current-pc.png,ui-steps.json}。隔离入口为 node scripts/scene-images-ui-fixture.mjs 输出的 workflowUrl。临时数据库在终止时清理，未使用真实模型、凭据或 ComfyUI。

本阶段证明版本与人工反馈链路，不证明真实生成图片的质量。自动批次执行、等待主图后的恢复、自动组织生成结果并调用视觉审阅，以及真实人物/场景实验仍未完成；完整创作 Goal 保持 active。
