# 任务进度：T-comfy-ops-33 H3 Ref2VA 对照：PDD 5s 与标准 20-step 5s

> 项目级私有进度（只有本任务线读写；多 PI Agent 并行时互不干扰）。
> 状态标记：🟡进行中 / ⏸暂停 / ✅完成。
> 共享状态（焦点/活跃决策/全局待办）在 `[STATE]`（hive-state），不写在这里。

## 任务
- 目标：在同一 Ref2VA 配置下严格对照 PDD Acc 8-step 与原版 20-step 的 5 秒片段（速度 + 质量），用于决定 PDD 能否作为 Ref2VA 日常快车道。
- 当前状态：🟡 跑批完成，等用户目视/试听验收
- 任务产物统一落 `/home/sean/projects/ComfyUI/input` 与 `/home/sean/projects/ComfyUI/output`；本项目仅保留本任务进度记录。

## 进度日志（append-only，每条带日期）

### 2026-09-15
- 开局 recall/对账：T-comfy-ops-33 未在 `docs/34` 定论，仅有一条「后续单独测试 PDD 5s 与无 LoRA 标准 20-step 5s，不能与 VDN Turbo 1024×576 结果混记」的边界说明；`[STATE]` 已有本任务认领（准备严格 5 秒对照跑批）。ComfyUI 在 8188 运行、队列空、GPU 空闲（约 0.4/24GB）。
- 环境事实：ComfyUI `input/vdn_audio_test/` 中准备测试音频；生成视频统一写入 ComfyUI `output/video/`。
- 脚本改造：`scripts/h3_ref2v_runner.py` 新增 `pdd` 支持（`MiniMaxH3PDDAccApply` → `MiniMaxH3SigmaShift` → `NativeAudioLock`，采样器自动切 `euler`、sigmas 取自 PDD 节点），并给 results.json 记录 `exec_ms`。
- 严格对照（除采样路线外全同参）：同一参考图 `ref2va_refs/digital_human/01_host_blank_gray_16x9.png`、同一 5.000s 粤语音频、同一六段式 prompt、同一 seed `20260914`、768×448、124 帧、shift 12/3、NativeAudioLock；A=无 LoRA `res_multistep` 20 steps，B=Ref2VA PDD Acc nfe 8 + `euler`。
- 结果：A 端到端 90.0s（ComfyUI 内部 86.50s，采样 20 步 53s）；B 端到端 40.0s（内部 33.38s，采样 8 步 19s，PDD 加载/打补丁约 2s）。两者均为 124 帧 / 5.167s / 768×448 / 24fps，音频流 163 帧，无冻结帧。
- 指标：整片 SSIM A-vs-B 0.867；运动能量（帧差）A face 0.70 / body 0.50，B face 0.84 / body 0.36；逐帧面部运动序列相关 0.616；音频包络 vs 面部运动代理相关 A 0.061、B −0.04（弱，只能当异常筛查，不能当口型结论）。
- PDD 侧日志确认走对通道：`partition check ok: ref2va file on ref2va model (fl2va 0.0504, ref2va 0.0017)`、`steps=8 blocks=4,4,4,4,4,4,4,4, heads fused`、`50 adaln modules rebased onto the ref2va curve basis`。
- 卡点：本机视觉质检通道不可用（DashScope VL 免费额度耗尽、LM Studio 未启动），**画质/口型结论只能由用户目视**。已备接触表 `contact_AB.png` + 8 张单帧。

## 下一步
1. 用户目视/试听 A（标准 20 步）与 B（PDD 8 步）成片，判定身份/构图/口型/稳定性是否可接受。
2. 若质量可接受 → 把 PDD 8-step 记为 Ref2VA 日常快车道；若不可接受 → 保留 20-step 质量基线，PDD 降级为预览档。
3. 可选延伸：同条件补 4-step 档（`nfe=4`）与更长时长（10s/15s）验证 PDD 在 Ref2VA 上的斜率是否与 FL2VA 一致。

## 关键链接
- 成片：`/home/sean/projects/ComfyUI/output/video/`
- 相关文档：`docs/34_ref2va_generation_guide.md`、`docs/35_vdn_h3_ref2va_route.md`
- 相关 ledger：`.pi/ledger/h3-speed.md`（C-20260915-01）

### 2026-09-15：用户澄清目标后的双角色参考图 probe

