# [Sean] 多视图统一性节点、LoRA 与工作流调研

owner: Sean
status: research baseline
date: 2026-09-26

## 结论先行

当前 Krea2 静态双栏 turnaround 的失败不是提示词长度不足，而是任务形态不对：模型需要在同一张画布上同时布局两个或三个独立主体，因此会重复正面、重解释肩甲或改写发型。

更适合作为辅助主流程的是 **H3 多视图轨迹 + 视角抽取**：让同一个角色在同一条 H3 latent/视频轨迹中按顺序经历 front、3/4、side、back，再从已经统一的轨迹抽帧。它把“前后对应”变成跨时间的连续性问题，而不是两张独立图片的布局问题。

## 候选方案

| 方案 | 视图机制 | 与当前问题的匹配 | 当前判断 |
|---|---|---|---|
| H3 ContactSheet + `minimax_h3_five_view_512_s1500` | 五槽联合去噪，一张输入直接输出 5 个独立视图 | 有跨视图联合 latent；已在本机安装和测试 | 恢复为第一候选，但保留写实/复杂服装边界 |
| OrbitSheets | H3 5 秒 I2VA、硬切 front/face/left/right/back，再按内容聚类抽帧 | 直接解决重复视图；硬切避免连续旋转中间漂移 | 最值得作为当前辅助流程验证 |
| H3 Edit Character Sheet | 73/124/171 帧校准角色轨迹，输出 4/6/8 视图 sheet 与单图 batch | 可按 clothing 6 views 或 canonical 8 views 组织结构 | 值得作为正式 H3 reference workflow 的候选升级 |
| JahJedi H3 Character Sheet | 5 帧冻结输出 8 面板，强调设计文档而非概念图 | 可一次获取角度+局部细节；网格仍有重复/串板风险 | 适合做结构/服装辅助板，不直接当 canonical 单图 |
| Krea2 CharacterSheet LoRA | Krea2 的 TripleView / QuadView / DynamicCharacterSheet | 正好是 3/4 视图，但模型卡明确一致性不是 100% | 可做静态对照，不优先于 H3 轨迹 |
| Flux Kontext turnaround LoRA | 一次静态 5/6 视图横向 sheet | 提示词和 LoRA 专门针对 turnaround | 需 Flux Kontext 环境；暂不并入 H3 正式链 |
| CharaConsist | 缓存 subject attention，在多次 T2I 中保持主体 | 解决跨图主体一致，不是专门视角轨迹生成 | 对当前 H3 任务是旁支，不作为首选 |

## 关键证据

### 1. H3 五视图 LoRA + ContactSheet

`matlod/minimax-h3-turnaround` 的设计是将 H3 的时间轴重新作为五个视角槽位：一个参考图和一个指令联合生成五个逐步旋转的独立图像 latent。模型卡明确要求使用 `ComfyUI-H3-ContactSheet` 的两个节点和专用五槽打包，不能把 LoRA 随便放进普通 sampler；普通视频生成会被该 LoRA 破坏。

本机已经具备：

- 节点：`/home/sean/projects/ComfyUI/custom_nodes/ComfyUI-H3-ContactSheet`
- LoRA：`/home/sean/projects/ComfyUI/models/loras/minimax_h3_five_view_512_s1500.safetensors`
- 现有工作流：`workflows/turnaround_test.json`、`workflows/h3_shushu_object_ref_probe.json`

本机历史实测：512 约 45 秒生成 5 视图，1024 约 50 秒；风格化/动漫角色一致性曾通过。写实角色旋转曾失败，不能把这条边界省略。相关历史记录在 `.pi/tasks/T-20260815-07/progress.md` 和 `.pi/ledger/h3-prompt.md`。

### 2. OrbitSheets：硬切多视图比连续旋转更适合抽取

`ComfyUI-OrbitSheets` 的 Character Turnaround Prompt 生成约 5 秒的 H3 I2VA 序列，用硬切固定 full body、face、left profile、right profile、back；其 README 明确指出硬切会迫使模型在每个视角重新建立稳定画面，避免连续 360° 旋转中出现滚转、地面和镜头漂移。

