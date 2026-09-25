# H3 社区与创作者资料

本文件只记录来源中明确出现的配置、时长、效果和失败，不将标题中的宣传语直接当作结论。

## 1. 4090 与本地速度

### InfiniteTalk：RTX 4090 基线

InfiniteTalk 官方实现基于 Wan2.1 I2V 14B，支持 480p/720p、I2V/V2V 和 streaming 模式；单 GPU 示例使用 40 steps。官方明确提示：单图 I2V 约 1 分钟后更容易发生色彩漂移，V2V 更适合保留原有动作和机位。[官方仓库](https://github.com/MeiGen-AI/InfiniteTalk)

公开的 4090 实测不能合并成一个固定速度结论：

- RTX 4090 24GB、720p、10 秒，创作者报告约 5.8 分钟；[Matthew Hallett 实测](https://www.linkedin.com/posts/matthew-hallett-041a3881_now-that-my-comfyui-image-infinitetalk-activity-7375709977866457088-WyKk)
- RTX 4090、约 41 秒长片验证成功，但作者同时记录了后段背景一致性问题；其公开配置还给出 30–60 秒高质量档约 25–45 分钟，属于单作者环境数据，不作普遍保证。[LUTA 实测](https://note.com/luta_ai/n/ne0898fa5faf9)
- 社区反馈显示，关闭加速通常质量更好但速度显著下降；长片滑窗在完整步数下可能达到每窗口约 1 小时以上。[社区讨论](https://www.reddit.com/r/comfyui/comments/1n4aapy/infinitetalk_is_just_amazing/)

因此，4090 上 InfiniteTalk 的合理定位是：可运行、口型和长时 streaming 很有竞争力，但正式质量的时间成本可能很高；必须按 I2V/V2V、分辨率、steps、加速方式和上下文窗口记录，不能只写“4090 能跑”。

### Pedro Alonso：单 RTX 4090 故事书影片

[原文](https://www.pedroalonso.net/blog/minimax-h3-local-rtx-4090/)

- RTX 4090 24GB，主机内存 62GB；
- 1344×768；
- 5 秒视频；
- 12 turbo steps；
- warm 约 300 秒，cold 约 330 秒；
- 观察到耳朵抽动、光线变化、行走和首尾帧之间的动作过渡；
- 三张角色参考图时，三个角色在 124 帧中保持可辨识；
- 多人物场景出现参考脸污染群演的问题；
- 结构化 prompt 的视觉质量明显好于自由散文 prompt。

### Reddit：4090 Ref2VA 基准

[原文](https://www.reddit.com/r/comfyui/comments/1vlgh88/minimax_h3_runpod_gpu_benchmark/)

- 约 1MP、5 秒、未优化 Ref2VA INT8；
- RTX 4090 24GB：约 6 分 47 秒；
- 测试没有使用加速或优化；
- 更长时长的成本可能明显增加；
- 低分辨率适合作为草稿，但低于约 1MP 可能损失画质。

### Reddit：16GB 4090 Laptop

[原文](https://www.reddit.com/r/StableDiffusion/comments/1ve6lvr/minimax_h3_first_local_test_5_seconds_at_960540/)

- RTX 4090 Laptop 16GB；
- 960×540、5 秒、20 steps、Euler、SageAttention；
- 使用 pruned INT8 H3 和 NVFP4/AWQ 文本编码器；
- 完整生成约 182 秒；
- 包含模型加载、Video VAE 和 Audio VAE 解码时间。

## 2. 长片与连续角色

### 2 分 47 秒纪录片

[原文](https://www.reddit.com/r/comfyui/comments/1vknr0v/followup_from_a_5second_clip_to_a_247/)

创作者使用 RTX 5060 Ti 16GB，把 36 个片段组织成 2 分 47 秒纪录片：

- 多场景、一个持续角色、旁白、人物台词和群演；
- 使用 H3 Ref2VA、Turbo LoRA 和 1344×768 原生输出；
- 通过上一段尾帧作为下一段首帧做接缝焊接；
- 报告首帧锚定的 SSIM 约 0.89；
- 标点会影响停顿时长；
- 多人场景出现参考脸复制到群演身上的问题；
- 自动 sharpness / optical flow 不能完全代替人眼检查。

### 4 分 40 秒口型视频

[原文](https://www.reddit.com/r/comfyui/comments/1vozoru/minimaxh3_%EB%A1%9C%EC%BB%AC_5060ti%EB%A1%9C_4%EB%B6%84_%EB%84%98%EB%8A%94_ai_%EB%A6%BD%EC%8B%B1%ED%81%AC_%EC%98%81%EC%83%81%EC%9D%B4_%EA%B0%80%EB%8A%A5%ED%95%A0%EA%B9%8C_%EC%A7%81%EC%A0%91/)

- RTX 5060 Ti 16GB、系统内存 64GB；
- 34 个 8 秒、约 1MP 片段；
- 每段约 12–14 分钟；
- 使用 Audio Lock 和自定义节点按歌词分段；
- 报告口型准确率约 85%，部分片段仍不同步；
- 用参考图或上一段最后一帧维持连续性。

它证明 H3 可以通过工程编排做分钟级成片，但不能证明 H3 单次生成具备分钟级持续状态。

## 3. H3 长视频社区共识

社区长视频讨论中反复出现：

- 保存 video latent，而不是只保存 mp4；
- 保存 audio latent，减少多次 VAE 编解码造成的音频劣化；
- 传递上一段若干尾帧作为 context；
- 使用隐藏重叠，避免简单 crossfade；
- 保持 prompt、身份和音频时间轴。

[LongMedia 讨论](https://www.reddit.com/r/StableDiffusion/comments/1vr7t5n/comfyuiminimax-h3-longform-minimax-h3/)、[H3 latent continuation 讨论](https://www.reddit.com/r/StableDiffusion/comments/1vujv5t/updated-methods-on-getting-long-videos-in-minimax-h3/)、[H3 clip chaining 讨论](https://www.reddit.com/r/StableDiffusion/comments/1vhppmv/clip-chaining-for-minimax-h3-motion-and-audio-genuinely-continue-across-joins/)

## 4. 音频、口型和多人

- 有创作者使用 H3 参考音频和官方 `<d>` prompt，报告得到克隆声线与指定台词；
- 也有人认为参考音频只是声音/表演条件，不能可靠保留外部原音频；
- NativeAudioLock 能改善固定 vocals 的口型，但仍有约 85% 同步率的长片报告；
- 社区有人发现 ComfyUI 的 `<d>` token 处理问题会导致 gibberish，更新后改善；
- 多说话人音频实验报告三种声音可以工作，但标签顺序脆弱，且需要大量试错。

以上经验主要不是粤语专项验证。InfiniteTalk 开源实现使用 `chinese-wav2vec2-base`，官方论文和仓库没有给出粤语专项口型精度，因此粤语结果必须单独测量，不能从普通话结果外推。

[16GB 本地口型案例](https://www.reddit.com/r/comfyui/comments/1vix8l9/roman_street_walkandtalk_with_cloned_voice_exact/)、[对话 token 修复讨论](https://www.reddit.com/r/StableDiffusion/comments/1vxpbo1/minimax_h3_gibberish_fixed_i_found_the_cure/)、[多说话人 H3 音频实验](https://www.reddit.com/r/comfyui/comments/1vj8nyp/forcing_minimax_h3_to_generate_multispeaker/)

## 5. B站创作者资料

以下视频页面的简介、标题或章节包含 H3 数字人、音频、参考图和长视频工作流线索。部分视频页面当前存在 412 风控，字幕和评论尚未完整抓取，因此暂不升级为强结论。

- [H3 人物/场景/音频全能一致性](https://www.bilibili.com/video/BV1cYuL6uEzp)
- [H3 多图参考与提示词反推](https://www.bilibili.com/video/BV15xuA6WEcE)
- [H3 动作迁移 + 数字人 + 对口型](https://www.bilibili.com/video/BV1SLuS6mEb2/)
- [H3 音频研究、FL2VA/Ref2VA 对比](https://www.bilibili.com/video/BV1P5gs6TEF7/)
- [H3 无限数字人：上传音频、手动分镜、自动拼接](https://www.bilibili.com/video/BV1rzuJ6SEiD/)
- [H3 15 秒和多人问题实测](https://www.bilibili.com/video/BV1ryMf6dEF3/)

## 6. 社区对动态能力的评价

正面反馈集中在镜头运动、走动、转头、手势、环境互动和首尾帧动作路径。负面反馈集中在大动作导致的脸部漂移、手部变形、远景脸、群演身份污染，以及低步数错误配置导致的色偏、条纹、坏音频和语义混乱。

## 7. 本轮 B 站抓取与新开源证据

新版 `sources-run` 已抓取以下三个视频的简介、元数据和弹幕：

- [Motion Context 连续衔接实测](https://www.bilibili.com/video/BV1xs8w6fEhy/)：简介明确指向 Motion Context，并同时提供 FL2VA、Ref2VA 工作流；标题和简介涉及音频时间线延续、跨轮次 Latent 保存。
- [H3 两段式潜空间放大](https://www.bilibili.com/video/BV1aY8v6aEhk/)：简介描述低分辨率结构采样→3D latent upscale→高分辨率二次精修，并提到 3D 时空放大用于减轻闪烁。
- [InfiniteTalk 动作迁移教程](https://www.bilibili.com/video/BV1nkjy6gEfJ/)：是分 P 教程，简介信息主要是整合包和工作流宣传，未提供可核验的 4090 速度或粤语专项数据。

这三个视频均未返回可下载字幕；评论接口本轮因 B 站视频信息 API 超时未完成，因此不能把视频讲解细节或评论区经验升级成已验证结论。已获得的弹幕很少，主要是“拼接工具”“预览雪花”“手穿模”“慢放”等问题反馈，能作为风险线索，不能作为统计证据。

比 B 站教程更有部署价值的是 [Contex Loop 的音频与连续性文档](https://github.com/ethanfel/ComfyUI-MiniMaxH3-Contex-Loop/blob/main/docs/AUDIO_AND_CONTINUITY.md)：它区分 source reference、generated continuity、lock source audio，并支持把外部 source track 编码进 H3 的音频 latent、锁定音频而只让视频继续去噪；同时保留最终外部音轨。这为“顶级粤语 TTS 做母带，H3 负责视觉口型与表演”提供了明确的本地实现方向。

脸部后处理也已有针对 H3 的专用实现：[H3 FaceRefine](https://github.com/Carasibana/ComfyUI-H3-FaceRefine) 按帧跟踪人脸、裁切放大后让 H3 重绘，再合成回原视频；其文档特别提醒小脸问题取决于脸在画面中的像素大小，720p 本身不一定解决。latent 放大方面，[H3 Latent Upscaler](https://github.com/LBH-123-AI/Comfyui_Minimax_h3_latent_Upscaler) 提供 24 通道、2D/3D 两种路径，并保留时间维；但其 issue 已出现 16GB 显存二次采样 OOM，时间分块和 overlap 是必要的工程问题。

另检索到一条直接针对长口播的 B 站线索：[Minimax H3 长口播-数字人一键生成](https://www.bilibili.com/video/BV1DubZ6HEs3/)，时长约 7 分半；页面没有可下载字幕，简介也没有公开步数、显存或接缝指标，只能列为待看样本，不能证明连续口播质量。
