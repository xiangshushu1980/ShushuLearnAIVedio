# 人物创作方案中的 V3 多视图

Owner: Sean。2026-10-04。

## 使用

在项目创作助手中要求人物概念图及三视图、表情＋正侧背，或脸部＋正面／背面／侧面。助手可把 V3 步骤与人物、实验变体、关系一起保存为创作方案。人工审阅并应用后，在「批次生成实验」选择步骤、保存计划、开始。概念图完成后人工选定每个人物自己的主形象，再恢复等待的多视图批次。

变体概念图仍可依赖基础人物主图；变体的 V3 必须依赖变体自己的主图。不自动替用户选择图片，不继承基础人物多视图确认状态。场景继续使用总览／其他角度／细节图片组。

V3 提示词、模型布局、风格与参数可在方案调整和步骤修订中审阅。独立修改布局模型后也应核对提示词中的布局描述，避免模型标签与文字要求不一致。当前 V3 创作步骤通过批次执行；「载入生成输入」保留给概念图步骤。既有三视图页面的独立生成和历史恢复继续可用，但另行创建的输入不冒充创作步骤的执行记录。

## 契约与安全边界

既有 `authoringPlanSchema` 的 images 新增 role `three_view`，代表人物多视图（包括全部三种 V3 布局）。该步骤必须满足：

- candidate.kind 为 character；modelId 为现有 V3 Simple 模型。
- useMainAppearance:true、useBaseAppearance:false、referenceAssetIds:[]。
- prompt、styleId、parameters、invariants、unknowns 按原完整 schema 保存。

Agent catalog 返回 V3 模型及各风格的原版布局提示词；运行时仍使用服务器固定模板，不允许 Agent 执行任意节点 JSON。人物主形象尚不存在时，方案可以保存／应用，但预览和运行准备拒绝；批次进入等待状态。主形象选定后，prepareRun 读取当前 appearanceId 和唯一 assetId，真实运行服务再次校验它们与选用步骤及当前主形象一致。已捕获主图发生变化的批次停止复核，不继续提交。

运行及输出沿用 authoring provenance，保留 stepId、planId、role、版本、不变量、未知项和批次来源，可加入现有逐张观察／一致性报告／反馈修订链路。输出本身仍不是人工确认；沿用原三视图确认及 Reference 导出规则。

旧方案、图片步骤、概念图草稿不迁移、不重写；schema 为新增角色兼容扩展。未新增生成权限。开发验证没有访问 ComfyUI、GPU 或凭据。

## 验证与复现

56 项自动测试通过，build 通过。新增5项验证覆盖：全部三种布局编译／真实运行快照预览、非法场景与错误引用依赖拒绝、变体本身主图要求、等待／人工恢复／主图变更中止，以及模拟 Agent 实际读取含 V3 模板的 catalog 并保存未应用方案。

PC 临时库验证：三布局步骤选择→保存批次→开始后等待→通过临时库 API 选定模拟概念图→网页恢复→3/3 模拟输出，控制台0错误／警告，无横向溢出。模拟派发器不调用模型，色块只验证持久化与交互，不证明真实三视图效果。证据：experiments/sean_reference_authoring_goal_20261004/v3-ui-{waiting,main,completed}.json、v3-batch-pc.png。

复现：在 reference-workspace 执行 `npm run build`，再运行 `REFERENCE_MULTIVIEW_FIXTURE=1 node scripts/scene-images-ui-fixture.mjs`。打开输出 workflowUrl；multiviewFixture 给出临时人物和概念图稳定 ID。停止进程自动清理临时库。此模式不读取模型凭据、不提交 ComfyUI。

持续目标尚未完成：真实模型对新布局方案的质量、真实图片逻辑一致性、声音步骤编排等仍待验证或实现。
