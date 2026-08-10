# 任务进度：h3-turbo-pilot（H3 Turbo LoRA 试点验证）

## 任务
- 目标：验证 4 步加速 LoRA（larryvrh 训练 / lightx2v 蒸馏）在 fl2va pruned int8/fp8 + 4090 上的速度/音频/画质，决定是否进快速档
- 当前状态：🟡 进行中（2026-08-07 启动）
- 我负责的文件区：scripts/h3_turbo_runner.py（独立 runner）、/tmp/h3_turbo_cases.json、video/h3_turbo_pilot/ 产物、本 progress

## 背景（用户决策 2026-08-07：试点 4 步 LoRA）
- 用户拍板：试点 4 步 lora（用 Kijai pruned 兼容版 + larryvrh 参数），音频作 gate，详见 h3-params progress「社区反应深挖」节
- 社区结论速查：larryvrh 官方推荐 4 步（custom sampler）；Reddit 经验 6-10 步（EMA 8-10 / ckpt500 6-8）；strength 0.8-1.8；pruned 模型必须用 pruned 版 lora；Kijai PR #15243 已合入 ComfyUI（音频修复）

## 环境改动（2026-08-07，已生效）
- ComfyUI 更新：v0.30.0 → 344b439（25 commits，含 PR #15243 音频修复/#15377 audio vae offload/#15339 res_multistep 等）
- venv 补装 comfy-kitchen 0.2.27（清华源无此包，用官方 PyPI；0.2.26 缺 AsymW4A8Int8Layout → fp8 模型加载崩）
- 新装 custom_nodes/ComfyUI-MiniMax-H3-Turbo（Larryvrh，含 TurboLoRA + TurboSampler 节点 + h3_silu_temb_grid.safetensors）
- 新下载 loras/（drbaph pruned ComfyUI 版，各 620MB）：
  - minimax_h3_turbo_4step_ema_ckpt850_pruned_comfyui.safetensors
  - minimax_h3_turbo_4step_ckpt500_pruned_comfyui.safetensors
- 下载源实测：hf-mirror 龟速（15s 392KB）→ 改 huggingface.co 直连（~1.1MB/s）OK

## 进度日志（append-only，每条带日期）
### 2026-08-07
- **全批 6 条完成，全部 ✅ 无错误**（seed 20260807 同 prompt 同首帧 @768×448×124）：
  - 速度矩阵（批内，TE/VAE 缓存生效）：base-14=97s / ckpt850-4-s1.0=**50s** / ckpt850-6-s1.0=51s / ckpt850-8-s1.0=66s / ckpt500-6-s1.0=51s / ckpt850-6-s1.2=50s
  - **4/6 步 ≈50s，较基线快 ~48%；8 步 66s；strength 1.0 vs 1.2 无速度差异**
  - 首次单跑 172s（含 TE 加载 ~80s 冷启动），批内缓存后 50s/条 → 生产连续跑批数字是 50s
