# T-comfy-ops-31｜H3 Extender 2.0 数字人连续性验证

## 状态

- 任务线：`comfy-ops_extender`
- 项目：`comfy-ops`
- 认领日期：2026-09-03
- 当前阶段：已认领，准备开展环境/节点与最小验证矩阵检查

## 任务目标

评估并实测 ComfyUI MiniMax H3 Extender 2.0，针对 Motion Context 连续跳帧与累计变形问题，先在 RTX 4090 本地完成小规模 4 段×5 秒验证。重点覆盖 FL2VA 多段、动态图片 Guide、视频/音频参考、项目恢复、逐段颜色校正，并比较：纯 MC、MC+主播身份图、MC+身份图+上一段视频/音频参考。检查第 3/4 段的脸部身份、口型、服装、背景和音频对齐；暂不自动扩展到 Director/GuideMaster。

## 工作日志

- 2026-09-03：完成任务认领，建立本任务进度文件。共享状态已写入；工作区存在其他任务的既有改动，后续仅修改本任务范围内文件。
- 2026-09-03：按 `sources` skill 调研。有效主线为官方 ComfyUI H3 文档与 `tritant/ComfyUI_MiniMax_H3_Extender` 仓库；B 站关键词检索未命中相关 H3 Extender 经验。仓库当前 HEAD 为 `d749e68`（版本 2.3.3），包含 2.0 的 FL2VA、速度/显存优化、项目恢复/预览恢复/连续性缓存，以及后续动态 FL2VA Guide、视频/音频参考、逐段颜色校正和 Full Batch。
- 2026-09-03：已将 Extender 仓库克隆至 `/home/sean/projects/ComfyUI/custom_nodes/ComfyUI_MiniMax_H3_Extender`；仓库自带 3 份工作流。安装说明仅声明依赖 `imageio-ffmpeg`，需重启 ComfyUI 后节点才会加载。
- 2026-09-03：只读资源检查确认 H3 FL2VA/Ref2VA diffusion、Qwen3-VL H3 text encoder、视频/音频 VAE、PDD 和相关 LoRA 均已在本机；无需重复下载大模型。ComfyUI `/queue` 当前为空，但 4090 仍占用约 23.0/24.6GB，且存在计算进程/ComfyUI 服务，因此暂不重启、不提交推理任务。

## 证据与结论

- 资料经验：Extender 建议在每个 clip prompt 开头重复 `subject_definitions`，固定 `<Picture N>` 与人物/环境角色；视频参考应提供原始 FPS，节点会重采样到 H3 要求的 24fps；配套视频音频可用于 timing/lip-sync 引导。
- 资料边界：官方/仓库文档说明了功能与输入约束，但没有给出 RTX 4090 上 4 段×5 秒的可靠速度、显存或第 3/4 段身份保持实测，因此这些必须等本地资源释放后验证，不能把文档能力描述当作效果结论。

## 阻塞与下一步

- 下一步：等待并复查 GPU 计算进程、显存和 ComfyUI 队列；仅当确认资源释放后，重启 ComfyUI 使节点加载，再导入仓库工作流并做不超过 4 段×5 秒的最小矩阵。
- 当前阻塞：GPU 显存/计算资源仍被占用；队列为空不足以证明可安全开始。

## 2026-09-07 交接：从 Ref2VA+MC 基线进入 Extender 2.0 矩阵

- T-comfy-ops-28 已完成中文 Breeze→H3 的 30 秒连续数字人实验：FL2VA+PDD+MC 和 Ref2VA+MC 均能生成三段并拼接；初版 Ref2VA 仅使用 `ref_audios`，用户确认口型没有对上，不能作为口型结论。
- 已补跑有效组合 `Ref2VA + 固定身份图 + NativeAudioLock + Motion Context`，A/B/C 全部成功；严格 240F/段拼接后产物：`/home/sean/projects/ComfyUI/output/video/h3_avatar_zh_breeze_ref2va_audio_lock_mc_30s/joined_30s_master_audio_timeline_fixed.mp4`。
- 用户当前观察：上一版 Ref2VA 无音频锁存在口型问题；当前需要同时解决“接缝跳动”和“身份/后段漂移”，不能简单去掉人物参考图。
- 本任务下一步按原计划执行，不把“最后一帧作为 Picture 2”当成既定结论：Extender 2.0 做 4 段×5 秒最小矩阵，比较纯 MC、MC+主播身份图、MC+身份图+上一段视频/音频参考；重点看第 3/4 段身份、口型、接缝和累计变形。
- ComfyUI 已确认加载 `MiniMaxH3Extender` 节点；下一会话可在资源确认后直接导入官方 `Workflow/MiniMax_Extender_video_refs.json`，优先使用社区原生视频参考/配套音频路径。

