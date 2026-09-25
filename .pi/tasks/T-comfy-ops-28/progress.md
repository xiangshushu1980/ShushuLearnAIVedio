# T-comfy-ops-28 进度：MiniMax H3 数字人成片链路

> 背景：单 4090 仅 H3 产能达标（3min≈58min，MC 链式线性估）。H3 立为 V1 数字人引擎。

## 状态总览
- [ ] ① 梳理 H3 数字人成片链路（ref_audio 口型 + MC 续接 + NativeAudioLock + FaceRefine）
- [ ] ② 粤语 TTS 母带口型验证（复用 h3-digital-human-research 固定粤语输入对）
- [ ] ③ 3min 长片产能实测（MC 链式，目标 1-2h 内）
- [ ] ④ 封装 HTTP 服务供 DGB 调用（对齐 T-dgb-01 依赖）

## 背景备注
- 产能：H3 5s≈1.6min → 3min≈58min（MC 链式线性估，需实测校准）。
- LongCat（T-comf-01 已 complete）产能判死刑；T-comfy-ops-27 为 LongCat 优化对比。
- 粤语口型是 H3 的核心待验证项（第一类验收），复用 research 固定输入对保证可对比。

## 2026-09-01：当前路线、外部检索与本轮执行方案

### 当前长视频数字人路线（项目现行口径）

```text
外部粤语 TTS 母带（最终音频真值）
→ 按语义/音频边界拆成 H3 短片段
→ Ref2VA/I2V + 角色参考图 + source audio reference
→ Motion Context：video/audio latent 续接（context=22，audio=24）
→ Trim 去掉重叠头部，保留未裁剪音频做 seam probe
→ 必要时 3D latent upscale + 正式步数精修
→ 必要时 FaceRefine 小脸局部修复
→ 最终外部 TTS 音轨复 mux，人工验收口型/身份/接缝
```

本轮先跑 2 段数字人冒烟，不把结果当作粤语正式验收：当前可访问的 `/tmp/eleven-cantonese-test.mp3` 实际时长约 2.6 秒，项目中两个 `V1_1024*` 文件实际约 5.18 秒，均不足以代表研究计划中的 20 秒/2 分钟母带。

### sources 扩展检索结论

- 官方/核心：ComfyUI 原生 H3 Ref2VA；H3 是联合音视频模型，参考音频、画面和动作同一采样链。
- 长视频候选：NikoDemon80 Motion Context（本机已装）、Herrgotts Infinite Continuation Suite、tritant H3 Extender、j955229 Motion Director、ethanfel Context Loop。
- 相关职责仍应拆开：Motion Context 负责 latent 连续；NativeAudioLock 负责锁外部 vocals；FaceRefine 负责小脸局部质量，不能当作口型模型。
- 选型：本轮不再叠加第二套会 patch H3 的长视频插件，避免多个 pack 争抢同一核心 patch；先验证现有 Motion Context 的数字人口播输入和实际 seam。

### 节点与素材核验

- 已就位：`ComfyUI-H3-Motion-Context`、`ComfyUI-H3-NativeAudioLock`、`ComfyUI-H3-FaceRefine`、VideoHelperSuite、H3 Turbo/CondCache/MotionCache。
- H3 模型/双 VAE/CLIP 均在位；本轮使用 `ref2va_pruned_int8_convrot`、768×448、14 steps 做冒烟，避免直接消耗正式长跑时间。
- 测试配置：`experiments/h3_digital_human/h3_avatar_smoke.json`；提示词：`experiments/h3_digital_human/avatar_prompt.txt`。

### 验收顺序

1. 清空 ComfyUI/GPU 状态并重启，确认所有节点加载无 error。
2. 跑 `avatar_seg1_audio_ref`：单段参考图 + 外部语音，先回答“能否形成可观察口型”。
3. 跑 `avatar_seg2_mc22`：同参考输入 + clip1 AV latent，回答 MC 是否能执行并正确 Trim。
4. 用 ffprobe、`seam_probe.py`、`level_step.py`、`freeze_detect.py` 做工程检查，最后人工看段 2 开头约 1 秒。
5. 冒烟通过后再接入真正 20 秒粤语母带，扩展 5+5+5+5、10+10、15+5 和 NativeAudioLock/FaceRefine 对照；未通过则先修输入/节点，不开 3 分钟长跑。

### 本轮实际执行结果

### 用户路线修正（2026-09-01）

- 当前不考虑高清、latent upscale 和修补；FaceRefine 历史效果不好，降为基础链稳定后的升级方案。
- InfiniteTalk 调查显示 RTX 4090 本机速度慢；其继任者 LongCat 本机同样很慢，均降为低优先级备选，不作为当前基础路线。
- 当前核心问题改为：H3 单段稍微拉长到 8/10/15 秒后，能否在 24GB 显存和可接受速度下稳定生成，并通过 MC 做长片续接。

- ComfyUI 曾在普通启动模式加载 H3 文本编码器时被系统回收；改为 `--lowvram --disable-smart-memory` 后稳定运行，当前 H3 运行期间显存峰值约 20.7GB，GPU 未分给其他推理服务。
- 首段 `avatar_seg1_audio_ref`：5.167s，768×448@24fps，H.264 + AAC 32kHz 双声道，已保存。
- 第二段 `avatar_seg2_mc22_retry`：188s，MC 成功加载 clip1 AV latent，22 帧视频/24 帧音频 pin，Trim 后 4.250s，已保存。
- seam probe：重建区 mean corr=0.920，32/35 窗口 >0.6，lag trend=0.02ms，residual rms=0.01ms；说明本次短音频链的相位连续性通过。
- level step：broadband 0.470（+8.9dB，MARGINAL），floor 0.937（+29.8dB，STEP）；短样本存在音量/底噪台阶，不能判为正式成片通过。
- freeze detect：第二段头 22 帧 motion=0.666，是片段中位 motion 的 1.36x；无冻结。
- Motion Context 离线 node smoke、payload gate、level/freeze 自测通过；mock harness 中故意改变上游音频布局时能拒绝 patch，说明保护门生效。
- 结果边界：当前冒烟音频 `/tmp/eleven-cantonese-test.mp3` 只有约 2.6s，本轮不能回答“粤语口型是否通过”或“长视频路径全部通过”；正式 20s 母带尚未登记。