- 用户明确：本任务第一目标不是再次证明 PDD 比 20-step 快，而是验证 **PDD 8-step 能否正确使用指定参考图**。
- 使用三张指定参考图：`sylvanas_style.png`（女精灵）、`original_caped_hero.png`（蓝衣红披风英雄）、`ice_fortress_background.png`（冰堡背景）。
- 最小化条件：PDD Acc 8-step、768×448、124 帧（实际 5.167s）、seed `20260915`、NativeAudioLock、固定双人中景、无镜头运动。
- 生成成功，ComfyUI 用时 35.0s；画面抽检 0.1/1.5/3.0/5.16s：两名角色和冰堡背景均正确出现，左右站位稳定，未见明显参考图漏用或角色串位。
- 产物：`/home/sean/projects/ComfyUI/output/video/h3_ref2va_pdd8_vdn_dual_ref_probe_5s_00001_.mp4`。

### 2026-09-15：同提示词标准 20-step 复测

- 按用户要求保持三张参考图、音频、prompt、seed、分辨率和帧数完全一致，仅移除 PDD，改用原生 Ref2VA 20 steps。
- 结果：`/home/sean/projects/ComfyUI/output/video/h3_ref2va_vdn_dual_ref_probe_5s/std20_vdn_dual_ref_probe_5s_00001_.mp4`，ComfyUI 用时 65.1s。
- 初步目视：标准 20-step 中女精灵、蓝衣红披风英雄、左右站位与冰堡背景均稳定可辨；相较 PDD 8-step，人物参考保持明显更好。
- 初步归因：同一 prompt 下标准版明显改善，当前更支持“PDD 8-step 参考图适配问题”，而不是 prompt 单独导致。
- 当前判断：**PDD 8-step 通过“是否使用三张参考图”的第一轮功能性验收**；最终是否达到用户要求的身份相似度，仍以用户看片为准。

### 2026-09-15：1024×576、5 秒 PDD/VDN 冷热启动时间补齐

- 条件统一：RTX 4090、1024×576、124 帧（约 5.167 秒）、同三张参考图、同 VDN prompt、同 `dialogue_dual_5s.wav`、同 seed `20260914`。
- PDD 8-step：卸载模型后端到端 115.4s，ComfyUI 实际执行 106.6s；同流程再次提交命中缓存，端到端 5.0s，实际执行 2.3s。
- VDN：卸载模型后端到端 130s，ComfyUI 实际执行 122.1s；同流程再次提交命中缓存，端到端 10s，实际执行 2.2s。
- 解释：冷启动包含模型重新加载/初始化与完整 5 秒视频生成；本轮热启动被 ComfyUI execution cache 命中，不能当作真实重新生成速度。冷启动下 PDD 比 VDN 快约 14.6s（约 12%）。
- 产物：`/home/sean/projects/ComfyUI/output/video/h3_ref2va_same1024_5s/` 下的 `pdd8_cold_00002_.mp4`、`pdd8_hot_00001_.mp4`、`vdn_cold_00002_.mp4`、`vdn_hot_00001_.mp4`。

### 2026-09-15：最终选型与产物整理

- VDN 768×448 5/10/15/20 秒全部成功，端到端约 90/140/190/230 秒；VDN 1024×576 10/15/20 秒全部成功，约 195/286/392 秒；VDN 1344×768 5/10 秒成功，12 秒以上出现系统内存搬运风险，15 秒不可接受，20 秒 OOM。
- PDD + SageAttention 1024×576/15 秒成功，约 235 秒；尚未完成 20 秒同口径验证。
- 正式生成建议：1024×576 + VDN + 8 steps + NativeAudioLock，时长 10–20 秒；768×448 仅作快速筛选；不再补测其他分辨率长时长，除非专门验证 PDD 20 秒替代方案。
- 产物已整理到 ComfyUI 输出目录：VDN `/home/sean/projects/ComfyUI/output/video/h3_vdn_ref2va_clean/`，PDD+Sage `/home/sean/projects/ComfyUI/output/video/h3_pdd_sage_ref2va_clean/`；普通 PDD/标准 20-step/重复缓存移入 `_discarded_t33_no_sage_or_duplicate/`。
- 现行结论已写入 `docs/34_ref2va_generation_guide.md`、`docs/35_vdn_h3_ref2va_route.md` 和 `.pi/ledger/h3-speed.md` C-20260915-02，并 retain 到 comfy-ops Mem0。

### 2026-09-15：H3-Optimizations 与采样后释放/tiled decode 硬件边界测试