它还提供按内容聚类的 frame selection，而不是简单按时间切片：当 H3 某个 shot 变长或重复正面时，内容聚类可以检测近重复，并在 `info` 中报告“实际 distinct views 少于请求 views”。这正好可以成为当前 QC 的机器门槛。

推荐优先验证：`shots=5`、`count=5`、`keep_first_frame=false`、`views by content`，并把角色设置为固定中立站姿；不要先用连续 360° orbit。

### 3. H3 Edit Character Sheet：更完整的 6/8 视图路线

`ComfyUI-MiniMax-H3-Edit` 已提供 calibrated character-sheet profiles：

- 4 panels / 73 frames：`2, 24, 45, 68`
- 6 panels / 124 frames：`2, 21, 42, 63, 84, 113`
- 8 panels / 171 frames：`2, 21, 42, 63, 84, 108, 131, 160`

其中 clothing 6 views 固定镜头、头到膝盖尺度和 0°/60°/120°/180°/240°/300° 角度，适合检查肩甲、衣领、腰带和服装结构；canonical 8 views 同时保留全身轨迹和面部/3/4 视角。它的 `Decode H3 Character Sheet` 可以同时输出组合板、独立视图 batch、全部轨迹帧和解析后的 frame indices，符合我们后续 manifest 的需要。

### 4. JahJedi 8 面板 H3 Character Sheet

`JahJedi/MiniMax-H3-Character-Sheet` 的提示词把结果定义为“已有设计的 documentation sheet”，而不是重新设计角色；它使用 5 帧冻结生成 8 面板，上排为 front / 3/4 / strict side / back，下排为四个细节区。

其经验对我们很重要：

- 严格侧面必须写明 90°、远侧手脚隐藏、脸为 edge-on，否则会重复 3/4；
- 每个 close-up 必须明确命名且声明只出现一次，否则会复制局部图；
- 盔甲/服装可以使用无脸黑色 mannequin，避免模型在各面板发明不同穿戴者；
- 网格本身是视频模型的弱点，必须禁止 panel bleed、重复、倾斜和阴影。

因此它更像“服装/装备结构检查板”，不是直接替代逐图 canonical reference。

### 2026-09-26 本地 CharacterSheet QuadView smoke

使用 `QuadView_krea2_v1.safetensors` 对 8 个已有正面锚点做了同条件静态测试：1536×1024、10 steps、CFG 1、Euler/simple、ref boost 1。8/8 成功，平均约 27.1 秒/张；输出均包含 face close-up、front、side、back 四栏，初检未见重复正面或第三主体。相比前一轮自由提示的 Krea2 双视图板，四视图槽位约束明显更强。

但这仍是一个组合图实验：面部特写和三张全身图共享一张画布，不能直接替换 `F0/W0 + H3 turnaround`。下一步应只在用户确认后测试 panel crop/放大、与 H3 ContactSheet/OrbitSheets 的同案例 A/B，以及把通过的独立视角写入 canonical manifest。

### 2026-09-26 DynamicCharacterSheet 本地 smoke

按官方结构化 prompt 格式测试 `DynamicCharacterSheet_krea2_v1.safetensors`：1536×1024、10 steps、CFG 1、LCM/simple、LoRA 1，8 个案例全部成功，平均约 27.1 秒/张。它确实能把内容扩展为 hero、turnaround、action、silhouette、expression/state、detail crops 等多个区域，身份和服装一致性保持良好。

限制也得到实测确认：版面内的英文标签和 metadata 文字大多是伪文字，部分视角标签会错位；动作和细节区域适合设计/QC，不适合作为直接的 canonical reference。因此当前分工为：QuadView 负责干净静态四视图，Dynamic 负责丰富设计资料板，H3 负责正式参考轨迹和视频视角。

### 2026-09-26 QuadView 三视图 prompt 实验

官方仓库没有 Krea2 专用 TripleView LoRA；但在同一 `QuadView_krea2_v1` LoRA 下，将触发词改为“front, side and back full body views only”，并加入禁止脸部特写、hero、动作、细节栏和第四视图的约束，东方女剑士测试成功生成恰好三栏。该能力属于 prompt-level 版式变化，不应等同于官方独立 TripleView 模式，仍需多角色复测。

