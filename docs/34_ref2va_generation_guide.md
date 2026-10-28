# H3 普通 Ref2VA 生成手册

> 普通 Ref2VA 的唯一日常入口。历史矩阵见 [09](09_h3_test_plan.md)、[19](19_h3_dual_track_gap_test.md)，提示词细则见 [17](17_h3_prompt_writing_rules.md)，连续视频见 [33](33_h3_mc_engineering.md)，VDN 独立路线见 [35](35_vdn_h3_ref2va_route.md)。
> 最后更新：2026-10-19（新增 PDD6 + LightVAE 超速预览实跑确认，并记录不在当前快车道/预览车道接 Sol-Attn 的选型）。

## 0. 当前正式路线（2026-10 更正）

普通 Ref2VA 成片的现行链条：

```
Ref2VA int8 convrot 底模
  → PDD Acc（8 nfe，euler，节点 sigmas）
  → PatchSageAttentionKJ（sage_attention=auto）
  → MiniMax H3 Low VRAM Attention（head_chunks=4）
  → MiniMax H3 Chunk FeedForward（chunks=4，seq_threshold=4096）
  → MiniMaxH3NativeAudioLock（外部台词锁口型时）
  → VRAM_Debug(unload_all_models) → VAEDecodeTiled
```

### 快车道 / 慢车道（Ref2VA 采样对照的简称）

本文及后续讨论中，**快车道**特指普通 Ref2VA 的 PDD 8 步路线；**慢车道**特指原生标准 20 步路线。不要把这里的“快车道”与 Turbo/LightX2V 4/8 步预览档混为一谈。历史同参对照见 [ledger C-20260915-01](../.pi/ledger/h3-speed.md)。

| 路线 | 采样过程 | 节点/组件 | 定位 |
|---|---|---|---|
| 快车道 | Ref2VA int8 ConvRot → PDD Acc（`nfe=8`）→ `euler` + PDD 节点 sigmas → 8 步采样 | `PDD Acc` + `SageAttention`；正式出片链可再加 KJ `MiniMax H3 Low VRAM Attention(head_chunks=4)`、`MiniMax H3 Chunk FeedForward(chunks=4, seq_threshold=4096)`；需要外部音频锁口型时接 `MiniMaxH3NativeAudioLock`；不接 Sol-Attn | 少步数快速生成；当前默认正式出片路线是在此基础上叠加加速/显存组件 |
| 慢车道 | 同一 Ref2VA 底模 → `res_multistep` + `simple` scheduler → 20 步标准采样 | 标准 `KSamplerSelect`、`BasicScheduler`、`BasicGuider`、`SamplerCustomAdvanced`；可接 `PatchSageAttentionKJ`。若测试目标是隔离采样差异，其他条件保持一致 | 高步数质量对照基线，不代表默认正式出片配置 |
| 超速预览车道 | Ref2VA int8 ConvRot → PDD Acc 官方 8-step sigmas → 从完整 schedule 只执行前 6 次评估 → 解码 denoised x0 estimate | `euler`、shift 12/3、`PatchSageAttentionKJ(auto)`、LightVAE INT8 H3 decoder；不接 Sol-Attn、KJ LowVRAM 双节点或 ChunkFeedForward；默认 928×544、约 5 秒、仅画面 | Sean 于 2026-10-19 选择默认 6 次评估；单次确认实测 28.168 秒产出 124 帧/5.167 秒；只看构图、主体大形和动作方向，不验收细节、身份稳定性、动作时序或音频；初版 3 步实测见 [run 001](../experiments/sean_h3_preview_lane_20261019/run_001/run-log.md)，6 步确认见 [run 011](../experiments/sean_h3_preview_lane_20261019/run_011_pdd6_workflow_confirmation/run-log.md)，默认工作流为 [sean_h3_preview_pdd6_lightvae_api.json](../workflows/sean_h3_preview_pdd6_lightvae_api.json) |