- 安装并加载 `/home/sean/projects/ComfyUI/custom_nodes/H3-Optimizations`，使用独立 systemd ComfyUI 服务重载；未产生重复进程。
- H3-Optimizations 单独测试：PDD 8-step + SageAttention + `H3MemoryOptimization(chunk_rows=4096, Preserve native, QKV Auto)`，1024×576、481 帧/20 秒成功，端到端 **335.3s**；峰值 GPU 约 23.0GB，系统内存约 52GB。日志显示外部 SageAttention 下 QKV bounded streaming 为兼容性关闭，实际启用 ConvRot MLP/FinalLayer 分块。
- 采样后释放 + 视频 tiled VAE：同配置增加 KJ `VRAM_Debug(unload_all_models=true)`，视频使用 `VAEDecodeTiled(tile=512, overlap=64, temporal=64/8)`，音频因 `VAEDecodeAudioTiled` 对 H3 joint latent 报 `IndexError` 改回普通 `VAEDecodeAudio`；强制改 seed 避免 execution cache 后完整运行成功，端到端 **336.7s**。
- 释放节点实测：可用显存从 `13,037,032,392` 增至 `23,915,458,652` bytes；采样后观测 GPU 显存约 6.3GB、系统内存约 15GB，说明模型回收真实生效。相对纯 H3-Optimizations 只增加约 1.4s，值得保留作为高分辨率/长视频安全路径，但它不降低采样阶段的 RAM 峰值。
- 音频 tiled 失败是节点兼容性问题，不计作整条流程失败；视频 tiled + 普通音频解码成功。
- 产物已整理到 `/home/sean/projects/ComfyUI/output/video/h3_pdd_sage_ref2va_clean/`：`pdd_sage_h3opt_1024x576_20s_335s.mp4`、`pdd_sage_h3opt_release_tiled_1024x576_20s_337s.mp4`。

### 2026-09-15：PDD + H3-Optimizations 冲击 1344×768/15s

- 配置：PDD 8-step + SageAttention + H3 `H3MemoryOptimization(chunk_rows=4096, Preserve native)` + KJ `VRAM_Debug(unload_all_models=true)` + 视频 `VAEDecodeTiled(tile=512, overlap=64, temporal=64/8)`；音频保持普通 `VAEDecodeAudio`。
- 结果：1344×768、361帧、15.083s 成功，端到端 **516.2s**（约8分36秒），未超过15分钟失败阈值。
- 资源：采样阶段 GPU约100%、显存约23GB、系统RAM约43GB、swap无明显增长；采样后释放前后可用显存 `22,029,620,168 → 23,915,458,652` bytes，收尾阶段显存约6.7GB、系统RAM约14GB。
- 结论：新流程把此前普通 PDD/VDN 1344×768/15s 的高内存风险压到可完成，但耗时显著高于1024×576/20s的336.7s；1344×768/15s可作为硬件上限/高分辨率直出档，不作为日常性价比档。
- 产物：`/home/sean/projects/ComfyUI/output/video/h3_pdd_sage_ref2va_clean/pdd_sage_h3opt_release_tiled_1344x768_15s_516s.mp4`。

### 2026-09-15：VDN 同流程边界复测与取消

- VDN 1344×768/15s：结构确认正确，为 `ApplyVDNH3(stream, retain_buffers=off, grouped)` → `NativeAudioLock` → 8步采样 → KJ `VRAM_Debug` → 视频 `VAEDecodeTiled`；运行约320s后按用户要求中断，实际停在 `SamplerCustomAdvanced`，未进入释放/解码，无产物。单一 systemd ComfyUI 进程，无重复服务。
- VDN 1024×576/25s：用20秒双人对白补5秒静音得到 `input/vdn_audio_test/dialogue_dual_25s.wav`，同一 VDN + 释放/tiled流程尝试；运行 **935s** 后仍停在采样阶段，系统RAM约44GB、可用约10–12GB、GPU约24GB满载，按15分钟阈值中断；未进入释放/解码，无产物。
- 脚本修复：`scripts/h3_batch_runner.py` 现在会将 ComfyUI `execution_interrupted` 正确记录为错误，不再误报成功。
- 清理后：队列为空、GPU约0%、显存约0.7GB；ComfyUI仍为单一systemd进程。当前结论：VDN 1024×576/25s 在本机资源边界内不可在15分钟内完成；下一步不再继续冲25s，优先保留已成功的1024×576/20s。

### 2026-09-15：失败原因归因与明日续测边界

