# H3 数字人未完整解析资料

本文件只保存已经发现但尚未完整阅读、下载字幕/评论、复现实测或核验参数的资料。这里的内容不能直接当作结论。

## 1. B站待深挖

本轮已用新版 `sources-run` 抓取三条核心视频的元数据和弹幕；字幕均不可下载，评论 API 超时。后续若要继续挖，优先补登录态评论/字幕，而不是继续扩大同类教程数量。

- [H3 人物/场景/音频全能一致性](https://www.bilibili.com/video/BV1cYuL6uEzp)：页面显示约 12 分钟，章节包含两种音频参考和本地测试；尚未完整解析字幕与评论。
- [H3 多图参考与提示词反推](https://www.bilibili.com/video/BV15xuA6WEcE)：页面简介含分段队列导演台；尚未核实实际工作流是否为本地 H3。
- [H3 动作迁移 + 数字人 + 对口型](https://www.bilibili.com/video/BV1SLuS6mEb2/)：尚未解析动作迁移节点和口型路径。
- [H3 音频研究、FL2VA/Ref2VA 对比](https://www.bilibili.com/video/BV1P5gs6TEF7/)：需要完整查看其对 FL2VA、Ref2VA、IndexTTS 和 Audio-T8 的实验条件。
- [H3 无限数字人：上传音频、手动分镜、自动拼接](https://www.bilibili.com/video/BV1rzuJ6SEiD/)：需要核实其“无限”究竟是首帧拼接、latent context 还是在线服务。

B站部分页面当前返回 412，字幕、评论和弹幕尚未完整抓取，因此暂不对创作者观点做强归纳。

## 2. 国外视频待深挖

- YouTube 上的 H3 ComfyUI 教程、4090 实测和 long-form chaining 视频：目前不少只返回标题或推荐卡片，尚未获取完整字幕和评论。
- Reddit 帖子中挂载的视频：尚未逐个下载视频并核对画面是否与文字描述一致。
- H3 社区创作者的 X/Discord 讨论：目前只使用公开可访问页面，未将登录态社区内容作为事实来源。

## 3. 需要后续核验的开源方向

- `ComfyUI-MiniMax-H3-LongMedia` 的实际 latent/context 传递方式、音频是否保留在 latent 层，以及长片后的音频衰减；
- `ComfyUI-H3-Motion-Context`、T8 Audio、H3 Continuation 系列之间的输入输出契约；
- H3 Turbo LoRA 不同版本、采样器和 audio steps 的质量差异；
- NativeAudioLock 在普通话、快速语速、多人轮流讲话和混音条件下的真实同步率；
- H3 FaceRefine 对小脸、侧脸、说话嘴部和身份 embedding 的实际增益；
- H3 社区许可证在不同业务主体和部署地区下的商业适用性。
- H3 本地 latent 是否能被线上 H3/API 直接接收；若不能，需区分“帧/视频级联动”和“latent 级联动”；
- 全精度 H3 分片在 30–60 秒粤语口播中的速度、显存峰值、音频连续性和身份收益；
- 同一粤语 TTS、同一角色参考下，H3 MC 与 InfiniteTalk I2V/V2V 的盲评差异。

## 4. 未确认的说法

以下表述在社区中出现过，但缺乏统一、可复现证据：

- “H3 可以无限时长一次生成”；
- “H3 原生参考音频就是 exact audio”；
- “某个 Turbo LoRA 可以无损四步完成视频和音频”；
- “8GB 显存达到 4090 质量”；
- “多人对谈已经稳定可商用”；
- “所有 H3 长片都不需要人工接缝处理”。

InfiniteTalk 的“支持粤语/任意语言”也暂不视为开源本地模型的已证事实：开源实现的音频编码器和公开评测没有给出粤语专项结果；商业 API 页面中的多语言宣传需单独核验。

在补齐原始 workflow、模型版本、显存、系统内存、分辨率、steps 和输出样本之前，这些说法均保持未确认状态。