2026-10-23 扩规格试跑使用独立 `h3-preview-v2` definition，在不改动 `h3-preview-v1` 边界的前提下测试 1088×608、8 秒：runner 161.891 秒完成，较同 seed/提示词/画布/时长的快车道音频版单次快约 7%；该规格仅单次实测，抽帧仍见近景裁掉脸、LightVAE 细节偏软，不能外推为稳定吞吐或质量基线。详见[试跑 QC](../experiments/h3_preview_8s_1088_20261023/solar_oracle/run_002_h3_preview_v2/QC.md)。

两条路线共用参考条件编码、latent 初始化和输出解码；进行快慢车道对照时，两边都使用 SageAttention 并尽量保持其他条件一致。采样后可按显存情况加入 `VRAM_Debug(unload_all_models)` 与视频 `VAEDecodeTiled`。PDD 对照实测的主要提速来自步数从 20 降至 8，单步耗时近似；PDD 8 步的画质仍应按具体素材验收。KJ 双节点用于降低正式成片的显存峰值，不是快车道定义本身的必要条件。

固定调用入口：共享 [工作流接口](/home/sean/.pi/agent/skills/comfyui/references/workflows.md) 提供 `h3-preview-v1`、实验扩规格 `h3-preview-v2`、`h3-fast-v1`、`h3-slow-v1` 四条 H3 流程。调用方只传参数与有序参考图；共享模板是固定调用快照，仓库 `workflows/` 中的图是维护来源。预览接口封装实测见 [接口实验](../experiments/h3_workflow_interface_20261022/REPORT.md)；快、慢车道定义已接入。`h3-fast-v1` 的标准音频解码、MP4 音轨封装已于 2026-10-23 完成一次 8 秒真实生成验证（见[音频样片](../experiments/h3_fast_audio_test_20261023/solar_oracle/run_003_h3_fast_v1_audio/QC.md)）；该验证确认 AAC 音轨存在且时长匹配，但未做主观试听，不能据此判断声音内容质量或作为多样本质量基线。慢车道仍按共享 definition 状态另行完成 Live preflight 和生成验收后，才可升级为已验证基线。

维护快/慢车道时成对更新 [`h3-fast_api.json`](../workflows/h3-fast_api.json) 与 [`h3-slow_api.json`](../workflows/h3-slow_api.json)，再同步用户级共享 skill 的 `assets/workflows/{h3-fast-v1,h3-slow-v1}.api.json` 节点图和同名 `.json` 参数定义/来源哈希。快车道音频由采样联合 latent 经 `VAEDecodeAudio` 解码后接到 `CreateVideo.audio`；2026-10-23 的[真实生成记录](../experiments/h3_fast_audio_test_20261023/solar_oracle/run_003_h3_fast_v1_audio/QC.md)验证了该接线及 AAC 封装。两条图都必须启用 `PatchSageAttentionKJ(sage_attention=auto)`；快车道固定 PDD8 + Euler + 节点 sigmas，慢车道固定原生 `res_multistep` / `simple` / 20 步。仅更改提示词、尺寸范围或模型参数时，仍同步更新 definition 的默认值、边界、映射和验证状态。保持预览 `h3-preview-v1` 独立，避免把 PDD 前六段和 LightVAE 设置带入完整 8 步快车道。

**超速预览车道**与快车道的区别是截断采样：它仍使用训练好的 PDD 8-step 完整 sigma schedule，只执行前 6 个 sigma 区间，并将 `SamplerCustomAdvanced.denoised_output` 作为 x0 估计交给 LightVAE 解码；不是把 PDD 改成 6 步蒸馏模型，也不从 latent 中途状态直接套完整 VAE。首次验证运行前 3 步，约 37.8 秒生成 928×544、124 帧/5.167 秒预览；768×448 的 3/4/5/8 步对照见 run 004/005。默认 6 步经 [run 011](../experiments/sean_h3_preview_lane_20261019/run_011_pdd6_workflow_confirmation/run-log.md) 单次实跑确认，28.168 秒输出相同规格；单次运行不足以建立稳定速度基准。当前默认 API 工作流见 `workflows/sean_h3_preview_pdd6_lightvae_api.json`。

