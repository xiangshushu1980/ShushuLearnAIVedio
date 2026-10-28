# Krea2 项目资料

> Krea2 专题入口。共享调用与模型参数以共享 comfyui skill 和实际工作流为准；本页不复制参数表或实验过程。

## 项目用途

| 用途 | 权威资料 | 当前边界 |
|---|---|---|
| 人物身份编辑与主图准备 | [Krea2 提示词与身份管线](../40_krea2_prompt_and_identity_pipeline.md) | `tools/krea2_prompt_profiles.py` 是提示词来源；主图结果再进入 Reference 下游流程 |
| 多视图/CharacterSheet 探索 | [多视图一致性研究](../46_multiview_consistency_research.md) | Krea2 QuadView 结果仍是实验候选；尚无 H3 下游验收或 canonical promotion |
| 基础生图 | [ComfyUI Krea2 图像说明](../../.pi/skills/comfyui-ops/references/image/krea2.md) | 适用于项目内基础路线与节点说明 |
| 正式人物 Reference | [Reference 资产手册](../45_ref_asset_handbook.md) | 当前正式链路不以 Krea2 独立多视图生成替代 H3 全视角与抽帧 |

## 相关项目记录

- [共享图片生成入口](../image-generation/README.md)：按任务查找 Qwen Image、Krea2 与正式 Reference 流程。
- [Krea2 模型与身份管线原文](../40_krea2_prompt_and_identity_pipeline.md)：保留稳定路径，供现有引用继续使用。