## 2026-09-07 实测：Extender 2.3.3 最小链

- ComfyUI 持久启动后，`MiniMaxH3Extender` 与 `MiniMaxH3MotionContextDiskFinalDecode` API 契约加载正常；当前服务使用 `--enable-assets`、SageAttention 关闭。
- 新增 `tools/t31_extender_runner.py`，使用本机 `input/start/alya_768.png` + `input/test/alya_5s.mp4`，修正当前磁盘实际模型名 `qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors`，提交 API 格式工作流。
- 单段基准提交成功：`ref2va`、4 steps、0.40MP，自动分辨率 `640×640`，5.167s，生成 H.264/AAC MP4。
- 四段链提交成功：`full_batch`、4×5s clip、固定身份图 + 1 个视频参考 + Motion Context；Extender 状态 `cached 4/4`、`generated 2,3,4`，最终 430 frames / 17.917s，文件：`/home/sean/projects/ComfyUI/output/T31_extender_video_ref_chain4_00001.mp4`。
- 日志记录三处接缝均自动 `seam shift=-1` frame；nominal jump ratio 分别为 `2.108 / 1.784 / 2.153`，这些是节点接缝选择的图像差异代理，不等同于主观质量评分。
- 抽查首帧、各接缝前后及末帧：人物脸、发型、校服、体态与夜景道路背景保持稳定，未见明显身份漂移或大幅接缝跳变；本次素材为无音轨视频，不能作为“配套视频音频参考”结论。

## 当前边界

- 已验证：Extender v2.3.3 节点加载、参考图导入、视频参考/FPS 输入、full batch 四段缓存/拼接、自动 seam shift 和最终音视频封装。
- 尚未验证：纯 MC 对照、身份图但无视频参考对照、带真实配套音频的视频参考、项目 Save/Load 恢复、逐段颜色校正；这些仍是 T31 后续矩阵。
- 当前最小链使用 `ref2va`（因为原始任务此前已完成 Ref2VA+MC 基线）；FL2VA 专用 4 段链仍需单独构造带 `fl2va_model` 的工作流，不能从本次结果外推。
- 用户于 2026-09-07 指定后续 T31 输出统一归档到 ComfyUI `output/video/T31/`；运行器已将 `output_directory` 设为该目录。

## 2026-09-07 实测：声音驱动链

- 使用此前 Breeze/NativeAudioLock 产出的带人声片段 `A_00001_.mp4` 作为参考，并抽取匹配首帧作为 Ref 1；原片段为 768×448、10.833s、H.264/AAC。
- Extender 四段 full batch 成功，状态明确报告 `reference_video_count=1`、`reference_video_audio_count=1`、`generated=1,2,3,4`、`cached 4/4`；自动输出 832×480、430 帧、17.917s、H.264/AAC。
- 结果归档副本：`/home/sean/projects/ComfyUI/output/video/T31/extender_audio_ref_chain4_existing.mp4`。原始生成文件因旧版 output_directory 为空而落在 `output/video_T31_extender_audio_ref_chain4.mp4`，未删除。
- 已修正运行器：将 `output_directory` 显式设为 `/home/sean/projects/ComfyUI/output/video/T31`，`filename_prefix` 改为 `extender_audio_ref_chain4`；后续新运行会真正落入该目录。
- 用户目视反馈：声音驱动链口型正确且跨段连续，但 Breeze 参考/生成音频听不清、音质差；后段身份漂移明显。该反馈确认本轮更适合作为 Ref2VA 口型/连续性证据，不能作为最终音频质量证据。
- 诊断边界：本轮是 Ref2VA + 身份图 + 视频参考 + 配套视频音频 + MC，不能把效果拆归音频单因素；后段漂移说明固定 Ref 1 与 MC 仍不足以锁住跨段身份。

## 2026-09-07 实测：独立 Breeze 音频驱动

