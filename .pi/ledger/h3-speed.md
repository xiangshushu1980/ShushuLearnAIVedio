# H3 速度/加速/管线结论谱系

> 速度定论演进史。规则见 README.md。append-only。

## 条目索引

| C-ID | 主题 | 状态 | 备注 |
|---|---|---|---|
| C-20260816-01 | H3 管线三档 + 15s 长档 | ✅现行 | valid_from 08-10 / 长档 08-12 |
| C-20260816-02 | TE/DiT 模型加载时间（80s→~11s） | ✅现行 | swap 污染修正 |
| C-20260816-03 | SageAttention 加速 | ✅现行 | 节点级定稿 |
| C-20260816-04 | Sol-Attn 弃用 | ✅现行 | 含结论反转过程 |
| C-20260816-05 | MotionCache 适用域 | ✅现行 | 14 步无价值 |
| C-20260816-06 | H3 两阶段流水线（cond 缓存） | ✅现行 | N=3 省 ~37s |
| C-20260816-07 | ComfyUI 0.32.0 修复验证 | ✅现行 | #15486 生效 |
| C-20260816-08 | fl2v Turbo LoRA 代际定案 | ✅现行 | F 维持/G 备选 |
| C-20260816-09 | Ref2VA Turbo 4 步速度 | ✅现行 | 2.5-3x |
| C-20260816-10 | Ref2VA ref_image_size 策略 | ✅现行 | match/max 实测反转 |
| C-20260914-01 | VDN Ref2VA 1024×576 双角色长时基线 | ✅现行 | valid_from 09-14 |
| C-20260914-02 | 普通 Ref2VA Turbo LoRA 1024×576 双角色长时基线 | ✅现行 | valid_from 09-14 |
| C-20260915-01 | Ref2VA PDD 8-step 与标准 20-step 5 秒同参对照 | ✅现行 | valid_from 09-15 |
| C-20260915-02 | H3 Ref2VA 双角色正式生成分辨率与路线选型 | ✅现行 | valid_from 09-15 |
| C-20260915-03 | PDD + Sage + KJNodes 低显存节点冲刺 1024×576/20s | ✅现行 | valid_from 09-15 |

---

### C-20260816-01 | H3 管线三档定稿（Turbo 时代）+ 15s 长档开放
- 状态：✅现行（valid_from 2026-08-10；长档 2026-08-12）
- 现行值：极速抽卡 fp8+sage+v4-600EMA 4步 @768×448 = 45s/8s；快速抽卡 fp8+sage+8步 @768×448 = 67s/8s（复杂动作 88s）；正式成片 int8_convrot+sage+8步 @1024×576 = 125s/8s；长档 15s = 成片档配置 ×360帧 = 230-275s/15s
- 时间线：
  - 2026-08-04 提出：base 双档（fp8+14步@768×448 = 75s/5s 快速；fp8+20步@1024×576 成片 5s≈2min / 10s≈5min / 15s≈8min）（任务线 h3-patch-test）
  - 2026-08-10 定稿：turbo 三档替代 base 双档（int8_convrot 消除 960/1024 offload 抖动；fp8 同规格 185-385s；来源任务 h3-turbo-pilot，mem0 25c7c379）
  - 2026-08-12 修正：成片档 0.32.0 复测 140s（125-158s 批次区间内基线水平）；15s 长档正式开放（≤10s 限制用户拍板放宽，内存峰值 45-51GB 安全；来源任务 T-20260812-07）
- 证据锚：params.md §管线三档 / docs/09_h3_test_plan.md（补测批 D）/ .pi/tasks/comfyui-032-verify/progress.md

### C-20260816-02 | H3 TE/DiT 模型加载时间（80s→~11s 修正）
- 状态：✅现行（valid_from 2026-08-16）
- 现行值：TE 冷全链 ~11s（load_clip 惰性 4.5s + 首次前向含 nvfp4 反量化 6.7s）/ 热 ~4s（二次前向 0.3s）；DiT int8 冷 14.6s / 热 3.4s
- 时间线：
  - 2026-08-05 提出：TE 加载 ~80s/次 = 最大固定开销，两阶段流水线立项依据（来源任务 h3-patch-test，WSL 内存顶满压力态）
  - 2026-08-16 修正：冷 ~11s / 热 ~4s（原因：80s 系 swap/内存压力污染，posix_fadvise 逐出页缓存受控复测，健康态真实值；覆盖 2026-08-05 版本；来源任务 T-20260816-01/02）
- 证据锚：params.md（加载耗时前提已修正）/ docs/10_h3_batch_optimization.md（已修正）/ scripts/h3_load_cost_probe.py / .pi/tasks/cond-cache-node/progress.md

### C-20260816-03 | SageAttention 加速
- 状态：✅现行（valid_from 2026-08-15）
- 现行值：默认 = 节点级 `PathchSageAttentionKJ`（sage_attention=auto）≈ 纯 attention 的 1.5-2x（@1024×576 8步 124帧：wave 44.3s / dance 43.9s vs plain 91.8s / 66.8s）；采样级 1.65x（生产单任务 77s→65s，采样 51s→31s）；对音频零影响（0.2 LU 不可辨）
- 时间线：
  - 2026-08-05 提出：全局 sage ~30% 提速、音频对照零影响（来源任务 h3-patch-test）
  - 2026-08-15 定稿：start.sh 去全局 sage 改节点级，干净对比 1.5-2x（来源任务 T-20260815-07）
  - 2026-08-16 补充：采样级分解 1.65x、单任务耗时构成定准（TE+DiT+LoRA 冷 ~22s / 热 ~7s + 采样 ~31s + decode ~12s；来源任务 T-20260816-01）
