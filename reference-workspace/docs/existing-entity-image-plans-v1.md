# 已有实体的图片工作流接续

Owner: Sean。2026-10-04。

## 用户流程

在项目创作助手中指定已有角色／场景，要求新增角度、细节、实验图或 V3 多视图。助手先完整读取该实体，再调用 propose_existing_entity_images。服务器从当前资料生成只读的实体与剧情作用快照，保存尚未应用的创作方案。无需重复填写或重新创建该实体。

在「实体创作工作流」审阅接续方案：明确显示“接续已有实体”、稳定 ID 和只读来源资料。点击「调整方案」可修改图片提示词、引用、风格和模型，已有实体文字及剧情作用不提供编辑框。保存调整版本，再接受应用。应用只追加步骤，保留实体 ID、字段、主形象、声音、空间、已有关系和运行历史。随后按原图片步骤准备／批次／检验流程操作。

新增用途需要新的图片 key；已有相同 key 时提出步骤修订，不另建同名逻辑步骤。未明确选图的参考不从关系自动带入。已有角色的 V3 引用本角色已选主形象；场景其他角度／细节可依赖当前总览主图。没有依赖主图时仍等待人工选择。

## 工具与接口

- Agent 工具 propose_existing_entity_images：entityId、kind（character/scene/object）、title、summary、images。必须先 get_project_entity；指定参考图仅能来自本轮用户选图。
- POST /api/authoring/:projectId/existing-image-plans：相同输入，返回完整待审阅方案（201）。此人工入口也不直接应用。
- 审阅、调整和接受复用原 plans/:planId、revisions、apply 接口；不会向 Agent 提供应用或生成工具。

images 使用 authoringImageSchema 全部字段。请求示例：

```json
{
  "entityId": "<当前项目实体 UUID>", "kind": "scene",
  "title": "增加长凳细节", "summary": "保留已有空间，只补一个细节角度",
  "images": [{
    "key": "bench_closeup", "label": "长凳细节", "role": "scene_detail",
    "prompt": "Use Image 1 as the same hall. Show the established bench; preserve the entrance.",
    "purpose": "观察长凳材质", "modelId": "qwen-image-2.1", "styleId": "original",
    "referenceAssetIds": [], "useMainAppearance": true, "useBaseAppearance": false,
    "parameters": {}, "invariants": ["保留已确认入口与长凳的位置关系"], "unknowns": ["绝对尺度待补充"]
  }]
}
```

应用回执新增 createdEntityIds、existingEntityIds，原 entities 映射、steps、planId 保留；旧已应用回执不重写。仅接续时项目成员／修订／资料内容不改变。

完整方案候选也可携带 optional existingEntityId，混合接续实体与新人物、变体或物品。此时 profile/projectRole 必须与当前快照一致；baseEntityId/variationOf 为空、changes 为空，不沿用空间草稿。混合方案显式关系依原设定／项目剧情分类新增；不是覆盖旧关系。拒绝同实体重复候选、通过别名建立自身关系或重复关系。文字修改使用已有实体修改提案，已有关系调整仍由关系编辑流程完成。

## 持久化与兼容

沿用不可变 entity_authoring_plans、entity_workflow_steps，无新表或既有行迁移。新方案规则版本3，旧方案继续使用原规则；来源仍固定项目上下文哈希和明确引用的字节哈希。未接受方案不增加步骤。字段修改、项目或选图变化使待接受方案过期；接受校验、步骤创建与回执为一个事务，重复接受幂等。并发接续若增加相同逻辑 key，后接受者409。

已存在实体的快照只用于审阅，不写回；包括现有声音说明的派生显示值也不会写回成为固定事实。旧实体类型未明时 kind 仅用于本次工作流角色校验，不写成新的实体属性。有明确类型时拒绝不匹配的 kind。保留本机 Host/Origin 边界与稳定 assetId，不接受文件路径。

## 验证

63 tests 与 build 通过，新增7项覆盖：人工应用门槛、原实体／项目资料保留、重复接受、范围与字段约束、并发 key 冲突、依据过期与事务回滚、混合方案关系、自身／已有关系拒绝、Agent 完整读取与选图约束、已有角色 V3 依赖。模拟运行时不调用模型。

PC 临时库：调整提示词→只读字段不提供编辑框→保存新版本→接受→刷新后仍已应用。前后实体 detail 与项目完整 context 比较完全一致，回执 createdEntityIds=[]，新步骤指向原实体。控制台0错误／警告，无横向溢出；未运行模型或 ComfyUI。证据在 experiments/sean_reference_authoring_goal_20261004/continuation-{receipt.json,before-context.json,after-context.json,before-entity.json,after-entity.json,applied-pc.png}。

复现：reference-workspace 中 `npm run build`，再运行 `REFERENCE_EXISTING_IMAGES_FIXTURE=1 node scripts/scene-images-ui-fixture.mjs`，打开输出 workflowUrl。临时库自动清理，正式库不包含模拟项目。

持续目标仍未完成：真实模型方案质量、真实多组图片一致性／反馈修正效果、声音流程编排仍需验证或实现。