### “稍微长一点”资源判断

- **不是完全跑不了**：既有 H3 速度矩阵已在 768×448、干净环境、int8 下跑过 5.2s=115s、10.1s=234s、15.1s=403s；因此 15 秒级单段在本机是可运行的，不应直接归因于显存不足。
- **当前风险是资源余量和速度**：本轮 5 秒数字人冒烟在低显存模式下峰值约 20.7GB；H3 文本编码器/扩散模型动态换入时普通模式曾把系统可用 RAM 压到接近 0 并被系统回收。低显存模式能稳定运行，但换入换出使首段/长段更慢。
- **推荐第一档**：先测 10 秒单段，再测 15 秒单段；续接用 22 帧视频 context + 24 帧音频 context，Trim 后每段损失约 0.92 秒。若 15 秒段速度或资源不理想，退回 8 秒/约 7.08 秒有效片段链。
- **不建议机械按 5 秒切**：3 分钟目标可按 10 秒生成/约 9.08 秒有效输出，约 20 段；或按 15 秒生成/约 14.08 秒有效输出，约 13 段。先以 10 秒作为速度/稳定性甜点候选，15 秒作为上限候选。

### 2026-09-01：普通模式长段资源观察

- 普通模式已实际提交 8 秒单段扫描；H3 模型初始化阶段系统 RAM 达约 51/54GB、Swap 使用约 13GB，采样无有效推进。该测试已中止，避免继续把系统拖入交换抖动。
- 结论暂定：长段的第一阻塞是 H3 模型与中间状态的系统内存/换入换出压力，不是 MC 不能续接；后续 8/10/15 秒扫描改用 `--lowvram --disable-smart-memory` 完成，并单独记录速度代价。
- 当前运行：`experiments/h3_digital_human/h3_avatar_length_scan.json`，ComfyUI 独占 GPU，8/10/15 秒串行。

### 2026-09-01：Ref2VA 优化补充检索与路线调整

- 数字人主线改为 **FL2VA + 短段续接/优化**；Ref2VA 只保留为多参考身份/声音条件的专项方案。
- 新发现候选：`Jalen-Brunson/ComfyUI-MiniMax-H3-PDD-Acc`，官方 MiniMax-H3 8-step PDD Acc LoRA，资料标注同时覆盖 FL2VA/Ref2VA；需单独验证参考音频、身份和音质，不能直接假定可用。
- 新发现候选：`BMB12d3/ComfyUI-H3-Ref2VA-Accelerator`，专门针对原生 Ref2VA 的 block-cache，目标是复用 transformer residual，资料标注支持 INT8 ConvRot；优先级高于早期 TeaCache。
- `Icyoung/ComfyUI-MiniMaxH3-TeaCache` 目前仍偏早期/scaffold，暂不作为可靠生产候选。
- vLLM-Omni H3 recipe 的当前说明：TeaCache 已针对 FL2VA 校准，Ref2VA 请求不走缓存；不能把 FL2VA 的缓存收益外推到 Ref2VA。
- 待执行顺序：先完成 FL2VA 8/10/15 秒 + MC；再测 PDD Acc 8 步 FL2VA；最后分别测试 Ref2VA Accelerator 与 PDD Acc Ref2VA。

### 2026-09-01：15 秒普通模式结果

- `avatar_single_15s` 成功：实际 15.125s，768×448@24fps，普通模式，14 steps，总耗时 538s，runner 记录峰值显存 17.9GB。
- 未发生 OOM 或 ComfyUI 回收；但任务结束后系统 RAM 只剩约 0.8GB 可用（Swap 约 446MB），说明普通模式虽然能完成，资源余量很小，不适合直接并行或连续堆积长任务。
- 结论：15 秒单段可运行；下一步应测试 10/15 秒 MC 续接的实际耗时和稳定性，生产默认仍建议单队列串行。

完整路径矩阵见：`experiments/h3_digital_human/long_video_path_matrix.md`。

### 2026-09-01：外部粤语音频 → FL2VA → PDD → MC 顺序测试

- 基础外部音频：真人高清上半身首帧，`hk_a_30s.wav`，FL2VA INT8，768×448，14 steps，10s 片段耗时 306s；输出含 32kHz 双声道 AAC，画面稳定，口型检查条件满足。
- PDD Acc：下载并安装 `ComfyUI-MiniMax-H3-PDD-Acc` 与 FL2VA 专用 `minimax_h3_fl2va_pdd_acc_8step_comfyui.safetensors`；使用专用 Apply 输出 SIGMA + Euler，8 nfe，外部音频锁定，5.167s 片段耗时 145s，成功。
- MC：基础 FL2VA 14 steps + NativeAudioLock + MotionCache，5.167s 片段耗时 155s；日志显示 `skipped 0/14 model calls`，本配置估算 1.00x 加速，无实际收益，但链路成功且音频封装正常。
- 本阶段顺序结论：外部音频锁定可用；PDD FL2VA 8-step 可用且比基础 14-step 短测明显更快；当前 5s/14-step 组合的 MC 无收益，不应继续投入该参数，后续长段或更高步数再评估。
- 长段 PDD 补测：同一真人上半身/完整粤语音频/768×448，10s 配置耗时 255s、输出 10.833s；15s 配置耗时 315s、输出 15.792s；两条均成功，无 OOM/节点错误，显存约 22.2GB，任务结束后系统可用内存约 7.2GB。容器输出存在 H3 帧网格导致的时长扩展，批量拼接前需按视频帧数统一裁切/对齐音频。

## 2026-09-02 断句切镜头测试