- 证据锚：params.md §加速策略 / scripts/h3_sage_breakdown.py / output/compare/attn3way_{wave,dance}.png

### C-20260816-04 | Sol-Attn 弃用
- 状态：✅现行（valid_from 2026-08-15）
- 现行值：弃用——耗时与 Sage 持平（44.9s/44.6s，无速度优势）、高动态 dance 鬼畜崩、首轮 1.07x 对比失真（当时 baseline 实为全局 sage）
- 时间线：
  - 2026-08-14 提出：sage 45s vs sol 42s = 仅 1.07x（远低于 README 宣称 1.14-1.44x，那是 5090 Blackwell 实测）；SSIM 0.786 / PSNR 23.9dB 画质差异明显 → 不建议默认采用（来源任务 T-20260815-07）
  - 2026-08-15 反转尝试：多内容对比 sol 稳定快 ~8%（portrait 56→52s / forest 48→44s / dance 48→44s）+ 用户目视 sol 无马赛克（sage 浪头有噪音）→ 结论待确认
  - 2026-08-15 最终：去全局 sage 改节点级后同 seed 2 场景×3 方式干净对比，sage/sol 耗时持平；**Sol-Attn 弃用**（无速度优势 + dance 鬼畜崩）；"sage 浪头马赛克"未复现（wave 三方式均无马赛克，疑 seed/内容相关），不构成 sage 系统性问题（覆盖 08-14/08-15 两版本；来源任务 T-20260815-07）
- 证据锚：params.md §加速策略（Sol-Attn 弃用）/ output/video/solattn_multi/ / workflows/solattn_test.json / .pi/tasks/h3-new-findings-test/progress.md

### C-20260816-05 | MotionCache 适用域
- 状态：✅现行（valid_from 2026-08-05）
- 现行值：14 步下无实用价值（默认只跳 1/14；激进 warmup2/thr0.25/maxskip3 跳 4/14 但 score 开销抵消，净收益 ~3s）→ 快速档去 MC；仅 20 步画质档可作加速选项（1.25-1.33x）
- 时间线：
  - 2026-08-05 提出：快速抽卡档实测，MC 在 14 步无实用价值 → 管线表更新（快速档去 MC、MC 定位改 20 步档；来源任务 h3-patch-test）
- 证据锚：params.md §关键参数（MotionCache）/ docs/09_h3_test_plan.md（补测批 D）

### C-20260816-06 | H3 两阶段流水线（cond 缓存批处理）
- 状态：✅现行（valid_from 2026-08-16）
- 现行值：cond 是标准 `[(tensor, {attrs})] list`（非 dict，docs/10 原假设需更新）；序列化往返逐位一致（MSE=0，video+audio latent）；自定义节点 Save/LoadMiniMaxH3Cond 落地；批处理脚本形态（非守护进程）N=3 实测总 158s vs 单任务 3×65s=195s，省 ~37s（≈(N-1)×~19s）
- 时间线：
  - 2026-08-16 提出：cond 往返逐位一致（MSE=0）、落盘 cond 采样 vs 热路径逐位一致 → 两阶段可行坐实（来源任务 cond-roundtrip）
  - 2026-08-16 修正：收益基数从「省 80s TE 重载」改为 ~22s/任务冷加载（联动 C-20260816-02；守护进程按 ~22s/任务评估判定过度设计，改批处理脚本；来源任务 T-20260816-01）
- 证据锚：custom_nodes/ComfyUI-MiniMax-H3-CondCache/ / scripts/h3_two_stage_batch.py / scripts/h3_condcache_verify.py / .pi/tasks/cond-cache-node/progress.md

### C-20260816-07 | ComfyUI 0.32.0 H3 修复验证
- 状态：✅现行（valid_from 2026-08-12）
- 现行值：#15486（峰值内存修复）生效——15s 长档从内存压力禁用变生产可用（fp8 15s 768×448 335s vs 旧 615s -46%；int8 245s vs 503s -51%；内存峰值 45-51GB @15s 1024 安全）；#15446（VAE 优化）无明显提速（成片档 140s 基线水平）
- 时间线：
  - 2026-08-05 提出：fp8 15s = 615s / int8 15s = 503s，15s 疑内存压力禁用（来源任务 h3-patch-test）
  - 2026-08-12 修正：0.32.0 下 -46%/-51%；成片档 15s 扩展 = 275s（新能力，8s 的 ~2x 线性）；≤10s 限制放宽由用户拍板（来源任务 T-20260812-07）
- 证据锚：params.md §0.32.0 验证补充 / .pi/tasks/comfyui-032-verify/progress.md

