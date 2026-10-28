# Reference 文档导航

> Owner: Sean。本页只负责主题路由和权威边界，不复制流程、参数或实验结论。

## 按目的进入

| 需要回答的问题 | 权威入口 | 相关资料 |
|---|---|---|
| Qwen Image 2.1 Character Design Sheet Maker 怎么用，能否作为视频参考？ | [Character Design Sheet Maker 专题记录](qwen-image-21-character-design-sheet-maker.md) | 固定 V3.0 版本说明、Production/Simple、Auto-PE/Static Prompt、视频参考用途和待核验项 |
| 如何制作、审核并打包当前正式 Reference 资产？ | [Reference 资产手册](../45_ref_asset_handbook.md) | [Krea2 主图与身份编辑](../40_krea2_prompt_and_identity_pipeline.md) |
| 多视图、LoRA 或布局方案有哪些证据和限制？ | [多视图一致性研究](../46_multiview_consistency_research.md) | [Reference 测试计划](../41_h3_character_reference_test_plan.md)，实测产物从 [实验索引](../../experiments/INDEX.md) 定位 |
| 如何选择 Qwen Image 或 Krea2 做人物/实体三视图？ | [跨模型三视图工作流](three-view-workflow.md) | [图片生成资料入口](../image-generation/README.md) |
| Reference 创建/编辑产品流程当前怎么定？ | [创建与编辑流程](../48_h3_reference_creation_editing_flow.md) | [实现前架构设计](../49_h3_reference_workspace_architecture.md) |
| 远景小脸和 FaceRefine 当前边界是什么？ | [FaceRefine 当前状态](../43_h3_facerefine_current_state.md) | [latent 二采研究](../39_h3_latent_upscale_face_research.md)、[二采策略](../40_h3_far_face_second_pass_strategy.md) |

## 文档职责与状态

- [Qwen Image 2.1 Character Design Sheet Maker 专题记录](qwen-image-21-character-design-sheet-maker.md)：Civitai 固定 V3.0 的页面说明与本轮讨论；尚未下载/检查 JSON 或本地运行，不是生产基线。
- [45 Reference 资产手册](../45_ref_asset_handbook.md)：正式生产资产链和审核门槛；生产流程以此为准。
- [40 Krea2 提示词与身份管线](../40_krea2_prompt_and_identity_pipeline.md)：Krea2 主图与身份编辑；不定义完整多视图资产链。
- [46 多视图研究](../46_multiview_consistency_research.md)：候选方法、研究证据和适用边界；研究结果只有经过审核并进入 45 的基线后才成为正式流程。
- [人物与实体三视图工作流](three-view-workflow.md)：跨模型任务入口与结果检查要求；不复写模型参数或实验流水。
- [41 人物 Reference 测试计划](../41_h3_character_reference_test_plan.md)：实验问题和对照设计；原始结果、QC 与 manifest 以实验目录为准。
- [48 创建与编辑流程](../48_h3_reference_creation_editing_flow.md)：Media Browser 创建/编辑阶段的当前流程决策。
- [49 工作区架构](../49_h3_reference_workspace_architecture.md)：实现前架构设计，不代表代码已实现或运行时已验证。
- [47 工作台重新设计草案](../47_h3_reference_workbench_redesign.md)：另一任务提出的较早画布方案；与 48 的 Media Browser 流程存在差异。整体实现规划前应回到相关任务对账，不把任一方案误当成对方已正式取代。
- [23 设定图体系设计](../23_refimage_system.md)：早期通用设计；角色多视图正式生成链已由 45 覆盖。
- [43 FaceRefine 当前状态](../43_h3_facerefine_current_state.md)：当前执行入口；历史判定及证据锚见 [h3-models ledger](../../.pi/ledger/h3-models.md) 和关联实验。

## 证据追溯

```text
实验目录 / manifest / QC
        ↓ 稳定结论与适用边界
.pi/ledger/ 对应条目
        ↓ 当前可执行流程
docs/45、docs/43 等现行基线
```

实验索引：[experiments/INDEX.md](../../experiments/INDEX.md)；结论账本索引：[.pi/ledger/README.md](../../.pi/ledger/README.md)。任务状态和 checkpoint 以 Task Center 为准。
