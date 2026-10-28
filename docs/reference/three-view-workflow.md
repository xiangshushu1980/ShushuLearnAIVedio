# 人物与实体三视图工作流

> 本文按共同任务整理 Qwen Image 与 Krea2 的路线。它说明如何选入口及如何理解结果，不复制各模型的提示词、参数或实验报告。

## 任务定义

三视图通常指同一主体的正面、侧面和背面视图。人物关注身份、体态、服装及装备在不同角度的延续；一般实体关注外轮廓、结构和可辨认部件。两类任务都需要逐视图检查：生成出三栏不代表主体细节已跨视角保持。

## 模型路线

| 路线 | 适合场景 | 当前边界 | 入口 |
|---|---|---|---|
| Qwen Image 2.1 `three-view` | 从一张已确认外观图生成前、侧、后组合图；人物与实体按不同描述约束 | 共享接口维护当前预设；配件在每个角度的可见性不保证。更完整条件见共享调用说明 | [Qwen Image 项目索引](../qwen-image/README.md) · [Qwen 调用说明](/home/sean/.pi/agent/skills/comfyui/references/qwen-image.md) |
| Krea2 CharacterSheet / QuadView | 探索生成三/四栏角色视图板、控制面板结构或比较角色细节 | 研究路线；视角间的装备、服饰与结构仍可能缺失或错位，尚未通过正式 Reference 的 H3 下游验收 | [Krea2 项目索引](../krea2/README.md) · [多视图研究](../46_multiview_consistency_research.md) |

两条路线服务于同一类需求，但不是同一工作流：调用入口、条件组织和结果边界分别由各自的模型说明维护。需要挑选模型时，按目标是直接获得三视图组合、探索不同面板布局，还是制作正式 Reference 资产来选择入口。

## 结果检查

至少检查：

- 主体是否确为同一人物或实体，视图数量与顺序是否正确；
- 正、侧、背是否给出可辨认的对应轮廓，而非重复或遗漏视角；
- 服装、标志性部件、装备及其左右位置是否跨视图保持；
- 面板是否完整、可分辨并适合后续裁切；
- 结果用途是否只是构思/QC，或已满足正式 Reference 的验收要求。

提示词和布局控制只代表生成条件，不等于结构保证。关键装备或非对称细节应分别核对正、侧、背；不合格结果留在候选阶段，不因版式正确而提升为正式资产。

## 正式 Reference 边界

当前正式人物 Reference 制作仍以 [Reference 资产手册](../45_ref_asset_handbook.md) 为准：Krea2 可用于主图阶段，但不能用独立逐视角生图替代既定的 H3 全视角、抽帧与 QC 链路。Qwen 或 Krea2 生成的组合图可用于探索和审核；正式采用仍须满足手册的来源一致性与验收要求。

## 证据与维护

- 模型接口和可执行约束：分别看共享 comfyui skill 的 [Qwen Image 说明](/home/sean/.pi/agent/skills/comfyui/references/qwen-image.md) 与 [Krea2 QuadView 说明](/home/sean/.pi/agent/skills/comfyui/references/krea2-quadview.md)。
- 视图板方法、失败类型和对照证据：看[多视图一致性研究](../46_multiview_consistency_research.md)及其中链接的实验报告。
- 当前项目入口：[图片生成资料入口](../image-generation/README.md)。
