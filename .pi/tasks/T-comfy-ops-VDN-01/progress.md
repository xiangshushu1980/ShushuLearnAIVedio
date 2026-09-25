# 任务进度：T-comfy-ops-VDN-01

> 任务：VDN-H3 Ref2VA 路线资源与文档维护

## 2026-09-13

- 已下载 VDN-H3 ComfyUI 节点仓库到 `/home/sean/projects/ComfyUI/custom_nodes/ComfyUI-VDN-H3`。
- 当前节点 commit：`3eb63496c24ca70faaf8a14b6c75fcb480e34bf1`（v1.5.2）。
- 已下载 INT8 ConvRot 8-step VDN 分支到 `/home/sean/projects/ComfyUI/models/vdn/vdn-minimax-h3-int8-convrot-comfyui`。
- 下载目录约 3.3GB，包含约 2.30GB 的 `linear_branch/model_int8_convrot_comfyui.safetensors`、default/turbo adapters 和 `model_spec.json`；临时 incomplete 文件已由 hf 下载流程完成收口。
- 新建统一维护文档：`docs/35_vdn_h3_ref2va_route.md`，并更新 `docs/INDEX.md`。
- 尚未重启 ComfyUI，尚未将 VDN 接入工作流，尚未执行 GPU Ref2VA 实测。

## 待办

1. 用现有 Ref2VA 工作流接入 Apply VDN-H3。
2. 按文档 VDN-R1 至 R4 做单卡 A/B，记录显存、RAM、采样/解码时间与质量。
3. 通过用户目视验收后，再将稳定结论追加到文档及 ledger/Mem0。

## 2026-09-14 实测

- 已新增工作流：`workflows/minimax_h3_vdn_ref2va_img_vid_api.json`；`ApplyVDNH3` 位于 UNETLoader 与采样器之间，INT8 ConvRot + turbo + `merge` + `stream` + grouped，8 steps。
- ComfyUI 0.35.0 / PyTorch 2.13.0+cu130 / RTX 4090 已加载节点并成功执行。
- VDN 576×576：5s/121帧约 147s；10s/241帧约 178s；15s/361帧约 241s。三次均 success，无 OOM，均生成 MP4；ffprobe 实际时长分别约 5.08s、10.13s、15.08s。
- 同设置原生 H3 对照：576×576、10s/241帧、20 steps，约 364s；VDN 8-step 约 178s，端到端耗时约降低 51%。这是首轮单次 A/B，尚未做画质/身份目视验收，显存峰值也尚未单独记录。
- 测试素材：`/home/sean/projects/ComfyUI/input/vdn_test/reference.mp4`；输出位于 ComfyUI `output/video/h3_vdn_ref2va/`。

## 当前状态

安装、节点加载、5/10/15 秒链路和首轮速度 A/B 已完成；待用户目视验收视频质量后，再决定是否进入长视频生产主线。

## 2026-09-16 基线复跑

- 按 33 号任务已成功配置复跑 VDN 基线：RTX 4090 24GB、ComfyUI 0.36.0、PyTorch 2.13.0+cu130、三张参考图、NativeAudioLock、VDN INT8 ConvRot + Turbo、`stream`、8 steps、1024×576、481 帧/20.04s；增加采样后 `VRAM_Debug` 释放与视频 `VAEDecodeTiled`。
- 结果：`experiments/h3_digital_human/vdn_baseline_retest_20260916.json.results.json` 返回 `error: null`，端到端 **395s**；正式输出 `/home/sean/projects/ComfyUI/output/video/h3_vdn_ref2va_clean/vdn_1024x576_20s_retest_395s.mp4`。
- ffprobe 核对：视频 1024×576、24fps、481 帧、20.041667s；音频 20.042s。说明当前环境和成功工作流仍可完整跑通。
- 采样中资源：GPU 约 23.8–24.1GiB、利用率 94–100%；ComfyUI RSS 约 50GiB；系统可用 RAM 最低约 7.3GiB，Swap 仅约 104KiB。完成后恢复至 GPU 5.9GiB、系统可用 RAM 约 37GiB。与 33 号成功基线一致，未发生 CUDA OOM 或系统 Swap 风暴。
- 这次复跑只验证基线可复现，不改变“两个取消样本属于采样阶段资源/时间边界”的归因；下一步仍应在用户确认后选择 21–23s 渐进或 1344×768/10s。

## 2026-09-16 KJNodes / H3-Optimizations 叠加验证

- KJNodes 两节点同时叠加 VDN（`MiniMaxLowVRAMAttention(head_chunks=4)` + `MiniMaxChunkFeedForward(chunks=4, seq_threshold=4096)`）在 1024×576/20s 于采样节点报错：`'list' object has no attribute 'shape'`，约20s返回；ComfyUI history 定位为 `SamplerCustomAdvanced`，执行链包含 KJ 节点。原因是 KJ LowVRAMAttention 只处理普通 H3 tensor 输入，VDN attention 路径传入特殊 list 结构，不能直接叠加。
- KJ `MiniMaxChunkFeedForward` 单独叠加 VDN：1024×576/5s 成功 **125s**；20s 成功 **395s**，视频已归入正式 VDN 目录的 `_diagnostics/`。20s 采样期间观察 GPU约22.8–22.9GiB，较基线约24.1GiB低约1.2GiB，但系统可用RAM约3.4–3.5GiB、Swap约0.85GiB，整体不是更安全，也未见耗时收益。
- H3-Optimizations `H3MemoryOptimization(chunk_rows=4096, Preserve native, qkv=Auto)` 单独叠加 VDN：1024×576/5s成功 **125s**；20s成功 **380s**，视频已归入正式 VDN 目录的 `_diagnostics/`。采样期间GPU约19.3–22.8GiB，系统可用RAM约3.6GiB、Swap约1GiB；当前只能确认兼容并有一定显存下降，不能把单次380s视为稳定加速。
- H3-Optimizations 仍应与 VDN 分开保持 A/B；当前生产默认继续用无额外 patch 的 VDN，只有显存余量不足时才考虑 H3MemoryOptimization。KJ LowVRAMAttention 不用于 VDN；KJ FFN 可用但代价是系统内存压力。

## 2026-09-16 PDD 长时/高分辨率扩展