### C-20260816-08 | H3 fl2v Turbo LoRA 代际定案
- 状态：✅现行（valid_from 2026-08-11）
- 现行值：成片档维持 **F（v4-600EMA 8步 @1024×576 int8_convrot）** 不动；**G（lightx2v v1.0 8step + res_multistep + SigmaShift 12/3 + 1024×576，144s）留作风备选**（画面干净但细节少）；4 步档全部判败（v1 代 ckpt500/850 画质胡/音频崩；v1.0-4step H 65s 糊淘汰）；v1-8step 在 768×448 下音频异常安静 12dB 不可用（须 1024×576）；TurboSampler 只配 v4/v0.1 4步，对 v1-8step 音频崩
- 时间线：
  - 2026-08-07 提出：v1 代 4 步（larryvrh / ckpt500/850 pruned）50s 快 ~48% 但 turbo 全胡、写实 480p 细节上限坐实 → 画质 gate 不通过判败（来源任务 h3-turbo-pilot）
  - 2026-08-11 修正：v1.0 8 步蒸馏在 1024×576 下可用（G 档清晰度 57.0 最高、响度 -14.8 正常）；H/D/E 糊淘汰；用户目视定案 F 维持、G 留作风备选（来源任务 h3-today-testing，mem0 34c933c9 / 4d53abcd）
  - 2026-08-12 收口：h3-today-testing T1 实测覆盖 h3-turbo-pilot 试点计划，两线合并收口
- 证据锚：params.md §管线三档 / .pi/tasks/h3-today-testing/progress.md / .pi/tasks/h3-turbo-pilot/progress.md / output/video/h3v1/

### C-20260816-09 | Ref2VA Turbo 4 步速度
- 状态：✅现行（valid_from 2026-08-14）
- 现行值：Ref2VA Turbo v0.1（lightx2v）4 步 = **40s**（960×544 / 124帧，同 prompt/seed）vs 官方 20 步 res_multistep 100-122.6s → **2.5-3x 提速**；对比成片档 F（158s）约 -75%
- 时间线：
  - 2026-08-14 提出：同 prompt/seed 对照 T1 3图=40.0s / T2 3图 seed2=40.0s / T3 2图=40.0s vs R1-R3 20步 100.0-122.6s（来源任务 T-20260814-11）
  - （身份一致性画质待用户目视验收，2026-08-14 挂起）
- 证据锚：params.md §Ref2VA Turbo / output/video/h3_ref2v/ / output/compare/h3_ref2v_20vs4.png / .pi/tasks/h3-ref2v-pilot/progress.md

### C-20260816-10 | Ref2VA ref_image_size 策略（match/max 实测反转）
- 状态：✅现行（valid_from 2026-08-15）
- 现行值：match 96s / max 60s——**官方称 max 慢但实测 max 更快**（原因：参考图 alya169_flat.png 原始分辨率 < 生成分辨率时，match 反而把参考图放大到生成分辨率）；max 仅对 >2048px 图有增益；语义 = match 缩放至生成分辨率（蒸馏训练一致）/ max 保持 ≤2048px 短边
- 时间线：
  - 2026-08-15 提出：同 seed 20260817 同参考图同 prompt 8步@1024×576 对比（来源任务 T-20260815-07）
- 证据锚：params.md §Ref2VA 参考（ref_image_size max 仅对 >2048px 有增益）/ .pi/tasks/h3-new-findings-test/progress.md

### C-20260828-01 | Spectrum 跳 transformer 加速适用域
- 状态：✅现行（valid_from 2026-08-28）
- 现行值：Spectrum v0.2.20（training-free 跳 H3 transformer blocks + anchor 预测，offline_smoothing_replay 默认开）——**仅推荐 std 慢车道 20 步 @1024×576**：采样 1.55x（124→80s）/端到端 1.22x/目视画质反升（replay 双向平滑≈去噪红利）；成片档 8 步采样 1.5-1.55x 但高动态严重劣化（2/10 涂抹/鬼影/面崩）；快速抽卡 8 步 @768×448 抽卡可接受但端到端零收益（固定开销稀释）；4 步档无步可跳零收益。与批量优化（两阶段/CondCache）收益独立可叠加；与 EasyCache/LazyCache 同分支互斥
- 时间线：
  - 2026-08-28 实测定论：同 seed 20260814 双臂 A/B（wave 低动态 + dance 高动态双场景 × s8/f4/f8/t20 四档），VL 初审 + 拼图目视（来源任务 T-comfy-ops-11）
- 证据锚：docs/09_h3_test_plan.md §补测批 E / docs/10_h3_batch_optimization.md §七 / experiments/spectrum_ab/ / output/video/spectrum_test/ / scripts/h3_spectrum_ab_runner.py

### C-20260902-01 | FL2VA PDD 8-step 长段可行性
- 状态：✅现行（valid_from 2026-09-02）
- 现行值：4090 24GB、FL2VA INT8、768×448、NativeAudioLock 外部粤语音频下，PDD 8 nfe 的 10 秒配置耗时 255s、15 秒配置耗时 315s，均成功；峰值显存约 22.2GB，结束后可用内存约 7.2GB。
- 时间线：2026-09-02 实测（来源任务 T-comfy-ops-28）。
- 证据锚：experiments/h3_digital_human/fl2va_pdd_long_audio_test.json.results.json / output/video/h3_avatar_pdd_long/ / .pi/tasks/T-comfy-ops-28/progress.md