- **已确认不是节点兼容性错误**：两次 VDN 任务都没有执行到 `VRAM_Debug` 或 `VAEDecodeTiled`；历史状态只显示采样节点 `SamplerCustomAdvanced` 被中断，没有 `execution_error`、CUDA OOM 或 tiled VAE 错误。因此不能把“采样后释放模型 + tiled VAE”判为 VDN 失败原因。
- **1024×576/25s 的直接原因**：VDN 采样阶段持续 GPU 满载、显存约24GB，系统RAM从约30GB逐步升到约44GB，可用内存降到约10–12GB；935秒仍未完成采样，接近系统内存/搬运风险，按15分钟阈值主动取消。它不是已捕获的硬 OOM，而是超过可接受时间并逼近内存边界。
- **1344×768/15s 的直接原因**：运行约320秒时用户观察到 GPU 长时间无动作，人工取消；复核时流程实际仍在 `SamplerCustomAdvanced`，未进入解码，故这是人工中断，不是生成错误。此前系统监控在部分时段可见GPU满载，说明不能仅凭一次GPU读数断言卡死。
- **当前可确认的根因层级**：VDN 的高分辨率/长时长主要受采样阶段的显存满载、DynamicVRAM/系统内存压力和整体采样时间限制；采样后释放模型只能改善后处理峰值，不能缩短或降低采样阶段资源需求。
- **明日续测策略**：先用 VDN 1024×576/20s 作为已成功基线，逐步测试21–23s或1344×768/10s；每次记录采样是否完成、GPU利用率连续性、RAM可用量和是否真正进入释放/tiled阶段。暂不直接再次冲25s。

### 2026-09-19：PDD + SageAttention 与 H3MemoryOptimization 质量 A/B

- 目的：在当前已能生成 1024×576/20s 的前提下，先验证 H3MemoryOptimization 是否会复现此前 patch/optimization 引起的闪动、身份漂移或语义串入；不测试 KJ Low VRAM、Sparse Attention、Sol、MC 或二采。
- 条件完全固定：三张 Ref2VA 参考图、既有双人对白 prompt、NativeAudioLock 音频、seed `20260920`、`minimax_h3_ref2va_pruned_int8_convrot.safetensors`、PDD Acc 8-step、SageAttention、1024×576、241 帧（约10.13s）、采样后释放、视频 tiled VAE。
- 基线：PDD + SageAttention；端到端 **135.4s**。
- 对照：基线加 `H3MemoryOptimization(chunk_rows=4096, Preserve native, QKV Auto)`；端到端 **115.4s**。
- 两段均成功输出，视频规格均为 1024×576、24fps、10.13s。接触表抽查约每2秒一帧：两组人物左右位置、服装、冰堡背景和英雄发光眼睛均保持稳定，未见明显闪动、松树串入、人物身份错配或额外角色。
- 两组视频 SSIM `All=0.851064`，说明优化路径并非逐像素相同；但该指标不是质量判定，目视结构与时序稳定性筛查通过。单次运行的 20s 时间差不能视为稳定加速，可能受模型/缓存与执行顺序影响。
- 结论：H3MemoryOptimization 可进入 **可选安全路径**，当前没有证据表明它造成此前的质量问题；但因为本轮是10s质量筛查而非20s显存峰值复测，暂不把它升级为强制默认，也不据此宣称稳定提速。正式长视频仍保留现有 `PDD + SageAttention + H3MemoryOptimization + 采样后释放 + 视频 tiled VAE` 作为候选路线，需以用户看片和必要的20s复测最终确认。
- 实验配置：`experiments/h3_digital_human/pdd_sage_vs_h3opt_1024x576_10s_20260919.json`；结果：同名 `.results.json`；输出位于 `/home/sean/projects/ComfyUI/output/video/h3_pdd_sage_ref2va_clean/`。
- 纠正：该轮 prompt 实际是旧式 `<Picture 1/2/3>` 简化字符串，不是标准六段式 Ref2VA，也没有用 `<Subject N>` 定义引用对象职责；因此只能作为 **未事先授权的 quick comparison / 优化稳定性筛查**，不得用于判断人物、服装或背景 reference object 是否正确生效。此前“质量筛查通过”的表述仅限于未见明显优化引起的闪动/错配，不能扩展为标准 Ref2VA 质量结论。

### 2026-09-19：标准六段式 Ref2VA + 正确三图字段的 H3MemoryOptimization A/B