- 按用户修正后的目标，先用 Breeze TTS 2 生成干净驱动音频：`outputs/breeze-tts/t31_audio_driver_20260907.wav`，参数为保守自然口播指令、`cfg_scale=1.5`、seed 42；格式 24kHz mono PCM，时长 22.96s。
- H3 Extender 改为真正 audio-only 条件：固定人物/场景首帧 Ref 1 + `ref_audio_1` + Motion Context，断开全部视频参考；运行状态 `video refs 0`、`audio refs 1`、`generated 1,2,3,4`、`cached 4/4`。
- 本轮仍是 `Ref2VA`，不是 FL2VA；输出 832×480、430 帧、17.917s，原生 Extender 输出：`/home/sean/projects/ComfyUI/output/video/T31/extender_audio_only_chain4.mp4`。
- 已另行用原始 Breeze WAV 替换最终播放音轨，母带版：`/home/sean/projects/ComfyUI/output/video/T31/extender_audio_only_chain4_breeze_master.mp4`；H3 输出音轨不再作为最终音质依据。
- 抽帧观察人物/场景总体保持稳定；最终口型、音质和后段漂移以用户完整试听/观看为准。

## 2026-09-08：加入自动媒体 QC

- 新增 `tools/t31_media_qc.py`，使用 ComfyUI venv 的 OpenCV/SciPy/SSIM，对 T31 成片自动输出：音视频时长、音频包络与嘴部运动的延迟代理、中心人物锚点相似度、MC 接缝前后帧 SSIM/跳变倍率。
- 对 `output/video/T31/extender_audio_only_chain4_breeze_master.mp4` 实测：视频 430 帧/24fps/17.9167s，音频 17.8774s，容器时长差约 39ms；音频—嘴部运动代理相关性仅 0.1506，最佳延迟约 500ms 档，不能据此判定严格口型同步，需要 SyncNet 级模型或人工复核。
- 接缝跳变倍率（相对普通帧间平均运动）为第 1/2/3 处 `1.027 / 4.889 / 3.593`；第 2、3 处为自动复核重点。接缝 SSIM 仍为 `0.981 / 0.968 / 0.979`，说明不是整幅画面硬切，但有明显姿态/动作变化风险。
- 中心人物锚点相对首帧 SSIM：5.17s=`0.798`、9.42s=`0.743`、13.67s=`0.782`、末帧=`0.771`；支持后段存在可量化的构图/人物外观漂移趋势。当前 OpenCV 5 无旧 Haar 检测器，报告标记 `fixed_center_proxy`，因此这是漂移筛查而非身份识别。
- 报告：`/home/sean/projects/ComfyUI/output/video/T31/extender_audio_only_chain4_breeze_master.qc.json`。下一步建议先修正驱动音频与生成时间窗/音频锁定链，再用同一 QC 对照；不要仅凭容器时长差判断音画同步。

## 2026-09-08：Ref2VA Extender 音频上下文对照

- 用户确认 T31 主线保持 Ref2VA，不切 FL2VA。检查 Extender v2.3.3 源码后确认：MC 是 latent 条件而非逐像素复制；Disk Final Decode 的自动 seam correction 只允许最多前移 1–2 帧，不能保证生成画面无跳变。Extender 支持 `clip_by_clip`（默认）和 `full_batch` 两条执行路径。
- 当前 runner 第一版使用 `full_batch`、`context_length=22`、`audio_context_length=0`；代码中的 0 代表自动取音频尾部，不等于此前独立 MC runner 的明确 24。
- 新建独立缓存 owner 后复跑 `audio_context_length=24` 的纯音频 Ref2VA+固定人物图+MC 链，真实状态 `ref2va / video refs 0 / audio refs 1 / generated 1-4 / cached 4/4`，输出 `/home/sean/projects/ComfyUI/output/video/T31/extender_audio_only_a24_chain4_00001.mp4`。
- 对照 QC：音频—嘴部运动代理相关性 `0.196`、最佳延迟约 `125ms` 档（比旧版约500ms改善）；但视觉接缝跳变倍率 `2.716 / 5.865 / 4.030`，没有改善。结论：音频上下文不是当前视觉跳变主因，下一步应测试 Extender 默认 `clip_by_clip` 的逐段验证/最终导出路径，并保持 audio_context=24。

## 2026-09-08：Ref2VA Extender clip_by_clip 逐段验证