- 找回粤语参考音频：`/home/sean/projects/avatar-runtime/data/duix/face2face/hk_a_30s.wav`，30s；另有 `hk_b_30s.wav`、`hk_c_60s.wav`。
- 资源确认：ComfyUI PID 493 在 `127.0.0.1:8188`；RTX 4090 空闲显存约 23.7GiB；系统可用内存约 50GiB；已取得 `T-comfy-ops-28-codex` GPU 租约。
- Krea 生成高清主播首帧：`/home/sean/projects/ComfyUI/output/h3_avatar/anchor_host_krea_00001_.png`，1024×1024，正面胸上构图。
- `hk_a_30s.wav` 按静音附近切为 00:00–00:10、00:10–00:19、00:19–00:30 三段；CUT 组三段独立 FL2VA PDD 8-step 均成功，耗时 125s/84s/114s。
- CUT 成片已按视频帧数裁成 240/216/264 帧并硬切拼接，重新挂回原始 30s 母带：`/home/sean/projects/ComfyUI/output/video/h3_avatar_cut/hk_a_cut_joined_30s_master_audio.mp4`。MC 对照组待视觉确认后运行。
- 16:9 复测：Krea 生成 `anchor_host_krea_16x9_00001_.png`（1024×576）；H3 直接使用 768×432 会触发 latent shape error，改用 768×448 网格生成后上下各裁 8px，最终成片严格 768×432/24fps/30s，无拉伸。
- 16:9 动态 CUT 三段均成功（PDD 8-step，耗时 102s/83s/112s）；提示词加入微笑、眉眼变化、点头、肩部和手势动作。
- 复拼成片：`/home/sean/projects/ComfyUI/output/video/h3_avatar_cut_16x9_grid/hk_a_cut_joined_30s_master_audio_16x9_motion.mp4`。
- 新一轮参考图：Krea 4K 直接横幅生成会重复主播；稳定方案为 Krea 1024×576 单主播图 `anchor_host_krea_hands_16x9_00001_.png`，再 Lanczos 放大到 3840×2160 `anchor_host_krea_hands_4k_16x9.png`。单人、双手可见、演播室背景。
- Motion Context 两种约 5s 链均成功：换气点切分 0–4.5s / 4.5–9.5s，首段 64s、MC 续段 48s；句中切分 0–6s / 6–11s，首段 56s、MC 续段 48s。修正 SaveLatent/LoadLatent 为显式文件名后链路通过。
- 换气点拼接样片：`/home/sean/projects/ComfyUI/output/video/hk_a_mc_breath_v2_joined_16x9.mp4`，226 帧、768×432、9.4167s。
- 句中切拼接样片：`/home/sean/projects/ComfyUI/output/video/hk_a_mc_mid_v2_joined_16x9.mp4`，260 帧、768×432、10.8330s。
- 2026-09-02 MC 接缝诊断：旧 MC 样片将原始母带按总时长重新挂回，但 MC 第二段经 Trim 同时去掉了 22 帧/约 0.92s 的画面和音频，导致第二段可见画面与母带音频错位；已另做“首段+MC Trim 续段自身音频”校正样片：`hk_a_mc_breath_v2_joined_generated_audio_16x9.mp4`、`hk_a_mc_mid_v2_joined_generated_audio_16x9.mp4`。
- 机制判断：MC 的 pinned head 确实取上一段 latent 尾部；若上一段尾部嘴闭，下一段的起始条件会继承闭嘴/停顿状态。即使 Trim 去掉 pinned head，后面的可见生成帧仍需从该状态过渡，因此句中切也可能先闭嘴。当前 B 段音频没有加入约 0.92s 的 MC pre-roll，却在 B 开头被 Trim 掉约 0.92s，是造成“音频先走、嘴后开”的主要可疑点。
- 下一轮应：B 段输入音频向切点前回溯约 0.92s（与 pinned head 对齐），生成后用 Trim 后音频拼接；MC 仅用于连续镜头/换气续接，真正切镜头改用独立 CUT。
- 最小变量复测：B 段去掉 `first_frame`、prompt 置空，仅保留 A 段 latent 的 Motion Context + NativeAudioLock 外部音频；换气点和句中切两条均成功。对照成片：`hk_a_mc_breath_minimal_no_anchor_16x9.mp4`、`hk_a_mc_mid_minimal_no_anchor_16x9.mp4`。

### 2026-09-02：保留 prompt/主播图 + B 音频前置 0.92s

- 四段均成功：A 换气点 4.458s、B 输入从 3.542s 开始；A 句中切 5.167s、B 输入从 4.25s 开始。B 均保留 prompt 与主播首帧图，并使用 A 段 Motion Context latent。
- 输出片段：`/home/sean/projects/ComfyUI/output/video/h3_avatar_mc_preroll/{breath_a_00001_,breath_b_mc_00001_,mid_a_00001_,mid_b_mc_00001_}.mp4`。
- 原始粤语音频回挂拼接样片：`hk_a_mc_breath_preroll_original_audio_16x9.mp4`（768×432，视频 8.667s，音频 8.709s；B 实际生成帧略少于目标，需视觉检查接缝）；`hk_a_mc_mid_preroll_original_audio_16x9.mp4`（768×432，9.417s，音频 9.408s）。
- 本轮最终音轨均来自 `/home/sean/projects/avatar-runtime/data/duix/face2face/hk_a_30s.wav`，没有使用生成片段音轨；因此若仍听到爆音，应归因于编码/播放链或母带本身，而非片段音频拼接。

### 2026-09-02：纯空白背景 + 场景 prompt 对照

- 已清理上一轮 GPU 租约并重新申请后测试；四段均成功，完成后已释放租约。
- 新参考图：`/home/sean/projects/ComfyUI/input/h3_avatar/anchor_host_blank_gray_16x9.png`，单主播、16:9、浅灰无纹理背景。
- runner 新增每 case 独立 `image` 参数；空白背景测试仍保留 prompt、主播图、MC 和 0.92s B 音频预滚。
- 成片：`/home/sean/projects/ComfyUI/output/video/hk_a_mc_blank_bg_breath_original_audio_16x9.mp4`、`hk_a_mc_blank_bg_mid_original_audio_16x9.mp4`。
- 规格与上一轮一致：768×432/24fps；音轨继续使用原始粤语母带。

### 2026-09-02：保留 MC 前置区间与第三段连续生成

- 新增 `trim:false` 诊断路径，生成完整 B 段（含前置约 0.92s），并使用原始母带制作观察片：`/home/sean/projects/ComfyUI/output/video/hk_a_mc_breath_untrimmed_B_debug_16x9.mp4`，9.625s。
- 第三段 C 已按同一 prompt + 主播图 + MC latent 流程成功生成；使用 B 段 sampler latent 继续，未使用裁切后的 B 视频：`/home/sean/projects/ComfyUI/output/video/hk_a_mc_breath_three_segments_original_audio_16x9.mp4`，13.875s。
- 两项测试结束后 GPU 租约已释放。

### 2026-09-02：39 帧 context 五段链

