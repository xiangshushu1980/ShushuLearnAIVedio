# Breeze TTS 2 情绪控制 POC

目标：为个人视频账号建立“稿件情绪 → Breeze 指令/参数”的可复用映射。

测试约束：固定同一中文稿件、同一模型、同一参考音色（Voice Clone 阶段）、同一 seed；每次只改变情绪和强度。当前 Voice Clone 仍待用户提供本人授权录音，本阶段可先用 Voice Design 验证指令行为。

## 第一轮矩阵

四类情绪：叹息、肯定、取消/否定、质疑。

三档强度：low / medium / high。

记录字段：文本、instruction、cfg_scale、seed、vocal event、生成时长、听感、是否唱腔、是否需要重生成。

## 当前保守基线

- 普通中文口播
- 不加 inline vocal event
- `cfg_scale=1.5`
- 固定 seed
- 指令只描述“自然、清楚、正常句子语调和自然停顿”

已知现象：强情绪词“明亮/感染力”与 `[笑]` 可能把中文口播推向唱腔，因此情绪应从低强度逐步增加。