- 测试前重启并清理：曾发现项目重启脚本与外部 `start.sh` 同时拉起两个 ComfyUI；已中断测试、清理队列，最终保留唯一 `start.sh` 管理实例。后续测试前必须确认 `python3 main.py` 进程数为1、队列为空。
- PDD + H3MemoryOptimization + 采样后释放/tiled VAE，1344×768/481帧/20s 运行15分钟仍停在采样阶段；GPU约23.1GiB、系统可用RAM约12GiB、Swap约2MiB，无CUDA OOM，按阈值中断，无输出。结果：`experiments/h3_digital_human/pdd_h3opt_1344x768_20s_20260916.json.results.json`。
- 同配置 1024×576/601帧/25s 运行15分钟仍未完成采样；GPU约22.9GiB、系统可用RAM约11GiB、Swap约2MiB，无CUDA OOM，按阈值中断，无输出。结果：`experiments/h3_digital_human/pdd_h3opt_1024x576_25s_20260916.json.results.json`。
- 结论：PDD + H3-Optimizations 比 VDN 长时路线更省资源、可跑通 1344×768/15s，但在本机15分钟可接受窗口内仍不能同时突破到 1344×768/20s 或 1024×576/25s；当前实用上限仍约为 1344×768/15s 或 1024×576/20s。

## 2026-09-16 Source 方案调查（落盘）