- 旧实验处理：原配置保留为历史记录，并将 case 名标注为 `legacy_simplified_*`、`legacy_simplified_historical_not_standard_ref2va`；不再作为标准基线。
- 修正了两个实际问题：prompt 改为标准六段式 `subject_definitions / summary / retention_analysis / detailed_description / overall_soundscape / non_diegetic_music`，并将 runner 配置字段从此前错误的 `refs` 改为实际生效的 `ref_images`。此前 runner 只读取 `ref_images`，旧实验虽然记录了 `refs`，实际工作流没有加载三张图。
- 正式 A/B 条件：三张引用图、标准 Ref2VA prompt、NativeAudioLock 音频、seed `20260921`、PDD 8-step、SageAttention、1024×576、241帧/10.125s、采样后释放、视频 tiled VAE；唯一变量为是否启用 `H3MemoryOptimization`。
- 基线：标准 Ref2VA + PDD + SageAttention，端到端 **145.1s**。
- 对照：基线加 `H3MemoryOptimization(chunk_rows=4096, Preserve native, QKV Auto)`，端到端 **125.3s**。
- 两组均成功。抽帧确认：冰堡城墙/拱门/积雪环境、白发尖耳女性的黑色冰甲与披风、蓝衣红披风英雄及金色面罩均实际进入画面；两组的人物左右关系和环境整体稳定，抽样未见明显闪动、身份串位或松树等无关物体串入。
- 结论：这一轮才是有效的“标准 Ref2VA reference object + 优化节点”对照。H3MemoryOptimization 在本轮没有表现出明显质量回退；运行时间单次差异仍不能视为稳定加速，20秒显存峰值尚未重新测量。
- 配置：`experiments/h3_digital_human/pdd_sage_vs_h3opt_standard_ref2va_1024x576_10s_20260919.json`；结果：同名 `.results.json`；输出：`/home/sean/projects/ComfyUI/output/video/h3_pdd_sage_ref2va_standard/`。

### 2026-09-19：标准 Ref2VA 20 秒复杂动作/镜头/背景动画 A/B

- 条件：沿用标准六段式 Ref2VA、正确 `ref_images` 三图、PDD 8-step + SageAttention、1024×576、481 帧/20.042s、同 seed `20260922`、同 `dialogue_dual_20s.wav`、采样后释放、视频 tiled VAE；20 秒明确记录为超出 H3 官方 4–15 秒目标范围的本地扩展压力测试。
- 复杂内容：六段时间线，宽景建立、推进、横向环绕、过肩、推近、半环绕、拉远；女性冰霜施法、头发/披风/冰晶运动；英雄前进、防御动作、红披风运动、蓝白眼部能量；背景雪、旗帜、火盆、冰晶、雾气和反光持续动画。
- 基线：标准 Ref2VA + PDD + SageAttention，成功，端到端 **330.2s**。
- 对照：加 `H3MemoryOptimization(chunk_rows=4096, Preserve native, QKV Auto)`，成功，端到端 **320.2s**。
- 两组输出均为 1024×576、24fps、20.042s。抽取约 0/3/6/9/12/15/18 秒关键帧：两组均保持冰堡空间、女性/英雄身份、服装、左右关系和镜头阶段；背景火盆、旗帜、积雪/冰面和风雪动画持续存在，暂未见明显闪动、额外角色、手部复制或身份串位。复杂动作是否逐帧自然仍需用户看片确认。
- 音频：两组封装规格一致（AAC 32kHz stereo，约128kbps）；EBU R128 综合响度均约 **-26.3 LUFS**，LRA 均约14.5–14.6 LU；Opt 真峰值约 **-11.6 dBFS**，基线约 **-10.5 dBFS**，Opt 低约1.1dB，和用户听到的轻微音质/力度劣化方向一致，但不是响度整体下降。
- 结论：在标准 Ref2VA 和复杂20秒内容下，H3MemoryOptimization 没有造成明显视频质量回退，运行时间只快约10秒，不能视为稳定加速；音频存在轻微劣化迹象，当前不建议把 Opt 版作为音频质量优先的默认流程。正式结论仍以用户完整看片/试听为准。
- 配置：`experiments/h3_digital_human/pdd_sage_vs_h3opt_standard_ref2va_1024x576_20s_complex_20260919.json`；结果：同名 `.results.json`；输出：`/home/sean/projects/ComfyUI/output/video/h3_pdd_sage_ref2va_standard/`。
- 事后纠正：原始 `original_caped_hero.png` 参考图不带眼罩；本轮标准 prompt 错误地自行加入了 `gold-trimmed eye mask`，并在多个镜头段重复。因此本轮视频的英雄外观还原结论作废，不能把生成出的眼罩归因于参考图。后续修正版必须删除所有眼罩描述后重跑；本轮仅保留为“含错误 prompt 的历史压力测试”。