若目标仅是看大形和动作，可参考 [run 003 分辨率阶梯](../experiments/sean_h3_preview_lane_20261019/run_003_resolution_ladder/)。同提示词/seed、5 秒、PDD 前 4 次评估的热跑中，640×352 用时约 9.84 秒且人物行走仍可辨，是当前最快可用候选；768×448 用时约 13.16 秒，人物轮廓更清楚。512×288 仅快约 1.2 秒但明显更糊。该分辨率阶梯实验只比较前 4 次评估，没有用于决定当前的 6 次默认值；6 次工作流现已由 [run 011](../experiments/sean_h3_preview_lane_20261019/run_011_pdd6_workflow_confirmation/run-log.md) 单独实跑确认。

768×448 下的 PDD 前 3/4/5 次评估对照见 [run 004](../experiments/sean_h3_preview_lane_20261019/run_004_768_step_ladder/)，8 步见 [run 005](../experiments/sean_h3_preview_lane_20261019/run_005_768_pdd8/)：单次分别约 16.4/12.8/13.9/17.9 秒。非单调的 3 步数据说明单次运行波动不可用来推断步数斜率；8 步比 4 步多约 5.1 秒。画面上 3 次较糊，4 次已能辨认走路姿态，5 次轮廓略清楚，8 步更完整。Sean 将车道默认定为 6 次评估。run 011 单次确认耗时 28.168 秒；计时仍需更多同条件重复运行，不能视为稳定基准。

### Sol-Attn（ComfyUI 官方 `Model Sparse Attention` 节点）调研，2026-10-19

当前 ComfyUI 0.42.1 已内置并注册 `BlockSparseAttention`（显示名 `Model Sparse Attention`），无需另装节点。`method=sol-attn` 对基础 H3 生效；`sla`/`vsa` 需要匹配训练权重。节点默认仅在序列达到 `min_tokens=12288` 且符合 CUDA、BF16、head_dim=128、无 mask 等条件时走稀疏 kernel；否则走 dense backend。官方说明短序列收益有限。用户决策：Sol-Attn 不接入当前 PDD 快车道或超速预览车道；两条标准路线保留 SageAttention 配置。

基于 ComfyUI 核心实现的阅读，`Model Sparse Attention` 会保留先前 attention override 作为 dense fallback，因此从代码路径看可接在 `PatchSageAttentionKJ` 后、sampler/guider 前；这不是当前车道的工作流建议。即使长序列可能受益，短片低分辨率的速度和画面收益也不确定；遵循用户选型，不将 Sol-Attn 加入快车道或超速预览默认图。若未来单独开展 Sol 研究，应作为独立实验与默认路线隔离。

