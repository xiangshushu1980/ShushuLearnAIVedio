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
