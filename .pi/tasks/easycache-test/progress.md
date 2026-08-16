# 任务进度：easycache-test（T-20260814-01 EasyCache 候选实测）

> 任务线：T-20260814-01 | 接力链：T-20260812-08 MC 验收 → 本线 → 链A T-20260812-03 设定图跑批
> 目标：EasyCache（ComfyUI 原生节点）在成片档上的提速 vs coherence 权衡实测，结论入 params.md

## 任务
- 目标：成片档（int8_convrot + sage + v4-600EMA 8步 @1024×576）同 seed 对比 baseline vs EasyCache(0.30/0.20/0.90)，度量=耗时 + SSIM + 目视
- 当前状态：🟡 进行中
- 我负责的文件区：
  - scripts/h3_easycache_runner.py（新建，本线专属）
  - workflows/easycache_{wave,dance}.json（从 attn3way_*_sage.json 派生）
  - ComfyUI/output/video/easycache_test/
  - .pi/skills/comfyui/references/params.md（结论写入点，只追加本线结论节）

## 背景要点（开场 recall 整合）
- EasyCache 出处：Reddit tips 帖 + comfyanonymous 认可（sage+easycache 好）；参数 0.30/0.20/0.90 = reuse_threshold/start_percent/end_percent；社区评价 quality drastically lowers、10s+ 更明显（h3-params 线记录）
- h3-params 结论（2026-08-07 社区调研）：EasyCache 劣化严重 + 音频问题（B 站实测），当时决策"不上生产"——但那是社区传闻，本线做同 seed 定量实测验证
- ComfyUI 0.33.0 原生 EasyCache 节点（comfy_extras/nodes_easycache.py，experimental）：视频+音频双路 cache diff（LTX2 AV list 格式），H3 forward 返回 [-video, -audio] list → `_extract_tensor` list 分支兼容 ✓；wrapper 挂 OUTER_SAMPLE/CALC_COND_BATCH/DIFFUSION_MODEL
- MotionCache 对照（已测）：20 步档 1.25-1.33x、14 步无实用价值；EasyCache 是 residual-reuse 家族唯一未测项（Cache-DiT 已由官方验证 1.41-1.50x 待本机实测，另一条线 T-20260815-10）
- 队列：mc-test 已确认 2026-08-14 释放；seedance-h3-verify 已收尾；无其他 GPU 线占用 → 可跑批
- 启动注意：start.sh 已去全局 sage（节点级控制），但 restart_comfyui.sh 旧版默认带 --use-sage-attention → 用 --nosage 或直接 start.sh 保持洁净

## 进度日志（append-only）
### 2026-08-16 开场
- 完成开场清单：recall EasyCache/MotionCache/[STATE]、TODO 对账、读 h3-params/mc-test/vllm-h3-stream-analysis 进度、读 params.md 成片档配置
- 环境确认：ComfyUI 0.33.0 @ /home/sean/projects/ComfyUI；EasyCache 原生节点（reuse_threshold/start_percent/end_percent，默认 0.2/0.15/0.95）；成片档基线 workflow = workflows/attn3way_wave_sage.json / attn3way_dance_sage.json（int8_convrot + v4-600EMA 1.0 + PathchSageAttentionKJ auto + 8步 simple/res_multistep @1024×576 124帧）
- H3 兼容性代码确认：comfy/ldm/minimax/model.py `_forward` 返回 `[-video_out, -audio_out]` list；nodes_easycache.py `_extract_tensor` 支持 list → 兼容；audio cache diff 独立通道（is_audio=True）→ 音频也会被近似
- ComfyUI 未运行 → 启动（--nosage，保持节点级 sage 唯一生效）

### 2026-08-16 跑批完成（同 seed 20260814，成片档 8步@1024×576 124帧，wave+dance 双场景）
- **runner**：scripts/h3_easycache_runner.py（从 attn3way_*_sage.json 派生，插 EasyCache 节点在 sage 后，verbose=True 采跳步日志）
- **跑批结果**：
  - wave: baseline 总98.1s/采样33s vs easycache 总86.7s/采样24s → **采样 1.38x、总 1.13x**；跳 2/8 步
  - dance: baseline 总74.9s/采样30s vs easycache 总62.9s/采样24s → **采样 1.25x、总 1.19x**；跳 2/8 步
  - EasyCache 节点报告 speedup 1.33x（2/8 跳步）；跳步在 start=0.20 后开始（第 2-3 步间），8 步档空间有限
- **SSIM**（ffmpeg ssim filter，全视频）：wave All=0.861（Y 0.803）/ dance All=0.862（Y 0.819）——SSIM 两场景几乎相同，但目视差异大，说明 SSIM 对运动伪影不敏感，目视才是决定性
- **目视（qwen3-vl-flash 初审，等待用户验收）**：
  - wave 低动态：内容/coherence 良好，仅轻微模糊+细节损失+对比度下降 → **可接受**
  - dance 高动态：**显著劣化**——动作失真变形（50%帧手位偏移/75%帧动作断层）、涂抹伪影/鬼影、高光崩溃、关节穿模 → **不可接受**
  - 与社区评价一致（quality drastically lowers、coherence 降）
- **音频客观**（16kHz mono RMS/过零）：wave RMS 0.047→0.034（-28% 音量）、过零率 0.061→0.085；dance RMS 0.197→0.195（持平）、过零率 0.087→0.100 —— audio cache diff 通道生效，音频同样被近似
- **产物**：ComfyUI/output/video/easycache_test/{wave,dance}_sage_00001_.mp4（base）/00002（ec）；对比图 output/compare/easycache_{wave,dance}.png（行=25/50/75% 帧，列=base|ec）
- **结论（待用户目视拍板）**：EasyCache 0.30/0.20/0.90 在成片档 8 步上跳 2/8（采样 1.25-1.38x），低动态场景画质代价可接受、高动态场景崩 → 与社区评价一致（coherence 降、quality drastically lowers）；音频同步被近似（audio cache diff）；8 步 turbo 档跳步空间小（2/8），与 MotionCache 在 14 步无实用价值同理，cache 类加速对低步数档收益有限；20 步 std 档可能收益更大（未测，Cache-DiT T-20260815-10 同族待测）

## 下一步
1. ✅ 启动 ComfyUI（--nosage）+ 跑批（wave/dance 双场景 baseline+easycache 已完成，队列已释放）
2. ✅ runner：scripts/h3_easycache_runner.py；SSIM + 目视初审完成
3. **等用户目视验收**：output/compare/easycache_{wave,dance}.png + output/video/easycache_test/ 产物
4. 验收后：结论入 params.md（加速策略节）+ 收尾四步（retain 经验 / progress 归档 / [STATE] ✅ 后删 / TODO 勾掉）

## 关键链接
- 节点源码：/home/sean/projects/ComfyUI/comfy_extras/nodes_easycache.py
- 基线 workflow：workflows/attn3way_wave_sage.json（成片档配置）
- 相关文档：.pi/skills/comfyui/references/params.md（加速策略节 2026-08-15 定稿）
- 相关 mem0：EasyCache/MotionCache 经验条目（comfy-ops 池）