参考：[ComfyUI H3 官方指南](https://docs.comfy.org/tutorials/video/minimax/minimax-h3#speeding-up-generation-with-sparse-attention)、[ComfyUI 核心 `BlockSparseAttention` 实现](https://github.com/Comfy-Org/ComfyUI/blob/master/comfy_extras/nodes_sparse_attention.py)、[Sol-Attn H3 上游节点说明与 GPU 支持矩阵](https://github.com/Saganaki22/ComfyUI-sol-attn)。上游 H3 kernel 的主要性能数据来自 RTX 5090/SM120；SM89（RTX 4090）有社区 smoke test，但尚无该仓库发布的性能基准。

| 档 | 画布 | 采样 | 加速组件 | 实测 |
|---|---|---|---|---|
| 筛选 | 768×448 | Turbo/LightX2V 4 或 8 步 | 可不加 | 4 步约 19.5s、8 步约 30.1s（5s 片段） |
| 正式成片 | 1024×576 | PDD Acc 8 步 | Sage + KJ 双节点 + NativeAudioLock | 20s 约 342s；22s 约 380s；23s 约 425s |
| 短片测试 | 1344×768 | PDD 8 步 | + H3MemoryOptimization + tiled VAE | 15s 约 516s，仅短测 |

正式档内部有两个并行组合，2026-09-16 起以 **KJ LowVRAM 路线为画面稳定性优先方案**：`H3MemoryOptimization + H3 专用 Sage patch` 组合曾出现松树侵入/枝叶贴脸的画面污染（`.pi/ledger/h3-speed.md` C-20260916-03/04），同条件 KJ LowVRAM 未复现。

现行值与兼容边界以 [ledger h3-speed.md](../.pi/ledger/h3-speed.md) 为准（证据链），本文只保留日常入口。筛选档只用于构图、参考图和动作粗筛，不能据此判断动作时序或二采价值。

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
- 可选 LoRA（筛选档）：`minimax_h3_ref2v_turbo_8step_v1.0_768p_comfyui_bf16.safetensors`、`minimax_h3_ref2v_turbo_4step_v0.1_comfyui_bf16.safetensors`、`ComfyUI-H3-LightX2V` Ref2VA Turbo 4/8-step
- 正式档加速组件：PDD Acc（核心自带 LoRA/patch 路线）、`PatchSageAttentionKJ`、KJ `MiniMax H3 Low VRAM Attention`、KJ `MiniMax H3 Chunk FeedForward`；原生 H3 Sparse 只作备用，且不与显式 SageAttention 叠加
- 运行器：`scripts/h3_ref2v_runner.py`；批量用例：`experiments/h3_ref2v/`

节点输入和 shift/sigma 配对见 [.pi/skills/comfyui-ops/references/nodes.md](../.pi/skills/comfyui-ops/references/nodes.md) 与 [params.md](../.pi/skills/comfyui-ops/references/params.md)。

## 4090 参数基线

| 档位 | 画布 | 步数/采样器 | 加速/LoRA | 用途 |
|---|---:|---|---|---|
| 预览 | 768×448 | 4 / `euler` | Ref2V Turbo 4-step | 构图和大致动作 |
| 快速抽卡 | 768×448 | 8 / `res_multistep` | Ref2V Turbo 8-step（或 LightX2V 4/8-step） | 日常筛选 |
| 质量对照 | 768×448 | 20 / `res_multistep` | 无 LoRA + Sage | 与加速档做画质对照的基线 |
| 正式成片 | 1024×576 | 8 / PDD 节点 sigmas | PDD Acc + Sage + KJ 低显存双节点 | 默认出片路线（第 0 节） |

H3 帧数按 `17k+5` 网格对齐；请求帧数不一定等于输出帧数，时长必须以实际帧数和帧率为准。`1024×576` 在 24GB 卡上可行，但不作为首次抽卡默认值。

## 参考图与提示词

角色、场景、道具分开提供；主体清楚、画幅接近目标画布、无水印和无关人物。多图数量增加会提高绑定难度，不能用拼图代替多张参考。每张图说明“参考什么、保留什么、允许变化什么”。六段式和官方样本见 [17](17_h3_prompt_writing_rules.md)、[18](archive/research/18_ir_sample_teardown.md)。

## 预览、验收与排错

采样后的 Preview 节点不会减少生成时间；live preview 还可能增加显存和传输开销。快速判断应另跑 4/8-step 短帧 case，并固定参考图、prompt、seed。

最低验收：视频可播放且帧率正常；音频存在且时长基本匹配；角色/场景/服装符合参考；无明显亮帧、马赛克、脸手崩坏和动作跳变。采样成功不代表 untiled VAE decode 不会 OOM，长片优先 tiled decode。

- 显存不足：先降到 768×448、减少参考条件、关闭 live preview，并使用 tiled decode。
- 参考不生效：检查图片是否独立、`<Picture N>` 顺序是否一致、prompt 是否明确绑定。
- 视频参考异常：先核对当前 ComfyUI 工作流、DynamicVRAM 日志与 hive-resource 运行时快照；TE 沿用默认设备，不使用历史 CPU 编码方案（见 [09](09_h3_test_plan.md)）。仅在确认实际 OOM 后按证据排查。
- 漂移或接缝异常：先回到无 LoRA 20-step 基线，不要直接叠加 FL2VA LoRA、VDN、SOL 等未验证 patch。

## 当前结论与资料边界

- 无 LoRA 20 steps 仍是画质对照基线；出片默认走第 0 节的 PDD 8 步正式路线；Turbo 8/4 步只用于筛选与预览。
- VDN 不是正式路线：与 KJ `MiniMaxLowVRAMAttention` 不兼容（采样阶段报 `'list' object has no attribute 'shape'`），且 1344×768/15s、1024×576/25s 在采样阶段撞资源边界被取消；详见 [35](35_vdn_h3_ref2va_route.md) 与 ledger C-20260915-06/07、C-20260916-02。
- 4090 上 768×448 是首次生成默认尺寸；1024×576 可行但吞吐和显存压力更高。
- 普通 Ref2VA、VDN、FL2VA、MC 是不同实验维度；比较时记录底模、参考图、帧数、seed、steps、采样器、LoRA、显存和 decode 时间。
- 新增稳定参数/流程进入本文；历史实验留在专题文档；单次耗时、画质印象和踩坑经验同步到 Mem0，并带日期与适用条件。
- 历史产物索引（路径未在本轮复核，不保证仍在 output；当前产物须按项目规则迁入 experiments）：当时双角色测试视频按路线整理到 ComfyUI 输出目录：VDN 见 `output/video/h3_vdn_ref2va_clean/`，PDD + SageAttention 见 `output/video/h3_pdd_sage_ref2va_clean/`；普通 PDD/标准 20-step 对照不再混放在主视频目录。

### 2026-09-19 H3Memory 与 Sparse 路线补充

- `H3MemoryOptimization(chunk_rows=4096, Preserve native, QKV Auto)` 已验证可用于 PDD 流程和原生标准20-step流程；但与 H3 专用 Sage patch 组合时出现过画面污染（见第 0 节），默认仍选 KJ LowVRAM 路线。
- H3 Sparse 使用 `Comfy Kitchen INT8 Sparse` 时必须独立使用，不能和显式 SageAttention 叠加；后者会使 Sparse fallback 到 existing dense。
- 当前正式速度优先仍为 `PDD + SageAttention`；原生备用路线为 `H3MemoryOptimization + H3SparseAttention(30%)`，其优势是相对原生 Dense 降低视频注意力计算，不是替代 PDD。

### 2026-09-15 正式生成选型（历史：VDN 曾被列为长片主力，2026-10 已更正）

> 本节以下三条已被顶部第 0 节取代：正式成片默认 PDD + SageAttention + KJ 低显存双节点（1024×576/20s 约 342s），VDN 保留为可复现的遗留对照，不再是长片主力。
- 默认正式画布：**1024×576（严格 16:9）**。
- 当时默认正式路线：**VDN + 8 steps + NativeAudioLock**；1024×576 下 10/15/20 秒均已跑通，20 秒约 392 秒（2026-10 起不再作为正式路线）。
- 快速试错：**768×448**；VDN 5/10/15/20 秒均跑通，约 90/140/190/230 秒，但该画布不是严格 16:9，主要用于构图、参考图和动作筛选。
- PDD + SageAttention：1024×576/15 秒已成功（约 235 秒）；叠加 KJNodes 的 `MiniMax H3 Low VRAM Attention`（head_chunks=4）与 `MiniMax H3 Chunk FeedForward`（chunks=4、seq_threshold=4096）后，1024×576/20 秒也成功（端到端约 342 秒）。该组合已成为正式成片默认路线。
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