- 将 MC context 从 22 提升到 39 帧（约 1.63s），连续生成 5 段，每段可见 124 帧；五段均成功，无 OOM/节点错误。
- 五段成片：`/home/sean/projects/ComfyUI/output/video/hk_a_mc_5seg_context39_original_audio_16x9.mp4`，768×432/24fps，画面约 25.792s，原始音频约 25.834s。
- 接缝亮度统计（YAVG，接缝前两帧→接缝帧→后两帧）：124 帧约 176.5→177.1→175.9；248 帧约 175.3→175.4→175.3；372 帧约 174.8→176.4→176.0；496 帧约 174.1→232.0→230.7。最后一个接缝出现严重亮帧/整体高亮，需目视确认并作为 39 帧长链的不稳定证据。
- 39 帧并未保证闪烁消失；前几个接缝较轻，后段出现明显亮度/画面退化，说明更长 context 可能加剧长期链稳定性问题。

### 2026-09-02：5 帧 context 五段严格同步链

- 更正记录：上一轮 39 帧五段成片是 Trim 后版本；第 4 接缝已确认身份漂移为非主播/严重场景漂移，不是单纯亮度问题。其连续音频回挂方式也不足以作为本轮严格同步基准。
- 社区反馈：经典 Motion Context 长链存在 photocopy effect，颜色、细节和身份会逐段累积漂移；原始实现推荐 22 帧，39 帧标注为未充分验证。MultiRef/新 fork 通过额外参考图、latent 直通或颜色重锚缓解，但不能保证无限长链稳定。
- 5 帧测试：5 段全部生成成功；B-E 每段输入仅前置 5 帧（约 0.208s），拼接时严格 Trim 掉这 5 帧的画面和对应音频，再统一回挂原始母带。
- 成片：`/home/sean/projects/ComfyUI/output/video/hk_a_mc_5seg_context5_trimmed_original_audio_16x9.mp4`，768×432/24fps，约 25.792s；GPU 租约已释放。

### 2026-09-02：22 帧 context 接缝移动 -5 帧

- 按用户方案保留 22 帧 MC context，但将 Trim 从 22 改为 17，保留 B 起始的最后 5 帧；拼接时 A 端裁掉最后 5 帧，等效于接缝提前 5 帧，保持原始音频连续。
- 测试成片：`/home/sean/projects/ComfyUI/output/video/hk_a_mc_breath_overlap5_original_audio_16x9.mp4`，768×432/24fps，视频约 8.667s、原始音频约 8.709s。
- 该测试用于判断闪烁是否随接缝位置移动；GPU 租约已释放。

### 2026-09-02：统一主播素材的 22 帧五段基准

- 重新从第一段开始生成，全部 5 段统一使用 `anchor_host_blank_gray_16x9.png`、同一服装/背景/灯光约束和同一类 prompt，避免旧黑衣 A 段与白衣 B 段混用。
- 22 帧五段均成功；最终拼接修正为不重复 Trim（runner 已对续段完成 22 帧 Trim，拼接层仅按每段 124 帧裁齐）。
- 有效成片：`/home/sean/projects/ComfyUI/output/video/hk_a_mc_5seg_context22_unified_trimmed_original_audio_16x9.mp4`，768×432/24fps，画面约 25.792s、原始音频约 25.834s。

### 2026-09-02：22 帧多片段、后续关闭 first_frame

- B-E 全部关闭 `first_frame`，仅保留 prompt + 22 帧 MC latent；A 使用统一浅灰主播图，避免每段首帧重新拉回固定参考图造成跳动。
- B-E 四段重新生成成功，使用连续 latent 链；最终成片：`/home/sean/projects/ComfyUI/output/video/hk_a_mc_5seg_no_first_frame_22_trimmed_original_audio_16x9.mp4`，768×432/24fps，约 25.792s。
- 原始音频回挂，GPU 租约已释放。

### 2026-09-03：严格时间线 A→B→C 基准复核

- 复核发现上一版“保留 B 前 22F”成片的第二接缝构造不严谨，不能作为有效结论。
- 重新使用“说话结束前 22F”参考生成 A/B/C；B/C 不使用 `first_frame`，只保留 prompt + MC。
- 有效基准片：`/home/sean/projects/ComfyUI/output/video/hk_a_mc_speaking_tail_strict_A_B_C_16x9.mp4`，768×432/24fps，视频音频均严格 13.25s。

### 2026-09-03：修正 C 段音频时间线

- 定位上一版 C 音画不同步原因：C 错误复用了 B 的输入音频片段，导致 C 的嘴型对应旧时间段，而成片回挂的是更后面的母带。
- C 已改用自身切点前 22F/约 0.9167s 的音频预滚（约 8.000s 起），重新生成并拼接。
- 修正版：`/home/sean/projects/ComfyUI/output/video/hk_a_mc_speaking_tail_strict_A_B_C_correct_C_audio_16x9.mp4`，视频/音频均严格 13.25s。

### 2026-09-03：正确逐段音频预滚的五段链

- A→B→C→D→E 五段全部成功；A 使用说话尾部 22F，B-E 关闭 `first_frame`，每段分别使用自己切点前 22F/约 0.92s 的原始音频预滚。
- 有效成片：`/home/sean/projects/ComfyUI/output/video/hk_a_mc_5seg_correct_timeline_16x9.mp4`，768×432/24fps，视频 24.4167s、音频 24.384s；GPU 租约已释放。

### 2026-09-03：按语音停顿切点的五段链

- 选用接近停顿/句末的切点：0 → 4.458 → 8.208 → 14.083 → 17.833 → 23.708s；不再按固定 5.166s 切段。
- 五段均生成成功；B-E 使用各自切点前 22F 音频预滚、关闭 `first_frame`、Trim 后连接。
- 成片：`/home/sean/projects/ComfyUI/output/video/hk_a_mc_semantic5_strict_timeline_16x9.mp4`，768×432/24fps；实际画面 23.667s、音频 23.709s，最后少 1 帧需后续统一帧数规则。

### 2026-09-03：B 前 22F 后无嘴型的初步归因