- 检索渠道：Exa、Tavily（含搜索回退）、Bocha；优先核对 OpenVDN/Hugging Face、GitHub 原始 README/评测，再参考社区节点说明。没有把搜索聚合页的摘要当作本机实测结论。
- 最有希望突破“时长”的路线是分块串行续接：[`HR Endless Sampler`](https://github.com/hradec/ComfyUI-HR-Endless-Sampler) 将长 latent 拆成连续小块，每块完成 H3 采样后把尾帧作为下一块的 Video/Audio continuation；文档声称可扩展到任意长度，但每块仍要在当前显存中完成，且存在接缝/连续性与额外 handoff 成本。其 16GB 示例是 1080p/625 帧、`chunk_frames=56`（不使用 KJ Low VRAM Attention 时示例为39），属于社区硬件报告，不等于本机验证。
- 最有希望提高“输出分辨率”的路线是两阶段 latent hi-res/refine：[`LongMedia Integrated Refine and Latent Hi-Res`](https://github.com/vizart-vj/ComfyUI-MiniMax-H3-LongMedia/blob/main/docs/TWO_PASS_LATENT_HIRES_REFINER_GUIDE_EN.md) 先在较低分辨率完成 MAIN，再对完整视频 latent 做学习式空间放大，最后用独立 refine sigma 做第二阶段；长/高分辨率 refine 可以 temporal-windowed。它提高的是最终画布，不是让原始高分辨率 MAIN 采样免费，且需要单独安装/验证 LongMedia 的 H3 路线。
- LongMedia 的 [`Sampler/VRAM/Performance Guide`](https://github.com/vizart-vj/ComfyUI-MiniMax-H3-LongMedia/blob/main/docs/SAMPLER_OPTIMIZATION_EN.md) 明确说明：`segmented`/5–10秒分段是容量与稳定性策略，不会减少每一步模型计算；latent hi-res 建议先尝试1.2–1.5倍，2倍需在小比例稳定后再试。这个路线与当前 VDN/PDD 的单段工作流不是可直接叠加的 patch。
- [`H3 Optimization Suite`](https://github.com/ByronLeeeee/ComfyUI-MiniMax-H3-Optimization-Suite) 的 Long-Sequence 节点是容量保护/MLP 分块，不切分时间线、不减少 steps；其 16GB/1280×736/15s/CAB-14 只是另一台 RTX 5070 Ti 的完成性评测（约1064s全流程），不能推导本机速度或画质等价。CAB 可减少模型评估次数，但以降低步数和画质偏差为代价；PDD 已是8步，继续压步应单独做质量验收。
- 官方 [`OpenVDN/vdn-minimax-h3`](https://huggingface.co/OpenVDN/vdn-minimax-h3) 的方向是 Diffusers `apply_group_offloading`、Flash/Flex/FP8、Ulysses 与多 GPU；官方说明24GB卡可用 block offload 跑约345帧，但这是官方优化栈/特定条件，不能覆盖当前 ComfyUI 的长序列瓶颈。真正同时改善容量和速度的官方路径需要2/4/8卡；单张 RTX 4090 不具备该条件。
- 暂不建议继续堆叠已验证的节点：VDN + KJ LowVRAMAttention 已报 list 结构错误，KJ FFN 只降低少量显存而增加系统 RAM/Swap；H3MemoryOptimization 可兼容但未证明稳定提速。当前最值得后续测试的顺序为：①先单段 5–10s 分块续接验证长时；②再在已稳定短块上接 latent hi-res/refine 验证高分辨率；③只有更换多 GPU 或官方推理栈时再追求整体吞吐。

## 2026-09-16 VDN 定向 Source 二次调查

- 本轮渠道：Exa、Tavily+DDG 回退、Bocha；已回到 [OpenVDN 官方模型卡](https://huggingface.co/OpenVDN/vdn-minimax-h3) 和 [ComfyUI-VDN-H3 原始 README](https://github.com/Saganaki22/ComfyUI-VDN-H3) 核验，Bocha 主要命中中文转载/整合包，未发现比官方实现更可靠的 VDN 专用方案。
- 找到一个此前未单独实测的本地候选：`ApplyVDNH3Advanced.fast_kernels`。它用 `torch.compile` 融合 VDN linear branch 的 RMSNorm/gate、state gather、frame-major q store 和 bidirectional scan，目标是减少 kernel launch/中间张量开销，属于**可能提速**而非扩展时长的方案。本地 v1.5.2 已包含该节点；上游明确警告在 torch 2.10 的8步 DMD stage可能产生数值漂移。当前环境是 PyTorch 2.13.0+cu130，版本条件不同，值得做一次5秒同参 A/B，但必须检查输出画质/口型和 latent 差异，不能直接用于生产。
- 第二个本地候选是 `attention_backend=flex`。上游说明它是可选 FlexAttention/BlockMask 路径，当前 `grouped` 默认路径在约34.5k tokens 的 RTX 5090测试中与 `flex` 持平，因此优先级低于 `fast_kernels`；它更可能改变窗口 attention 的 kernel 行为，不会改变 VDN 的线性分支或单段时间线容量。
- `retain_buffers=on` 仍是一个已存在的速度/显存开关：上游报告保留 scratch 可减少逐块分配，可能比 `off` 快，但会增加显存占用；本机长片已接近24GB，当前使用 `off` 是容量优先选择，不列入高优先级测试。
- 第三个是官方单卡优化栈：FP8 wide linears、FlashAttention-4/Flex、torchao、Diffusers block offload；官方24GB示例为345帧约22GB（FP8约20GB），但官方 FA4依赖 Hopper/数据中心 Blackwell，且官方单卡 benchmark 是 H200/B200，不是 RTX4090。ComfyUI移植 README 也明确说明 headline 数字包含FP8、FA4和8卡并行，不能外推到当前单卡。
- 当前模型层面不建议再次降精度：本机已用 INT8 ConvRot VDN branch；上游工具仅提供 `quantize_vdn_branch_int8.py`，没有已验证的更低精度 VDN branch。基础模型的 `fp8_scaled` 变体在本地 README 中只是无法使用 cu130 INT8 时的备选，不能预设比现有 `int8_convrot` 更快或更稳。
- 结论：值得实测的 VDN 专用候选只有 `fast_kernels`（优先）和 `flex`（低优先级 A/B）；它们可能改善速度/少量显存，但不会把1024×576/25s或1344×768/20s从当前单卡边界直接变成可用。官方 FP8/FA4/多GPU是架构级方案，需换推理栈或硬件，不在当前 ComfyUI 单卡测试中混入。

## 2026-09-16 系统内存构成与磁盘后端分析

- 当前空闲态：ComfyUI RSS约6GB、系统可用RAM约47GB、Swap约2MB、GPU约554MB；64GB不是被永久占满，而是生成期间的峰值。
- ComfyUI启动日志给出直接证据：总RAM 56,236MB；启用 pinned memory **50,612MB**；DynamicVRAM 分别为视频 VAE **4,965MB staged**、Qwen文本编码器 **14,956MB staged**、音频 VAE **576MB staged**、H3/PDD或VDN主体 **19,995MB staged**，合计约40.5GB，剩余约9–12GB由采样激活、参考条件、Python/ComfyUI和分配器缓存消耗。这与历史采样时 ComfyUI RSS约50–52GiB一致。
- 当前日志中的模型策略为 `fast_disk=False`。ComfyUI本身提供 `--fast-disk`，可优先使用磁盘后端的 DynamicVRAM loading/offload，减少未锁页 RAM；但每次权重搬运会更多依赖 NVMe，速度可能下降，且不能把采样激活/latent直接变成磁盘流式计算。
- 可卸载/转磁盘的对象：未使用的模型、VDN branch 权重（当前 `stream` 已尽量按块从磁盘取）、动态VRAM模型权重，以及生成块之间保存的 latent/参考帧。不可在单段采样中安全转磁盘的对象：当前步的 attention/MLP 激活、采样状态和必须同时参与计算的完整条件；把这些交给 OS Swap 通常会变成极慢的抖动，不是可用扩容。
- 可选实验开关：`--fast-disk`（优先磁盘后端）、`--disable-pinned-memory`（禁用锁页内存但会损失异步搬运性能）、较低的 `--cache-ram` 阈值（更早清理缓存）。其中只有 `--fast-disk` 直接针对当前50GB staging问题；必须单独 A/B，不能与 fast_kernels 或其它节点同时改动。
- 结论：`MiniMax H3 Low VRAM Attention` 的确是用系统内存换显存，但当前64GB峰值的主因是 ComfyUI DynamicVRAM 的 pinned CPU staging，尤其是约20GB H3主体+约15GB文本编码器，而不是普通缓存或输出视频。优先验证磁盘后端和分块续接；不建议把系统Swap当作长片扩容方案。

## 2026-09-16 Source：VDN 与 KJ MiniMaxLowVRAMAttention 兼容性核验

- 检索渠道：Exa、Tavily+DDG回退、Bocha；最终回到 [ComfyUI-VDN-H3源码/README](https://github.com/Saganaki22/ComfyUI-VDN-H3)、[KJNodes源码](https://github.com/Kijai/ComfyUI-KJNodes/blob/main/nodes/minimax_nodes.py) 和 GitHub API commit记录。没有找到 KJ 或 VDN 官方 issue 明确宣称两者已经兼容。
- VDN官方移植文档只说明：VDN会接管 `blocks.*.attn.forward`，不要与会接管同一路径的 Scheduled Sol 叠加；KJNodes可作用于普通 H3/其他 attention 路径，不等于可作用于 VDN 自己的 attention forward。
- KJ当前源码（本机与上游最新相关 commit `da90cca`，提交信息为 `Fix MiniMax H3 VRAM Attention`）的 `MiniMaxLowVRAMAttention` 将 block 输入包成单元素 `list`，再由 KJ attention forward `pop()` 后按普通 H3 tensor处理。该修复是 KJ自身普通H3/Sage组合的接口修复，不是 VDN适配。
- VDN源码的 `make_vdn_forward` 仍要求 `x.shape`、`x.device`，并且内部使用 VDN自己的 `AttentionTensorContainer` 和 linear-branch 状态；当 KJ block patch把 list传给 VDN forward时，VDN路径无法按KJ普通 attention契约处理。这与本机实测的 `'list' object has no attribute 'shape'` 一致。
- 结论：截至本轮 source 核验，**没有证据支持 KJ MiniMaxLowVRAMAttention 与当前 VDN v1.5.2 可直接兼容**；本机失败不是漏装依赖或简单参数问题。除非有人专门改 VDN forward/做适配补丁，否则继续叠加不值得。KJ ChunkFeedForward与VDN可单独运行，但不能替代 attention 节点。

## 2026-09-16 H3 staging / LowVRAM 预算再分析

- H3主体不是“只在显存”或“只在内存”二选一。日志中的 `19,995MB Staged` 表示 DynamicVRAM 为模型准备了 CPU侧 backing/staging；采样时按 block 把当前需要的权重/中间结果搬到 GPU，GPU侧约24GB满载时仍可能继续计算，只是需要等待释放空间或搬运。`Staged` 数字不能直接当成显存占用。
- TE也不是简单“用完仍完整占在GPU”。日志显示其 DynamicVRAM staging约14,956MB、load device为cuda/offload device为cpu；文本编码完成后，conditioning embedding必须保留给采样，但TE模型权重本身可以被 ComfyUI DynamicVRAM 卸载/驱逐。若启用 `--fast-disk`，可进一步让这类权重优先走磁盘-backed loading；理论上可释放接近TE staging量，但实际收益取决于缓存和仍被引用的张量，不能承诺完整回收15GB。
- 之前两次VDN取消不能表述为“显存一满就停止运算”：1024×576/25s在15分钟阈值时GPU约24GB且仍处于采样，系统RAM约44GB、可用约10–12GB，没有CUDA OOM；这是GPU高占用/搬运压力下进展太慢后主动取消。1344×768/15s也是采样阶段人工中断。只有768×432/30s那次有明确 `CUDA out of memory`，属于即时硬失败。
- Low VRAM Attention的目标是降低QKV/attention激活显存，但会增加分块循环、CPU中间缓冲和GPU↔CPU搬运；它不释放H3主体、TE或完整采样latent。历史PDD 1024×576/20s的 KJ LowVRAMAttention+ChunkFeedForward 已成功约341.7s、未OOM，但运行期系统RAM约45GB且收尾曾接近50GB，说明“能跑”不等于有很大RAM余量。
- 对VDN，当前KJ `MiniMaxLowVRAMAttention` 已实测因 VDN 特殊 list attention 输入报 `'list' object has no attribute 'shape'`，不能直接采用该节点做“显存换内存”。VDN目前兼容的 `H3MemoryOptimization` 20s观察到GPU约19.3–22.8GiB，但系统可用RAM约3.6GiB、Swap约1GiB，属于危险边界，不是安全方案。
- 可行的预算策略应是两层同时控制：①保留VDN `stream`、`retain_buffers=off`，避免GPU常驻分支；②用 `--fast-disk` 让模型权重/非活动 staging优先落NVMe，并让TE权重在编码后被驱逐；③仍保留至少8–12GB系统可用RAM，不以Swap承载采样激活。磁盘可以承载权重和块间latent，不能承载当前步必须参与矩阵计算的激活。

## 2026-09-16 PDD 1024×576/21秒自然完成

- 配置：PDD Acc 8-step + H3MemoryOptimization(chunk_rows=4096, Preserve native, QKV Auto) + NativeAudioLock + 采样后释放模型 + 视频 tiled VAE；与20秒成功基线相同，仅 `length=505`，使用25秒音频输入。
- 结果：自然完成，runner端到端 **741s（12分21秒）**，结果文件 `experiments/h3_digital_human/_discarded_t33_no_sage_or_duplicate/pdd_h3opt_1024x576_21s_20260916.json.results.json`，输出已移入 `/home/sean/projects/ComfyUI/output/video/_discarded_t33_no_sage_or_duplicate/pdd_h3opt_1024x576_21s_20260916_00001_.mp4`。
- ffprobe：1024×576、24fps、515帧、视频21.458333s，音频21.450s。H3帧网格/封装使实际视频略高于21秒目标，音画同步正常。
- 采样资源：GPU约22.9–23.1GB、利用率持续100%；系统RAM约43GB、可用约11GB；Swap约2.2MB。显存接近满载时GPU仍持续计算，并在约12分后自然进入释放/解码；未发生CUDA OOM或系统内存OOM。
- 口径修正：本次21秒批跑的实际工作流没有接外部 SageAttention（ComfyUI启动日志为 `Using pytorch attention`）；此前335.3秒的PDD 20秒基线是 `PDD + SageAttention + H3MemoryOptimization`。因此741秒不能直接证明“只增加1秒就产生非线性拐点”，它同时混入了 attention backend 差异和冷启动/缓存差异。21秒仍证明该无Sage配置可自然完成、资源未爆，但下一步若比较时长必须补做同一 Sage/无Sage口径的20/21秒 A/B。

## 2026-09-16 PDD 1024×576/22s Sage 特效版复测

- 配置：PDD Acc 8-step + **KJ `MiniMaxH3MemoryEfficientSageAttentionPatch`** + H3MemoryOptimization(chunk_rows=4096, Preserve native, QKV Auto) + NativeAudioLock + 采样后释放模型 + tiled VAE；1024×576、529帧目标、3张参考图、特效版提示词、seed `20260920`。
- 结果：自然完成，端到端 **380s**，无执行错误；正式输出 `/home/sean/projects/ComfyUI/output/video/h3_pdd_sage_ref2va_clean/pdd_sage_1024x576_22s_effects_380s.mp4`。
- ffprobe：1024×576、24fps、532帧、视频22.166667s，音频22.167s；H3帧网格使实际时长略高于22秒，音画同步正常。
- 资源：采样观察到显存约23.1GB、GPU利用率100%、系统RAM约41GB/可用16GB、Swap 0；完成后队列为空、显存/内存回落，单一 ComfyUI 实例保持运行。
- 结论：22秒在本机 4090 上以 **PDD + H3专用 Sage + H3MemoryOptimization** 可自然完成；相较21秒无Sage的741s不可直接做速度比较。该结果证明 Sage 版本不是“显存满即停止”，仍能在接近显存上限时持续采样。

## 2026-09-16 PDD 1024×576/22s LowVRAM 对照复测

- 严格保持上一条 22 秒测试的提示词、三张参考图、seed `20260920`、音频、分辨率和长度不变；技术路线改为 PDD + Sage + KJ `MiniMaxLowVRAMAttention(head_chunks=4)` + `MiniMaxChunkFeedForward(chunks=4, seq_threshold=4096)`，移除 H3MemoryOptimization。
- 结果：自然完成，端到端 **380s**，无执行错误；正式输出 `/home/sean/projects/ComfyUI/output/video/h3_pdd_sage_ref2va_clean/pdd_sage_lowvram_1024x576_22s_effects_380s.mp4`。
- ffprobe：1024×576、24fps、532帧、视频22.166667s，音频22.167s。
- 目视抽帧：未复现上一条中的松树侵入、枝叶贴脸和英雄脸部污染；英雄近景基本干净。镜头仍会中景/过肩/近景切换，这是提示词明确要求的镜头变化，不能归因于优化节点。
- 结论：在相同提示词和输入下，问题范围已缩小到上一轮 `H3MemoryOptimization + MiniMaxH3MemoryEfficientSageAttentionPatch` 组合或其交互；不能把问题归咎于提示词单独作用。当前 PDD 画面稳定性优先保留 LowVRAM 路线，后续如需定位应分别做“仅 H3Opt”和“仅 H3 Sage”单变量 A/B。

## 2026-09-16 PDD 1024×576/23s LowVRAM 延长测试

- 保持 22 秒稳定版的提示词、三张参考图、seed `20260920`、音频和技术路线不变，仅将目标长度从 22 秒增加到 23 秒（553 帧）。
- 配置：PDD + Sage + `MiniMaxLowVRAMAttention(head_chunks=4)` + `MiniMaxChunkFeedForward(chunks=4, seq_threshold=4096)` + 采样后释放/tiled VAE；不使用 H3MemoryOptimization。
- 结果：自然完成，端到端 **425s**，无执行错误；正式输出 `/home/sean/projects/ComfyUI/output/video/h3_pdd_sage_ref2va_clean/pdd_sage_lowvram_1024x576_23s_effects_425s.mp4`。
- ffprobe：1024×576、24fps、566帧、视频23.583333s，音频23.575s。抽帧未见上一轮的松树侵入或树叶贴脸；英雄近景和双人镜头主体保持正常。
- 资源：采样阶段可用内存最低约10GiB，Swap未增长；完成后可用内存回升约42–45GiB，队列为空。
- 结论：稳定 LowVRAM 路线可从22秒延长到23秒；端到端时间由约380s升至425s，增加约45s。镜头切换仍来自提示词中的过肩/近景要求。

## 2026-09-16 PDD 23s 分角色对白音频复测

- 新音频 `/home/sean/projects/ComfyUI/input/vdn_audio_test/dialogue_dual_roles_23s.wav` 由原有分角色片段重新拼接：Sylvanas 01 → Hero 01 → Sylvanas 02 → Hero 02 → Sylvanas 03 → Hero 03 → Sylvanas 04 → Hero 04；每句间约250ms停顿，音频严格23.000s。
- 提示词明确写入八句角色映射，视频技术路线保持已验证的 PDD + Sage + LowVRAMAttention + ChunkFeedForward，唯一输入变化为对白音频与角色映射说明。
- 结果：自然完成，端到端 **425s**，无执行错误；输出 `/home/sean/projects/ComfyUI/output/video/h3_pdd_sage_ref2va_clean/pdd_sage_lowvram_1024x576_23s_roles_audio_425s.mp4`；ffprobe 566帧/23.583333s视频、23.575s音频。
- 抽帧：未见上一轮的松树/树叶污染；英雄脸部近景保持稳定。最终口型和每句实际说话归属仍需用户听看成片确认，不能仅由静帧判定。

## 2026-09-16 最终 Breeze 新音频复测

- 先清空并中断 ComfyUI 中残留的非本测试任务；最终提交前确认队列为空、GPU 空闲。
- 由于旧 Hero 参考音频没有逐字稿，未冒险把未知文本用于 Breeze voice clone；改用 Breeze Voice Design 固定角色指令与 `cfg_scale=1.5`，Hero 四句共用同一男性声线指令，Sylvanas 四句共用同一女性声线指令。八句短对白均重新生成，未复用旧 `hero_01..04.wav`。
- 新音频 `/home/sean/projects/ComfyUI/input/vdn_audio_test/dialogue_dual_breeze_final_20s.wav`：24 kHz、单声道、严格 20.000s；顺序 Sylvanas/Hero 交替四轮。
- 技术路线：PDD + Sage + `MiniMaxLowVRAMAttention(head_chunks=4)` + `MiniMaxChunkFeedForward(chunks=4, seq_threshold=4096)`；不启用 `H3MemoryOptimization`；保持三张参考图、1024×576、553帧/目标23s、8 steps、seed `20260920`。
- 结果：无错误，端到端 **425s**；输出 `/home/sean/projects/ComfyUI/output/video/h3_pdd_sage_ref2va_clean/pdd_sage_lowvram_1024x576_23s_breeze_final_20260916_00001_.mp4`。
- ffprobe：视频 1024×576、24fps、566帧、23.583333s；音频 23.575s。队列为空，显存约6.2GiB、GPU利用率0%。
- 说明：此次 Breeze 是固定 Voice Design 声线，不是用旧参考音频做克隆；因此保证本次四句 Hero 内部一致，但不承诺与历史 Hero 声音完全相同。视频是否仍有漏台词/口型错配需用户试听成片确认。

## 2026-09-16 Breeze Voice Clone 固定 ref 对照

- 确认：Whisper 不是 Breeze 生成对白的必要组件；只有在不知道参考音频逐字稿时，才用它自动补 `ref_text`。
- 未下载新模型。使用本地官方 CLI Breeze 模型、已知逐字稿的 Breeze 参考片段：Hero ref=`breeze_final_hero_01.wav`，Sylvanas ref=`breeze_final_sylvanas_01.wav`；每个角色固定同一 ref、同一 `ref_text`、`cfg_scale=1.0`。
- 重新生成 8 句 Voice Clone 片段，并按角色交替加停顿合成为 `/home/sean/projects/ComfyUI/input/vdn_audio_test/dialogue_dual_breeze_clone_final_20s.wav`。
- ffprobe：24kHz、mono、严格 20.000s；ComfyUI 队列为空。
- ComfyUI Speaker/Multi-Speaker 流程已验证到节点输入层，但当前 ComfyUI 安装缺少 Breeze 节点权重；本次用本地 CLI 完成等价 Voice Clone，避免下载新权重。

## 2026-09-16 Breeze Multi-Speaker 最快固定 ref 测试

- 后续默认对白流程确定为：ComfyUI Breeze `BreezeTTS2LoadModel` 一次加载 → 两个 `BreezeTTS2Speaker` 固定 ref/ref_text → `BreezeTTS2MultiSpeaker` 一次生成；不使用 Whisper，不逐句重启 CLI。
- ComfyUI Breeze bf16 权重已存在本地，无新增下载；使用 CUDA Graphs + SDPA。
- 结果：执行约 **49.37s**，无错误；输出 `/home/sean/projects/ComfyUI/output/h3_digital_human/breeze_clone_known_ref_dual_dialogue_20s_20260916_00001.flac`。
- 输出为 24kHz mono，实际 **22.600s**；目标对白约20s，额外长度来自模型自然停顿/EOS尾部。队列为空，单一 ComfyUI 实例。
- 结论：这是当前最快、最适合后续复用的固定声线对白流程；后续视频使用其音频母带，严格20s时再在末端裁切或收紧对白停顿。

## 2026-09-16 VDN + Breeze Clone 20s 视频测试

- 配置：VDN Ref2VA、1024×576、481帧/目标20s、8 steps、三张同一参考图、NativeAudioLock；唯一变量为 Breeze 固定 ref 生成的 `breeze_clone_known_ref_dual_dialogue_20s_20260916_00001.flac`（实际22.6s）。
- 结果：运行 **943s** 后仍停在 `SamplerCustomAdvanced`，按15分钟阈值中止；无 CUDA OOM、无视频产物。中止后队列为空、GPU释放。
- 结论：不能把本次超时直接归因于 Voice Clone；VDN 采样阶段本身已接近内存/搬运边界，且输入音频实际22.6s而不是严格20s。后续若继续用该对白母带，应先裁成严格20s，并优先使用已验证 PDD 20/23s路线；VDN 20s不再视为当前可接受的快速路线。

## 2026-09-16 VDN 失败后的资源归因与清理

- 失败前队列已空、GPU仅约1.36GiB占用，但 ComfyUI Python RSS约54GiB，系统可用内存约6.6GiB、Swap约1.2GiB；说明主瓶颈是中断后残留的CPU侧 H3/DynamicVRAM staging，而不是显存未释放。
- ComfyUI `/free` 能将显存降到约1.36GiB，但未显著释放进程RSS；重启唯一实例后，RSS约86MiB、系统可用内存约55GiB、Swap约136MiB、显存约384MiB。
- 因此本次 VDN 943s 超时的直接环境原因是内存压力/分页导致采样极慢。NativeAudioLock 源码会将超出目标 latent 长度的音频裁到 `target_t`，所以22.6s音频不是序列长度翻倍的证据，但下次仍应先准备严格20s音频。

## 2026-09-16 清理后 VDN + Breeze Clone 严格20s复测

- 将22.6s Breeze Clone母带以 `atempo=1.13` 保留全部对白压缩为严格19.982583s：`input/vdn_audio_test/dialogue_dual_breeze_clone_vdn_strict20s.wav`。
- 清理后重启单一 ComfyUI，开始时系统可用内存约55GiB、Swap约136MiB、显存约384MiB；配置仍为 VDN、1024×576、481帧、8 steps、NativeAudioLock、三张参考图。
- 结果：成功，端到端 **431s**，无 OOM/中断；视频 `/home/sean/projects/ComfyUI/output/video/h3_vdn_ref2va/breeze_clone_1024x576_20s_20260916_00001_.mp4`。
- ffprobe：1024×576、24fps、481帧、20.041667s；音频20.042s，同步正常。采样期间可用内存最低约10GiB、Swap未增长。
- 收尾释放后：显存约664MiB、系统可用内存约48GiB、队列为空、单一 ComfyUI 实例。
- 结论：VDN之前成功的能力得到复现；上次943s失败主要由中断后残留约54GiB CPU staging/分页造成，而非VDN或Breeze Clone音频本身失败。

## 2026-09-14 1024×576 双角色 VDN 音频/镜头测试

- 统一配置：RTX 4090 24GB、Ref2VA、3 张图片参考、VDN INT8 ConvRot + Turbo、`res_multistep`、8 steps、24fps、1024×576；使用 `NativeAudioLock` 时不使用 `ref_audios`。
- 10s 输入音频版：`dialogue_dual_10s.wav` + NativeAudioLock；采样约 158s（8/8 约 2:38），ComfyUI 总耗时 194.71s；输出 `output/video/h3_vdn_ref2va/dual_dialogue_10s_input_audio_fx_1024x576_00001_.mp4`。
- 10s 原生音频对照：未使用 NativeAudioLock；总耗时 193.36s；输出 `output/video/h3_vdn_ref2va/dual_dialogue_10s_generated_audio_fx_1024x576_00001_.mp4`。另有 voice-ref 原生音频实验输出 `dual_dialogue_10s_voice_refs_native_1024x576_00001_.mp4`，总耗时 199.37s；该实验环境音较弱、角色口型/声线绑定不稳定，不作为主链路。
- 10s 输入音频第二次复测：短提示词、`dialogue_dual_10s.wav` + NativeAudioLock；采样约 160s（8/8 约 2:40），总耗时 220.01s；输出 `output/video/h3_vdn_ref2va/dual_dialogue_10s_run2_1024x576_00001_.mp4`。
- 15s 输入音频版：`dialogue_dual_15s.wav` + NativeAudioLock；采样约 233s（8/8 约 3:52），ComfyUI 总耗时 286.39s；输出 `output/video/h3_vdn_ref2va/dual_dialogue_15s_input_lock_fx_1024x576_00001_.mp4`。
- 20s 输入音频版：`dialogue_dual_20s.wav` + NativeAudioLock；采样约 313s（8/8 约 5:13），ComfyUI 总耗时 391.90s；输出 `output/video/h3_vdn_ref2va/dual_dialogue_20s_input_lock_fx_1024x576_00001_.mp4`。
- 15/20s 运行日志的 DIT 序列分别约 66,562/87,143 rows；采样时 GPU 约 18–24GB，DynamicVRAM 会把约 20GB DIT staged 到系统内存，ComfyUI RSS 峰值约 50–52GiB；任务均无 OOM并完成。测试后重启/清缓存可恢复约 2–3GiB系统内存占用。

### 2026-09-14 普通 Ref2VA + Turbo LoRA 对照

- 配置：普通 `MiniMaxH3ReferenceToVideo`，无 `ApplyVDNH3`；基础模型 `minimax_h3_ref2va_pruned_int8_convrot.safetensors`，加速 LoRA `minimax_h3_ref2v_turbo_8step_v1.0_768p_comfyui_bf16.safetensors`，强度 1.0，`res_multistep`，8 steps，1024×576，三张角色/英雄/冰堡参考图，NativeAudioLock 外部对白，seed 20260914。
- 15s：端到端 393.1s；ComfyUI 日志 390.41s；输出 `output/video/h3_ref2va_ordinary_lora/dual_dialogue_15s_lora8_input_lock_1024x576_00001_.mp4`，实际 15.083s/362 帧。
- 20s：端到端 615.1s；ComfyUI 日志 626s（约 10:26）；输出 `output/video/h3_ref2va_ordinary_lora/dual_dialogue_20s_lora8_input_lock_1024x576_00001_.mp4`，实际 20.042s/481 帧。
- 对照结论：这是 Turbo 8-step LoRA，不是 PDD；同分辨率下普通 LoRA 15/20s 均慢于此前 VDN NativeAudioLock 基线 286.39/391.90s。测试期间 DynamicVRAM 正常把约 20GB DIT staged 到系统内存，未发生 OOM。
- 结论：1024×576、3 图参考、VDN 8-step + NativeAudioLock 在 10/15/20s 均可完成；20s 当前稳定耗时约 6.5 分钟。`ref_audios` 是声音参考/模仿路径，不与 NativeAudioLock 混用；长纯人声 ref 会削弱环境音并造成角色口型/声线绑定不稳定。

## 2026-09-14 高分辨率写实测试

- 用户目视确认前轮 5/10/15 秒画质良好，音频质量尚佳。
- 按要求仅使用 VDN 工作流，不使用 OpenVDN H3 base；改为写实题材、16:9、1024×576、10 秒、241 帧、8 steps。
- 测试成功，端到端耗时约 695 秒；ffprobe：1024×576、24fps、243 帧、10.125 秒，输出：`/home/sean/projects/ComfyUI/output/video/h3_vdn_ref2va/vdn_r241_576sq_00002_.mp4`。
- 资源监控：GPU 利用率 100%；峰值显存按资源采样约 18.2GB/24GB；系统内存峰值约 92.3%（可用约 6.3GB）；无 OOM。
- 资源观测已登记：`3ca7aefa-f894-4977-8dd4-290a212399f2`。
- 结论：VDN 在 4090 上可稳定完成 16:9 1024×576 写实 10 秒生成，但当前高分辨率单条耗时约 11.6 分钟，且系统内存余量偏低；适合继续做质量/长视频验证，暂不视为高吞吐生产参数。

## 2026-09-14 暂停高分辨率 20 秒测试

- 用户确认暂停当前 1344×768、20 秒纯 T2V 任务；该任务在 DIT 阶段 GPU/CPU offload 路径上长时间无有效进展，已停止 ComfyUI 进程并释放 GPU 租约。
- 目标改为寻找 20 秒、16:9、`branch_weights=cache_gpu`、`retain_buffers=on` 的无流式搬运分辨率。
- 依据已测数据：1344×768 在 stream 下约 23.5GB；1024×576 约 18.2GB。要给约 12GB 显存余量以满足 retain buffer，首选候选为 768×448（0.344MP），保守备选 832×480（0.399MP）。候选需用资源监控实测确认，暂不自动执行。
- 0.33MP 纯提示词验证已完成：768×432、20 秒、481 帧、VDN `cache_gpu` + `retain_buffers=off`，DIT 8/8 约 150 秒，整个 prompt 208.3 秒，输出约 10.125 秒视频。采样期间 GPU 约 17.6–18.2GB、100%，系统内存约 45.1GB；无 OOM。日志仍显示 H3 主模型启用 dynamic VRAM loading（约 20GB staged），因此 CPU 侧仍承担主模型 staging，但未观察到 GPU 空转。
- 0.33MP Ref2VA Pic 1 验证已完成：768×432、20.04 秒、481 帧、单张 `03_host_krea_16x9.png`、无参考视频，VDN `cache_gpu` + `retain_buffers=off`。Runner 端到端约 212 秒，ComfyUI 日志 prompt 218.35 秒；DIT 8/8 约 151 秒。资源峰值约 GPU 17.8GB/24GB、系统内存 50.3GB/54.9GB；无 OOM。输出：`/home/sean/projects/ComfyUI/output/video/h3_vdn_ref2va/vdn_ref2va_pic1_768x432_20s_cachegpu_00001_.mp4`。
- 0.33MP Ref2VA Pic 1 30 秒尝试失败：768×432、721 帧、单图、中文固定口播、`cache_gpu`，在 `SamplerCustomAdvanced` 阶段 GPU OOM。错误：当前已分配 5.32GiB、请求 4.07GiB、CUDA 可用 0 bytes；不是系统 CPU 内存 OOM。作业约 40 秒返回 error，未生成视频。
- 1024×576 Ref2VA Pic 1 20 秒测试完成：481 帧、单图、中文固定口播、`branch_weights=stream`、`retain_buffers=off`，成功耗时约 692 秒，实际输出 20.042 秒/481 帧/24fps。资源峰值约 GPU 23.4GB/24GB、系统内存 50.6GB/54.9GB（约 92.1%），无 OOM；观测 ID `24d1849c-8ff3-4fa0-967a-7d91a68dd07c`。输出：`/home/sean/projects/ComfyUI/output/video/h3_vdn_ref2va/vdn_ref2va_pic1_1024x576_20s_stream_00001_.mp4`。
- NativeAudioLock + VDN 20 秒单段测试完成：768×432、481 帧、单张 Pic 1、单文件 `hk_a_30s.wav`（未拼接，NativeAudioLock 锁定外部音频）、`cache_gpu`，成功耗时约 223 秒；实际输出 20.042 秒/481 帧/24fps。DIT 8/8 约 157 秒；峰值 GPU 约 18.8GB、系统内存约 47.4GB；无 OOM。资源观测 ID `960ef544-f02c-417d-b0b1-8fe7230f158d`。输出：`/home/sean/projects/ComfyUI/output/video/h3_vdn_ref2va/vdn_ref2va_nativeaudiolock_vdn_pic1_768x432_20s_00001_.mp4`。
- 修正版 NativeAudioLock + VDN 20 秒测试完成：768×432、481 帧、Pic 1 主角 + Pic 2 演播室背景、单文件 `hk_a_30s.wav` 音频驱动；提示词移除固定台词并明确禁止字幕/文字/图表，成功耗时约 211 秒，实际输出 20.042 秒/481 帧/24fps。峰值 GPU 约 18.0GB、系统内存约 47.4GB；无 OOM。资源观测 ID `71ed2fec-3871-4998-a6cf-a5da2708168f`。输出：`/home/sean/projects/ComfyUI/output/video/h3_vdn_ref2va/vdn_ref2va_nativeaudiolock_vdn_pic1_pic2_768x432_20s_audio_00001_.mp4`。

## 2026-09-16 VDN 简化中远景 1024×576 20 秒复测

- 配置：VDN Ref2VA、三张既有参考图、严格约20秒 Breeze 固定 ref 克隆对白、1024×576、481帧、24fps、8 steps、`branch_weights=stream`、`retain_buffers=off`、分块 VAE 解码；提示词改为固定中远景、完整冰堡背景、禁止特效/松树/叶片/镜头切换。
- 首轮运行因用户观察到 GPU 空转而中止时，实际检查显示任务仍在队列：GPU 23.3/24.6GiB、100%，系统内存已用49GiB、可用8.3GiB；清理后恢复为显存0.76GiB、内存可用48GiB。
- 清理后复测成功，端到端 **380s**，无错误；输出 `/home/sean/projects/ComfyUI/output/video/h3_vdn_ref2va/breeze_clone_1024x576_20s_simple_medium_20260916_00001_.mp4`。
- ffprobe：1024×576、24fps、481帧、20.042s；音频同步存在，时长20.042s。采样峰值约显存23.9/24.6GiB、系统内存已用49GiB/可用8.2GiB，Swap约88MiB且未增长；结束后显存5.9GiB、内存可用38GiB。
- 资源结论：本配置启动前建议系统可用内存至少40GiB、Swap保持基本空闲；显存基线至少预留约1GiB（实际峰值余量约0.6GiB）。运行中可用内存降至8GiB仍能完成，但不应把3–4GiB以下视为安全区。显存接近满并不等于 GPU 停止，本次显存23.9GiB时GPU仍为90–100%；真正的失败风险是CPU侧 DynamicVRAM/staging 与 latent/解码缓存把内存推近上限。中断后的残留RSS必须通过重启唯一ComfyUI实例清掉，单独 `/free` 不足以恢复内存。

## 2026-09-17 VDN 简化提示词成片视觉归因

- 对 `breeze_clone_1024x576_20s_simple_medium_20260916_00001_.mp4` 抽取首段、中段和结尾关键帧，并与三张输入参考图对照。
- 直接原因：该次 prompt 明确包含 `no special effects`、`no frost particles`、`no energy glow`、`no trees`、`no pine branches`、`no leaves`。因此冰霜粒子、额外能量/眼睛闪光被主动压制；Hero 参考图本身也没有发光眼睛，且 prompt 未正向指定 Hero 眼睛发光，所以模型没有生成该效果。
- 背景并非完全消失：参考图中的红色远景魔法光在关键帧仍可见，城堡、火盆和冰雪结构也保留；消失的是未被正向要求的动态霜雾/粒子等效果。静态背景参考图本身不会自动变成动态特效。
- 结尾出现两棵松树属于长序列末端的背景语义漂移/模型先验补全。`no trees` 是负向约束，不能保证20秒内绝对不插入新背景物，尤其在中远景、较小角色和固定背景条件下。现有 metadata 确认本次仅使用 VDN grouped attention、stream、retain_buffers off，未使用 LowVRAMAttention、ChunkFeedForward 或 H3MemoryOptimization，因此没有证据把这些节点作为本次视觉异常原因。
- 后续若要恢复效果，应把“禁止新增物体”和“保留既有效果”分开：正向写明保留原背景的冷蓝霜雾、细雪/冰晶、远处红色魔法天光与火盆火光，并单独指定 Hero 眼睛为 subtle blue-white glow；负向只保留新增松树、松枝、叶片、人物遮挡和镜头切换。不能再使用笼统的 `no special effects`。

## 2026-09-17 标准 H3 Ref2VA 六段式 + NativeAudioLock 复测

- 先核对官方 H3 Ref2VA 六段式：`subject_definitions`、`summary`、`retention_analysis`、`detailed_description`、`overall_soundscape`、`non_diegetic_music`；本次 prompt 3040 字符、六段齐全、未写负面词。
- NativeAudioLock 兼容性核对：外部 `dialogue_dual_breeze_clone_vdn_strict20s.wav` 由 LoadAudio 输入，经 Audio VAE 编码后替换 AV latent 的 audio 部分；`audio noise_mask=0`、`video noise_mask=1`，因此 prompt 不重复编写对白，只用 `<Audio 1>` 说明外部完整对白，并将 `<Subject 1> (S1)` 绑定女性 Sylvanas、`<Subject 2> (S2)` 绑定男性 Hero。
- 配置：VDN、1024×576、481帧、8 steps、三张同一参考图、严格约20秒 Breeze 双人对白、`stream`、`retain_buffers=off`、tiled VAE；唯一 ComfyUI 实例，启动前显存约384MiB、系统可用内存约54GiB、Swap为0。
- 结果：技术执行成功，端到端 **410s**；输出 `/home/sean/projects/ComfyUI/output/video/h3_vdn_ref2va/breeze_clone_1024x576_20s_crisis_effects_positive_20260917_00001_.mp4`。ffprobe：1024×576、24fps、481帧、20.042s，音频32kHz双声道、20.042s。
- 视觉复核：冰霜蓝白效果、冰晶/地面霜光和远处城堡红光均出现，说明正向特效提示生效；但前半段出现 Sylvanas/Hero 近景切换，后半段才回到远景，未完全保持预期的单一固定中远景。NativeAudioLock 本身只锁音频/口型条件，不锁镜头；六段式格式兼容不等于镜头约束硬锁。后续若保留六段式，需要进一步压缩 `detailed_description` 的叙事变化并强化单镜头构图锚点，单独验证镜头稳定性。

## 2026-09-17 六段式分段镜头与分配特效复测

- prompt 按用户指定拆为三段：00:00–00:04 推镜，两人进入，Sylvanas 站定、Hero 向前几步，冰霜只在她出场时响应；00:04–00:16 中景对白，Hero 在 Audio 1 的决心台词处眼部闪光；00:16–00:20 拉镜，远景红光随对白接近结束而增强。
- 结果：VDN + NativeAudioLock 成功，端到端 **411s**；输出 `/home/sean/projects/ComfyUI/output/video/h3_vdn_ref2va/breeze_clone_1024x576_20s_shot_timed_effects_20260917_00001_.mp4`。ffprobe：1024×576、24fps、481帧、20.042s，音频32kHz双声道、20.042s。
- 关键帧复核：开场推入/冰霜响应、两人对白、结尾拉远/远处红光均出现；Hero 在中段出现强调性近景，符合决心表现但超出预设的纯中景，说明 H3 会把情绪重点转成景别变化。三段时间控制有效，镜头景别仍是软约束。
