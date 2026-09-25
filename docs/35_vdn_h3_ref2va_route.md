# VDN-H3 Ref2VA 路线与资源维护

> 当前定位：MiniMax H3 Ref2VA 的独立实验路线。本文是 VDN-H3 的唯一维护入口；后续下载、参数、兼容性和实测结论追加到此处。生产主线仍为原生 H3 + PDD/Spectrum/Sage + Motion Context + NativeAudioLock。
>
> 最后更新：2026-09-25

## 1. 路线判断

VDN（Video Delta Net）不是普通缓存，而是 H3 的混合注意力：近邻帧保留精确 softmax attention，远距离时序上下文通过 Video Delta Attention 的线性递归分支处理。目标是让 attention 成本随长序列近似线性增长，而不是解决身份锁定或自动消除跨段漂移。

对当前 RTX 4090 24GB，VDN 的主要价值是验证 10–15 秒及以上 Ref2VA 的显存曲线和长时序可扩展性；5 秒短片不应预设更快。VDN 分支会增加计算，且 Ref2VA 的参考条件、H3 base、Qwen3-VL 编码器和最终 VAE decode 仍可能成为显存瓶颈。

VDN 与 SOL/Scheduled Sol Attention 不叠加：两者都会接管 H3 的 attention 路径，叠加后可能跳过 VDN linear branch，结果不再是经过训练匹配的 VDN。

## 2. 已下载资源

### 节点

- 仓库：`/home/sean/projects/ComfyUI/custom_nodes/ComfyUI-VDN-H3`
- 版本：v1.5.2
- commit：`3eb63496c24ca70faaf8a14b6c75fcb480e34bf1`
- v1.5.2 修复当前 OpenVDN 下载中的 `adapter_spec.json` 识别问题，并保留旧 `adapter_config.json` 回退。
- 无新增 pip 依赖；不修改 ComfyUI core。

### VDN 分支