- 修改 T31 runner 为独立 cache owner，使用 `run_mode=clip_by_clip`、`context_length=22`、`audio_context_length=24`；连续提交 4 次，每次将前序段标记 validated 后再生成下一段。四次均成功，最终状态 `cached 4/4`，确认后续段确实读取了前序 validated MC cache。
- 输出：`/home/sean/projects/ComfyUI/output/video/T31/extender_audio_only_clip_by_clip_a24_chain4.mp4`。
- QC：接缝跳变倍率 `3.657 / 6.020 / 4.164`，相对 full_batch 的 `2.716 / 5.865 / 4.030` 没有改善；接缝 SSIM `0.9823 / 0.9537 / 0.9777`，中心锚点末段 SSIM `0.7659`。因此问题不是 full_batch 单独造成，也不是“没有 validated MC”造成。
- 当前结论：Ref2VA Extender+MC 可以完成长链缓存/导出，但这组 4-step、5 秒卡片的生成 latent 在 MC 边界仍会产生明显姿态跳变；后续优先测试更长单卡（减少接缝数量）或提高采样步数/关闭 turbo LoRA，再考虑调整 seam decoder。不要把当前链直接作为连续长视频生产方案。

## 2026-09-08：路线1 Breeze 最终母带封装

- 未重新生成画面，使用已归档的 `clip_by_clip` Extender 视觉结果，丢弃 H3 音轨，重新挂回原始 Breeze WAV。
- 最终文件：`/home/sean/projects/ComfyUI/output/video/T31/extender_route1_breeze_master_clip_by_clip.mp4`；H.264 832×480/430F/24fps，AAC 24kHz mono。该文件验证了最终播放音轨可不使用 H3 音轨，但不会改变原有视觉跳变/漂移，也不能证明软参考音频与最终 Breeze 母带逐音素同步。

## 2026-09-08：路线1用户复核，否决

- 用户复核路线1后确认两个明确问题：音画不同步；画面持续漂移，后段越来越模糊。
- 诊断：`ref_audio` 只是软参考，H3 生成画面时仍使用内部重新生成的音频/表演时间轴；后处理挂回 Breeze 只能改变最终听到的声音，不能保证画面口型对应 Breeze。持续变糊是视觉 latent 重复续接与 4-step turbo 低步数重采样的独立问题，音轨封装无法修复。
- 结论：路线1不作为生产方案，暂停继续生成。下一步必须先讨论“Extender 内部接入 NativeAudioLock”或外部 lip-sync 方案，再决定是否继续跑视觉质量对照。

## 2026-09-08：标准 20-step audio ref / NativeAudioLock 单段对照

- 固定同一人物/场景图 `T31_audio_ref.png`、同一 Breeze 驱动音频、同一 seed `71090801`、768×448、124 帧（约 5 秒）、20 steps；Extender 侧为单段 Ref2VA + `ref_audio_1`，NativeAudioLock 侧为标准 Ref2VA + NativeAudioLock，均不接 MC，避免把长链漂移混入口型判断。
- Extender 输出：`/home/sean/projects/ComfyUI/output/video/T31/t31_audio_ref_20_probe.mp4`；NativeAudioLock 输出：`/home/sean/projects/ComfyUI/output/video/T31/t31_native_lock_20_probe_00001_.mp4`。
- 自动粗筛结果：Extender 音频包络—嘴部运动相关性 `0.2997`、最佳延迟约 `125ms`；NativeAudioLock `0.3650`、约 `83ms`。两者均只能视为粗筛，不能替代逐音素 SyncNet；输出封装音频均是 H3 Audio VAE 解码后的 32kHz 双声道，不应以 PCM 逐样本相等判断 NativeAudioLock 是否生效。
- 目视首/中/尾抽帧：两者均保持人物与场景，但 NativeAudioLock 的音频驱动口型基线略稳；本次单段没有接缝，不能解释长链漂移。
- 关键机制结论：Extender 的 `ref_audio_1` 是“参考/模仿”条件，不能锁定目标音频时间轴；NativeAudioLock 是把外部音频编码后替换联合 AV latent 的 audio 半部，并用 video-only noise mask 采样，因此应作为精确音频口型基线。当前 Extender 节点不暴露内部 AV latent，二者不能直接串接；要做 Extender 原生锁音频，需要把 NativeAudioLock 的替换与 mask 逻辑并入 Extender 每段 sampler，或改用标准 NativeAudioLock+MC 管线。

## 2026-09-08：Extender/MC 漂移研究与社区结论

