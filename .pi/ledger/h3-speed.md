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
