# Qwen Image 2.1 资料索引

> 本页归拢项目内与 Qwen Image 2.1 相关的现行说明、专题资料和结论演进入口。模型调用契约以共享 comfyui skill 为准；本索引不复制参数表或实验结论。

> 跨模型任务入口： [人物与实体三视图工作流](../reference/three-view-workflow.md) · [图片生成资料入口](../image-generation/README.md)。

## 当前使用与 ComfyUI 实测

| 主题 | 资料 | 用途与边界 |
|---|---|---|
| 共享调用契约 | [Qwen Image 共享说明](/home/sean/.pi/agent/skills/comfyui/references/qwen-image.md) | 通用图片生成与 Qwen Image 2.1 BF16 Character Sheet LoRA 三视图调用；属于用户级共享能力 |
| 角色外观参考图 | [character-reference-image skill](/home/sean/.pi/agent/skills/character-reference-image/SKILL.md) | 独立编写参考图提示词、生成、检查，并把图像与精确提示词成对保存；当前提供 Qwen Image 2.1 provider route |
| 角色三视图方法 | [qwen-character-sheet skill](/home/sean/.pi/agent/skills/qwen-character-sheet/SKILL.md) | BF16 Character Sheet LoRA 的输入模式、角色提示词、空间一致性检查、定点修正与 H3 交接 |
| 节点、参考图与 Tiny VAE | [Qwen Image 2.1 节点与 Tiny VAE 实测](../50_qwen_image_2_1_nodes_and_tiny_vae.md) | 本机节点识别、四张有序参考图调用及预览解码验证；不是完整工作流总手册 |
| 图表美学当前基线 | [Qwen 图表美学基线](../qwen-chart-aesthetics-baseline.md) | 固定数据图表的参考图编辑路线与适用范围 |
| 模型与环境 | [本地模型清单](../02_models.md) · [运行环境](../01_environment.md) | 查看模型文件与环境背景；实际可用状态以当前运行时和共享说明为准 |

## 专题与研究资料

| 主题 | 资料 | 状态说明 |
|---|---|---|
| Character Design Sheet Maker | [工作流专题记录](../reference/qwen-image-21-character-design-sheet-maker.md) | 固定版本页面说明与讨论；尚未下载、检查工作流 JSON 或本地运行，不是生产基线 |
| Character Dataset Builder | [Qwen Image 2.1 Character Dataset Builder 专题](character-dataset-builder.md) | 单图参考＋角度提示词批量生成独立角色图片；外部说明已整理，JSON 与本机效果待核验 |
| 图表参考编辑实验 | [Qwen Turbo 美学实验](../../experiments/sean_qwen_turbo_chart_aesthetics_20261015/README.md) | 固定数据几何与美学重构的分阶段实验记录 |

## 结论演进与节点路由

- [Qwen 节点结论 ledger](../../.pi/ledger/qwen-nodes.md)：节点、缓存、参考图输入及调用方复核的演进记录。
- [Qwen 图表结论 ledger](../../.pi/ledger/qwen-charts.md)：固定数据图表实验的结论与覆盖关系。
- [comfyui-ops 项目研究索引](../../.pi/skills/comfyui-ops/INDEX.md)：项目级 ComfyUI 能力导航。
- [图像生成能力索引](../../.pi/skills/comfyui-ops/references/image/README.md)：Qwen、Krea2、ANIMA 等图像能力的路由入口。

## 上级入口

- [Comfy-ops 文档总索引](../INDEX.md) · [Reference 专题索引](../reference/README.md) · [项目研究与运维总索引](../../.pi/skills/comfyui-ops/INDEX.md)