- 路径：`/home/sean/projects/ComfyUI/models/vdn/vdn-minimax-h3-int8-convrot-comfyui`
- 来源：[drbaph/vdn-minimax-h3-int8-convrot-comfyui](https://huggingface.co/drbaph/vdn-minimax-h3-int8-convrot-comfyui)
- 类型：INT8 ConvRot 8-step DMD 分支
- `metadata.json`：`turbo_num_steps=8`、`video_shift=12.0`、`audio_shift=3.0`
- 包含：`linear_branch/`、`adapters/default/`、`adapters/turbo/`、`model_spec.json`
- 下载完成后目录约 3.3GB，其中线性分支文件约 2.30GB；线性分支采用 INT8，adapter 保持 safetensors。
- 不包含 H3 base；不需要下载 OpenVDN 仓库中约 72GB 的 `h3-base/`。

## 3. Ref2VA 必需资源与选择

推荐使用现有的 H3 Ref2VA INT8 ConvRot 栈：

| 组件 | 推荐文件 | 说明 |
|---|---|---|
| Diffusion base | `minimax_h3_ref2va_int8_convrot.safetensors` | 必须与 Ref2VA 对应，不能换 FL2VA base |
| Text encoder | `qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors` | 24GB 优先量化版 |
| Video VAE | `minimax_h3_video_vae_int8_convrot.safetensors` | 优先用于 decode 显存控制 |
| Audio VAE | `minimax_h3_audio_vae_fp32.safetensors` | H3 原生音频输出 |
| VDN branch | INT8 ConvRot 8-step | 4090 首选 |

可选 VDN 分支：

- BF16 `stage-dmd-step-250`：参考质量路径，但分支约 4.3GB，4090 首测不选。
- INT8 ConvRot 8-step：分支约 2.2GB，官方仓库称输出与 BF16 对齐，适合 24GB 卡。
- `stage-b-step-2000` 50-step：用于普通高步数实验，不与 8-step Turbo adapter 混用。

## 4. 4090 Ref2VA 首测参数

```text
Apply VDN-H3
  vdn_checkpoint       = vdn-minimax-h3-int8-convrot-comfyui
  apply_turbo_adapter  = ON
  strength              = 1.0
  lora_mode             = merge
  branch_weights        = stream
  attention_backend     = grouped
  retain_buffers        = auto

Apply VDN-H3 Advanced
  fast_kernels           = OFF
  window_radius/chunk    = released defaults
  anchor_frames          = both
  text_state             = ON
  linear_branch          = ON
```

`merge` 是 8-step DMD 的硬要求；`bypass` 会在深层累积 bf16 舍入噪声，出现颗粒和质量退化。`fast_kernels` 在 torch 2.10 的 8-step DMD 上已知会漂移，最终渲染关闭。`grouped` 是默认且无需 Triton/compile 的路径。

分辨率/时长阶梯：

1. 512–576 square，5 秒：确认 Ref2VA 图、音频和 VDN 节点链路。
2. 576–640 square，5 秒：与原生 H3/Sage 或 PDD 做速度/质量 A/B。
3. 约 0.4–0.6MP，10 秒：观察 VDN 的实际长序列收益。
4. 约 0.4–0.6MP，15 秒：观察 OOM、系统 RAM、身份和音频连续性。

最终使用 tiled VAE decode；采样成功不代表 untiled decode 不会 OOM。

## 5. 证据与社区资料

- [VDN-H3 ComfyUI 移植仓库](https://github.com/Saganaki22/ComfyUI-VDN-H3)：节点、权重布局、Ref2VA 支持、4090 设置边界。
- [VDN-H3 v1.5.2 release](https://github.com/Saganaki22/ComfyUI-VDN-H3/releases/tag/v1.5.2)：adapter metadata 修复。
- [OpenVDN reference implementation](https://github.com/OpenVDN/vdn-minimax-h3)：原始架构与官方数据中心实现。
- [OpenVDN weights](https://huggingface.co/OpenVDN/vdn-minimax-h3)：BF16 stage 与 adapter 来源。
- [INT8 ConvRot ComfyUI weights](https://huggingface.co/drbaph/vdn-minimax-h3-int8-convrot-comfyui)：24GB 方向的量化分支。
- [Reddit 24GB 社区实测](https://www.reddit.com/r/StableDiffusion/comments/1wcsk7l/comfyui_vdnh3_24gb_v110_update_better_prompt/)：另一实现作者在 RTX 3090 24GB 上测试 5/10/15/20 秒 0.4MP，并测试 10 秒 0.8MP；可作可行性信号，不等同于本节点 v1.5.2 的 4090 基准。

社区证据目前支持“24GB 消费卡可以尝试”，但没有足够的同设置 RTX 4090 Ref2VA v1.5.2 重复基准，不能宣称 15 秒以上稳定生产。

## 6. 验收矩阵（待实测）

| Case | 模式 | 分辨率 | 时长 | 对照 | 关注点 |
|---|---|---:|---:|---|---|
| VDN-R1 | Ref2VA | 576×576 | 5s | 原生/Sage | 能否跑通、画质、音频 |
| VDN-R2 | Ref2VA | 640×640 | 5s | 原生/Sage | 速度、峰值显存 |
| VDN-R3 | Ref2VA | 576×576 | 10s | 原生/Sage | 长序列成本、脸和服装 |
| VDN-R4 | Ref2VA | 约0.5MP | 15s | 原生/Sage | OOM、RAM、时序连续 |
| VDN-R5 | Ref2VA→MC | 768×448 | 多段 | 当前 MC 链 | 跨段身份、接缝、音画同步 |

每次记录：ComfyUI commit、base/VDN 权重、分辨率、帧数、steps/sigmas、seed、参考图数量、峰值显存、系统 RAM、采样时间、decode 时间、视频/音频验收结果。

## 7. 当前结论

- VDN 是长序列 attention 方向，不是身份保持模块。
- RTX 4090 24GB 的首选是 INT8 ConvRot + 8-step + `merge` + `stream`。
- 5 秒只做链路验证；10–15 秒才有比较价值。
- 不与 SOL、Spectrum 或其他会覆盖同一 attention forward 的 patch 盲目叠加；每条路线独立 A/B。
- 2026-09-14 首轮 RTX 4090 实测：576×576 Ref2VA，VDN 8-step 的 5/10/15 秒均成功，端到端约 147/178/241 秒，无 OOM。
- 同设置 10 秒原生 H3 20-step 对照约 364 秒；VDN 单次 A/B 约快 51%。该速度结论尚未经过重复测试，且未包含独立峰值显存记录。
- 输出实际视频时长与帧率正常（约 24fps；5/10/15 秒分别约 5.08/10.13/15.08 秒）。
- 目前只证明“可在 4090 上跑通并具备速度收益”，尚未完成用户目视画质、身份保持、音频连续性验收；在验收前 VDN 仍不进入生产主线。
- 用户已目视确认前轮 VDN 5/10/15 秒输出画质良好，音频质量尚佳。新增写实 16:9 测试：1024×576、10 秒、241 帧、8 steps，成功耗时约 695 秒；峰值显存约 18.2GB，系统内存约 92.3%，无 OOM。该分辨率可行但吞吐较低，仍需长视频连续性专项验收。

### 2026-09-14 双角色 1024×576 基线

在三张图片参考、VDN INT8 ConvRot + Turbo、`res_multistep`、8 steps、`NativeAudioLock` 外部中文双人对白的统一配置下：

| 时长 | 帧数 | DIT采样 | ComfyUI总耗时 | 结果 |
|---:|---:|---:|---:|---|
| 10s | 241 | ≈158s | 194.71s | 成功 |
| 15s | 361 | ≈233s | 286.39s | 成功 |
| 20s | 481 | ≈313s | 391.90s | 成功 |

输出已整理到 `/home/sean/projects/ComfyUI/output/video/h3_vdn_ref2va_clean/`：`vdn_1024x576_10s_audiofx_195s.mp4`、`vdn_1024x576_15s_effects_286s.mp4`、`vdn_1024x576_20s_effects_392s.mp4`。三条均为 1024×576/24fps，使用同一组角色与背景参考，不使用 `ref_audios`。DynamicVRAM 会把 DIT staged 到系统内存，运行期间 ComfyUI RSS 约 50–52GiB；这是当前 24GB 卡的正常代价，但必须监控 Swap 与系统可用内存。
### 2026-09-14 普通 Ref2VA Turbo LoRA 对照

为与 VDN 长时基线对照，使用同一组 3 张参考图、同一 1024×576 画幅、NativeAudioLock 和 8 steps，但移除 `ApplyVDNH3`，改用普通 Ref2VA + `minimax_h3_ref2v_turbo_8step_v1.0_768p_comfyui_bf16.safetensors`。

| 时长 | 端到端计时 | ComfyUI 日志 | 输出 |
|---:|---:|---:|---|
| 15s | 393.1s | 390.41s | `dual_dialogue_15s_lora8_input_lock_1024x576_00001_.mp4` |
| 20s | 615.1s | 626s | `dual_dialogue_20s_lora8_input_lock_1024x576_00001_.mp4` |

本组是 Turbo 8-step LoRA，不是 PDD。与此前 VDN 的 286.39s/391.90s 相比，普通 LoRA 在 1024×576 长视频上更慢。

### 2026-09-15 双角色测试产物整理

- VDN 成片统一目录：`/home/sean/projects/ComfyUI/output/video/h3_vdn_ref2va_clean/`。
- PDD + SageAttention 成片统一目录：`/home/sean/projects/ComfyUI/output/video/h3_pdd_sage_ref2va_clean/`。
- 普通 PDD、标准 20-step、PDD 无 SageAttention，以及重复的冷/热缓存副本已移出主视频目录，放入可恢复隔离目录：`/home/sean/projects/ComfyUI/output/video/_discarded_t33_no_sage_or_duplicate/`。
- VDN 768×448 序列文件：`vdn_768x448_5s_effects_90s.mp4`、`vdn_768x448_10s_effects_140s.mp4`、`vdn_768x448_15s_effects_190s.mp4`、`vdn_768x448_20s_effects_230s.mp4`；VDN 1344×768 文件：`vdn_1344x768_5s_240s.mp4`、`vdn_1344x768_10s_410s.mp4`、`vdn_1344x768_10s_effects_401s.mp4`。
- PDD + SageAttention 文件：`pdd_sage_1024x576_15s_effects_235s.mp4`、`pdd_sage_1024x576_22s_effects_380s.mp4`、`pdd_sage_1344x768_5s_145s.mp4`、`pdd_sage_1344x768_10s_295s.mp4`。
- 本轮整理保留 VDN 和 PDD + SageAttention，主目录不再混入普通 PDD/标准 20-step 对照文件。

### 2026-09-15 当前正式生成建议

- **正式成片首选：VDN、1024×576、10–20 秒。** 其中 20 秒已成功跑通，约 392 秒；这是当前已验证的长视频性价比主线。
- **快速筛选：VDN、768×448、5–10 秒**；如需完整动作预览，768×448 的 15/20 秒也已跑通，但不作为最终画布。
- **PDD + SageAttention、1024×576、15 秒**已成功，约 235 秒；叠加 `MiniMax H3 Low VRAM Attention(head_chunks=4)` + `MiniMax H3 Chunk FeedForward(chunks=4, seq_threshold=4096)` 后，20 秒成功，端到端约 342 秒、ComfyUI 实际执行约 341 秒。它现在可以作为速度优先的 20 秒候选，但仍需人工画质验收。
- 1344×768 在 12 秒以上会显著增加系统内存压力，15 秒超过可接受时间，20 秒 OOM；不进入日常正式生成。
- 暂不需要继续补测其他分辨率；PDD 长片替代路线已用低显存节点完成 1024×576/20 秒验证。

### 2026-09-15 低显存节点冲刺结果

- 组合：普通 Ref2VA + PDD Acc 8-step + SageAttention + `MiniMax H3 Low VRAM Attention`（head_chunks=4）+ `MiniMax H3 Chunk FeedForward`（chunks=4、seq_threshold=4096）+ NativeAudioLock。
- 结果：1024×576、20 秒成功，端到端约 341.7 秒，ComfyUI 实际执行约 340.9 秒；输出为 `/home/sean/projects/ComfyUI/output/video/h3_pdd_sage_ref2va_clean/pdd_sage_lowvram_1024x576_20s_342s.mp4`。
- 资源观察：采样阶段 GPU 约 100%，显存约 23.0GB；系统内存约 45GB 平台运行，解码/收尾阶段最高约 50GB，未 OOM。该方案减少峰值显存，但不能消除长视频对系统 RAM 的需求。

### 2026-09-15 H3-Optimizations 与采样后释放测试

- H3-Optimizations 单独路径：PDD 8-step + SageAttention + `H3MemoryOptimization(chunk_rows=4096, precision=Preserve native, qkv=Auto)`，1024×576/20s 成功，端到端 **335.3s**。该节点在外部 SageAttention 下保留兼容的标准 QKV，但启用 ConvRot MLP/FinalLayer 分块；比 KJ 低显存双节点的约341.7s略快。
- 采样后释放路径：增加 KJ `VRAM_Debug(unload_all_models=true)`，视频使用 `VAEDecodeTiled(tile=512, overlap=64, temporal=64/8)`，音频使用普通 `VAEDecodeAudio`，1024×576/20s 成功，端到端 **336.7s**。可用显存从约13.0GB升至约23.9GB，采样后实际观测显存约6.3GB、系统内存约15GB。
- 结论：**采样后释放模型 + 视频 tiled decode 值得保留**，额外时间约1.4s，主要价值是降低解码收尾峰值，为后续更高分辨率/更长视频争取余量；它不减少采样阶段的系统 RAM 峰值。当前 `VAEDecodeAudioTiled` 对 H3 joint audio latent 报 `IndexError`，不可用于本流程。
- 产物：`/home/sean/projects/ComfyUI/output/video/h3_pdd_sage_ref2va_clean/pdd_sage_h3opt_1024x576_20s_335s.mp4`、`pdd_sage_h3opt_release_tiled_1024x576_20s_337s.mp4`。

### 2026-09-15 PDD + H3-Optimizations 冲击 1344×768/15s

- 同一 H3-Optimizations + 采样后释放模型 + 视频 tiled VAE 路径，PDD 8-step + SageAttention 在 1344×768、361帧/15.083秒下成功，端到端 **516.2s**（约8分36秒），未超过15分钟阈值。
- 采样阶段 GPU约100%、显存约23GB、系统RAM约43GB、swap无明显增长；释放前后可用显存 `22,029,620,168 → 23,915,458,652` bytes，收尾阶段显存约6.7GB、系统RAM约14GB。
- 结论：该流程可以把 1344×768/15s 从此前不可接受风险推进到可完成，但耗时明显高于 1024×576/20s 的约336.7s；1344×768/15s只作为高分辨率硬件上限档。
- 产物：`/home/sean/projects/ComfyUI/output/video/h3_pdd_sage_ref2va_clean/pdd_sage_h3opt_release_tiled_1344x768_15s_516s.mp4`。

### 2026-09-15 VDN 同流程边界复测

- VDN 1344×768/15s 的流程结构已确认正确：`ApplyVDNH3(stream, retain_buffers=off, grouped)` → `NativeAudioLock` → 8步采样 → KJ `VRAM_Debug` → 视频 `VAEDecodeTiled`；本轮约320s时人工中断，停在采样节点，未进入释放/解码，无产物。
- VDN 1024×576/25s 同流程运行935s仍停留采样阶段，GPU约24GB满载、系统RAM约44GB，按15分钟阈值取消；未产生视频。20s仍是当前VDN长片上限档。
- 取消后确认队列为空、GPU约0%、显存约0.7GB、ComfyUI仅一个systemd进程。`h3_batch_runner.py` 已修复中断状态误报。

### 2026-09-15 VDN 长时高分辨率边界原因

- 两次取消都发生在采样阶段，未到 `VRAM_Debug` 或 `VAEDecodeTiled`，没有 CUDA OOM、节点错误或 tiled 解码错误；因此“采样后释放模型 + tiled VAE”与 VDN 的兼容性尚未被否定。
- VDN 1024×576/25s：935秒仍未完成采样，GPU约24GB满载，RAM约44GB、可用约10–12GB；按15分钟和内存搬运风险主动取消。
- VDN 1344×768/15s：约320秒人工取消；复核时仍在采样，部分时段GPU实际满载。该条不是流程报错，而是用户观察到GPU无响应后的人工中断。
- 因此当前失败原因应写成：**VDN 长时/高分辨率的采样阶段本身触及时间、显存和系统RAM压力边界；采样后释放节点无法改善采样阶段。** 明日先从1024×576/20s基线向21–23s渐进，或先复测1344×768/10s。

### 2026-09-16 KJNodes 与 H3-Optimizations 的 VDN 兼容性

- `MiniMaxLowVRAMAttention(head_chunks=4)` + `MiniMaxChunkFeedForward(chunks=4, seq_threshold=4096)` 同时接在 `ApplyVDNH3` 后：1024×576/20s 在 `SamplerCustomAdvanced` 报 `'list' object has no attribute 'shape'`，判定 KJ LowVRAMAttention 与 VDN attention 输入结构不兼容。
- KJ `MiniMaxChunkFeedForward` 单独接入 VDN 可跑通：1024×576/5s 125s，20s 395s；视频归档在 `h3_vdn_ref2va_clean/_diagnostics/`。显存观察约22.8–22.9GiB，但系统可用内存约3.4–3.5GiB、Swap约0.85GiB，未带来耗时收益。它是显存换系统内存，暂不作为默认 VDN 节点。
- H3-Optimizations `H3MemoryOptimization(chunk_rows=4096, precision=Preserve native, qkv=Auto)` 单独接入 VDN 可跑通：1024×576/5s 125s，20s 380s；视频归档在 `h3_vdn_ref2va_clean/_diagnostics/`。观察显存约19.3–22.8GiB、系统可用内存约3.6GiB、Swap约1GiB。兼容性通过，但单次20s较基线395s快约15s，受缓存/seed/运行态影响，不能视为稳定加速。
- 当前建议：VDN 默认保持原生 `ApplyVDNH3(stream, grouped)`；需要压低显存时优先评估 H3MemoryOptimization，KJ LowVRAMAttention 不与 VDN 叠加，KJ FFN 仅作为显存紧张时的备选。

### 2026-09-16 PDD 长时与高分辨率边界

- PDD + H3MemoryOptimization + 采样后释放/tiled VAE：1344×768/20s 运行15分钟仍停在采样阶段，GPU约23.1GiB、系统可用RAM约12GiB、Swap约2MiB，无CUDA OOM，按阈值中断。
- 同流程 1024×576/25s 运行15分钟仍未完成采样，GPU约22.9GiB、系统可用RAM约11GiB、Swap约2MiB，无CUDA OOM，按阈值中断。
- 因此 PDD 确实比 VDN 更适合扩展：已成功完成 1344×768/15s；但在当前单卡和15分钟窗口内，1344×768/20s、1024×576/25s 均尚未达到实用可完成性。优化节点降低的是峰值显存，不会消除长序列的采样时间。
## 2026-09-16 Source 方案调查

本轮外部资料检索优先使用官方仓库/原始 README，结论仅作为候选路线，不替代本机实测：

- 长时：[`HR Endless Sampler`](https://github.com/hradec/ComfyUI-HR-Endless-Sampler) 通过 H3 分块串行续接，把上一块尾帧作为下一块 continuation；理论上可扩展到任意长度，但每个块仍必须在当前显存中完成，不能解决单段高分辨率采样，也会引入接缝和 handoff 成本。
- 高分辨率：[`LongMedia Latent Hi-Res/Refine`](https://github.com/vizart-vj/ComfyUI-MiniMax-H3-LongMedia/blob/main/docs/TWO_PASS_LATENT_HIRES_REFINER_GUIDE_EN.md) 先低分辨率 MAIN，再做 latent 空间放大并用第二阶段 refine；长视频 refine 可用 temporal window。它是提高最终输出画布的候选，不是直接高分辨率采样的加速器，且不是当前 VDN/PDD patch，可单独开新 A/B。
- 分段与内存：[`LongMedia Sampler/VRAM Guide`](https://github.com/vizart-vj/ComfyUI-MiniMax-H3-LongMedia/blob/main/docs/SAMPLER_OPTIMIZATION_EN.md) 建议长片用5–10秒段来控制容量和稳定性，并明确说明这不减少每步计算；latent hi-res 先从1.2–1.5倍开始。
- `H3 Optimization Suite` 的 [`Long-Sequence`](https://github.com/ByronLeeeee/ComfyUI-MiniMax-H3-Optimization-Suite) 只做激活/MLP分块容量保护，不切时间线、不减少 steps；其 1280×736/15s/CAB-14 完成性结果来自 RTX 5070 Ti 16GB，不能直接外推到本机 RTX 4090/PDD。
- 官方 [`OpenVDN`](https://huggingface.co/OpenVDN/vdn-minimax-h3) 的真正吞吐/容量路线是官方 Diffusers 优化栈、FP8/Ulysses 和多 GPU；单卡 offload 主要是让任务能装下，不会消除长序列采样时间。

因此，后续若继续验证，应保持唯一 ComfyUI，先测试分块续接的5–10秒块，再测试低分辨率 MAIN→latent hi-res/refine；不再期待单纯把显存换成系统内存的节点突破当前单段时长上限。

### VDN 专用二次调查

本轮检索了 Exa、Tavily+DDG 回退、Bocha，并回到 [OpenVDN 官方模型卡](https://huggingface.co/OpenVDN/vdn-minimax-h3) 与 [ComfyUI-VDN-H3 原始 README](https://github.com/Saganaki22/ComfyUI-VDN-H3) 核验。

- **优先候选：`ApplyVDNH3Advanced.fast_kernels`。** 本地 v1.5.2 已包含，使用 `torch.compile` 融合 VDN 分支热点，可能减少 kernel launch 和中间张量开销。上游警告 torch 2.10 + 8步 DMD 会有数值漂移；当前为 PyTorch 2.13.0+cu130，因此可做一次5秒同参 A/B，但必须做画质和 latent 差异验收。
- **低优先级：`attention_backend=flex`。** 是可选 FlexAttention/BlockMask 路径；上游公开的约34.5k token RTX5090测试与 grouped 持平，不能预期它解决长时容量。
- **谨慎候选：`retain_buffers=on`。** 上游称其可减少逐块分配、改善速度，但会增加显存；本机长片已经接近24GB，现有 `off` 是容量优先选择。
- **不建议当前测试：官方 FP8/FA4/Ulysses。** 官方24GB示例和单卡 benchmark 使用的是官方 Diffusers 栈及 H200/B200；ComfyUI移植明确说明 headline 数字还包含 FP8、FA4和多GPU并行。RTX4090当前 INT8 ConvRot 分支没有等价、已验证的更低精度 VDN 权重。

本轮没有安装新节点、没有启动第二个 ComfyUI，也没有改变现有工作流；如继续实测，必须先做 `fast_kernels off/on` 的5秒 A/B，再决定是否跑20秒。

### 系统内存构成与磁盘后端

当前空闲态 ComfyUI 约6GB RSS、系统可用内存约47GB，说明64GB峰值只发生在生成期间。2026-09-16启动日志记录了：pinned memory **50,612MB**；视频 VAE **4,965MB staged**；Qwen文本编码器 **14,956MB staged**；音频 VAE **576MB staged**；H3主体 **19,995MB staged**。这些 DynamicVRAM CPU staging 合计约40.5GB，另加采样激活、参考条件和 Python/分配器开销，解释了历史约50–52GiB RSS。

当前启动策略是 `fast_disk=False`。ComfyUI提供 `--fast-disk`，可以优先磁盘后端的动态加载，减少锁页 RAM，但会增加 NVMe I/O和搬运等待；它不能把正在计算的 attention/MLP激活放到磁盘。`--disable-pinned-memory`也可降低锁页内存，但通常损失异步搬运性能，不作为默认方案。若要验证，建议只改变启动参数 `--fast-disk` 做一次同参5秒/20秒 A/B，并继续保持唯一 ComfyUI。

### H3主体、TE与 Low VRAM Attention 的内存边界

`19,995MB Staged` 不是“19,995MB全部在显存”，而是 DynamicVRAM 的 CPU侧 backing/staging预算；运行时当前block才搬到GPU。因此GPU显存接近满载仍可能持续计算，除非下一次临时分配无法满足而触发CUDA OOM。TE编码完成后，conditioning embedding仍需保留，但TE权重可被DynamicVRAM驱逐；`--fast-disk`可让这类权重优先使用磁盘-backed loading，理论上减少接近14,956MB的TE staging，实际回收量取决于缓存/引用。

VDN 1024×576/25s的历史取消是GPU约24GB高压、RAM约44GB但仍有10–12GB可用、15分钟仍未完成采样后主动中断，不是“显存一满就停止计算”；768×432/30s才是明确CUDA OOM。Low VRAM Attention虽然能降低QKV激活显存，却会增加CPU中间缓冲和搬运；KJ版本对当前VDN特殊list输入已不兼容。PDD上该节点曾跑通20s，但RAM约45–50GB，余量不大。VDN当前只能用兼容的H3MemoryOptimization，且已观察到可用RAM约3.6GB/Swap约1GB的危险状态。

后续如验证“低显存且不爆RAM”，应优先单独测试 `--fast-disk` + VDN `stream/retain_buffers=off`，先做5秒资源剖面；不要把OS Swap当作采样激活的扩容，也不要把KJ LowVRAMAttention直接接到VDN。

### PDD 1024×576/21秒实测

PDD 8-step + H3MemoryOptimization + NativeAudioLock + 采样后释放/tiled VAE 在 `length=505` 下自然完成，端到端 **741s**。ffprobe为1024×576、24fps、515帧、21.458333s视频和21.450s音频。采样时GPU约22.9–23.1GB且利用率持续100%，系统RAM约43GB/可用11GB，Swap约2.2MB；显存接近满载并未停止计算，约12分钟后才进入释放/解码。注意：该批跑未接外部 SageAttention，而此前335.3秒的20秒基线包含 SageAttention，故不能把741s与335–342s做一秒增量的直接比较；下一步需统一 attention backend 后再判断是否有非线性拐点。

### Source核验：VDN × KJ MiniMaxLowVRAMAttention

本轮检索 Exa、Tavily+DDG回退、Bocha，并核对 [VDN源码/README](https://github.com/Saganaki22/ComfyUI-VDN-H3)、[KJ MiniMax源码](https://github.com/Kijai/ComfyUI-KJNodes/blob/main/nodes/minimax_nodes.py) 和上游 commit。未找到官方兼容声明或已合并的 VDN 专用适配。

KJ节点将 block 的 attention 输入包装成单元素 list，KJ forward 先 `pop()` 后按普通 H3 tensor读取 `.shape/.device`；VDN自己的 `make_vdn_forward`则直接要求 tensor，并额外维护 `AttentionTensorContainer` 与 linear-branch 状态。因而KJ的普通H3接口修复不等于VDN兼容，本机实际的 `'list' object has no attribute 'shape'` 与源码契约冲突完全吻合。当前结论仍是：KJ `MiniMaxLowVRAMAttention` 不应直接接在 VDN 后；若要兼容，必须做专门的 VDN forward 适配并重新验证数学/画质。

### 2026-09-17 当前验收结论

- **正式 VDN 基线**：VDN Ref2VA、三张参考图、1024×576、24fps、8 steps、INT8 ConvRot、`ApplyVDNH3(stream, retain_buffers=off, grouped)`、NativeAudioLock、视频 tiled VAE；20 秒已多次成功，当前稳定耗时约 380–411 秒。
- **对白链路**：Breeze 固定声线生成严格约20秒 WAV，经 `MiniMaxH3NativeAudioLock` 锁定外部对白；该节点不是普通 `ref_audios` 音色参考，而是把音频编码后写入 H3 AV latent，音频保持外部真值、视频根据音频生成口型和表演。
- **提示词链路**：H3 视频任务默认必须加载 `.pi/skills/h3-prompt-writing/SKILL.md`；Ref2VA 使用六段式 prompt，并明确 `<Subject N>`、`<Audio N>` 与参考资产/说话人映射。正向分段描述可触发 Sylvanas 出场冰霜、Hero 决心时眼部闪光、结尾城堡红光与拉镜。
- **画面控制边界**：三段时间线和特效时序有效，但景别仍是软约束；H3 可能在情绪重点处自动加入近景。NativeAudioLock 不负责锁定镜头。
- **资源边界**：启动前系统可用内存建议至少40GiB、Swap保持空闲；采样峰值约显存23.9/24.6GiB、系统内存约52GiB已用，运行中可用内存约5–10GiB仍可完成，但低于3–4GiB不安全。中断后的CPU staging残留需要重启唯一ComfyUI实例清理。
- **VDN v1.5.2**：本地已是 v1.5.2；其主要作用是正确读取新版 `adapter_spec.json` 并兼容旧 `adapter_config.json`，保障当前 adapter 正确加载，不直接突破显存、内存或时长上限。
- **最终选型**：当前任务验收通过，不再继续叠加 KJ LowVRAMAttention、ChunkFeedForward 或未经验证的 VDN 变体；后续若追求更长/更高分辨率，应另立分段续接或低分辨率 MAIN→latent hi-res/refine 任务。

### 2026-09-25 动态/动作场景启用边界

当前尚未开始动态场景或动作场景测试，因此不能把 VDN 的动作优势写成已验证结论。现有实测只证明：VDN 在当前 RTX 4090 上可以完成既定 Ref2VA 长片，并未证明它在快速动作、镜头运动或高动态特效中优于 PDD。

官方 OpenVDN 的设计理由是：用局部 Softmax 保留细粒度帧间交互，用线性记忆处理长程视频上下文，目标是兼顾长序列效率与时序质量；这使它理论上适合验证快速位移、肢体/武器交互和多运动源场景，但不等于已经证明画质领先。[OpenVDN 项目](https://openvdn.github.io/)、[原始论文](https://arxiv.org/abs/2609.20744)

因此，VDN 在本机暂不作为默认快车道或分辨率/时长升级方案，只保留一个明确用途：**动作戏专项质量 A/B 分支**。后续应以 768×448、124 帧、两边均 8 steps、相同 seed/参考图/prompt/audio，对照当前 PDD + SageAttention，优先测试：

- 剑斗、挥砍、闪避等快速位移；
- 跑动/冲刺跟拍与快速镜头变化；
- 舞蹈旋转、跳跃等多关节动作；
- 龙俯冲、喷火、烟尘/碎片与镜头同时运动。

评价重点为动作节拍完成度、拖影、手脚与武器拓扑、镜头轨迹、15–20 秒后段的时序稳定性，以及指令动作是否按顺序执行。只有 VDN 在多个高动态案例中稳定胜出，才建立“动作戏模式”；在此之前继续使用 PDD 作为默认路线。社区反馈目前也是混合且偏轶事，不能替代本机同条件 A/B。[社区讨论](https://www.reddit.com/r/StableDiffusion/comments/1wcal7sk/comfyui_vdnh3_24gb_v110_update_better_prompt/)
