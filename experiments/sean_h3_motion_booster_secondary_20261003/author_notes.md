# Motion Booster 作者说明复核

Owner: Sean。2026-10-03。外部作者陈述与本地实测分开记录，不改变生产配置；本轮仅调研，没有安装其他LoRA或改工作流。

用户当前反馈：0.7动作有穿帮，1.0动作还好。反馈指向人物动作质量，而非飘带独立动态；没有多seed或重复执行来确认故障机制。

## 对应版本的关键限制

本机文件对应 [V0.2 REF2VA / 3246346](https://civitai.com/models/2840146?modelVersionId=3246346)，作者FourBunny。作者明确说明这版原生Ref2VA训练提高参考角色一致性，但会牺牲部分画质和整体稳定性；也不意在取代普通V2在FL2VA/Ref2VA Hybrid上的使用。此前回答只强调动作增强，没有充分说明这个稳定性代价。

这使LoRA影响本例穿帮成为合理怀疑，但作者没有解释我们这一条的故障点，也未发现针对高权重黑边或近方形内容的说明。作者的稳定性陈述不能替代因果验证。

[V2总页](https://civitai.com/models/2840146?modelVersionId=3228867)定位是人体动作节奏、接触回弹及身体次级跟随，并加入动作音频。家族说明建议`dynv2`、0.6–0.8、从0.7开始，强调I2V与正确起始姿态；REF版未找到独立的数值推荐。1.0超出上述推荐范围，但不代表每条必然更差。

旧V1公开说明是20段视频、1600步的概念验证，不能套在V2或REF版。当前REF文件头实际为ai-toolkit 1.18.2、step2000、epoch18、base minimax_h3_ref2va。元数据不能还原完整数据集、分辨率分布或训练配置，未定位到该REF版本公开的完整训练代码/数据集。

## 版本与工作流差异

标题的[ANIME Edition / 3299686](https://civitai.com/models/2840146?modelVersionId=3299686)是独立动漫素材训练版本，作者强调姿态跳变、快速反转、延迟跟随及动漫动作语言。它不是本机的REF文件；当前测试不能被称为Anime版测试，也不能直接套用其风格建议。

作者当前另推[BUNNY SelfLift Hybrid工作流](https://civitai.com/models/2956102)，依赖JR、SelfLift、SolAttn和T8等节点。其混合底模/渐进分辨率采样链路与本轮native Ref2VA标准20步不同。上游[JR Hybrid说明](https://github.com/Goldlionren/ComfyUI_JR_MiniMaxH3Node#hybrid-loader-与模型-patch-链)将混合定义为参数来源策略；[SelfLift说明](https://github.com/facok/comfyui-SelfLift#selflift-progressive-sampler-minimax-h3)明确H3适配是实验性质，采样器限定Euler。不能仅把本轮res_multistep工作流换一个名字就视为作者方案。

## 更接近“穿帮”的作者项目

[BUNNY General Motion Continuity Repair / 2890788](https://civitai.com/models/2890788)针对动作断链、异常肢体轨迹、动作协调与提示词遵循；V2特别强调旋转、翻转和姿态恢复。作者描述筛选100段片段、人工逐帧复核加AI复核，并建议单独使用约0.9，二采约0.2–0.3。这些是该修复LoRA的作者建议，不能当作Motion Booster权重建议或本机已验证结果。V2公开文件名Motion_Repair_V2.safetensors；原生REF兼容与本机效果尚未验证。

因此若后续目标是减少转身穿帮，值得单独验证这条修复路线。应先确认适用底模与兼容性，再用有明确故障的同参考/同prompt/同seed基线对比，避免初次就叠多个LoRA而失去归因。

## 检索覆盖

已直接读取Civitai官方API的当前模型/版本正文及作者相关模型正文；核对本机safetensors元数据；Web与Exa用于线索，GitHub核对作者依赖节点的上游说明。不是仅靠聚合摘要。选定REF版本API可访问的三个示例都是视频，meta仅含prompt，没有steps/sampler等参数。RunningHub作者工作流返回401，需要登录，本轮未取得完整工作流JSON；Civitai评论与示例视频内容尚未逐条复核。未找到可解释本例穿帮/黑边的作者技术报告。技术快照见author_details.json和author_related_models.json，省略成人示例prompt。本轮20步是本机原生基线，不能称为完整复现作者示例配置。