随后用东方女剑士和冰狼复测两种三栏布局：`face close-up + front full body + back full body` 与 `upper-body front portrait + front full body + back full body`。4/4 成功，均去掉了侧面和第四栏；前后服装、发型/角、武器和背部轮廓保持可读。说明 QuadView 的第一栏内容也能通过 prompt 改变，但仍应作为组合图预览，单栏进入 canonical 前需裁切、放大和 QC。

进一步将画布扩为 1792×1024，并要求左侧脸部栏加宽、脸部放大，同时保持中间/右侧前后全身栏的原始窄长比例。东方女剑士测试成功，说明该非等宽布局也可以通过 prompt 稳定诱导；在批量采用前仍需用第二个角色复测。

随后在统一目录 `experiments/krea2_quadview_fixed_layout_batch_20260927/` 中保存全部布局 prompt、特征说明、manifest 和脚本，并以东方女剑士、红法师、矮人工程师、冰狼测试当前布局。4/4 成功；1792×1024 的加宽左脸 + 窄长正面/背面布局对人类和怪物均保持可读，暂列当前 QuadView 静态预览候选。

2026-09-27 又将四种已保存布局对同一批四个角色全部生成，形成 16 张比较矩阵。所有任务成功；按角色和按布局的 contact sheet 与原图均放在同一实验目录的 `all_layouts/` 下，供人工选择，不改变 canonical reference 规则。

### 半身/脸部 panel 版式复核

社区方案通常把 portrait/bust 定义为“头部 + 双肩 + 上躯干”，而不是在脖子或单侧肩膀处截断；TurnSheet 将 character portrait 描述为 head、shoulders、torso 的 medium shot，动画角色表也用肩膀、肘部、腰部等水平 landmark 检查比例。多视角 AI 方案则倾向把 face close-up 与 full-body turnaround 分开，避免一个 panel 同时承担脸部识别和服装展示。

因此当前保存两种 active QuadView 配置：

1. `face_front_back_focused_head`：左栏聚焦头部，保留发际线、耳朵、颈部和双肩顶部作为身份/服装锚点，不扩展到完整半身。
2. `upper_front_back_full_upperbody`：左栏完整显示头部到腰/中躯干，双肩、衣领、上胸、上臂、肩甲/袖子/背带必须完整可见。