- 检查四组未裁剪 B（`h3_avatar_mc_break22_debug/break1..4`，每组 56F，`first_frame=false`）：B[0:22] 是 MC context，B[22:] 才是新生成区；四组并非 B[22:] 永远完全不动，break1/3 在后续音频重新进入后能明显张嘴，break2/4 在对应静音区保持闭嘴。
- 四组 B 音频均为 2.3333s，22F 对应 0.9167s。静音检测：break1 为 0.472–0.928s，break2 为 0.547–0.992s，break3 为 0.875–1.238s，break4 在 0.974–1.223s 还有一段静音。因此 B[22] 恰好位于或接近断句后的静音，不应期待第 23F 立即张嘴。
- 当前证据更支持“断句后真实音频处于静音/低能量，模型保持闭嘴”是主因；“context 第 0F 的嘴型状态导致后续不说话”仍需控制变量测试，不能仅凭这四组下结论。下一轮应固定同一 prompt/主播/seed，分别选择 context 第 0F 为闭嘴、微张、明显张嘴的说话尾部，并比较 B[22:] 在相同音频位置的嘴型。

### 2026-09-03：F22 连续语音测试设计

- 测试目的：确认 B[0:22] 均为断点前说话尾部时，B[22:] 能否在不同断点和音素条件下继续张嘴；将“正常停顿”“说话中间切断”“低能量/不明显吐词”分开。
- 三类断点：①纯 break：最后 22F 是完整尾词，断点后有约 80–150ms 短停顿再进入下一词；②说话中间：在连续元音/词中切断，断点后无静音；③不明显吐词：切在弱辅音、轻声、鼻音或低能量音节附近，音频有声但能量较低。
- 语言矩阵：粤语使用现有 `hk_a_30s.wav`；普通话和英语用同一主播图、同一 prompt 生成短控制音频，日语作为可选第四语言。首轮 3 语言 × 3 断点 = 9 个 B 片段，每段 56F、context_length=22、`first_frame=false`、不裁剪保存诊断版。
- 判定指标：记录 B[22] 后首次明显张嘴帧、音频有效能量起点、二者差值；同时观察身份/位置/背景是否漂移。若只有重新开口延迟而人物稳定，归为音频触发/局部运动惯性；若身份和画面也逐段偏移，才归为 latent 漂移叠加。

### 2026-09-03：F22 三语言九组首轮生成

- 粤语/普通话/英语各生成 1 个 3.75s A 基准和 3 个 2.333s B 诊断片（纯 break、说话中间、弱起音），全部 12 个任务成功；B 均 `first_frame=false`、context=22、trim=false。
- 原始输出为 768×448；已统一中心裁切为严格 768×432/24fps，并按语言合成三段对照片：`/home/sean/projects/ComfyUI/output/video/h3_avatar_f22_lang_16x9/yue_3case_compare.mp4`、`zh_3case_compare.mp4`、`en_3case_compare.mp4`。
- 首轮抽帧观察：三种语言三类条件在 B[22:] 均最终重新出现嘴型，没有“永久闭嘴”；差异主要是重新开口延迟。后续需按音频起音帧逐组量化延迟，确认哪类断点最容易触发运动惯性。
- 运行峰值观测登记：GPU 约 21.9–22.3GB/24GB，系统内存约 47.6GB/54.9GB；租约已释放。

### 2026-09-03：暂停人工拼接音频的扩展批次

- 用户确认声音在中间出现小卡顿会影响判断；已停止尚未完成的 18 组 clean-audio 扩展批次，ComfyUI 队列已确认为空，租约已释放。
- 已完成的旧三语言九组仅作为初步嘴型观察，不作为音频连续性结论。下一轮改用单段连续原始母带，只移动 F22 接缝位置，避免 TTS 片段拼接成为混淆变量。

### 2026-09-03：连续粤语母带 F22 三断点复测

- 使用同一份 `/home/sean/projects/ComfyUI/input/hk_a_30s.wav`，按真实时间窗制作三组 A/B：纯 break `T=7.837875s`、说话中间 `T=5.5s`、弱起音 `T=6.2s`。B 音频均直接截取母带 `[T-0.916667, T+1.416667]`，没有 TTS 拼接或 crossfade。
- A 三组和 B 三组全部成功；16:9 结果位于 `/home/sean/projects/ComfyUI/output/video/h3_avatar_f22_master_16x9/`，单独文件分别为 `b_pure_break_00001_.mp4`、`b_mid_speech_00001_.mp4`、`b_weak_onset_00001_.mp4`。
- 抽帧初检：说话中间和弱起音两组在 B[22:] 保持连续嘴型；纯 break 在真实停顿期间闭嘴，声音重新进入后再开口。该批可作为无人工音频拼接的有效基准。
- GPU 约 21.5GB/24GB，系统内存约 48.2GB/54.9GB；租约已释放。

### 2026-09-03：本轮收束与后续方向