- Extender 确实是长视频编排/续接节点，但不是“消除漂移”的硬约束器：它把每段重新扩散生成，再用 MC latent 尾部作时序条件；MC 保留运动/音频上下文，不是逐像素复制，因此仍可能姿态跳变、身份漂移、细节变糊。其 seam correction 目前最多只做约 1–2 帧偏移，不能修复持续漂移。
- 官方 Extender 文档明确建议 `Generate → Preview → Retry if needed → Validate → Continue`，并说明后段依赖前段缓存；这解释了坏段一旦验证/继续会把问题传播到后面。社区 Motion Context 文档推荐视频 latent 直传、`encode_mode=video`、`context_length=22`、显式 `audio_context_length`，并用 Trim 去掉重复头，避免音画时间误差逐段累积。
- 社区共识不是“MP4 拼接/最后一帧图像锚定”，而是同一模型、同一分辨率/参数下把 video+audio latent 传给下一段，并保留可重试的逐段缓存；但社区也明确反馈每段仍会有轻微质量损失，长链音频尤其会逐段变闷。对不可接受的漂移，实际生产更稳的是切成短镜头/重新建立镜头，而不是无限延长一条生成镜头。
- T31 当前 4×5 秒 Ref2VA Extender 链已实测：full_batch 与 clip_by_clip 均出现明显边界跳变及后段漂移；因此下一条工程路线应是 20-step 的 NativeAudioLock+MC latent 链，或把 NativeAudioLock 集成进 Extender，再比较 2×10 秒/3×10 秒，禁止继续用 4-step turbo 链作为质量结论。

## 2026-09-08：社区长视频续接方案检索

- Bilibili 搜索到的高相关样本包括：Time-AI 的 Motion Context 详解（BV1Wsgg6AEeR）、Aiden_0 的多参考长视频循环（BV1xmgs6CE48）、遇见AI的音频时间线/跨轮次 latent 教程（BV1xs8w6fEhy）、Doc_workBox 的“无限时长数字人”工作流（BV1jztk69EhE）、以及 H3 多参考长视频/AV 循环方向。B站当前没有返回可下载 AI 字幕，因此只能把标题、简介和配套仓库作为方案线索，不能把视频演示当成独立质量证据。
- 当前开源方案可分三档：①普通 MC latent chaining；②带准确音频时间线、Trim、最后帧参考和自动队列的 Auto-Chain/Context Loop；③更新的 MultiRef/latent-masking/AV Extension，把已知 video/audio token 置 0 mask 保留，只对新增区域 denoise，并支持 de-rope seam。第三档比单纯 MC 更接近“减少漂移”的工程方案，但仍是实验性 fork，不是模型级硬锁。
- 社区仓库明确的抗漂移要点：同一模型/分辨率/采样参数；恒定 24fps；保存并加载 paired video+audio latent，不能 decode 后再 encode；`context_length=22`（或兼容网格的更长上下文）、`encode_mode=video`、音频单独按绝对时间线切片；Trim 去掉重复头；人物/场景需要 `last_frame` 或稳定 Picture reference。音频“原始母带最终覆盖”只能修声音，不能修口型。
- 新的 MultiRef fork 另有 AV Extension、V2V latent motion transfer、AV Bridge 和 2MP de-rope continuation；其文档说明可保护已知 AV 区域，仅让边界少量 token 重新生成。这是目前最值得与标准 MC 做 A/B 的开源路线。新 Auto-Chain addon 要求 ComfyUI 0.34.0+，当前本机 0.33.0，暂不直接安装，避免改变现有环境。
- 结论：B站所谓“很长且连续”的 H3 主播，多数仍是分段链式方案，通常额外使用最后帧参考、latent 保存/加载、音频时间线和自动循环；“无限时长”不等于单次生成，也不能证明没有累计漂移。当前 T31 应先测“标准20步 NativeAudioLock+MC”与“MultiRef latent-mask/AV Extension”两条，先解决视频边界和身份漂移，再评估 Extender封装。

## 2026-09-08：Ref2VA 加速 LoRA 检索