### C-20260902-02 | NVIDIA H3 Super Acceleration 架构边界
- 状态：✅现行（valid_from 2026-09-02）
- 现行值：NVIDIA 方案是 H3 4-step LightX2V 草稿 + LTX-2.5 3-step 精修的两模型流水线，不是 H3 原生两阶段，也不等同于 PDD 8-step；其公开速度基于 GB200 热服务并排除模型加载/warmup。
- 时间线：2026-09-02 资料核查（来源任务 T-comfy-ops-28）。
- 证据锚：NVIDIA 官方 H3 Super Acceleration 页面 / docs/h3-digital-human-research/01-official-facts.md §6

### C-20260905-01 | SageAttention post6 H3 一致性
- 状态：✅现行（valid_from 2026-09-05）
- 现行值：基于 `woct0rdho/SageAttention` 提交 `e147939`（CUDA-level zero-fill，post6 修复）在 Torch 2.13.0+cu130、RTX 4090/sm89 上重编译；短序列/非整除序列 smoke test 通过；固定 H3 工作流新旧构建视频与音频解码流完全一致。
- 时间线：
  - 2026-09-05 修正：旧本机 2.2.0 构建无法证明含 post6；改用 e147939 重编译并完成 H3 端到端对照。
- 证据锚：`/tmp/SageAttention-post6`（e147939）/ `output/video/attn3way/{old_dance,post6_dance}_00001_.mp4` / 视频 MD5 `a848b09c21260cc46e06b3fc2ed0cb1f` / 音频 MD5 `34d028a8284eec2cc02f00bc1933c468` / [上游修复说明](https://github.com/woct0rdho/SageAttention/pull/98)

### C-20260906-01 | H3 20 步 Sage 开关动作差异
- 状态：✅现行（valid_from 2026-09-06）
- 现行值：同模型/提示词/seed/1024×576/124 帧/20 步下，Sage 开与关会产生不同采样轨迹；本轮无 Sage 版本动作连续性主观更接近舞蹈，需把 Sage 作为速度-动作风格权衡项，而非只看清晰度。
- 时间线：
  - 2026-09-06 实测：Sage `118.61s`，无 Sage `164.0s`；视频 PSNR `20.63dB`、SSIM `0.709`，确认不是封装差异。
- 证据锚：`output/video/attn3way/{post6_20step_dance,nosage_20step_dance}_00001_.mp4` / `docs/09_h3_test_plan.md` §20 步 Sage A/B

### C-20260914-01 | VDN Ref2VA 1024×576 双角色 NativeAudioLock 时长基线
- 状态：✅现行（valid_from 2026-09-14）
- 现行值：RTX 4090 24GB、3 张图片参考、VDN INT8 ConvRot + Turbo、`res_multistep`、8 steps、1024×576、24fps、`NativeAudioLock` 外部 Breeze 对话音频；10/15/20 秒均成功。
- 时间：10s 总耗时 **194.71s**（DIT 8步约158s）；15s **286.39s**（DIT约233s）；20s **391.90s**（DIT约313s）。20s 当前稳定基线约 **6分32秒**。
- 资源：DynamicVRAM 会将约20GB DIT staged 到系统 RAM；本轮 ComfyUI RSS 峰值约50–52GiB，GPU 约18–24GB，未发生 OOM。GPU-only 会因 VDN adapter 分配直接 OOM，不适合这套24GB卡。
- 音频结论：`NativeAudioLock` 是外部音频锁定，不使用 `ref_audios`；输出视频仍带锁定音频。`ref_audios` 仅作声线/音频参考，长纯人声参考会抑制环境音并造成角色口型/声线绑定不稳定。
- 证据锚：`output/video/h3_vdn_ref2va/{dual_dialogue_10s_input_audio_fx_1024x576_00001_,dual_dialogue_15s_input_lock_fx_1024x576_00001_,dual_dialogue_20s_input_lock_fx_1024x576_00001_}.mp4`；`.pi/tasks/T-comfy-ops-VDN-01/progress.md` 2026-09-14 双角色测试段。
C-20260914-02 | 普通 Ref2VA Turbo LoRA 1024×576 双角色长时基线 | 2026-09-14

配置：无 VDN，`minimax_h3_ref2va_pruned_int8_convrot.safetensors` + `minimax_h3_ref2v_turbo_8step_v1.0_768p_comfyui_bf16.safetensors`，强度 1.0，`res_multistep`/8 steps，三张参考图，NativeAudioLock，1024×576。

结果：15s 端到端 393.1s（ComfyUI 390.41s），20s 端到端 615.1s（ComfyUI 626s）。输出：`output/video/h3_ref2va_ordinary_lora/dual_dialogue_15s_lora8_input_lock_1024x576_00001_.mp4`、`output/video/h3_ref2va_ordinary_lora/dual_dialogue_20s_lora8_input_lock_1024x576_00001_.mp4`。这是 Turbo LoRA，不是 PDD；同条件下慢于 VDN 15s/20s 的 286.39s/391.90s 基线。

### C-20260915-01 | Ref2VA PDD 8-step 与标准 20-step 5 秒同参对照
- 状态：✅现行（valid_from 2026-09-15）
- 现行值：RTX 4090 24GB、普通 Ref2VA（`minimax_h3_ref2va_pruned_int8_convrot`）、单张参考图、`NativeAudioLock` 外部 5.000s 粤语音频、768×448、124 帧、shift 12/3，除采样路线外全同参（同参考图/同音频/同六段式 prompt/同 seed `20260914`）：
  - A 无 LoRA `res_multistep` 20 steps：端到端 90.0s，ComfyUI 内部 **86.50s**，采样 20 步 53s（2.67s/it）
  - B Ref2VA PDD Acc `nfe=8` + `euler` + 节点 sigmas：端到端 40.0s，ComfyUI 内部 **33.38s**，采样 8 步 19s（2.48s/it），PDD 加载/打补丁约 2s
  - 加速比：热启动 2.59×（33.38 vs 86.50）；含冷加载端到端 2.25×（40.0 vs 90.0）。**加速来源是步数 20→8 的线性减少，不是单步更快**（单步耗时 2.67 vs 2.48s/it 基本持平），因此 PDD 的价值前提是 8 步画质可接受。
  - 两者输出规格一致：124 帧 / 5.167s / 768×448 / 24fps / 音频流 163 帧，均无冻结帧。
- 质量侧（仅客观代理，非定论）：整片 SSIM A-vs-B `0.867`；帧差运动能量 A face 0.70 / body 0.50，B face 0.84 / body 0.36；逐帧面部运动序列相关 0.616；音频包络 vs 面部运动代理相关 A 0.061、B −0.04（弱，只能筛异常）。观察项：PDD 版面部/嘴部运动更活跃而身体更静，**是否更好或更差需人工目视，本机视觉质检通道不可用（DashScope 免费额度耗尽、LM Studio 未启动）**。
- 通道正确性：PDD 日志 `partition check ok: ref2va file on ref2va model (fl2va 0.0504, ref2va 0.0017)`、`steps=8 blocks=4,4,4,4,4,4,4,4, heads fused`、`50 adaln modules rebased onto the ref2va curve basis`。
- 时间线：
  - 2026-09-15 实测（来源任务 T-comfy-ops-33）：跑批成功，质量结论待用户目视验收。
  - 覆盖关系：与 C-20260905-01（Ref2VA A/B/C 4 秒口型对照，当时 PDD 8 比 20 步快约 26–27%）不矛盾——本轮用官方 5 秒合法档并完整记录分阶段耗时；此前 docs/34 的 VDN Turbo 1024×576 结论是另一条路线，不可与本条混记。
- 证据锚：`experiments/h3_ref2v/cases_pdd_vs_std20_5s_20260914.json`（配置）、`.json.results.json`（耗时）、`experiments/h3_ref2v/pdd_vs_std20_5s_20260914/`（contact_AB.png + 8 张抽帧 + audio/hk_a_5s.wav）、`output/video/h3_ref2va_pdd_vs_std20_5s/A_std20_5s_00001_.mp4`（md5 `59f855911ecd9de4878fe4a98835be86`）、`.../B_pdd8_5s_00001_.mp4`（md5 `bcadec06570ae0a8ff8423a3fcd01233`）、脚本 `scripts/h3_ref2v_runner.py`（新增 `pdd` 分支）
### C-20260915-02 | H3 Ref2VA 双角色正式生成分辨率与路线选型
- 状态：✅现行（valid_from 2026-09-15）
- 现行值：正式成片默认 1024×576、VDN、8 steps、NativeAudioLock；10/15/20 秒均已跑通，20 秒约 392 秒。768×448 的 VDN 5/10/15/20 秒约 90/140/190/230 秒，作为快速筛选档。PDD + SageAttention 的 1024×576/15 秒约 235 秒，具备速度候选资格；20 秒尚未完成同口径验证。1344×768 仅适合 5/10 秒短测，12 秒以上出现明显系统内存压力，15 秒不可接受，20 秒 OOM。
- 时间线：
  - 2026-09-15 提出：以 1024×576 VDN 作为 15–20 秒正式生成主线，并保留 768×448 快速筛选档（来源任务 T-comfy-ops-33）。
- 证据锚：`docs/34_ref2va_generation_guide.md` §2026-09-15 正式生成选型；`docs/35_vdn_h3_ref2va_route.md` §2026-09-15 当前正式生成建议；产物 `/home/sean/projects/ComfyUI/output/video/h3_vdn_ref2va_clean/`、`/home/sean/projects/ComfyUI/output/video/h3_pdd_sage_ref2va_clean/`。

### C-20260915-03 | PDD + Sage + KJNodes 低显存节点冲刺 1024×576/20s
- 状态：✅现行（valid_from 2026-09-15）
- 现行值：PDD Acc 8-step + SageAttention 后串接 `MiniMax H3 Low VRAM Attention(head_chunks=4)` 与 `MiniMax H3 Chunk FeedForward(chunks=4, seq_threshold=4096)`，在 RTX 4090 24GB、1024×576、20 秒、NativeAudioLock 下成功；端到端约 341.7s，ComfyUI 实际执行约 340.9s，未 OOM。
- 原理：Low VRAM Attention 释放 QKV/输入中间张量并按独立 head 分组；Chunk FeedForward 将 packed-token SwiGLU/MLP 分块，分别压低 attention 与 FFN 激活峰值；两者不改变模型分辨率或步数，代价是额外循环开销和更高系统 RAM 依赖。
- 证据锚：本机 `ComfyUI/custom_nodes/ComfyUI-KJNodes/nodes/minimax_nodes.py`；`docs/35_vdn_h3_ref2va_route.md` §2026-09-15 低显存节点冲刺结果；产物 `/home/sean/projects/ComfyUI/output/video/h3_pdd_sage_ref2va_clean/pdd_sage_lowvram_1024x576_20s_342s.mp4`。

### C-20260915-04 | H3-Optimizations 与采样后释放/tiled VAE 硬件边界
- 状态：✅实测（valid_from 2026-09-15）
- 现行值：RTX 4090 24GB、普通 Ref2VA、PDD 8-step + SageAttention、1024×576/481帧/20s 下，`H3MemoryOptimization(chunk_rows=4096, precision=Preserve native, qkv=Auto)` 成功 **335.3s**；外部 Sage 使 QKV bounded streaming 关闭，但 ConvRot MLP/FinalLayer 分块仍生效。H3-Optimizations 比此前 KJ 双节点约341.7s略快。
- 采样后 `VRAM_Debug(unload_all_models=true)` + 视频 `VAEDecodeTiled(tile=512, overlap=64, temporal=64/8)` 成功 **336.7s**；释放前后可用显存 `13,037,032,392 → 23,915,458,652` bytes，采样后观测显存约6.3GB/系统内存约15GB。说明模型回收值得做，尤其为高分辨率解码留出余量；但不降低采样阶段 RAM 峰值。
- 限制：`VAEDecodeAudioTiled` 对当前 H3 joint audio latent 报 `IndexError`，当前组合使用普通 `VAEDecodeAudio`；视频 tiled 路径成功。该节点不能作为 H3 音频 tiled 的可用性结论。
- 证据锚：`/home/sean/projects/ComfyUI/custom_nodes/H3-Optimizations`；任务进度 `.pi/tasks/T-comfy-ops-33/progress.md`；产物 `/home/sean/projects/ComfyUI/output/video/h3_pdd_sage_ref2va_clean/pdd_sage_h3opt_1024x576_20s_335s.mp4`、`pdd_sage_h3opt_release_tiled_1024x576_20s_337s.mp4`。

### C-20260915-05 | PDD + H3-Optimizations 1344×768/15s 冲刺
- 状态：✅实测（valid_from 2026-09-15）
- 现行值：PDD 8-step + SageAttention + H3 `H3MemoryOptimization(chunk_rows=4096, Preserve native)` + KJ `VRAM_Debug(unload_all_models=true)` + 视频 `VAEDecodeTiled(512/64, temporal 64/8)`，普通音频解码；RTX4090 24GB、1344×768、361帧/15.083s 成功，端到端 **516.2s**，未超过15分钟阈值。
- 资源：采样峰值GPU约23GB、系统RAM约43GB、swap无明显增长；释放前后可用显存 `22,029,620,168 → 23,915,458,652` bytes，收尾阶段约6.7GB VRAM/14GB RAM。
- 结论：采样后释放 + 视频 tiled 使此前高分辨率15s风险路线成功，但约8分36秒，显著慢于1024×576/20s约336.7s；1344×768/15s适合作为高分辨率硬件上限档，不作为日常性价比档。
- 证据锚：`.pi/tasks/T-comfy-ops-33/progress.md`；产物 `/home/sean/projects/ComfyUI/output/video/h3_pdd_sage_ref2va_clean/pdd_sage_h3opt_release_tiled_1344x768_15s_516s.mp4`。

### C-20260915-06 | VDN 高时长边界取消
- 状态：✅实测边界（valid_from 2026-09-15）
- 现行值：VDN 1344×768/15s 使用 `ApplyVDNH3(stream, retain_buffers=off, grouped)` + NativeAudioLock + 采样后释放/tiled decode，结构正确但在约320s时按用户要求中断，停在采样节点，无产物；不能视为流程失败或成功。
- VDN 1024×576/25s 使用同流程、25s音频（20s双人对白+5s静音）运行 **935s** 后仍在采样阶段，RAM约44GB、GPU约24GB满载，按15分钟阈值中断，无产物；说明该配置不适合继续冲25s。
- 证据锚：`.pi/tasks/T-comfy-ops-33/progress.md`；`scripts/h3_batch_runner.py` 已修复 `execution_interrupted` 误报成功问题；无输出视频。

### C-20260915-07 | VDN 边界取消原因归因
- 状态：✅边界结论（valid_from 2026-09-15）
- 已确认：VDN 1344×768/15s 与 1024×576/25s 均在 `SamplerCustomAdvanced` 采样阶段被中断，未执行 `VRAM_Debug`/`VAEDecodeTiled`，没有 CUDA OOM、节点异常或解码错误；不能归因于“采样后释放模型 + tiled VAE”与 VDN 不兼容。
- 1024×576/25s：采样935s仍未结束，GPU约24GB满载，系统RAM约44GB、可用约10–12GB，逼近内存搬运和时间上限后主动取消；属于资源/时间边界，不是捕获到的硬OOM。
- 1344×768/15s：约320s因用户观察到GPU长时间无动作而人工取消；复核时仍在采样，部分监控时段GPU实际满载，属于人工中断，不是生成失败。
- 现行判断：采样后释放只改善采样完成后的解码峰值，不能解决VDN长时高分辨率采样阶段的显存和系统RAM压力；明日应从1024×576/20s基线向21–23s渐进，或先复测1344×768/10s，不直接冲25s。
- 证据锚：`.pi/tasks/T-comfy-ops-33/progress.md`；两次 ComfyUI history 的 `execution_interrupted`；无输出视频。

### C-20260916-01 | VDN 1024×576/20s 基线可复现性复测
- 状态：✅现行（valid_from 2026-09-16）
- 现行值：同 33 号任务成功路线在当前 ComfyUI 0.36.0 + PyTorch 2.13.0+cu130 + RTX 4090 24GB 环境仍可完整跑通；VDN INT8 ConvRot + Turbo、`stream`、8 steps、NativeAudioLock、1024×576、481 帧/20.04s，含采样后释放与视频 tiled VAE，端到端 **395s**。
- 资源：采样阶段 GPU 约23.8–24.1GiB、利用率94–100%，系统可用 RAM 最低约7.3GiB，Swap约104KiB；完成后 GPU约5.9GiB、系统可用 RAM约37GiB。未发生 CUDA OOM 或系统内存硬 OOM。
- 时间线：
  - 2026-09-16 复测通过（来源任务 T-comfy-ops-VDN-01，继承 T-comfy-ops-33）；覆盖同路线 2026-09-15 的单次成功结论的可复现性，不改变其参数选型。
- 证据锚：`experiments/h3_digital_human/vdn_baseline_retest_20260916.json` 及 `.results.json`；产物 `/home/sean/projects/ComfyUI/output/video/h3_vdn_ref2va_retests/vdn_baseline_1024x576_20s_20260916_00001_.mp4`；`.pi/tasks/T-comfy-ops-VDN-01/progress.md`。

### C-20260916-02 | VDN 与 KJNodes / H3-Optimizations 兼容性边界
- 状态：✅实测边界（valid_from 2026-09-16）
- 现行值：KJ `MiniMaxLowVRAMAttention` 与 VDN 不兼容，叠加后在采样阶段报 `'list' object has no attribute 'shape'`；KJ `MiniMaxChunkFeedForward` 单独可用但20s未提速且增加Swap压力；H3-Optimizations `H3MemoryOptimization` 单独可用并观察到显存下降，但尚无稳定加速定论。
- 时间线：
  - 2026-09-16 实测：KJ双节点20s失败；KJ FFN单独5s/20s成功（125s/395s）；H3MemoryOptimization单独5s/20s成功（125s/380s）。
- 证据锚：`.pi/tasks/T-comfy-ops-VDN-01/progress.md`；结果文件 `experiments/h3_digital_human/vdn_kj_baseline_20260916.json.results.json`、`vdn_kj_ffn_20s_20260916.json.results.json`、`vdn_h3opt_20s_20260916.json.results.json`；产物目录 `/home/sean/projects/ComfyUI/output/video/h3_vdn_ref2va_retests/`。

### C-20260916-03 | PDD 22秒 Sage 特效版通过
- 状态：✅实测（valid_from 2026-09-16）
- 现行值：PDD Acc 8-step + KJ `MiniMaxH3MemoryEfficientSageAttentionPatch` + H3MemoryOptimization + NativeAudioLock + 采样后释放/tiled VAE，在 RTX 4090、1024×576、22秒目标、3图参考下自然完成，端到端 **380s**；无 CUDA/RAM OOM。
- 资源：采样显存约23.1GB、GPU 100%，RAM约41GB/可用16GB，Swap 0；完成后资源回落。
- 证据锚：`experiments/h3_digital_human/pdd_sage_1024x576_22s_effects_20260916.json` 及 `.results.json`；产物 `/home/sean/projects/ComfyUI/output/video/h3_pdd_sage_ref2va_clean/pdd_sage_1024x576_22s_effects_380s.mp4`。

### C-20260916-04 | PDD 22秒 LowVRAM 画面稳定性对照
- 状态：✅实测（valid_from 2026-09-16）
- 现行值：在完全相同提示词、参考图、seed、音频、1024×576/22s 条件下，PDD + Sage + KJ `MiniMaxLowVRAMAttention` + `MiniMaxChunkFeedForward` 未复现上一条 H3MemoryOptimization + H3 Sage 组合中的松树侵入/枝叶贴脸；端到端 **380s**。
- 结论：问题范围缩小到上一轮 H3MemoryOptimization 与 H3 专用 Sage patch 的组合或交互；镜头切换仍由提示词中的过肩/近景要求触发。LowVRAM 路线暂作为 PDD 画面稳定性优先方案。
- 证据锚：`experiments/h3_digital_human/pdd_lowvram_sage_1024x576_22s_effects_20260916.json` 及 `.results.json`；产物 `/home/sean/projects/ComfyUI/output/video/h3_pdd_sage_ref2va_clean/pdd_sage_lowvram_1024x576_22s_effects_380s.mp4`。

### C-20260916-05 | PDD 23秒 LowVRAM 延长通过
- 状态：✅实测（valid_from 2026-09-16）
- 现行值：PDD + Sage + KJ LowVRAMAttention + ChunkFeedForward 路线在 1024×576、23秒目标（566帧封装时长23.58s）、特效提示词下自然完成，端到端 **425s**；未复现松树/树叶污染，Swap未增长。
- 结论：稳定路线相较22秒增加1秒仍可完成，但耗时增加约45秒；当前可行长时档推进至23秒。
- 证据锚：`experiments/h3_digital_human/pdd_sage_lowvram_1024x576_23s_effects_20260916.json` 及 `.results.json`；产物 `/home/sean/projects/ComfyUI/output/video/h3_pdd_sage_ref2va_clean/pdd_sage_lowvram_1024x576_23s_effects_425s.mp4`。

### C-20260919-01 | 原生 H3 Sparse 与 Sage 的证据边界
- 状态：✅实测边界（valid_from 2026-09-19）
- 结论：当前没有严格同条件的原生 H3 + Sparse 与原生 H3 + SageAttention A/B。无 Sage 隔离测试中，H3 Sparse30 + H3Memory 使用 `Comfy Kitchen INT8 Sparse`，1024×576/5s 为140.1s，匹配 Dense190.7s，约快26.5%；10s/20s分别235.2s/545.5s。显式 Sage 与 Sparse 叠加会 fallback 到 existing dense，不应叠加。
- 证据锚：`experiments/h3_digital_human/native20_h3sparse30_no_sage_1024x576_5s_20260919.json.results.json`、`native20_dense_no_sage_1024x576_5s_20260919.json.results.json`、`native20_h3sparse30_no_sage_1024x576_10s_corrected_20260919.json.results.json`、`native20_h3sparse30_no_sage_1024x576_20s_corrected_20260919.json.results.json`；`docs/09_h3_test_plan.md`。

### C-20260919-02 | H3MemoryOptimization 跨 PDD/原生流程可用
- 状态：✅实测（valid_from 2026-09-19）
- 现行值：`H3MemoryOptimization(chunk_rows=4096, Preserve native, QKV Auto)` 已在 PDD + Sage 和原生 H3 20-step 流程成功运行；PDD 标准 Ref2VA 1024×576/20s 约320–337s，原生无 Sage Dense 1024×576/5s 190.7s。可作为两类流程的可选显存/执行优化，不直接视为稳定提速保证。
- 限制：PDD + H3Memory 视频筛查通过，但音频有轻微劣化迹象；Sparse 组合不能再叠加显式 Sage。
- 证据锚：`docs/09_h3_test_plan.md`、`docs/34_ref2va_generation_guide.md`、`experiments/h3_digital_human/pdd_sage_vs_h3opt_standard_ref2va_1024x576_20s_complex_20260919.json.results.json`、`native20_dense_no_sage_1024x576_5s_20260919.json.results.json`。

### C-20260919-03 | Sources 复核 Sparse 的 LoRA 与组合条件
- 状态：✅资料复核（valid_from 2026-09-19）
- 结论：普通 H3-Optimizations Sparse 不需要特殊 LoRA；推荐与 H3MemoryOptimization 组合，在原生 H3 长视频/高计算压力时使用。SLA Sparse 是独立路线，通常需要相应 SLA/Turbo LoRA 与 kernel 适配。显式 Sage 与当前 Sparse backend 不应叠加；正式出片仍优先 PDD + Sage，SLA LoRA 暂不引入。
- 证据锚：`docs/09_h3_test_plan.md` 的 Sources 复核段；[H3-Optimizations](https://github.com/Zironic/H3-Optimizations)；[MiniMax H3](https://github.com/MiniMax-AI/MiniMax-H3)；[SLA LoRA 配对说明](https://huggingface.co/Smite79/MiniMax-H3-Longvideos/commit/9f31ba49200b24dae3e5573fddc19aba4a3ed769)。

### C-20260920-01 | H3 Ref2VA + SelfLift 在 RTX 4090 上的证据边界
- 状态：🟡待验证
- 现行值：RTX 4090 跑 H3 Ref2VA 本身已有公开证据，但截至 2026-09-20 没有找到同一 4090 上 Ref2VA conditioning 与 SelfLift 渐进采样的可复核视频、日志或 A/B 质量数据；SelfLift 路线暂不继续前沿测试。
- 时间线：
- 2026-09-20 提出：社区已有 SelfLift H3 实验节点、Ref2VA/SelfLift 工作流接口和 4090 单独 Ref2VA 证据，但组合证据不足（来源任务 T-comfy-ops-42）。
- 证据锚：`docs/38_h3_selflift_ref2va_4090_research.md`；[comfyui-SelfLift](https://github.com/facok/comfyui-SelfLift)；[X-MinimaxH3 validation](https://github.com/PullMyBoots/X-MinimaxH3/blob/main/VALIDATION.md)；[X-MinimaxH3 SelfLift constraints](https://github.com/PullMyBoots/X-MinimaxH3/blob/main/docs/SELFLIFT_PROGRESSIVE_GENERATION.md)。