- 用户目测确认连续母带三组测试的嘴型都很好：F22 本身可以连续衔接，之前的异常更可能来自视频时间线偏移、错误 Trim、重复首帧锚定或音频窗口错位，而非 F22 口型条件失效。
- 三语言首轮对照中的三遍并非重复：顺序为纯 break、说话中间、弱起音；但因测试音频由 TTS 片段拼接，出现声音小卡，不能用于音频连续性结论。后续音频测试必须使用单段连续母带。
- 已验证的有效基准：`/home/sean/projects/ComfyUI/output/video/h3_avatar_f22_master_16x9/b_pure_break_00001_.mp4`、`b_mid_speech_00001_.mp4`、`b_weak_onset_00001_.mp4`；三者均来自 `hk_a_30s.wav` 的严格时间窗，768×432/24fps。
- 机制结论：FL2VA 的 MC latent负责动作/时间连续；Ref2VA/MultiRef负责多参考身份、构图和外观锚定。MultiRef 不等于 Ref2VA，也不是必须依赖 Ref2VA；二者可组合。FL2VA 的 `last_frame` 是生成目标尾帧，不是把 A 尾帧当作 B 开头；MC 已负责 B 开头的 22F。
- 高清尾帧建议：不要用 Krea 重新生成；应从 A 实际最后一帧抽帧后做普通超分，再作为软参考。latent upscale 主要提升细节，不能优先解决身份/位置/亮度漂移，建议放到稳定长链之后。
- 推荐后续测试顺序：当前 FL2VA+MC 22F 基线 → Ref2VA/MultiRef + 主播身份图 → 再加入 A 最后一帧真实抽帧图；不使用每段硬 `first_frame`，避免与 MC pinned head 冲突。
- Ref2VA+MC 身份锚定最小对照（2026-09-03）：新增 `experiments/h3_digital_human/ref2va_mc_identity_min_cases.json`，使用同一主播参考图、连续粤语 A/B 音频和 22F MC；三项为 Ref2VA 首段 A、续段仅 MC 无参考图 B、续段 MC + 同一身份参考图 B。
- 三项全部成功，结果见 `experiments/h3_digital_human/ref2va_mc_identity_min_cases.json.results.json`：A 90F/3.75s/88s/峰值 23.4GB；B 无参考图 136F/5.667s/120s/23.5GB；B 身份参考图 136F/5.667s/128s/23.1GB。
- 输出：`/home/sean/projects/ComfyUI/output/video/h3_avatar_ref2va_mc_identity_min/A_00001_.mp4`、`B_no_ref_00001_.mp4`、`B_identity_ref_00001_.mp4`。三条均为 768×448/24fps；Ref2VA 续段与 MC 节点兼容。
- 接缝抽帧初检：A 尾帧、B 起始和约 22F 后，人物脸、服装、灰背景、构图未见明显漂移；两种 B 续段均能继续张嘴。当前仅记为单样本可行性证据，不升级为长链身份收益结论。
- 资源事实：Ref2VA+MC 在本机 768×448、20 steps、22F context 的续段约 120–128s/5.667s，峰值显存最高约 23.5GB，余量很小；不适合并行跑批。
- 下一步：把 A 实际最后一帧抽帧作为第三类软参考，与“仅 MC”和“固定主播图 + MC”做同切点对照；随后再评估 4 段小链。不要把本轮单样本视觉初检升级为长链身份结论。
- 协作记录：`hive-task claim` / `hive-state set` 因沙箱对 `~/.pi/agent/runtime` 只读而失败；项目内矩阵、结果和本进度已正常落盘。
- 软尾帧补测（2026-09-03）：从 Ref2VA 首段 A 的实际最后一帧抽出 `/home/sean/projects/ComfyUI/input/h3_avatar/ref2va_identity_min_A_last.png`（768×448），作为 B 的唯一图像参考；沿用同一 A latent、B 连续粤语音频、22F MC 和 20 steps。
- 软尾帧续段成功：`r2v_mc_soft_tail_ref_B` 136F/5.667s，耗时 130s，峰值显存 21.7GB；结果 `/home/sean/projects/ComfyUI/output/video/h3_avatar_ref2va_mc_identity_min/B_soft_tail_ref_00001_.mp4`，规格 768×448/24fps。
- 抽帧初检：软尾帧 B 起始与约 22F 后人物身份、背景和构图稳定，后续能正常张嘴；与固定主播图 B、无图 B 一样，仅说明三种条件在该短样本可行，未证明哪种对长链更优。

### 2026-09-04：Ref2VA + MC 固定身份图四段小链

- 新增矩阵：`experiments/h3_digital_human/ref2va_mc_identity_4seg_cases.json`；A→B→C→D 使用 `semantic5_seg1..4.wav`，每段均保留同一主播身份参考图，B-D 使用上一段保存的 AV latent、`context_length=22`，20 steps。
- 四段全部成功，结果见 `experiments/h3_digital_human/ref2va_mc_identity_4seg_cases.json.results.json`：A 65s/22.4GB，B 96s/22.2GB，C 145s/21.8GB，D 97s/21.9GB。
- 单段输出目录：`/home/sean/projects/ComfyUI/output/video/h3_avatar_ref2va_mc_identity_4seg/`；runner 输出的 B/C/D 已自动删除 22F MC 重叠区，拼接时不能再次 Trim。
- 最终观察片：`/home/sean/projects/ComfyUI/output/video/h3_avatar_ref2va_mc_identity_4seg/joined_4seg_identity_ref_trimmed_16x9.mp4`，768×432/24fps，19.375s，465F；音画来自各段已 Trim 结果后拼接。

### 2026-09-07：中文 Breeze 音频驱动 30 秒 FL2VA+PDD+MC 初测

- 使用本地 Breeze TTS 2 生成固定主持人口吻的中文母带 `/home/sean/projects/ComfyUI/input/h3_avatar/zh_breeze_test_30s.wav`，实际 41.600s、24kHz 单声道；本轮取前 30s。
- 按 0–10s、9.083–20s、19.083–30s 切分，B/C 各保留约 0.92s MC 音频预滚；新增矩阵 `experiments/h3_digital_human/zh_breeze_mc_30s_cases.json`。
- A/B/C 均成功：A 260F/10.833s，B 255F/10.625s，C 255F/10.625s；单段耗时约 104–128s（A 首次冷启动约 155s），B/C 使用 `context_length=22`，均完成 trim。
- 三段按真实输出帧数拼接并挂回同一 Breeze 母带：`/home/sean/projects/ComfyUI/output/video/h3_avatar_zh_breeze_mc_30s/joined_30s_master_audio.mp4`，719F/24fps/30.000s。
- 结论边界：中文 Breeze→H3 FL2VA/PDD→MC→原始母带回挂在 30s 规模已跑通；尚未做人工口型/接缝目视验收，也未与 Extender 2.0 做同条件对照。
- 时间线复核：原始拼接误用了 H3 实际输出全长（A=260F、B/C=255F），直接累加为 770F 后再裁到 30s；但 Breeze 母带切点是 10s/20s，A 接缝实际落在 10.833s，B 后累计偏移约 1.458s，故音画不同步很可能从 A→B 第一处接缝开始，而非从 C 才开始。
- 已生成严格时间线修正版：每段取前 240F（10.000s），三段共 720F，再挂同一 Breeze 母带；产物 `/home/sean/projects/ComfyUI/output/video/h3_avatar_zh_breeze_mc_30s/joined_30s_master_audio_timeline_fixed.mp4`。

### 2026-09-07：中文 Breeze 音频驱动 30 秒 Ref2VA+MC 对照