- 当前 T31 Extender 长链实际使用的是 `minimax_h3_ref2v_turbo_4step_v0.1_comfyui_bf16.safetensors`，强度 `0.95`、`steps=4`、Euler/simple；本机另已存在 `minimax_h3_ref2v_turbo_8step_v1.0_768p_comfyui_bf16.safetensors`，但尚未测试。
- 当前公开可确认的 Ref2VA 加速选项：LightX2V `Ref2VA Turbo 4-step v0.1` 与 `Ref2VA Turbo 8-step v1.0 768p`；它们是 task-specific adapter，不能和 FL2VA LoRA 混用。社区/第三方还存在 Larry v4-600 EMA、PDD/Ref2VA student、RefMOD 等，但质量与兼容性不能视为官方定论。
- 社区实测报告普遍指向：4-step Turbo 会软化、产生脸部伪影、运动漂移；8-step 比4-step好但仍可能漂移。另有报告指出 Kitchen Attention 保持20步、约省30%时间，质量损失远小于 Turbo LoRA；这是后端加速，不改变采样轨迹。当前 T31 的4-step链出现后段变糊/漂移，Turbo LoRA 是高度可疑因素，但尚不能单独归因，必须用同seed/同MC做无LoRA 20步和8-step v1.0对照。
- 下一步：先跑标准 Ref2VA/NativeAudioLock+MC 的无LoRA 20步连续性基线；随后跑 LightX2V Ref2VA 8-step v1.0（严格8步，不把8步LoRA硬跑20步）；4-step只保留速度参考。若无LoRA显著稳定，说明当前主要问题确由加速 LoRA/低步数放大。

## 2026-09-08：A 组无 LoRA NativeAudioLock+MC 长链复核

- 发现并复核已有 A 组结果：标准 Ref2VA + NativeAudioLock + MC，20 steps、无 LoRA、768×448、24fps，A/B/C 三段约30秒；A/B/C 配置见 `experiments/h3_digital_human/zh_breeze_ref2va_audio_lock_mc_30s_cases.json`。
- 成片：`/home/sean/projects/ComfyUI/output/video/h3_avatar_zh_breeze_ref2va_audio_lock_mc_30s/joined_30s_master_audio_timeline_fixed.mp4`。
- 自动 QC：720帧/30.000s；接缝1（约9.25s）跳变倍率3.401、SSIM 0.9609，需复核；接缝2（约19.25s）跳变倍率0.942、SSIM 0.9908，较平滑；中心锚点末帧 SSIM 0.8894，未见持续恶化到不可用的量化趋势。音频为24kHz mono最终母带，粗同步相关性0.1947、最佳延迟约167ms，仅为代理指标。
- 抽帧显示人物身份/服装/背景保持，第一处存在动作状态变化，第二处基本平滑；尚不能仅凭自动代理判定“完全无漂移”，但无 LoRA 20步明显比当前4-step Extender链更适合继续作为质量基线。暂不测试 B（8-step）。

## 2026-09-08：Ref2VA 人物图是否干扰 MC 开场 A/B

- 新建严格 A/B：同一 A 段 paired latent、同一 NativeAudioLock 音频、同一 seed `62090811`、20 steps、768×448；A 不接图片参考，B 接原人物/场景图并在 prompt 中声明“identity only，不影响 opening pose/framing/background”。
- 输出：无图 `/home/sean/projects/ComfyUI/output/video/T31/t31_mc_native_no_image_ref_B_00001_.mp4`；有图 `/home/sean/projects/ComfyUI/output/video/T31/t31_mc_native_identity_image_only_B_00001_.mp4`。
- 两者均 255 帧/10.625s。无图组末帧相对自身首帧 SSIM `0.8787`、粗同步相关性 `0.3074`；有图组末帧 SSIM `0.8002`、相关性 `0.1629`，帧间运动 p95 也更高（3.065 vs 1.016）。
- 抽帧结果：无图组开头更贴近 MC 续接状态，后段保持较稳；有图组虽 prompt 明确禁止参考图影响开场，后段仍出现明显背景/光照漂移。结论：普通 Ref2VA image reference 会影响整段生成，prompt 只能改变语义解释，不能把它变成“只影响身份”的隔离条件；在当前 Ref2VA+MC 路线下，人物图可能与 MC latent 形成竞争。下一步应测试“只用 MC+NativeAudioLock”与“只提供人物裁切/中性背景图”的策略，暂不测试 8-step LoRA。

## 2026-09-08：A 段分别连接人物图/无图 B 段

- 将同一个 A 段分别连接两条 B 段，未交叉淡化：
  - `/home/sean/projects/ComfyUI/output/video/T31/t31_A_plus_B_no_image_ref.mp4`
  - `/home/sean/projects/ComfyUI/output/video/T31/t31_A_plus_B_identity_ref.mp4`