两者共用 1792×1024、左 43% / 中 28.5% / 右 28.5% 的无留白版式；S/side 配置暂缓。参考：[TurnSheet](https://turnsheet.ai/)、[RetroSupply character reference sheet guide](https://www.retrosupply.co/blogs/tutorials/character-reference-sheet)、[InVideo character reference pose guide](https://invideo.io/faq/what-is-the-best-pose-for-a-character-reference-sheet)、[YouMind multi-angle layout example](https://youmind.com/prompts/character-reference-sheet-layout-20199)。

### 2026-09-27 active 布局四角色 preview

对四个角色各生成两张 active 布局预览，共 8 张，均为 `1792×1024`：`face_front_back_focused_head` 与 `upper_front_back_full_upperbody`。8/8 成功，单张约 30.1–30.8 秒。脸部布局四个角色均形成目标三栏；上半身布局中东方女剑士、矮人工程师、冰狼通过初检，但红法师额外出现侧面栏，形成四栏，标记为 `layout drift / review`。结果位于 `experiments/krea2_quadview_fixed_layout_batch_20260927/active_preview/`，等待人工检查。

这次结果只验证 prompt/layout 的可用性，不改变 canonical reference 规则：组合图仍是预览和 QC 索引，不能直接替代 H3 turnaround 或进入 `F/W/WB/S/Q/B` manifest。

随后将 `face_front_back_focused_head` 调整为左 52% / 中 24% / 右 24%，并强化唯一正面、唯一背面及禁止第二背面的约束。单张版式 preview 显示脸部明显增大，前后全身栏仍完整；该结果尚未进行四角色批量复测。

### 2026-09-27 社区使用经验复核：QuadView 的真实控制边界

本轮复核了官方 Hugging Face 模型卡与 workflow、作者 demo、ComfyUI Wiki、Tensor.Art 模型页及社区整理文章。资料来源：[官方 CharacterSheet 模型卡](https://huggingface.co/Alissonerdx/CharacterSheet)、[官方 QuadView workflow](https://huggingface.co/Alissonerdx/CharacterSheet/blob/main/workflows/QuadView_krea2_v1.json)、[作者 demo](https://huggingface.co/spaces/Alissonerdx/charactersheet-lora-demo)、[ComfyUI Wiki 介绍](https://comfyui-wiki.com/en/news/2026-07-31-charactersheet-multiview-loras)、[Tensor.Art 页面](https://tensor.art/models/1030040032741713875)。

资料与本地实测形成以下边界：

1. `QuadView_krea2_v1` 的训练目标是脸部特写 + 正面/侧面/背面全身，推荐 Krea2 Turbo `1536×1024`、10 steps、CFG 1、Euler/simple、LoRA strength 1.0。
2. Prompt 可以改变视图语义和视图数量；本地已经验证四视图可压缩为三视图，也能把第一栏改为脸部或上半身。官方没有提供栏位宽度、面板比例或空白区域参数。
3. 官方 workflow 的默认 prompt 很短，主要作用是触发 CharacterSheet 结构；额外 prompt 可补服装、姿势、材质和背景，但不能视为自由排版指令。
4. 当前 `43/28.5/28.5`、`52/24/24`、`60/20/20` 的本地结果都回到接近等宽栏，说明 LoRA 的布局先验强于比例 prompt。所谓“左栏变宽”更多是内容占比或脸部尺度变化，不是稳定的像素级栏宽变化。
5. 官方限制与本地重复背面、额外侧面栏现象一致：视角之间的脸、服装、配件和比例不保证一致；侧面和背面可能需要多次生成或人工清理；复杂配件、非对称服装和非人类角色更容易失败。

因此当前 [定论候选] 是：QuadView 应定位为“多视角身份/服装关系生成器”，而非“面板排版器”。基础流程先接受其近似等宽的三/四视图组合图，再对脸部、正面、背面进行裁切、放大和重新合成；不要继续把精确 `60/20/20` 交给 prompt。当前基础 60/20/20 preview 尚未由 Sean 验收，也未提升为 active canonical 布局。

### 5. Krea2 CharacterSheet LoRA

`Alissonerdx/CharacterSheet` 提供：

- `TripleView_klein9b_v1`：front / side / back；
- `QuadView_krea2_v1`：face close-up / front / side / back；
- `DynamicCharacterSheet_krea2_v1`：实验性实体板，包含 hero、front/side/back、动作、剪影、表情和细节。

Krea2 QuadView 的推荐起点也是 1536×1024、10 steps、CFG 1；但模型卡明确写出视图一致性不是 100%，侧面和背面可能需要重复生成或手工清理。因此它值得做静态 A/B，但不能据此假设会自动解决本轮 eastern/red mage 的结构错位。

#### 2026-10-22 Turbo QuadView 正面留空脸试跑

将官方 UI workflow 复制为本机 Turbo 版本，保留模型卡原句作为通用触发提示，只追加面板级规则：左侧脸部特写与第三栏侧面显示正常五官，第二栏正面全身留空脸；角色专属提示只补充辨识性外观和签名物品。对剑士、红法师、矮人工程师三张参考图做同 seed 两轮对照。首轮把特写脸也画空，第二轮按“第 1/2/3 栏”写清面板归属后，三例均正确显示特写脸、正面留空、侧面保留脸。四栏结构三例均正确。

配件仍不稳定：红法师法杖在两轮都缺失；矮人工程师背部铜齿轮包未稳定还原。Turbo 运行器 wall time 第二轮约 21.1 秒/张（包含提交和轮询，不等同纯采样时间）。这验证的是 prompt 对脸部 panel 的局部控制，不是 H3 下游或 canonical reference 验收。输入、prompt、seed、两轮图和实际 workflow 见 [`krea2_quadview_turbo_fourview_20261022`](../experiments/krea2_quadview_turbo_fourview_20261022/REPORT.md)。

#### 2026-10-22 清晰锚图下的三栏/四栏配对测试

用户指出装备一旦进入多视图就容易缺失、换手或错位；本轮先用 Krea2 Turbo + Jibs 生成三张细节醒目的正面锚图（红鞘长剑/指南针胸针、月牙长柄斧/吊坠、双青色药瓶/匕首/太阳胸饰），确认物品清晰后，再对每个锚图使用相同 seed 和 QuadView 设置配对生成：三栏正面/严格侧面/背面，对比四栏脸特写/正面/侧面/背面。除布局和正面留空脸约束外，条件相同。

三栏输出有 2/3 遵循严格三栏，炼金术士多出一个重复侧面栏；四栏布局为 3/3 正确。风暴信使的红鞘长剑在两者中都保持；沙漠守卫长柄斧在三栏背面换边、侧面不清楚，在四栏侧/背也不稳定且被放大挤进特写；炼金术士的药瓶与匕首在正面醒目，但侧面只露出一瓶、背面消失。清晰锚图没有消除物品跨视角缺失问题。

因此少一个 panel 可能让部分物品更突出，但目前不能归纳为更高控制力。旧版三栏“脸特写/正面/背面”曾在 10/10 样本保留标志装备，却牺牲侧视图；本轮真正的正/侧/背布局有一例结构失败。两种三栏布局不应混称为同一验证结果。报告、逐图 prompt/seed、参考图与输出见 [`krea2_quadview_items_3vs4_20261022`](../experiments/krea2_quadview_items_3vs4_20261022/REPORT.md)。

### 6. Flux Kontext / CharaConsist

`reverentelusarca/kontext-turnaround-sheet-lora-v1` 用 Flux Kontext LoRA 直接生成 5/6 视图静态 sheet；其 prompt 要求 front、3/4 left、left profile、back、right profile、3/4 right。它与当前 Krea2 双栏测试的思路接近，但需要另一个基础模型生态。

`Comfyui_CharaConsist` 是 training-free attention-cache 方法，支持 FLUX、Chroma、Qwen-Image 和多主体，重点是多张独立生成之间的 subject attention 一致性，不是专门的 front/back/side turnaround。可作为未来跨镜头一致性旁支，不应混入本次 H3 reference 主流程。

## 建议的恢复顺序

1. **先恢复 OrbitSheets/H3 硬切 5 视图辅助流程**：一个角色一张主图，输出独立 full/face/left/right/back 图，按内容聚类和 distinct-view 报告验收。
2. **再比较 H3 ContactSheet 五槽**：同一输入、同一角色、同一 seed，与 OrbitSheets 比较身份、肩甲、发型、背部装备和视角覆盖。
3. **若 clothing 结构仍不稳，再跑 H3 Edit 的 clothing 6 views**：固定头到膝盖尺度，专门验证肩甲、领口、腰带和饰物位置。
4. 组合图只作为 index/QC，不直接进入 canonical；最终仍按 `F0/W0/WB + H3 通过帧 → F/WB/S/Q/B` 组织。

这意味着：我们之前把五视图 ContactSheet 作为主流程辅助的方向是正确的；需要修正的是它的定位——它不是“生成一张完美三视图图片”，而是“在同一 H3 条件轨迹中生成并抽取一组相互约束的视角”。

## Sources

- [matlod/minimax-h3-turnaround](https://huggingface.co/matlod/minimax-h3-turnaround)
- [ComfyUI-H3-ContactSheet](https://github.com/matlowai/ComfyUI-H3-ContactSheet)
- [ComfyUI-OrbitSheets](https://github.com/lumos675/ComfyUI-OrbitSheets)
- [ComfyUI-MiniMax-H3-Edit](https://github.com/ethanfel/ComfyUI-MiniMax-H3-Edit)
- [JahJedi/MiniMax-H3-Character-Sheet](https://huggingface.co/JahJedi/MiniMax-H3-Character-Sheet)
- [Alissonerdx/CharacterSheet](https://huggingface.co/Alissonerdx/CharacterSheet)
- [Flux Kontext turnaround sheet LoRA](https://huggingface.co/reverentelusarca/kontext-turnaround-sheet-lora-v1)
- [ComfyUI-CharaConsist](https://github.com/thatname/Comfyui_CharaConsist)