- **音频 gate 通过**：7 个产物全部 32kHz 立体声 5.17s 完整无缺；volumedetect 无削波（max -18~-22dB）；**4 步响度最接近基线**（mean -31.7 vs -31.0 dB），6/8 步稍安静（-35.6 dB）
- 画质：对比图 /tmp/h3_frames/{mid,end}_compare.png（base/850-4/850-6/500-6 四格）——**待用户主观确认**
- 产物：ComfyUI/output/h3_turbo_pilot/*.mp4（7 个）

### 2026-08-07（二批：动漫风 WoW 8s 对比，用户要求）
- 首帧：anima-base 文生图生成「血精灵法师施法」（768×448，无角色 lora），落 input/start/wow_anime_768.png
- 8s（192帧）四档同 prompt/seed：**wow-base-14=185s / wow-850-4=50s（-73%）/ wow-850-6=65s / wow-500-6=65s**
- 音频 gate：全部 8.0s+8.0s 32kHz 立体声完整；响度 turbo 各档一致（mean -16.0~-16.2dB）vs 基线 -14.6dB，无削波
- 产物：video/h3_wow/*.mp4 + 对比图 video/wow_{mid,end}_compare.png（四格顺序：base-14|850-4|850-6|500-6）——**待用户目视**

### 2026-08-07（三批：写实美女 10s 768×448 + 用户目视反馈）
- **用户目视反馈（关键）**：WoW 动漫 8s——**只有 base-14 能看，turbo 全胡**；写实 10s 768——**turbo 胡，且 base-14 也胡**（写实 480p 细节上限坐实）
- 写实批速度：base-14=203s / 850-4=66s / 850-6=65s / 500-6=66s（turbo 快 68%但画质崩）
- **初判：turbo lora 画质 gate 不通过，不进生产**；用户提新方向：1024×576 验证（写实 1024 首帧 krea2 重生成，base-14 vs 850-6 对比批跑中）
- 产物：video/h3_real/*.mp4 + video/real_mid_compare.png（四格：基线|850-4|850-6|500-6）

### 2026-08-07（四批：1024/960 验证 + sage 节点确认）
- **用户目视：1024×576 14 步可用**（写实）；960×544 16 步单条（执行 ~280s，runner 1420s 含排队等待——提交时队列有他人任务插队）
- 1024 批：r1024-base-14=293s / r1024-850-6=127s（turbo 快 57% 但用户未认可画质）
- 对比图：video/r960_vs_1024.png（左 960×544-16 步 | 右 1024×576-14 步，5s 处）
- **sage 启用方式确认：`--use-sage-attention` 启动参数（全局），未用 KJ 专用节点 MiniMaxH3MemoryEfficientSageAttentionPatch**；当前 24GB 无显存压力不换，若遇 15s+/低显存内存压力再试专用节点

## 产物规范（用户 2026-08-09 指示）：全部产物放 ComfyUI output/（试点归档 output/pilot_archive/），项目 video/ 目录已废弃删除；新产物按 分辨率_时长_优化_步数 命名

## 下一步
1. **今日新武器（v1 代判失败后重启试点）**：
   - lightx2v v0.1（官方团队，FL2V 蒸馏，无需插件）：Kijai 转换下载 → 4 步 + er_sde + beta57 + shift 12/10 + strength 0.75/1.0 两档；只支持 T/I2V（我们用 I2V ✓）
   - larryvrh v4-600 EMA：替换 ckpt500/850 旧档 → 6 步 + strength 1.0 + simple；预期静帧/微细节大提升
   - 同 seed 写实泳池首帧对比 base-14 @1024；音频 gate 不变
2. 待用户确认 960 vs 1024 档位偏好（对比图 video/05_compare/cmp_real_960vs1024_mid.png）
3. 收尾：progress + [STATE] + scoped commit（含 video 重组 8da72c5/f99ce3c）

## 关键链接
- 测试用例：/tmp/h3_turbo_cases.json，结果 /tmp/h3_turbo_cases.json.results.json
- runner：scripts/h3_turbo_runner.py
- 上游：github.com/Larryvrh/ComfyUI-MiniMax-H3-Turbo、HF drbaph/MiniMax-H3-Turbo-Lora-ComfyUI
- 社区调研：h3-params/progress.md「社区反应深挖」节

### 试点候选执行计划（2026-08-09 立，用户拍板「一个个来」）
**P0 目视 gate（欠账，先清）**
- [x] P0.1 v1 批作废：首帧手太不明显（侧面全身，手指不可辨）→ 重做「手可见+有动作+非主体」首帧（用户 2026-08-09 指示）；旧批产物已清理
- [x] P0.2 1024 手部五档结论（用户 2026-08-09 目视）：s2 糊（郭吉军说法不成立）；v4 各档手部均正常（手为主体时表现好=此前已判断）；成片档待定（用户未再表态，默认维持 base-14 待 P1 后统一定）
- [x] 快速档正式定档：**v4-8 @768×448（67s/8s）**（用户 2026-08-09 确认）
- [x] **960×544 分辨率档测试**（用户 2026-08-09）：v4-8 @960×544 8s = 168s（768 档 67s 的 2.5x）——960/1024 同处 offload 区，等 int8 验证后再定分辨率
- [x] **复杂动作（转身甩发）4/6/8 对比**（用户 2026-08-09）：用户目视「都还可以」；4 步 45s/6 步 67s/8 步 88s（复杂场景步数差异显现）
- [x] **社区步数建议**（2026-08-09 查证）：larryvrh v4 官方 README = 4 步最小、**6-8 步甜点**、超 8 步无益；ANe5s 双采样器两阶段（ckpt850 5-7 步 + ckpt500 0.7 强度 7-8 步 ≈ 13 步，v1 代玩法，被质疑违背加速初衷）；h3-prompt-agent 本地 8 步≈std94%——**共识 = 8 步甜点，与我们定档一致**

**P1 画质 gate 通过后的速度甜点探索**
- [ ] P1.1 v4-4 步档 @768×448（静帧/小动作场景，README 卖点）→ 预期 40-50s，快速抽卡再提速
- [ ] P1.2 v4 大动作边界（4 vs 6 步同场景）→ 确认拖影边界，快动作场景选档依据

**P2 管线优化**
- [ ] P2.1 SeedScout 多 seed 试镜试点（抽卡档：先预览后渲染，省全渲染碰运气）
- [ ] P2.2 params.md 管线表定稿（含 8s/10s 数据点 + turbo 结论 + 观望清单）

**P3 移交 h3-prompt-agent（提示词方向，用户 2026-08-09 指示在提示词 Agent 对话继续）**
- lightx2v Prompt-Rewriter-LoRA（本地 IR 备选）/ 机智罗预设节点——由提示词线评估

**P4 观望清单（发布即复测，同套 seed）**
- [ ] larryvrh v5 成品（拖影修复，experimental_v5_step_600.bin 训练中）
- [ ] lightx2v v0.2（「几天内出更新版」）
- [ ] Ostris DMD lora（音频算法 borked，未发布）

### 2026-08-09 定档收尾（用户确认）
- **快速档（定）**：fp8+sage+v4-600 EMA 8 步 @768×448 = 67s/8s（复杂动作 88s；社区共识 8 步甜点）
- **极速档（定，用户「可以了」）**：v4-4 步 @768×448 = 45s/8s（挥手 46s/转身 45s 复测稳定）
- **成片档**：挂起等 int8（下载 21GB 2.2MB/s 进行中）→ 验证省显存消除 offload 后 960/1024 速度 → 再定成片档分辨率/步数
- 产物规范：全部在 ComfyUI output/（pilot_archive/ 7 文件锚点）
- 网络问题解决记录：Clash 原节点白天拥塞 → 换美国节点后国外 2.1MB/s（国内 672M 一直正常）；WSL 连 7890 需 Clash 开混合端口 + 9090 external-controller

### 2026-08-10 第六轮社区调研（今日 H3 动态）
- **unsloth 官方 GGUF 包发布**（8/10 06:46 UTC）：fl2va/ref2va Q2-Q8 + UD 动态量化 + **TE 也 GGUF 化**（qwen3vl 32B Q2_K_M 12.2G/Q4_K_M 17G）；sd-cli/stable-diffusion.cpp/ComfyUI 全通；示例 UD-Q2_K_XL @960×544 124帧 8步可跑。低显存/CPU 卸载路线已打通
- **Kijai experimental 仓库**：w4a8（4bit 权重 + int8-convrot 激活）测试中，Comfy-Org comfy-kitchen PR#90，需 ComfyUI 0.31.0；**int8_convrot VAE 解码快 1.5x**（需 0.31.0，官方仓库暂无此 VAE 文件）；ref lora 实验性
- **官方仓库 8/9 更新**：新增 qwen3vl_32b_minimax_h3_nvfp4_awq TE（15.7G，本地已在用且 4090 实测可跑——Abiray README 说 NVFP4 仅 Blackwell，本地证伪）
- **Abiray 仓库 8/10 更新**：nvfp4 全家族 + mixed int4/int8 + TE int4/nvfp4；24GB 卡推荐 INT8（与我们一致）
- larryvrh v5 无成品（8/8 后无更新）；lightx2v 无 v0.2（8/7 后无更新）
- 新讨论：#31 LabMike3D 低显存音频修复 4 步（8/9）、#32 stable-diffusion.cpp 体验（8/9）
- X：AMD RDNA4 补丁 + turbo lora = 82s（Italianclownz）
- **int8 DiT 下载完成**（20970379616 字节 = 远程大小一致 ✓，wget 完成；网络恢复后提速至 ~5MB/s）
- 结论：turbo/模型主线无重大变化；新动向 = GGUF 生态（unsloth）+ w4a8/int8 VAE（需 ComfyUI 0.31.0，暂观望）；我们 4090+fp8 路线不受影响

### 2026-08-10 第六轮调研补充（用户三问：fp8/int8、TE 版本、X/Reddit）
- **官方量化推荐**（Comfy-Org README 原话）：「For diffusion_model prefer int8_convrot if you are able to use pytorch with cu130. Fp8_scaled should only be used if you for any reason can not use the int8_convrot」——**int8 是官方首选，fp8 是兜底**；本地 torch 2.13.0+cu130 ✓ 条件满足（sage 2.2.0 兼容）
- **TE 推荐**（官方 README 原话）：「This nvfp4 text encoder does not require Blackwell GPU to use」——**nvfp4_awq TE（15.7G）4090 可用且为最小档，本地用法正确**；NVFP4 DiT（Abiray）才是 Blackwell/CUDA13-only（X: Bin Chen 5090 480p 5s=48s/turbo 32s 佐证）
- **INT8-Fast**（BobJohnson24/ComfyUI-INT8-Fast，284★）：30 系卡 int8 matmul triton 内核 1.5-2x 加速（Reddit 1vhi2n7 有复刻帖）；40 系 cu130 原生 convrot 路径即可，非必需
- **X（8/10）**：Maki L4(Colab) 1280×704 turbo v4 8步 5s=21:56；Bin Chen 5090 nvfp4 480p=48s/32s(turbo)；Jun 3060 8GB turbo 480p 10s≈10min（本地试戏+RunPod 生产模式）
- **Reddit AMA（8/7，官方 6 人，939 赞，443 评论）重磅**：
  1. **稀疏注意力推理版「near term」发布**（Kiro_Song：train-aware 稀疏化，保守配置无感画质损失，先参考实现）——未来 H3 提速大事件
  2. **官方考虑 4-step 低步数版本**（「actively considering a lower-step version, such as a 4-…」，非蒸馏极端低步数）
  3. **H3-Regenerate-2K**：专用 latent-space DiT 再生 checkpoint（高分辨率 + base 输出上下文），非普通 upscaler；官方计划开源（效率优化中）——官方 2K 画质来源
  4. Ref2VA 视觉质量差 FL2VA 官方承认（post-training 差异），改进中；技巧=用最高质量参考输入
  5. 官方将发 comprehensive technical report

### 2026-08-10 成片档定案（用户目视 gate 通过）
- **正式成片档 = int8_convrot + sage + v4-600EMA 8步 @1024×576 = 125s/8s**（单模型连续批稳定值）
- 多 seed 对比（3 seeds int8 vs fp8 @1024，用户逐条目视）→ int8 画质可接受
- fp8 1024 同规格 185-345s（offload 抖动）——int8 为唯一成片档
- 管线三档定稿（params.md 已更新）：极速 fp8-4步@768=45s / 快速 fp8-8步@768=67s / 成片 int8-8步@1024=125s
- 清理：wave 系列全删、fp8 1024 对照删、int8 768/960 删；archive 保留 turn 4/6/8 + 1024cmp int8 ×3 + base 参照 ×2 + README

### 2026-08-10 ref2va 优化现状专项（用户问：ref2va 一直没优化吗）
- **步数加速（turbo lora）：无**。larryvrh/lightx2v 均只做 fl2va；YouTube 教程（emmPVR0n9LQ）确认 ref2va 加速只能靠通用手段：sage + 20→15 步 + EasyCache ≈ 3x（4min→1:25），turbo 测试与 ref2va 无关
- **量化：齐全**。官方 pruned int8/fp8（本地已有 int8 ref2va 21GB ✓）；Kijai w4a8 ref2va（8/7）；unsloth GGUF ref2va Q2-Q8+UD（8/10）；Abiray nvfp4/mixed；MLX 4/8bit（Mac）
- **新发现（Kijai 8/8）**：**ref lora**（loras/minimax_h3_ref_lora_rank_256_bf16.safetensors）= fl2va↔ref2va delta 权重；Kijai 标注完全实验性（"don't even know if it has a use case"）；**潜在价值：fl2va+turbo lora+ref lora 组合 = ref2va 慢车道提速路径（未验证）**
- **Kijai experimental 仓库全清单**（8/8）：fl2va w4a8、ref2va w4a8、video_vae_int8_convrot（int8 VAE 在此，需 ComfyUI 0.31.0 否则黑输出）、ref lora
- 官方：AMA 承认 Ref2VA 画质差距改进中；无 ref2va 专属低步数计划
- 结论：ref2va 慢车道（h3-prompt-agent 多角色场景）维持 std 步数；w4a8/ref lora 组合列为可选试点（实验性，等 Kijai 或社区验证后再说）

### 2026-08-10 第七轮调研（扩大范围：GitHub/B站/官方仓库/推理栈）
- **ComfyUI 原生 AV 采样确认**：bdcb886（8/6，「Fix sampler issues for audio with minimax」）已并入本地 0.30.0 → 4 步不爆音原理实锤（双时钟 euler 自动转官方路径）；shuaixn/ComfyUI-MiniMaxH3DualClockSampler（25★）仅旧版 ComfyUI 需要，我们无需安装
- **NicoLab28/ComfyUI-ClipProj（32★，矩阵仓库 8/10 12:50 更新）——TE 瘦身 POC**：Qwen3-VL-4B（2560 dims）+ 线性/MLP 投影 → 5120 dims；TE 15.7GB→4.5GB（int8 4B），同一 tokenizer（151936 tokens）位置对齐可学习；实测出片（3090/4070/3060，ComfyUI 0.31.0）；4B/8B × 线性/MLP × celeb（身份优化）/普通 变体 + control-identity；**TE 加载 80s + 显存 15.7GB 痛点的最有希望方案（POC 风险：0.31.0 测试、投影画质未定）**
- **t8star**：ref2va_patchin_hf102（8/10，视频 patch 投影 2×2 高频 +2% 去油感，作者自称「肉眼未确认有效，仅 EXP 对照」——ref2va 画质修复无成）；minimax-h3-4step-turbo-loras-comfyui-exp（4 步移植版：euler/beta、要求完整非 pruned 模型、爆音→8-10 步或双时钟）；T8mars/comfyui-minimax-h3-prompt-enhancer-T8（78★，提示词增强，提示词线相关）
- **Work-Fisher（B站）**：12G 显存加速整合包（10s 视频 300s，530% 提速）——低显存向；comfyui秋葉 加速插件 45%
- **官方 MiniMaxAI/MiniMax-H3 8/10 README #68**：vLLM 部署示例（--performance-mode speed，4×ulysses）；官方仓库 3682★
- **其他 8/10 新仓库**：H3-Inpaint（latent mask 编辑）、H3-Auto-Director（多段自动导演）、Prompt-Rewriter-ComfyUI（lightx2v 适配）、MLX 节点（Apple Silicon）、kevrai-omni 工作站
- 结论：生态在 8/10 扎堆爆发（提示词/编辑/多段/瘦身）；**对 pilot 最大价值 = ClipProj（TE 瓶颈）**，建议试点 P1.4

### 2026-08-10 P1.4 ClipProj 试点（升级 0.31.0 + 节点 + 矩阵 + 首测）
- **ComfyUI 升级 0.31.0**（344b439→7d11ec3，含 Optimize MiniMax-H3 VAE #15446 + ER-SDE 扩展 #15428）
- **安装 ComfyUI-ClipProj**（nicolab28，0.1.4）+ 矩阵 mmh3-4b-ClipProj-celeb-mlp.safetensors（304MB）
- **测试配置**：ClipProjLoader（qwen3vl_4b_fp8_scaled + celeb-mlp 投影，type=auto，resident）+ int8 DiT + v4-8 8s @1024×576
- **速度：首条 ~180s（含载）→ 驻留 ~60s vs 32B TE 的 125s = 快 2.1 倍**（TE 15.7GB→5.2GB + 加载 80s→秒级）
- 产物：output/h3_clipproj/cp_1024_s{20260810,42}.mp4（对照 pilot_archive 旧 1024cmp_int8_s* 同 seed）
- **注意：output/pilot_archive/ 已被用户手动清理**（output 根目录与子目录全清，仅留 anima/audio/h3_clipproj/krea/ref_lib/review/video）——归档目录概念暂停，产物按用途放子目录
- 待用户目视：画质（挥手场景）+ 音频；已知局限=非英语语音降级、图像参考投影出分布
