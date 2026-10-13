# Reference 实体创作持续目标

Owner: Sean。2026-10-04。Goal 保持 active。原目标：自然语言驱动人物/场景设定、关系、图片提示词/工作流/生成与逻辑检验，支持多组独立变体和保持一致的场景多角度/细节图片。

已完成阶段：结构化方案工具及审阅 UI，原子建立实体/项目角色/设定与剧情关系/变体，固定图片步骤预览和生成草稿准备，运行/输出 provenance，实际看图范围约束的视觉报告。证据：build、7 新隔离测试及全部 19 测试通过；两次真实 Pi 对话均生成 3 候选/5 步骤并在临时数据库应用，无 ComfyUI 调用。第二次空间事实保留未知，变体等待基础主图，证据见 experiments/sean_reference_authoring_goal_20261004/。

不得据此完成 Goal。完整缺口列表和下一步入口：reference-workspace/docs/entity-authoring-workflow-v1.md 的“验证证据与完整目标差距”。先补 PC 交互与真实 Pi 对话验证，再推进批次执行/依赖恢复/反馈修订及场景多图确认导出；实际 ComfyUI 验证沿用明确授权、共享资源规则。

本次未自动创建远程 Task Center 任务，前两个 Agent/项目任务保持 awaiting_acceptance；仅查询冲突，不借用其 lifecycle。提交信息见阶段交付。

2026-10-04 场景图片组阶段：人工确认、变化复核、删除保护与三种scene_*导出角色已完成，项目上下文包含图片组；24测试/build、隔离PC操作通过。未调用模型/ComfyUI。权威 docs/scene-images-v1.md。下一步仍为自动批次执行/依赖恢复与反馈修订，真实图片实验需授权。

2026-10-04 图片步骤修订：不可变候选/采用/恢复/并发与来源核对已完成；Agent需实际读取步骤，PC验证修订并恢复旧版。28测试/build通过，无真实模型/ComfyUI调用。下一阶段自动批次执行与依赖恢复、真实生成质量仍待做。

2026-10-04 批次阶段：固定范围、串行调度、主图等待/恢复、失败停续、重启找回run、跨实验选图已实现；36测试/build、隔离2步PC完整操作通过。仅模拟数据、没有真实模型或ComfyUI调用。下一步真实Agent视觉检验与反馈修订链路、人物V3/声音编排及多组真实图像实验；完整Goal不完成。

## 2026-10-04 图片反馈修订阶段

Owner: Sean。检验报告的 workflowSources 由真实 Reference run 来源生成；报告→图片步骤修订保留 reportId/hash/原图版本。PC 模拟证实只填文字不自动发送，主动发送后待审阅v2和来源刷新保留。新模块 server/image-feedback.mjs；手册 docs/image-feedback-v1.md。完整目标保持未完成，接下来继续 V3/声音编排及真实图像反馈效果验证；不应把 mock 工具成功当作模型品质。

## 2026-10-04 场景变体一致性前提

Owner: Sean。场景变体自动基础图依赖、可关闭的空间草稿沿用及旧规则兼容已实现。锚点保留ID，全部pending，以新entityId为范围；不继承核对图片/确认。47测试与隔离PC通过，sourceSpatialVersionId与未确认导出核对完成。真实生成验证许可已通过异步问题请求，目前未收到回复；独立实现继续推进，完整目标保持active。

## 2026-10-04 已有实体自然语言修改

Owner: Sean。增加不可变实体文字提案、字段预览、人工作用与原子应用修订；模型只能提案，不能执行接受。51测试/build与模拟PC通过，真实模型/图像验证仍待完成，之前真实生成权限问题仍未收到回复。完整目标active。

2026-10-04 Owner: Sean — V3 三种多视图布局新增 three_view 创作步骤，概念图/变体与本实体主图依赖、实验批次、逐张检验衔接。56 tests/build 与临时库 PC 三布局等待→人工选图→恢复→3/3 模拟输出通过；零真实生成/模型调用。文档 reference-workspace/docs/authoring-multiview-v1.md。持续目标 active，声音编排及真实图片质量仍待完成。

2026-10-04 Owner: Sean — 已有项目实体图片接续：Agent读取完整实体后规划，网页只读字段+可改图片，接受保留原实体ID/主图/文字/空间/声音。混合新旧候选可明确新增关系，重复key/自身关系/旧关系拒绝。63tests/build及隔离PC调整→接受→刷新验证通过，前后entity detail与project context完全一致、createdEntityIds=[]。未调用模型或ComfyUI；持续目标active。说明 reference-workspace/docs/existing-entity-image-plans-v1.md。

2026-10-04 Owner: Sean — 完成 deepseek/deepseek-flash 三真实对话（已有实体/V3接续、腕伤+绷带关系、世界规则审阅），临时库5步骤、零图片生成。发现未知几何被写成否定、无伤断言等来源问题；收紧方法后单次接续重测人物改进，但场景仍自行指定未知材质/照明，语义质量未通过。文字报告新增本轮完整读取引用约束与partial/complete/unreviewed IDs，67tests/build与PC部分范围显示通过。详见 reference-workspace/docs/authoring-real-dialogue-verification.md；完整目标active。

2026-10-04：图片一致结论补齐实体及生成步骤完整读取要求；comparisonCoverage 持久化与 PC 显示，76 测试/build/mock PC 通过。未调用真实模型或 ComfyUI；整体目标继续，实际图像反馈再生成验证仍待授权及执行。
