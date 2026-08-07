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
- 冒烟：ckpt850-4-s1.0 @768×448×124 = 172s（含 TE 加载 ~80s 固定开销）✅
- 全批 6 条提交后台跑（base-14 对照 + ckpt850 4/6/8 步 + ckpt500-6 + ckpt850-6-s1.2），seed 20260807 同 prompt 同首帧（start/krea_alya_768_00001_.png）
- 环境坑：ComfyUI 更新后 comfy_kitchen 0.2.26 与 #15308 不兼容 → fp8 加载崩（'NoneType' Params）→ 升 0.2.27 解决；此坑已 retain mem0

## 下一步
1. 等全批结果 → 速度矩阵（对照基线 75s/条）
2. 音频 gate：ffprobe 每条音频流（时长/采样率）+ 爆音抽查（astats）
3. 画质主观评估（用户看片）
4. 结论：是否进快速档 / 定参数（步数×strength×ckpt）
5. 收尾：progress + [STATE] + scoped commit

## 关键链接
- 测试用例：/tmp/h3_turbo_cases.json，结果 /tmp/h3_turbo_cases.json.results.json
- runner：scripts/h3_turbo_runner.py
- 上游：github.com/Larryvrh/ComfyUI-MiniMax-H3-Turbo、HF drbaph/MiniMax-H3-Turbo-Lora-ComfyUI
- 社区调研：h3-params/progress.md「社区反应深挖」节
