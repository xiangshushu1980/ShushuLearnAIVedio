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

## 下一步
1. **用户画质确认**（对比图 /tmp/h3_frames/ + 产物 mp4）→ 定最终档（初步：ckpt850-4 或 6-s1.0）
2. 若达标：进快速档替换方案（快速档 75s → 50s，2 分钟成片从 30min 降到 ~20min），更新 params.md 管线表 + docs
3. 长期项：等 Ostris/larayvrh 新 checkpoint 再复测；Sol-Attn+EasyCache 仍不在生产候选（社区劣化报告）
4. 收尾：progress + [STATE] + scoped commit

## 关键链接
- 测试用例：/tmp/h3_turbo_cases.json，结果 /tmp/h3_turbo_cases.json.results.json
- runner：scripts/h3_turbo_runner.py
- 上游：github.com/Larryvrh/ComfyUI-MiniMax-H3-Turbo、HF drbaph/MiniMax-H3-Turbo-Lora-ComfyUI
- 社区调研：h3-params/progress.md「社区反应深挖」节
