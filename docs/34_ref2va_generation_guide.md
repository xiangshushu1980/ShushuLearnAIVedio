# H3 普通 Ref2VA 生成手册

> 普通 Ref2VA 的唯一日常入口。历史矩阵见 [09](09_h3_test_plan.md)、[19](19_h3_dual_track_gap_test.md)，提示词细则见 [17](17_h3_prompt_writing_rules.md)，连续视频见 [33](33_h3_mc_engineering.md)，VDN 独立路线见 [35](35_vdn_h3_ref2va_route.md)。

## 第一次生成清单

1. 图片参考用 `workflows/minimax_h3_ref2va_img_api.json`；图片+视频参考用 `workflows/minimax_h3_ref2va_img_vid_api.json`。
2. 使用 `minimax_h3_ref2va_pruned_int8_convrot.safetensors`，不要换 FL2VA 底模。
3. 参考图放在 `/home/sean/projects/ComfyUI/input/ref2va_refs/`；一张图只表达一个条件，不要使用九宫格。
4. 在 prompt 中用 `<Picture 1>`、`<Picture 2>` 绑定参考图，并采用 Ref2VA 六段式；模板见 [17](17_h3_prompt_writing_rules.md)。
5. 4090 首次跑 `768×448`、合法帧长 `39/56/73/99`、8 steps；确认方向后再跑 20 steps 或 `1024×576`。
6. 先验收视频、音频、身份和构图，再进入 NativeAudioLock/MC 或长视频路线。

## 路线分流

Ref2VA 是 H3 的多参考条件生成：文字提示结合角色、场景、道具、动作/风格视频和声音参考，输出视频及原生音频。它适合多参考身份与场景组合；只有首帧并追求快速生成时优先考虑 FL2VA。

| 需求 | 入口 |
|---|---|
| 普通图片参考、5 秒抽卡/成片 | 本文第 3 节 |
| 图片+视频参考 | `img_vid_api.json`；视频参考会增加编码耗时和显存压力 |
| 外部音频精确锁定口型 | [33](33_h3_mc_engineering.md) |
| 多段续接 | 单段验收后看 [33](33_h3_mc_engineering.md) |
| 10–20 秒长序列实验 | [35](35_vdn_h3_ref2va_route.md)；不要与普通路线混记 |

## 资源与工作流

- 底模：`ComfyUI/models/diffusion_models/minimax_h3_ref2va_pruned_int8_convrot.safetensors`
- 文本编码器：`ComfyUI/models/text_encoders/qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors`
- 视频/音频 VAE：`minimax_h3_video_vae_int8_convrot.safetensors` / `minimax_h3_audio_vae_fp32.safetensors`
- 可选 LoRA：`minimax_h3_ref2v_turbo_8step_v1.0_768p_comfyui_bf16.safetensors`、`minimax_h3_ref2v_turbo_4step_v0.1_comfyui_bf16.safetensors`
- 运行器：`scripts/h3_ref2v_runner.py`；批量用例：`experiments/h3_ref2v/`

节点输入和 shift/sigma 配对见 [.pi/skills/comfyui/references/nodes.md](../.pi/skills/comfyui/references/nodes.md) 与 [params.md](../.pi/skills/comfyui/references/params.md)。

## 4090 参数基线

| 档位 | 画布 | 步数/采样器 | LoRA | 用途 |
|---|---:|---|---|---|
| 预览 | 768×448 | 4 / `euler` | Ref2V Turbo 4-step | 构图和大致动作 |
| 快速抽卡 | 768×448 | 8 / `res_multistep` | Ref2V Turbo 8-step | 日常筛选 |
| 质量基线 | 768×448 | 20 / `res_multistep` | 无 | 质量对照 |
| 成片对照 | 1024×576 | 20 / `res_multistep` | 无 | 显存允许时使用 |

H3 帧数按 `17k+5` 网格对齐；请求帧数不一定等于输出帧数，时长必须以实际帧数和帧率为准。`1024×576` 在 24GB 卡上可行，但不作为首次抽卡默认值。

## 参考图与提示词

角色、场景、道具分开提供；主体清楚、画幅接近目标画布、无水印和无关人物。多图数量增加会提高绑定难度，不能用拼图代替多张参考。每张图说明“参考什么、保留什么、允许变化什么”。六段式和官方样本见 [17](17_h3_prompt_writing_rules.md)、[18](18_ir_sample_teardown.md)。

## 预览、验收与排错

采样后的 Preview 节点不会减少生成时间；live preview 还可能增加显存和传输开销。快速判断应另跑 4/8-step 短帧 case，并固定参考图、prompt、seed。

最低验收：视频可播放且帧率正常；音频存在且时长基本匹配；角色/场景/服装符合参考；无明显亮帧、马赛克、脸手崩坏和动作跳变。采样成功不代表 untiled VAE decode 不会 OOM，长片优先 tiled decode。

- 显存不足：先降到 768×448、减少参考条件、关闭 live preview，并使用 tiled decode。
- 参考不生效：检查图片是否独立、`<Picture N>` 顺序是否一致、prompt 是否明确绑定。
- 视频参考极慢或爆显存：检查 CLIP 编码设备，必要时按 [09](09_h3_test_plan.md) 的 CPU 编码方案处理。
- 漂移或接缝异常：先回到无 LoRA 20-step 基线，不要直接叠加 FL2VA LoRA、VDN、SOL 等未验证 patch。

## 当前结论与资料边界