- 两条 A→B 容器接缝（约10.17s）都因 MC Trim 对齐而非常平滑：无图 SSIM `0.9965`、跳变倍率 `0.53`；有人物图 SSIM `0.9964`、跳变倍率 `0.419`。这说明人物图并未改善真正的接缝，二者边界都由 MC/Trim 对齐。
- 后续漂移区别仍然存在：无图组末帧中心锚点 SSIM `0.8312`；有人物图组 `0.8160`，且人物图组帧间运动基线更高，肉眼更容易出现背景/光照变化。暂定结论：人物图提高单段静态观感，但没有改善 A→B 接缝，并可能加重后段漂移。

## 2026-09-09：标准 20-step NativeAudioLock+MC 重新生成

- 按统一时间线重新生成，未使用加速 LoRA：768×448、24fps、20 steps、A/B 各 243 帧；B 使用 A 的 paired latent，`context_length=22`、`audio_context_length=24`，并由 Trim 裁掉 22 帧重叠。
- 音频切片严格按原始 Breeze 母带：A=`0–10.125s`，B 预滚=`9.208333–19.333333s`；因此 B 裁剪后从全局 `10.125s` 接续。最终只挂载一次原始 `/home/sean/projects/ComfyUI/input/h3_avatar/zh_breeze_test_30s.wav`。
- 输出：A `/home/sean/projects/ComfyUI/output/video/T31/t31_std20_native_mc_ref_A_00001_.mp4`（243帧/10.125s）；B `/home/sean/projects/ComfyUI/output/video/T31/t31_std20_native_mc_ref_B_00001_.mp4`（221帧/9.208333s）；母片 `/home/sean/projects/ComfyUI/output/video/T31/t31_std20_native_mc_ref_master_original_audio.mp4`（464帧/19.333333s，24kHz mono 原始母带）。
- QC：接缝 10.125s，边界 SSIM `0.9776`、face SSIM `0.9740`，比此前手工拼接可控但跳变倍率 `3.173` 仍是复核标记；末帧相对首帧 SSIM `0.7548`，说明后段仍有明显漂移/构图变化。粗同步代理相关性 `0.2204`、最佳延迟约 `-333ms`，只能作为异常筛查，不能替代 phoneme SyncNet。此次流程本身已标准化，但质量结论仍是“接缝改善、漂移未解决”。

## 2026-09-09：T31 标准 MC 四段流程定版与防错

- 最终有效样本：`/home/sean/projects/ComfyUI/output/video/T31/t31_std20_legal_four_segment_master.mp4`，481 帧/20.041667s；A=124 帧，B/C/D 使用合法 141 帧生成并各裁 MC 22 帧，实际各保留119帧；视频与最终原始 Breeze 音频均为20.042s。
- 146 帧实验被判定为无效：146 不满足 H3 `17*k+5` 网格，MC 实际输出只裁约10帧，造成续接音频预滚与视频实际起点相差约0.5s，并引发杂音/音画错位。错误版本不作为质量结论。
- 工程化落地：新增 `docs/33_h3_mc_engineering.md`；`scripts/h3_mc_runner.py` 增加合法帧长预检、MC 段必须保存 latent、latent 缺失时不跳过、输出媒体元数据记录。当前流程 reference 为 Ref2VA 的静态 `ref_image`（可选身份/场景条件）+ NativeAudioLock 当前段音频 + MC 上一段 AV latent；不使用 `ref_audios`，暂不加入 last_frame。

## 2026-09-09：A-D 四头像换脸 / 统一场景测试

- A-D 均成功生成：每段分别使用暗影精灵女王、赛博朋克女主、高等精灵法师、黑暗奇幻女骑士头像；统一使用 `ref_scene_hd_v2.png`，提示词要求只换脸部身份，保持原主播衣服、身体、手势、动作和机位。
- 最终成片：`/home/sean/projects/ComfyUI/output/video/T31/t31_four_avatar_face_swap_master.mp4`，481 帧/20.041667s；原始 Breeze 音频单次挂载，视频音频时长经编码约20.011s，容器总长20.041667s。

## 2026-09-09：A 身份+服装+场景，B-D 新脸+场景固定机位测试