- 按用户要求改用 Ref2VA：固定主播参考图 + 外部中文 Breeze 音频参考 + Motion Context，标准 20 steps，不叠加 PDD/Turbo；配置 `experiments/h3_digital_human/zh_breeze_ref2va_mc_30s_cases.json`。
- A/B/C 全部成功：A 240s/21.9GB，B 290s/21.7GB，C 290s/19.6GB；三段均使用 context=22、audio context=24 和同一主播身份图。
- 严格按每段 240F 拼接并挂回同一 Breeze 母带：`/home/sean/projects/ComfyUI/output/video/h3_avatar_zh_breeze_ref2va_mc_30s/joined_30s_master_audio_timeline_fixed.mp4`，720F/30.000s。
- 尚未人工看片；待比较 FL2VA 与 Ref2VA 的 A→B、B→C 接缝和 C 段后半段漂移。Ref2VA 速度约为 FL2VA 的 2 倍以上，但本轮目标是连续性而非产能。

### 2026-09-07：Ref2VA + NativeAudioLock + MC 口型修正版

- 用户目视反馈上一轮 Ref2VA 口型没有对上；复核确认上一轮只把 Breeze WAV 作为 `ref_audios` 参考，没有接 `NativeAudioLock`，因此最终回挂 Breeze 母带时不能保证逐帧口型一致。
- 修正 `scripts/h3_mc_runner.py`，加入 Ref2VA + NativeAudioLock + Motion Context 组合，并修复音频锁/Trim/SaveLatent 节点编号冲突。
- A/B/C 全部成功：A 222s/20.6GB，B 281s/20.2GB，C 280s/20.0GB；严格按每段 240F 拼接并挂回 Breeze 母带。
- 修正版产物：`/home/sean/projects/ComfyUI/output/video/h3_avatar_zh_breeze_ref2va_audio_lock_mc_30s/joined_30s_master_audio_timeline_fixed.mp4`。
- 该版才是有效的 Ref2VA 口型对照；待用户检查口型后，再判断 Ref2VA 是否同时改善接缝/后段漂移。
- 三处接缝抽帧（约 4.46s、8.71s、15.08s 前后）初检：身份、服装、浅灰背景、构图保持稳定，动作变化连续，未见明显亮帧/身份漂移；这只是抽帧初检，仍需用户完整观看确认，不能替代长片验收。
- 拼接纠错记录：首个命令误对 runner 已 Trim 输出再次裁 22F，生成了错误的 399F 中间片；已用未重复裁切的 465F 版本覆盖为最终观察片，错误片未作为结果引用。
- 当前结论：Ref2VA + 固定身份图 + MC 在 4 段/约 19.4s 小链可运行且初步稳定；下一步可做同一切点的“纯 MC 无图”4 段对照，或进入 30s/5 段身份稳定性验证，优先用户目视选择后再扩展。

### 2026-09-04：四段链原始母带复挂与接缝复核

- 将原始粤语母带 `/home/sean/projects/avatar-runtime/data/duix/face2face/hk_a_30s.wav` 从 0s 起直接挂到四段视频，未重新编码视频：`/home/sean/projects/ComfyUI/output/video/h3_avatar_ref2va_mc_identity_4seg/joined_4seg_identity_ref_original_audio_16x9.mp4`。
- 原始音频版规格：768×432/24fps/465F/19.375s，音频为 32kHz 双声道 AAC；用于隔离各段 H3 解码音频的编码/拼接跳变。
- 用户反馈：原四段版声音有跳变；1→2 接缝可察觉且出现亮帧，后续接缝有轻微视觉区别。帧统计支持该观察：第一接缝附近 YAVG 约 `163.6 → 165.5 → 162.7`，后两处约 `162.4 → 162.4 → 161.0`、`159.0 → 159.0 → 159.5`。
- 方案判断：最终音轨固定使用原始母带；NativeAudioLock 只作为口型/表演条件，不使用 H3 各段解码音频做最终拼接。视觉上优先比较“B-D 仅 MC 无图”与“B-D 固定身份图 + MC”；若无图明显更稳，再测逐段真实尾帧软参考。颜色/亮度校正和 2–4F 软焊接只能作为后处理兜底，不能替代条件链路对照。
- 用户复核反馈：原四段版声音有跳变；1→2 亮帧明显，后续接缝仍能察觉轻微视觉区别。已制作原始母带复挂版供直接试听；其视频帧不变，因此声音若平滑即可把音频跳变从视觉问题中隔离出来。
- 时间线疑点：输入 `semantic5_seg2..4.wav` 时长分别为 4.6667/6.7917/4.6667s，但 runner 已 Trim 后的 B/C/D 视频时长为 4.25/6.375/4.25s；不能再凭参数名假设实际交付裁掉了 22 个输出帧，后续应以节点实际 `trim_frames`/输出帧数和原始母带切点逐段对齐。该疑点优先级高于继续调参考图。
- 当前讨论方案：①最终音轨永远使用原始母带；②先跑同切点“B-D 仅 MC、无固定身份图”四段对照，判断固定参考图是否引入亮度/外观重绘；③若无图更稳，再做逐段真实尾帧软参考（A 尾帧→B，B 尾帧→C，C 尾帧→D）；④后处理只做轻微亮度/色彩匹配和 2–4F 焊接，避免用 crossfade 掩盖尚未解决的时间线错位。
- 2026-09-04 时间线核查修正：H3 `length` 在 `nodes_minimax_h3.py` 中通过 `align_frame_count` 向上吸附到 `17k+5`；因此请求 B/D=112F 实际生成124F，MC trim=22F后交付102F；请求 C=163F实际生成175F，trim后交付153F。22F 确实生成并被 Trim，但输入音频的“可见段”时长不能直接等于输出时长。
- 已按原语义切点 `0 → 4.4583 → 8.2083 → 14.0833 → 17.8333s`，从现有已 Trim 片段取 A=107F、B=90F、C=141F、D=90F，再挂 `hk_a_30s.wav` 生成时间线修正版：`/home/sean/projects/ComfyUI/output/video/h3_avatar_ref2va_mc_identity_4seg/joined_4seg_identity_ref_timeline_fixed_original_audio_16x9.mp4`，768×432/24fps/428F/17.8333s。
- 修正版音画时间线已对齐；抽帧仍可见 1→2 的视觉亮帧和后续轻微差异，说明时间线/音频问题修正后，视觉接缝仍独立存在。后续应分开处理：先用修正版判断口型，再做无固定身份图和逐段尾帧参考对照。

### 2026-09-04：真实未 Trim 片段与可移动接缝 A-B 对照

