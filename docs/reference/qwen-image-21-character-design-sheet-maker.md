# Qwen Image 2.1 Character Design Sheet Maker（Civitai Workflow）

> 范围：只记录 NeuroContent 发布的 Character Design Sheet Maker 工作流及本轮关于它的讨论；不汇总 Qwen Image 2.1 的其他模型、节点或工作流资料。
>
> 状态：外部页面说明整理，尚未下载或检查工作流 JSON，也未在本地 ComfyUI 运行。页面说明与作者评论属于上游描述/作者意图，不等于本地验证。
>
> 核对日期：2026-10-22（Asia/Shanghai）。

## 固定版本与入口

- 用户提供的 Civitai 版本链接：[Qwen Image 2.1 Character Design Sheet Maker，modelVersionId=3377047](https://civitai.com/models/2960750/qwen-image-21-character-design-sheet-maker-workflow?modelVersionId=3377047)
- 对应归档页面显示该版本为 **V3.0**：[CivArchive V3.0 页面](https://civitaiarchives.com/models/2960750?modelVersionId=3377047)
- 版本页面所列文件：`QwenImage21Character_qwenImage21V30.zip`；归档页面给出的 SHA256 为 `c9a760f237ee6044aa527949cca4ed0986539cbebda94002a7631710e06f2347`。
- 作者较早的 V2.0 说明页：[CivArchive V2.0](https://civitaiarchive.com/models/2960750?modelVersionId=3358399)。用于理解演进和评论，不替代固定 V3.0 的说明。
- 相关对照工作流：[Character Dataset Builder，用户提供的版本链接](https://civitai.com/models/2719177/character-dataset-builder?modelVersionId=3411837)。它以逐条角度提示词批量产出独立图片为目标；详见[独立专题记录](../qwen-image/character-dataset-builder.md)。

## V3.0 的工作方式

作者说明 V3.0 将此前 Production 与 Simple 两种工作流合并到一个包中，并增加静态提示词支持。两条选择轴要分开理解：

1. **版式/用途**
   - `Production`：偏精致、细节丰富、审美化的角色设定表。
   - `Simple`：更精简，作者明确称其面向视频动画使用。
2. **提示词路线**
   - **Auto-PE**：使用 Prompt Enhancer 根据参考图和角色信息自动生成/扩展设定表提示词。
   - **Static Prompt**：由使用者提供已经组织好的提示词，跳过 PE 的自动规划；作者建议在不需要 PE 对背景故事或精细角色特征作额外控制时使用，以缩短流程。

页面的能力表按 `Production` / `Simple` 列出 PE 和 Static Prompt 支持标记：Production 支持 PE，未标静态提示词；Simple 两者均标支持。下载工作流后应以具体节点图为准，确认模式切换和输入字段。

V3.0 的 Auto-PE 改用 Qwen 3.5 4B Safetensors 路线。作者称 int8 下提示词生成通常约 30 秒至 2 分钟；推荐依据可用显存选择 Qwen 3.5 4B/9B，也允许其他本地或云端 PE。页面还提到可启用 thinking mode 改善构图推理，但会增加提示词生成时间。上述耗时是作者描述，不是本机测量。

作者列出的依赖包括 ComfyUI-KJNodes、ComfyUI-DeGrid，以及 Qwen 3.5 4B/9B PE 权重（Safetensors 放入 `ComfyUI/models/text_encoders/`）。实际节点版本、是否可以替换为现有本地 PE，以及输出图的具体分辨率/采样参数，需检查 V3.0 JSON 才能确定。

## 产物形态与视频用途

作者把结果称作 Character Design Sheet，并描述 PE 规划表情、姿势、可选装备等主要内容。结合 V2 说明，常见内容包括：

- 面部表情：中性状态优先，再按角色描述决定其他表情；
- 姿势；
- 可选的装备/配件细节。

因此，按页面描述，它的主要产物是**包含多个内容面板的角色设定表**，不是默认逐项生成并保存的大量独立图片。当前尚未检查 V3.0 图，因此“是否单次生成、面板如何排布、是否有拆分/单独保存节点”仍待 JSON 核验。

### 可用于视频的素材组织方式

讨论中形成的使用假设：

1. 先用角色参考图生成设定表，丰富角色的身份、服装、表情、姿势和配件参考。
2. Agent 或使用者根据剧本/镜头确定要控制的角色状态。
3. 选择与镜头相关的面板；必要时从大图裁切，或单独重生成高分辨率特写，再作为 H3 参考图。
4. 视频提示词仍需描述镜头里的动作、表情变化和时间顺序。静态设定表提供视觉参照，不代替镜头指令。

这不是作者规定的唯一流程，也未在本地验证。若整张表直接输入 H3，多个面板可能同时争夺注意力；面板中文字、尺寸和细节密度也可能影响可读性。逐面板裁切、单独生成和直接整图参考三种方式应视具体镜头验证。

页面评论中，作者表示自己会预先安排符合角色性格/故事的情绪状态，用于明确控制生成视频中的角色状态，避免视频模型自行发明不合适的情绪。他举的方向包括角色长期悲伤时的中性/悲伤状态和微笑状态。作者也确认 Simple 流程有 `Character Description` 字段；Production 可用 `Entity Name` 与多行文本拼接描述。这些评论进一步支持“设定表可作为主动控制素材”，但不证明 H3 对整张表或裁切面板的具体服从效果。

## 与 Agent 提示词的分工

本轮讨论的工作假设（尚未做 A/B 验证）：

- Agent（DeepSeek/Codex）擅长结合角色设定、剧本、人物关系和镜头决定“这次要表达什么”。要稳定生成符合工作流版式的提示词，应提供专门的输出约束/技能，而不能只假设通用智能会自动掌握工作流要求。
- PE 是工作流中的自动提示词模块，优势是按作者设计的角色表任务将角色信息扩成表格提示词；它未必知道项目剧本和具体镜头意图。
- 有 Agent 时可由 Agent 先确定状态和控制点，再使用 Static Prompt。Auto-PE 适合快速探索，或暂时没有外部 Agent/不想手写面板提示词时使用。
- 目前没有证据说明 PE 或 Agent 的提示词质量必然更好。公平比较需固定参考图、角色描述、版式和目标面板，分别运行两条提示词路线并做视觉检查。

这里的 **PE** 指 Prompt Enhancer 模块，**Auto-PE** 指启用该模块自动生成提示词的模式；二者不是两个互相独立的节点流程。Static Prompt 是绕过自动提示词路线、提供预先写好的提示词。

## 已确认、推论与待核验

### 页面明确说明

- 固定版本 `3377047` 为 V3.0。
- V3.0 合并 Production 与 Simple 工作流，并增加静态提示词支持。
- Production 面向精致、细节丰富的角色设定表；Simple 面向视频动画用途。
- Auto-PE 用于角色特征、服装和细节的自动提示词组织；Static Prompt 可减少自动提示词阶段。
- 作者希望预先指定角色状态，以限制视频模型自行发挥不符合人物设计的情绪。

### 基于说明的合理推论

- Production 适合人审阅、角色塑造和美术探索；Simple 更适合作为视频模型的直接参考素材。
- 设定表面板可按镜头挑选，作为 H3 视觉参考；必要时拆成独立图片可降低不同状态互相干扰的风险。

### 尚未确认

- V3.0 JSON 的真实节点连接、每个模式的确切画布尺寸、图像模型权重与采样参数。
- 每次运行究竟输出几张图、面板是否由单张大图构成，以及是否已有自动裁切/逐项保存能力。
- 整张表、单个裁切面板分别输入 H3 后的效果和对表情控制的提升。
- Agent Static Prompt 与 Auto-PE 在相同输入下的质量、耗时和稳定性差异。

## 后续讨论入口

先重读本文，再按问题进入来源页面。若要实施本地复现，应先检查下载包中的 V3.0 JSON 与 README/节点说明；不要仅凭页面描述把未验证的切图或多图保存能力写成本地基线。