- 无 LoRA 20 steps 是稳妥质量基线；8-step 适合筛选，4-step 只适合预览。
- 4090 上 768×448 是首次生成默认尺寸；1024×576 可行但吞吐和显存压力更高。
- 普通 Ref2VA、VDN、FL2VA、MC 是不同实验维度；比较时记录底模、参考图、帧数、seed、steps、采样器、LoRA、显存和 decode 时间。
- 新增稳定参数/流程进入本文；历史实验留在专题文档；单次耗时、画质印象和踩坑经验同步到 Mem0，并带日期与适用条件。
- 当前双角色测试视频已按路线整理到 ComfyUI 输出目录：VDN 见 `output/video/h3_vdn_ref2va_clean/`，PDD + SageAttention 见 `output/video/h3_pdd_sage_ref2va_clean/`；普通 PDD/标准 20-step 对照不再混放在主视频目录。

### 2026-09-19 H3Memory 与 Sparse 路线补充

- `H3MemoryOptimization(chunk_rows=4096, Preserve native, QKV Auto)` 已验证可用于 PDD 流程和原生标准20-step流程。
- H3 Sparse 使用 `Comfy Kitchen INT8 Sparse` 时必须独立使用，不能和显式 SageAttention 叠加；后者会使 Sparse fallback 到 existing dense。
- 当前正式速度优先仍为 `PDD + SageAttention`；原生备用路线为 `H3MemoryOptimization + H3SparseAttention(30%)`，其优势是相对原生 Dense 降低视频注意力计算，不是替代 PDD。

### 2026-09-15 正式生成选型

- 默认正式画布：**1024×576（严格 16:9）**。
- 默认正式路线：**VDN + 8 steps + NativeAudioLock**；1024×576 下 10/15/20 秒均已跑通，20 秒约 392 秒，是当前长片主力方案。
- 快速试错：**768×448**；VDN 5/10/15/20 秒均跑通，约 90/140/190/230 秒，但该画布不是严格 16:9，主要用于构图、参考图和动作筛选。
- PDD + SageAttention：1024×576/15 秒已成功（约 235 秒）；叠加 KJNodes 的 `MiniMax H3 Low VRAM Attention`（head_chunks=4）与 `MiniMax H3 Chunk FeedForward`（chunks=4、seq_threshold=4096）后，1024×576/20 秒也成功（端到端约 342 秒）。该组合成为速度优先的正式候选，但需要人工确认画质/动作与 VDN 20 秒的一致性。
- 1344×768（约 1 MP）仅建议短片测试：5/10 秒可跑，12 秒开始出现明显系统内存搬运风险，15 秒以上不适合作为当前 24GB 卡的正式路线。
- 当前无需继续补测其他分辨率的长时长；只有在需要把 PDD + SageAttention 作为 20 秒正式替代方案时，再单独补一条 1024×576/20 秒即可。

### 2026-09-23 人物 reference 组织实测（T1/T2）

在 RTX 4090、普通 H3 Ref2VA、768×448、124 帧、`res_multistep`、无 LoRA、20 steps 条件下，完成了单人物 T1 和双人物多对象 T2 对照。T2 使用 4 个方案、5 个 seed（20 条正式视频），资产与逐条结果见 ComfyUI 输出目录中的 `sean_h3_character_reference_manifest.json`。

- 单人物：独立多图 A 与“角色板 + 独立脸部图”B 在 3 个 seed 的静态中景中均保持稳定，当前没有证据表明 B 普遍优于 A。
- 多对象：A（独立多图）、C（双人物构图板）、D（按人物语义簇混合）均保持人物身份、左右站位、法术归属和物品归属；E（一张总板）虽然可生成，但语义分离最弱，不作为默认方案。
- 当前工作流选择：单人物/少对象优先 A；复杂双人物场景优先候选 D；需要强制站位时使用 C；近景保留独立脸部图。该结论适用于本次低动作、无对白、768×448/20-step 条件，进入复杂动作或更高分辨率前仍需复核。

### 2026-09-23 T4 reference 数量消融

T4 在 768×448、124 帧、无 LoRA、20 steps、3 个 seed 下完成 7 个 reference 数量 cell。初始单人物批次因 prompt 在通用句中意外提到 Subject 2 而作废，修正后重新完成 4 个单人物 cell；复杂 D、删除法术、删除物品 3 个 cell 的初始结果有效。

- `id_only`：脸部身份控制最直接，但不提供服装、体型和场景信息。
- `id_wardrobe`：增加全身/服装图后，服装轮廓和身体信息更完整。
- `id_wardrobe_scene`：再加入场景图后，可同时锁定角色与环境；当前抽检未见身份交换。
- `board_face_scene`：角色板压缩多视角，独立脸部图负责近景；当前抽检未见持续的角色板布局复制。
- `complex_D`、`D_minus_spell`、`D_minus_object`：均成功，用于衡量复杂场景中删除低优先级条件的代价；尚未做盲评分，不把单项目视印象写成质量优胜。

工程方面，ComfyUI 开启的 output Asset Seeder 会在每次生成后扫描整个 output 根目录；本批次曾出现约 112 秒全量扫描，造成等待假象。该扫描不是 H3 推理所需，后续大批量实验应关闭资产索引或使用独立 output 根目录。

### 2026-09-14 1024×576 三参考图边界实测

普通 Ref2VA + `minimax_h3_ref2v_turbo_8step_v1.0_768p_comfyui_bf16.safetensors` 在 1024×576、三张角色/英雄/背景参考、NativeAudioLock 条件下完成了 15s/20s，但端到端分别约 393.1s/615.1s，明显慢于同条件 VDN 约 286.39s/391.90s；用户目视反馈为人物参考出现明显走样。因此该 Turbo LoRA 结果不改变上面的 768×448 快速抽卡基线，也不代表 1024×576 的推荐配置。后续单独测试 PDD 5s 与无 LoRA 标准 20-step 5s，不能与本组 Turbo 结果混为同一路线。