- 核查发现旧 `h3_mc_runner.py` 对 `trim:false` 无效：只要存在 `mc` 就无条件连接 Trim。已修正为仅在 `trim` 默认值为 true 时连接 Trim，并通过 `py_compile`。
- 重新生成真实未 Trim B/C/D：`/home/sean/projects/ComfyUI/output/video/h3_avatar_ref2va_mc_identity_4seg_untrim_real/B_00001_.mp4`、`C_00001_.mp4`、`D_00001_.mp4`；分别为完整 124/175/124F，latent 链也分别保存，可用于后续移动接缝测试。
- 新增参数化拼接脚本 `scripts/h3_join_overlap_shift.py`：`--keep-head k` 控制 A 末尾减少 kF、B 起点从 22-kF 开始，同时保持总输出长度不变。
- A-B 严格对照已生成至 `/home/sean/projects/ComfyUI/output/video/h3_avatar_ref2va_mc_identity_shift_real/`：
  - `AB_k0_original_audio_16x9.mp4`：A 107F + B[22:112]，接缝 4.4583s；
  - `AB_k5_original_audio_16x9.mp4`：A 102F + B[17:112]，接缝 4.25s；
  - 两版均 197F/8.2083s，并直接挂 `hk_a_30s.wav`。
- 抽帧对照可见两种版本的接缝内容随位置移动，k=5 不是消除模型差异，而是把接缝从 A 尾部换到 B 的 MC 头部过渡区；需用户试听/观看确认哪一版更自然。
- 之前生成的 `AB_k0/k5`（目录 `h3_avatar_ref2va_mc_identity_shift`）因输入 B 已被错误 Trim，不作为结果使用。

### 2026-09-04：B→C k=0 原始母带对照

- 使用真实未 Trim B/C，严格取 B[22:112]=90F、C[22:163]=141F，保持 `k=0`，原始母带从 4.4583s 起挂接。
- 有效产物：`/home/sean/projects/ComfyUI/output/video/h3_avatar_ref2va_mc_identity_shift_real/BC_k0_original_audio_16x9.mp4`，231F/9.625s，768×432/24fps；接缝位于片内 3.75s，即母带约 8.2083s。
- 曾生成一个错误的同名版本（把 `-ss 4.4583` 误作输出 seek，只有124F），已用正确输入音频 seek版本覆盖，不引用旧版本。
- B→C 接缝附近 YAVG 约 `161.72 → 161.08 → 161.12`，未出现 A→B 的明显亮帧；该结果支持“亮帧/高亮问题主要集中在 A→B，可能与首段到首个 MC 续段的状态过渡有关”，但仍需用户目视确认。

### 2026-09-04：中文驱动 B→C 最小复现

- 用 `edge-tts` 新生成普通话驱动：`/home/sean/projects/ComfyUI/input/h3_avatar/zh_probe_20260904/zh_driver.wav`，24kHz 单声道，9.288s；按 24fps 切出 `zh_A.wav` 3.750s、`zh_B.wav` 4.6667s（含 22F 前导）、`zh_C.wav` 2.700s。
- 新增测试矩阵：`experiments/h3_digital_human/ref2va_mc_zh_probe_20260904_cases.json` 及 Trim 对照矩阵 `..._trim_cases.json`。
- 中文 Ref2VA+MC 未 Trim 产物：A=90F、B=124F、C=73F；Trim 后 B=102F/4.25s、C=51F/2.125s。B/C 均严格减少 22F，且音频同步减少，未发现“F22 未切除”的节点 BUG。
- B→C 可播放拼接产物：`/home/sean/projects/ComfyUI/output/video/h3_avatar_ref2va_mc_zh_probe_20260904/BC_trim_joined_original_generated_audio.mp4`，153F/6.375s；B/C 各自输出音频随视频生成，作为接缝试听基准。
- 当前判断：B→C 大跳变若在该中文片仍存在，优先指向 MC 续段首帧/latent 条件的视觉连续性，而不是 Trim 数量；“切 C 后端后音画不同步”还需以这版的片内口型和原始母带对齐进一步确认。另一个已知风险是 C 的有效时长由 `length` 吸附后再 Trim 决定，不能用输入音频名义时长直接拼接。

### 2026-09-05：Ref2VA A/B/C 加速对照（排除 Spectrum/MC）

- 用户要求直接比较三条：A=原生 Ref2VA 20 步；B=Ref2VA 专用 PDD Acc 8 步；C=LightX2V Ref2VA Turbo v1.0 768p 8 步。三条固定同一参考图 `anchor_host_blank_gray_16x9.png`、同一粤语音频 `speaking_s1_a.wav`、同一 prompt/seed=42090301、768×448、90F（3.75s），均使用 NativeAudioLock，不叠加 Spectrum、MotionCache 或其他 step-cache。
- 权重补齐：PDD 原始 `MiniMax-H3-Ref2VA-Acc-8Step.safetensors` 与 LightX `minimax_h3_ref2v_turbo_8step_v1.0_768p_comfyui_bf16.safetensors` 均完整下载；Turbo 使用专用 shift 6/3，PDD 使用 12/3 + 专用 sigmas/Euler。
- 三条均成功：A `75s`，B `56s`，C `55s`；峰值显存未单独记录但任务结束后 RTX 4090 仅占用约 0.94GB，未 OOM。输出：`/home/sean/projects/ComfyUI/output/video/abc_ref2va/{A_base20_00001_.mp4,B_pdd8_00001_.mp4,C_turbo8_00001_.mp4}`。
- 抽取四个同时间点初检：A/B/C 人物身份、灰背景、服装和构图均稳定；未见明显脸部/手部崩坏或亮帧。单帧/接触表不足以判定口型和整段动作质量，需用户完整看片或后续逐帧/音频专项。
- 重要音频事实：三条都走同一外部音频锁定条件，但 MP4 内解码后的 PCM MD5 不同（A `908725...`、B `7f1572...`、C `2f7996...`），因此不能写成“输出音频逐字节相同”；只能说测试使用了同一音频条件，需进一步试听确认是否存在可感知差异。
- 当前速度结论仅是本机单样本：PDD 8/C Turbo 8 比原生20步快约26–27%，两者速度几乎相同；尚未形成质量胜负定论。下一步优先用户目视/试听 A/B/C，再决定 PDD 或 Turbo 作为 Ref2VA 快车道。
