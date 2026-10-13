# Krea 2 参考一致性：外部评价摘记

> Owner: Sean。检索日期：2026-10-01。此处整理官方产品说明、社区节点作者说明和使用者帖子；不是独立 benchmark。

## 检索结论

公开反馈与本实验相符：Krea2 的单图观感、风格控制评价较好，但普通参考图不应被当作严格的角色或场景锁定。人物脸、服装、物品会漂；场景参考较擅长传递色彩、材质、气氛与元素，不保证复现同一空间。社区常以角色 LoRA、逐轮编辑、低 denoise 或视频/3D 重建补足。

证据要分管线看：本实验使用 ComfyUI `ComfyUI-Krea2-Reference` 节点和社区 Reference LoRA。它不同于 Krea 网页的官方 Style Reference / Moodboard，也不同于社区 `Krea2 Identity Edit` LoRA。不同节点、LoRA、分辨率、prompt、参考图裁切会显著改变结果。

## 一手说明与社区实测

1. **Krea 官方把常规 image reference 定位为 style/mood 控制。** 官方 technical report 描述的是通过 style-reference system 注入一张或多张图的风格/氛围，并控制风格强度；官方 Style References 指南称强度高时可能压过主体，推荐将 S-Refs 用于单次精确风格迁移，多图探索可用 moodboard。Krea 官方将可复用角色一致性主要导向专门训练的 Character LoRA，而不是宣称一张普通参考图能锁定身份/场景。[Technical Report](https://www.krea.ai/blog/krea-2-technical-report) · [Style References](https://www.krea.ai/blog/style-references-krea-2) · [Krea 2 LoRA Training](https://www.krea.ai/blog/krea-2-lora-training)

2. **本实验使用的社区 Reference 节点作者也列出类似失败边界。** README 支持最多 4 张参考图，靠 prompt 将 `character1..4`、`style1..4` 绑定角色；作者称 `layout_split=0.25` 能减少拼板，并明示角色设定表可能生成多个克隆、style reference 会带入原角色、两张参考组合效果有限。作者也建议单姿势图。我们的复现里 0.25 让单脸及脸+服装达到各 2/2 单主体；全四参考仍 0/2 单主体，场景两参考也只有 1/2 干净。[ComfyUI-Krea2-Reference README](https://github.com/KonokoAz/ComfyUI-Krea2-Reference)

3. **社区对场景几何锁定偏保守。** r/comfyui 有人询问能否跨不同人物/角度保持同一家咖啡馆；回复直言目前很难做到高一致性，并转向视频帧/3D 等办法。讨论只有少量投票，属于使用者反馈而非系统评测。[Reddit: consistent environment/location](https://www.reddit.com/r/comfyui/comments/1wi7ndx/krea_2_is_it_possible_to_keep_a_consistent/)

4. **Identity Edit 的社区模型卡承认人物与服装边界。** 该项目建议 Turbo 8–12 steps，并列出脸部几何会向平均比例回归、双人脸会漂向彼此、换装命中不稳定、编辑可能改变画面色调等限制；也说明高分辨率有重复/泄漏风险。它是社区编辑 LoRA 的说明，不能直接等同本实验的 Reference LoRA 结论，但说明 Krea2 生态内不同“参考”路线也需要折中。[Krea 2 Identity Edit model card](https://huggingface.co/conradlocke/krea2-identity-edit)

5. **其他创作者给出混合评价。** Aurel Manea 记录自己试过四格角色参考流程后，因分辨率/制作限制转向每张图重复完整文字角色描述；他报告文本方案在自己的样本中保持角色相似。此结论依赖密集文字重述，不证明引用同一参考图能锁几何。[Aurel Manea: consistency by description](https://aurelm.com/2026/07/02/krea-2-and-maybe-others-infinite-scene-images-with-consistancy-using-description-comfy-ui-workflow/)

## B 站命中与限制

- 用户先前给的两个视频抓取到标题和简介：`BV1CRbQ6tESj`《图像编辑流+397种风格扩展》、`BV1kHTQ6vEuf`《全攻略/模型盘点/风格 LoRA/动漫方案》。匿名抓取无可用字幕，因此只作教程线索，不把视频正文当成已核实的评价。
- 站内搜索命中 `BV1fHGN62EmN`《Krea-2也能图生图改图，支持多图参考，人物一致性保持不错》；标题是正向自述，但没有拿到字幕/方法细节。
- 也命中 `BV1X2TW6CE2M`《Krea2没有稳定参考图？用LoRA解决角色一致性》；简介主张角色 LoRA 工作流能改善变脸/复杂背景重复人物，但这同样是教程作者的推广性摘要，不是无偏对照。
- 因视频字幕不可匿名读取，正反视频标题只能说明社区叙述并不一致，不能用于效果量化。

## 外部检索覆盖

已查 Krea 官方博客、ComfyUI 社区节点 README、Hugging Face 模型卡与讨论、Reddit、B 站标题/简介，以及 Tavily / Exa 聚合搜索。未找到对 Krea2 普通多参考角色与场景几何保持的公开、可复现 benchmark；论坛样本很少，容易受具体 workflow 影响。YouTube 与 X 未深入核查。
