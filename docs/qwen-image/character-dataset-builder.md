# Character Dataset Builder（Qwen Image 2.1）

> 范围：记录 Sean 提供的 Character Dataset Builder Civitai 工作流及其 Qwen Image 2.1 路线，供后续讨论和节点图核验使用。不在此汇总 Qwen Image 2.1 的其他模型、实验或工作流。
>
> 状态：外部页面与第三方页面说明整理；尚未下载或检查 ComfyUI JSON，也未在本机运行。耗时和 Ghosting 均为作者报告，不能视为本机实测。
>
> 核对日期：2026-10-22（Asia/Shanghai）。

## 入口与版本识别

- 用户提供的固定 Civitai 链接：[Character Dataset Builder，modelVersionId=3411837](https://civitai.com/models/2719177/character-dataset-builder?modelVersionId=3411837)
- PromptHero 工作流页：[Character Dataset Builder](https://prompthero.com/ai-models/character-dataset-builder-2719177-download)
- PromptHero 的 Qwen 版本页：[Q21_CharDataSetBuilder_v1](https://prompthero.com/ai-models/character-dataset-builder-2719177-download/character-dataset-builder-q21_chardatasetbuilder_v1)
- PromptHero 当前同时列出 `Q21_CharDataSetBuilder_v1` 和 `Q21_CharDataSetBuilder_v2`。公开镜像没有显示 Civitai modelVersionId，因此**尚未核实用户链接中的 `3411837` 精确对应 Q21 v1 还是 v2**。后续检查工作流文件名/页面版本信息时再消除此项。
- 与角色设定表的关系：作者将 Character Sheet Builder 作为制作角色参考图的前置工具；Q21 v2 页面建议使用其 Basic 版生成输入图。可参阅 [Character Sheet Builder 相关工作流页面](https://civitai.com/models/2966369/qwen-21-character-sheet-builder-no-llm)。这两个工作流不是同一个节点图：一个生成角色表，另一个按独立提示词批量生成角色图。

## Qwen 2.1 路线的目标

Q21 版本把一张角色图作为参考，配合一组视角/取景/表情提示词，逐条批量生成独立图片，组成角色数据集。作者提到数据可用于后续角色 LoRA 训练；工作流本身负责生成图片数据，并不负责训练 LoRA。

它与 Character Design Sheet Maker 的主要区别：

| | Character Dataset Builder Q21 | Character Design Sheet Maker V3 |
|---|---|---|
| 主要输出 | 多张单独生成的角色图 | 角色设定表/多面板图（依页面说明；图节点尚未检查） |
| 生成组织 | 角度提示词逐条运行，组成批量数据集 | 根据设定表任务生成内容面板 |
| 主要用途 | 参考素材库、角色数据集、LoRA 训练素材 | 角色塑造、表情/姿势/装备设定图，也可挑选为视频参考 |
| 典型角度 | 正面、左右 45°、左右侧面、左右 135°、背面；全身、胸像、头像等 | 表情、姿势和可选装备等设定面板 |

此表是对两个工作流页面描述的归纳，不代表已在同一输入上比较其角色一致性。

## 作者对 Q21 v1 的说明

作者称 Q21 版本相较 FK9 版本简化了图像输入和采样子图，直接使用 Qwen 2.1 的 encode 节点；其经验是 Qwen 对参考图数量较敏感，所以该版只使用一张参考图。作者只用角色设定表和较简单角色测试过，复杂角色/多参考图扩展没有被证明。

Q21 v1 描述中的核心数据：

- 默认有 **30 条角度/表情提示词**，可改提示词数量。
- 每条提示词对应一次独立生成；默认约 30 张图，而不是把 30 个视图排成一张大图。
- 作者报告：1 MP、30 张数据集约 8 分钟。机器、模型量化、步数、缓存、队列和端到端计时范围未充分说明，这只是作者提供的速度参考。
- 作者说可选择使用 Turbo LoRA，但不是必需；页面没有说明模型文件名、权重或节点图上的具体接法。这里的 Turbo LoRA 指可选的生成加速组件，不是要训练出来的角色 LoRA。
- 作者报告结果可能有 Ghosting，需要生成后人工筛除；成因和自动 QC 方法没有给出。

作者说明 Q21 v1 的参考输入倾向单图，推荐较简单的角色测试。FK9 通用版本“1–3 张参考图”“先用 3–4 视图表和头像作参考”等建议不应未经节点核查直接套用于 Q21 单图版。

## 提示词结构与示例覆盖

Q21 v1 页面列出的提示词组共 30 条，大致由以下部分组成：

1. **全身角度**：正面、左右 45°、左右 90°侧面、左右 135°背侧、正背面，共 8 个方向。
2. **胸像角度**：相同的 8 个方向。
3. **头肩特写角度**：相同的 8 个方向。
4. **正面表情**：中性、开心微笑、悲伤、噘嘴、尴尬/痛苦表情、调皮吐舌，共 6 条。

角度提示词以“一个人、取景范围、身体旋转角度/朝向、站姿或表情”为主。作者称可调整 Angle Prompts；Q21 版本页没有列出与 FK9 流程完全相同的所有操作字段，实际节点名称和 batch 对齐方法需从 JSON 检查。

## 页面提供的使用指引及其边界

PromptHero 镜像将工作流通用操作写为：载入参考图、按运行子图设置参考图数量、填写 Master Prompt、调整 Angle Prompts、指定输出目录并运行；每一条角度提示对应一次运行，新增/删除提示词后同步调整批次数。

但这段明确标注在 **FK9 Version** 说明下。Q21 版本说明只明确说单图输入、Qwen encode 子图、角度提示词和批量数据集，没有完整重述全部字段。所以后续使用 Q21 时，先查看它自己的 JSON 注释/输入控件，不能假设 `Ref Image #`、多图输入或 FK9 wildcard 节点仍同名存在。

作者关于服装/配件的建议是：如果角色换装或配件变化，最好提供相应的新参考表，不要期待所有 30 张输出仅靠 Master Prompt 保持一致；页面还提到可增加第三张参考图。但这主要来自通用/FK9 操作说明，与 Q21 v1 的“只用一张参考图”经验有张力。Q21 具体版本如何处理换装、多参考图须以节点图和实测为准。

FK9 v2 的 wildcard 背景/灯光变化也是 FK9 路线说明，**不能据此认定 Q21 节点已有同样功能**。

## 与 H3 视频参考的可能关系

本轮讨论中的用法推论：批量生成的独立图片可组成可筛选的参考图库。若某个 H3 镜头需要特定 3/4 角度、侧面、背面或表情，可以挑选相应图片作为角色/外观参考；若镜头普通且提示词已能控制，则未必需要额外参考图。

这不是作者对 H3 工作流的明确保证。页面所述主要目标包括制作角色数据集和 LoRA 训练素材；并未证明批量图在跨视角身份一致性、服饰细节保留或 H3 条件跟随上达到何种精度。作者报告的 Ghosting 也意味着不能把批量结果直接当作全部合格资产，需要人工筛查。

## 已确认、推论与待核验

### 页面明确说明

- Q21 版采用单张输入参考图的简化路线；作者认为 Qwen 2.1 对参考图数量敏感。
- 多条 Angle Prompts 可生成多张独立图片；Q21 v1 页面提供 30 条提示词。
- 数据可用于后续角色 LoRA 训练；Turbo LoRA 可选，不是必需。
- 作者报告 1 MP、30 张约 8 分钟，并报告 Ghosting，需要人工筛除。
- Q21 v2 被描述为更简化但更刚性的版本，并建议使用特定 Character Sheet Builder Basic 版的图作为输入。

### 尚未核实

- `modelVersionId=3411837` 对应 Q21 v1 或 v2 的精确映射。
- 固定版本 JSON 中所用 Qwen Image 2.1 权重、量化、分辨率、步数、采样器、批次和 Turbo LoRA 节点/强度。
- 30 张是否全部由单个 ComfyUI batch 节点执行，还是经子图/队列逐条执行；失败重试和文件命名规则。
- 作者报告的 8 分钟是否只计采样，是否包括模型加载和节点前处理。
- Ghosting 具体表现、发生频率及和参考输入/采样参数的关系。
- 对同一角色和服装而言，30 张间的身份/服装一致性；以及用作 H3 视频参考时的收益。

## 续聊时建议从这里开始

1. 先核对用户链接版本 `3411837` 的文件名/版本名，并查看 JSON 内节点组和注释。
2. 从参考图数量、Master Prompt、Angle Prompts、batch 数、输出路径、Turbo LoRA 开关和保存命名梳理实际操作方法。
3. 若要试跑，先挑少量提示词覆盖 3/4 视角、全身/近景和一种表情；记录各图是否完成、耗时范围及人工筛查结果，再决定是否扩大到 30 张。
4. 将“作者报告的速度/质量”与“本机执行事实”和“H3 实际参考效果”分开记录。

## 来源

- [Civitai：Character Dataset Builder（用户固定版本链接）](https://civitai.com/models/2719177/character-dataset-builder?modelVersionId=3411837)
- [PromptHero：项目总页及 FK9 通用操作说明](https://prompthero.com/ai-models/character-dataset-builder-2719177-download)
- [PromptHero：Q21_CharDataSetBuilder_v1 页面](https://prompthero.com/ai-models/character-dataset-builder-2719177-download/character-dataset-builder-q21_chardatasetbuilder_v1)
- [PromptHero：Q21_CharDataSetBuilder_v2 页面](https://prompthero.com/ai-models/character-dataset-builder-2719177-download/character-dataset-builder-q21_chardatasetbuilder_v2)
- [相关 Character Sheet Builder](https://civitai.com/models/2966369/qwen-21-character-sheet-builder-no-llm)