- 配置：`experiments/h3_mc_locked_camera_face_clothing_scene.json`。A 同时使用 `ref_identity_hd_v2.png`、`ref_outfit_hands_hd.png`、`ref_scene_hd_v2.png`；B-D 使用同一张新脸 `ref_game_banshee_queen.png` 和同一场景图，不再输入服装图。
- 提示词明确固定中景机位：无 pan/tilt/zoom/dolly/reframing；B-D 只允许改变脸部身份，衣服、身体、手势、动作和背景继承。
- 最终成片：`/home/sean/projects/ComfyUI/output/video/T31/t31_locked_camera_face_clothing_scene_master.mp4`，481 帧/20.041667s；原始 Breeze 音频单次挂载，音频编码流约20.011s，容器总长20.041667s。
- 经验结论：服装参考图若包含大面积身体/双手和不同构图，可能诱导镜头转为衣服特写；必须在提示词中声明服装图只定义材质/衣服，不能定义构图。B-D 看不到明显换脸，仍说明 MC latent 对脸部身份的继承强于后续静态头像参考；连续性与换脸是冲突目标。

## 2026-09-09：三参考图高清重制

- 重制并检查三张 1672×941 高清参考图：`ref_face_hd.png`（脸部身份）、`ref_scene_hd.png`（特色电视演播室，无人物/手）、`ref_outfit_hands_hd.png`（服装与手势）。
- `experiments/h3_mc_three_ref_four_chain.json` 已切换到新参考图；旧的 `ref_face_only.png`、`ref_gray_studio_scene.png`、`ref_outfit_hands.png` 已移入系统回收站。原始主播全身锚定图和音频保留。
- 2026-09-12：复核三参考图四段链 `t31_three_ref_four_segment_master.mp4`。四段均成功，481 帧/20.042s，A=124 帧、B-D 各保留119帧，latent 齐全；输出为 `ComfyUI/output/video/T31/t31_three_ref_four_segment_master.mp4`。
- 2026-09-12：T31 QC（接缝帧 124/243/362）显示边界 SSIM `0.9199/0.9021/0.9715`，跳变倍率 `1.62/1.584/1.047`；第三处接缝已平滑，前两处仍是轻度复核项。中心锚点相对首帧 SSIM 在 5.17/10.125/15.083/20.0s 为 `0.7381/0.1937/0.3210/0.2067`，说明第2段后构图/姿态累计漂移明显。音频20.0534s、视频20.0417s，但包络—嘴部代理相关性仅 `0.0918`、最佳延迟约625ms；不能作为逐音素同步结论。
- 2026-09-12：抽帧目视确认身份/服装未崩坏，但各段动作与裁切状态持续变化，静态身份+场景参考没有解决 MC 链累计漂移。下一步不再堆静态参考图，优先比较 latent-mask/AV Extension 或更短镜头重建策略；三参考图链保留为当前标准20步对照样本。
- 2026-09-12：按用户确定的官方式最简参考角色 prompt 做 A→B 对照：两段均只使用 `The woman from <Picture 1> speaks to camera in the studio from <Picture 2>.`，不写 same/uninterrupted/match，也不写镜头禁止词；配置 `experiments/h3_mc_minimal_roles_ab.json`，输出 `t31_roles_A124_00001_.mp4`、`t31_roles_B141_00001_.mp4`。
- 2026-09-12：A→B 两段均成功（A约120s、B约130s，峰值显存23.7/23.8GB）。目视显示 A 段内部仍从宽景桌面切到近距离胸像再回到中景，B 段主要维持宽景；仅用 `<Picture>` 角色标签和一句 prompt 没有锁定固定镜头。结论：问题不是 prompt 缺少 `same/uninterrupted/match`，而是 Ref2VA 的普通参考图条件本身不提供固定镜头锚点；需要换成完整构图锚点/FL2VA 或其他硬约束路线，暂停继续扩展链长。
- 2026-09-13：Ref2VA 清理与最小基线：历史 Ref2VA/T31 输出已移入 /tmp/ref2va-cleanup-20260913/，保留 input 参考图、experiments 工作流/结果记录及模型文件。
- 2026-09-13：单段无 MC/无 LoRA 基线（1 张 h3_avatar/anchor_host_blank_gray_16x9.png，768×448，length=99，20 steps，res_multistep，seed 20260913）成功，runner 耗时 78.7s；请求 99 帧，实际输出 107 帧/4.458s。未见 OOM。
- 2026-09-13：启动日志仍有既有 RMBG 依赖缺失提示及 comfyui.db 数据库锁错误；任务结束后 ComfyUI 端口不可用，下一轮需先确认重复实例/锁状态。