### 2026-09-19：原生 H3 20-step Dense vs H3 Sparse 30% 隔离探测

- 条件：标准 Ref2VA 六段式 prompt（复用既有标准测试文本）、正确三张 `ref_images`、原生 `res_multistep` 20 steps、1024×576、约10秒、同 seed；Dense 与 Sparse 唯一目标变量为 `H3SparseAttention(video_budget=0.30, denser_early=True)`。
- Dense：`PathchSageAttentionKJ + H3MemoryOptimization + 原生20步` 成功，端到端 **275.2s**，输出已生成。
- Sparse：同一条 Sage + H3Memory 链路再接 `H3SparseAttention` 后，GPU 持续工作、显存约23GB，但运行约 **55分钟** 仍未完成；已中断，未得到可用输出。
- 结论：当前这条“显式 Sage + H3Memory + H3Sparse”组合在本机不具备快速通道意义。该结果不能证明 Sparse 算法本身质量差，更可能说明节点组合触发了不兼容/回退路径；在未做后端隔离前，不继续调低 budget，也不进入 Sol/VSA 对比。
- 配置：`experiments/h3_digital_human/native20_dense_vs_h3sparse_1024x576_10s_20260919.json`；Dense 输出：`/home/sean/projects/ComfyUI/output/video/h3_pdd_sage_ref2v_sparse_probe/native20_dense_1024x576_10s_20260919_00001_.mp4`。

### 2026-09-19：无 Sage 的 H3 Sparse backend 隔离与 Dense 对照

- 条件：5 秒、1024×576、原生 `res_multistep` 20 steps、同 seed、同三张参考图、同标准 Ref2VA prompt、同 H3MemoryOptimization；唯一变量为 `H3SparseAttention(video_budget=0.30)`。
- Sparse：日志明确为 `Comfy Kitchen INT8 Sparse`，20/20 步完成，ComfyUI 执行 **135.19s**，runner 端到端 **140.1s**。
- Dense：20/20 步完成，ComfyUI 执行 **190.25s**，runner 端到端 **190.7s**。
- 初步速度结果：Sparse 比 Dense 少约 **50.6s（26.5%）**。这是单次短片测试，不能直接外推到20秒，但已证明 Sparse backend 在无 Sage 时真实生效并有加速。
- 当前建议：H3 Sparse 可作为独立快速路径；不要与显式 SageAttention 叠加。FlashAttention 暂不安装，当前 Comfy Kitchen INT8 Sparse 已正常工作；后续优先做两组输出的画质/闪动检查，再决定是否做更长视频复测。
- 配置：`native20_h3sparse30_no_sage_1024x576_5s_20260919.json` 与 `native20_dense_no_sage_1024x576_5s_20260919.json`；结果文件分别为同名 `.results.json`。

### 2026-09-19：修正已知眼罩误加后的 Sparse 10/20 秒测试

- 修正方式：没有重新描述主角，只对复用的历史标准 Ref2VA prompt 做窄范围删除，去掉此前错误加入的 `gold-trimmed mask/eye mask`；三张 reference object、字段结构和其余内容保持不变。
- 10 秒：无 Sage + H3Memory + H3Sparse30，成功，端到端 **235.2s**；日志为 `Comfy Kitchen INT8 Sparse`，无 fallback。
- 20 秒：同条件，成功，端到端 **545.5s**；日志为 `Comfy Kitchen INT8 Sparse`，无 fallback。
- 与已有 PDD+Sage 参照相比：10 秒 PDD+Sage 为145.1s，Sparse原生20步慢约90.1s；20秒 PDD+Sage为330.2s，Sparse原生20步慢约215.3s。二者步数/架构不同，不能作为纯 backend 对比；说明 Sparse 的优势是相对同等原生 Dense，而不是替代当前 PDD+Sage 的端到端速度。
- 配置：`native20_h3sparse30_no_sage_1024x576_10s_corrected_20260919.json`、`native20_h3sparse30_no_sage_1024x576_20s_corrected_20260919.json`；结果文件为同名 `.results.json`。画质仍需看片确认。
