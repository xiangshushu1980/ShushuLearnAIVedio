# H3 数字人长视频路径测试矩阵

更新时间：2026-09-01。统一硬件为 RTX 4090 24GB；测试原则是单队列、ComfyUI 独占 GPU、同一角色图和同一外部语音。`已跑` 只表示有本机产物或本轮实测，不代表已经完成正式粤语验收。

| 路径 | 作用 | 本机状态 | 当前结论/下一步 |
|---|---|---|---|
| 原生 H3 Ref2VA + 参考音频 | 单段人物/声音/动作生成 | 已跑 | 本轮首段 5.167s 成片，768×448，32kHz 双声道；需换入真实 20s 粤语母带做正式口型验收 |
| Motion Context latent chain | video/audio latent 跨段续接 | 已跑 | 本轮第二段成功，22 帧 + audio 24，Trim 后 4.25s；seam corr 0.920，lag trend 0.02ms，暂无冻结 |
| NativeAudioLock | 外部 vocals 锁入 H3 audio latent，仅视频继续去噪 | 已安装/工作流可用 | 尚未用正式母带跑独立 A/B；下一批与“参考音频但不锁”对照 |
| FaceRefine rect | 小脸跟踪、局部 H3 重绘、回贴 | 已安装/历史试过效果不好 | 当前不纳入基础链；仅作为基础链稳定后的升级方案 |
| FaceRefine + SAM | 更精细人脸 mask | 已安装示例，缺 Impact/SAM 依赖核验 | 暂停；不影响当前长视频路线 |
| 首尾帧/普通帧链 | 画面接缝/动作基线 | 历史已跑 | 只能做辅助基线；不能替代 latent MC 的音画连续性验收 |
| MotionCache / CondCache / Turbo | 加速/条件缓存 | 已安装，历史有速度/音质对照 | 数字人正式链默认关闭 MotionCache/Spectrum/Turbo，先保证音频和口型；完成质量基线后再做单变量加速 |
| LongMedia / Context Loop / H3 Extender / Motion Director | 自动时间线、多片段编排或封装 | 未安装 | 不与现有 MC 重复安装 patch；等核心路径通过后，择一做流程层对照，不当作独立生成引擎 |
| InfiniteTalk | 长时音频驱动保底基线 | 调查确认 4090 较慢 | 优先级靠后，不作为当前基础方案 |
| LongCat Avatar | InfiniteTalk 后继者/本机备选 | 历史实测本机很慢 | 优先级靠后，不投入当前长视频主线 |

## 当前已产物

- 首段：`/home/sean/projects/ComfyUI/output/video/h3_avatar_smoke/avatar_seg1_audio_ref_00001_.mp4`
- 第二段 MC：`/home/sean/projects/ComfyUI/output/video/h3_avatar_smoke/avatar_seg2_mc22_retry_00001_.mp4`
- 首段 AV latent：`/home/sean/projects/ComfyUI/output/h3_avatar_context/clip_00001.safetensors`
- 第二段未裁剪音频：`/home/sean/projects/ComfyUI/output/video/h3_avatar_smoke/avatar_seg2_mc22_retry_untrimmed_00001.flac`

## 下一批正式测试

1. 登记真正的 20 秒粤语母带及逐字稿 hash/时间轴；当前冒烟音频只有约 2.6 秒，只做链路验证。
2. 同一输入跑 `5+5+5+5` 普通拼接、`10+10` 普通拼接、`5+5+5+5` MC、`10+10` MC、`15+5` MC。
3. 每个 MC 版本固定 `context_length=22`、`audio_context_length=24`，另做 `context=5/39` 和 `audio=0` 单变量对照。
4. 选择最稳定片段做 NativeAudioLock A/B；高清、FaceRefine、InfiniteTalk、LongCat 均不阻塞基础链。
5. 通过口型、身份、接缝和声音检查后，优先实测 8/10/15 秒 chunk，再跑 30/60 秒链，最后线性估算并实测 3min。
