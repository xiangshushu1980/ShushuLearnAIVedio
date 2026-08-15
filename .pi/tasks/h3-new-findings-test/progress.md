# 任务进度：h3-new-findings-test

> H3 新发现实测（2026-08-14/15 调研产出，依次验证）
> 共享状态（焦点/队列声明）在 mem0 [STATE]（comfy-ops 池，agent_id=h3-new-findings-test）

## 任务
- 目标：依次实测四类新发现——①Hybrid FL2VA+Ref2VA 模型 ②Sol-Attn 加速 ③turnaround LoRA ④六块提示词结构
- 当前状态：✅ 完成（2026-08-15 四类全部实测收口）
- 我负责的文件区：ComfyUI/models/diffusion_models/（Hybrid 权重）、ComfyUI/custom_nodes/（Sol-Attn）、ComfyUI/models/loras/（turnaround）、comfy-ops/workflows/ 与 output/ 测试产物

## 调研结论（2026-08-14）
- 新源头：`MiniMax-AI/awesome-minimax-h3-integration`（官方社区整合索引，08-14 更新），一站式覆盖模型/优化/提示词/玩法
- 网速：hf-mirror 修复后 5.2 MB/s（Hybrid 20.97GB ≈ 67min）；GitHub 小文件 OK；磁盘 553G
- **Hybrid 模型**（smhfacct）：FL2VA 底座 + 后 N 层 adaln_proj 换 Ref2VA，权重选择 merge（非微调），Ref2VA drop-in 替换；四档 b15/20/25/30-49（越往后越偏 FL2VA 画质）；作者推荐 b25-49。**实测 dtype = int8 混合精度**（F32/BF16/F16/I8/U8），20.97GB 与现有 pruned_int8 同类，24GB 可跑
- **Sol-Attn**（kijai/ComfyUI-SolAttn_triton）：training-free 稀疏注意力，Triton；README 明示已在 4090+H3 测过；参数 start_percent/end_percent/tau；要求 Triton 3.6+（本地 3.7.1 ✓）、SM89-121（4090=SM89 ✓）

## 进度日志（append-only）
### 2026-08-14
- 网速复测通过（hf-mirror 5.2MB/s），Ref Patch 148MB 已顺手下到 /tmp
- 确认 Hybrid dtype=int8 混合精度、Sol-Attn 4090 兼容
- 启动 Hybrid b25-49 后台下载（20.97GB）；装 Sol-Attn 节点

### 2026-08-14 Sol-Attn 实测结论（初步）
- 配置：fl2va_pruned_int8 + v4-600EMA 8步 @1024×576 124帧，同 seed 20260814
- 干净对比：sage 45s vs sol-attn(tau1.3) 42s = **仅 1.07x**（远低于 README 宣称 1.14-1.44x，那是 5090 Blackwell 实测）
- 画质：SSIM 0.786 / PSNR 23.9dB（同配置一致组基准 ~0.865）→ 差异明显，7% 加速换画质损失不划算
- 日志确认 sparse 生效（`sparse (1,21778,56,128) tau=1.3 int8 pointer`，sink conditioning 装入）
- 对比图：output/compare/solattn_vs_sage_1024x576_8step.png（待用户目视）
- **结论：4090 上 Sol-Attn 价值低，不建议默认采用；不再深挖 tau/morton 调参**

### 2026-08-14 turnaround LoRA 实测
- 安装：LoRA 61MB（默认 512_s1500）+ 专用节点 ComfyUI-H3-ContactSheet（codeload tarball，git clone 走不通用 curl 替代）
- 配置：ref2va_pruned_int8 + 28步 res_multistep/simple + strength 1.0 + size 512 + 参考图 start/alya_768.png
- 结果：**45s 出 5 视图 + 拼接 strip**（输出 img_turnaround/alya_{sheet,views}_512_*.png），功能验证通过
- 待用户目视：身份一致性 / 旋转连贯性 / 画质；size 1024（sweet spot）待测
- 关键认知：此 LoRA 是 ref2va 分区 + 五槽打包，必须用 ContactSheet 节点，普通 sampler 做不到且会降级运动
- 1024（sweet spot）：50s 成功（img_turnaround/alya_sheet_1024_*.png）

### 2026-08-14 六块提示词（块5文字+块6否定）对照实验
- 配置：fl2va_pruned_int8 + v4-600EMA 8步 @1024×576 62帧，同 seed
- 对照（不打字）：36s；实验（打字+否定列表）：28s
- 对比图：output/compare/text_spell_ctrl_vs_test.png（左=不打字 右=打字+否定），待目视文字清晰度

### 2026-08-15 官方参数 + 三方 Ref2VA 方案对比（同 seed 20260817 同参考图同 prompt 8步@1024×576）
- **ref_image_size match vs max（官方参数）**：match 96s / max 60s。⚠️ 官方称 max 慢，但实测 max 更快——因参考图 alya169_flat.png 原始分辨率 < 生成分辨率，match 反而放大了参考图；语义= match 缩放至生成分辨率、max 保持≤2048px 短边
- **三方方案（Ref2VA 画质痛点）**：
  | 方案 | 耗时 | 清晰度(Laplacian var) |
  |---|---|---|
  | ref2va_pruned_int8 基线 | 80s | 43 |
  | **hybrid b25-49** | 60s | **54（+26%）** |
  | fl2va+RefPatch(112/112 keys) | 56s | 46 |
- hybrid 清晰度最高符合预期（FL2VA 底座画质好）；RefPatch 提升有限；三者身份一致性/参考忠实度需用户目视
- 三方对比图：output/compare/ref2va_vs_hybrid_vs_refpatch.png

### 2026-08-15 用户目视反馈 + 补测（用户：sol 更好 baseline 浪头有马赛克；turnaround 身份一致好；文字右侧好但要同 UI；hybrid 好但只有动画版）
- **Sol-Attn 多内容（3 类 × sage/sol，同 seed）**：portrait 56→52s、forest 48→44s、dance 48→44s，sol 稳定快 ~8%。用户目视认为 sol 无马赛克（sage 浪头有噪音），结论反转：**sol-attn 可能兼具提速+去马赛克**，待用户看视频确认
- **turnaround 写实（wow_real 1024）**：48s 成功，验证真实照片 OOD 身份迁移
- **文字同情况对比**：同 UI 布局，对照(不打字)36s / 实验(打字+否定)28s
- **Hybrid 写实（wow_real 参考图）**：ref2va 60s / hybrid 60s（写实下耗时打平；动画版 hybrid 更快）
- 视频：output/video/{solattn_multi,text_ctrl2,hybrid_real}/；图：output/img_turnaround/wow_real_sheet_1024_*.png

### 2026-08-15 第二轮用户反馈 + ref2v turbo 实测
- 用户目视：sage 整体好但海浪有马赛克、sol 高动态(dance)崩；turnaround 写实全崩（都是正面旋转=OOD 确认）；文字左好右整体性好（微妙待再测）；hybrid 写实没脸、ref2va 写实胡了+背面变正面错误
- **start.sh 改节点控制（用户拍板）**：去掉全局 --use-sage-attention，加速靠节点（PathchSageAttentionKJ 可 auto/int8/fp8/disabled、SolAttnPatch）逐个视频选
- **ref2v turbo 4步实测**（同 seed 20260821，1024×576）：ref2va+turbo4步=81s vs 裸跑8步=80s（无优势）；hybrid+turbo4步=65s vs 裸跑8步=60s（更慢）→ ref2v turbo 4步在 1024 不划算

### 2026-08-15 三方加速对比跑批（去全局 sage 后首测，真纯 attention 基线）
- 背景：旧 solattn_baseline 实为全局 sage 结果（start.sh 当时未改），本次为去全局后首轮干净对比
- 设计：2 场景（wave=surfer 海浪 / dance=breakdance 高动态）× 3 方式（plain 无 patch / sage PathchSageAttentionKJ(auto) / sol SolAttnPatch tau1.3），同 seed 20260814 @1024×576 8步 124帧，v4-600EMA
- 产物：ComfyUI/output/video/attn3way/{wave,dance}_{plain,sage,sol}_00001_.mp4；对比图 output/compare/attn3way_{wave,dance}.png（行=50%/75% 帧，列=plain|sage|sol）

### 2026-08-15 三方对比第二轮：排除冷启动精确计时（用户目视反馈后补跑）
- 用户目视（2026-08-15）：①wave 三方式均无马赛克（首轮"sage 浪头马赛克"未复现，疑 seed/内容相关）②sol dance 鬼畜崩（确认高动态崩）③sage dance 有穿帮但明显轻于 sol
- 精确计时（模型已加载，日志 Prompt executed，同 seed 20260814 @1024×576 8步 124帧）：
  | 场景 | 纯 attention | Sage(auto) | Sol(tau1.3) |
  |---|---|---|---|
  | wave | 91.8s | 44.3s（2.07x）| 45.0s（2.04x）|
  | dance | 66.8s | 43.9s（1.52x）| 44.6s（1.50x）|
- 关键发现：①**sage/sol 耗时几乎持平**（wave ~2x / dance ~1.5x），Sol 无速度优势（首轮 1.07x 对比失真——当时 baseline 实为全局 sage）②sage 第一轮 45s 与本次 44.3s 一致（复现稳定）③wave plain 91.8s vs dance plain 66.8s 差异大，疑内容 tokens 差异
- **结论：Sol-Attn 无存在价值（无速度优势+高动态崩）；Sage 为默认加速，高动态内容注意穿帮风险（可降级纯 attention）**
- 队列踩坑：POST /prompt 校验即入队（首轮误重复排队 10 个已 clear；补跑前先确认队列空闲）

### 2026-08-15 六块文字再测（换场景矩阵实验，T-20260815-07 收口项）
- 背景：前两轮"左好右整体性好（微妙）"不清，换场景+拆变量澄清
- 设计：首帧=KREA 新生成无文字夜景街道（input/start/text_ctrl3_firstframe.png，1024×576）；I2V fl2va+v4 8步 62帧 同 seed 20260815；四组矩阵同公共六块 prompt（风格/时间线/摄像机/音频）
  - A_base：公共（无文字描述无否定）
  - B_block5：+块5 逐字打字（霓虹招牌"MIDNIGHT CAFE" clean sans-serif 全可读）
  - C_block6：+块6 否定列表（no gibberish/misspelled/extra text/subtitles/watermarks）
  - D_full：块5+块6 完整
- 耗时：A 60.5s（含首帧编码）/ B/C/D 各 ~37s
- 产物：ComfyUI/output/video/text_ctrl3/{A_base,B_block5,C_block6,D_full}_00001_.mp4；对比图 output/compare/text_ctrl3_matrix.png（行=A/B/C/D，列=40%/80% 帧）
- **用户目视 + 定论**（2026-08-15）：A/C 无字；B 有字在窗子上；D 字被强调、旁边无杂散。→ ①块5 逐字打字=文字生成必要条件（A/C 无字 vs B/D 有字，差异完全来自块5）②块6 否定单用无效（C=A），但**块5+块6 组合质量最佳**（D 主文字清晰+无杂散）③位置控制弱（写 on the wall 实际挂窗户，需更具体定位或接受模型自选）④已落 params.md 提示词控制技巧
- **本线四类新发现全部收口**：①Hybrid→T-20260815-09 ②Sol-Attn 弃用 ③turnaround 仅动漫/风格化 ④六块文字=块5必要+块6提升；T-20260815-07 完成，接力链B T1 社区技巧调研收口

### 2026-08-15 Hybrid 调研深入 + 任务拆分（用户决策）
- **原理确认**（scottmudge minimax_h3_analysis.md + smhfacct README 互证）：fl2va/ref2va 两 checkpoint >97% 权重 bit 同或 cos≥0.9997；唯一显著差异=每 block adaln_proj.linear（cos −0.74~−0.81 被训练完全重写）+ final_layer.adaln_proj（最差异张量 cos −0.83，疑似 ref2va 画质差根源）+ 输出头轻度；token_refiner/condition_proj 两模型基本相同→reference pathway 结构上都有，差异在调制层
- **Hybrid = fl2va 全权重为底 + 后 N 层（b15/20/25/30-49）adaln_proj 换 ref2va**，静态 merge 单文件（20.97GB），推理只 load 一份不翻显存（scottmudge 运行时版 mmap 流式峰值也仅 1 模型量）
- **社区反应**：模型 08-11 发布仅 4 天；HF 35 likes / HybridLoader 节点 112 stars / awesome 索引收录 4 档+N VFP4 量化跟进（abakanai 16.38/14.03GB）/ ComfyUI-Manager 已收录；但分类在 FL2VA 表下、无官方（MiniMax/Comfy-Org）背书、"drop-in replacement"系作者自述→**未到社区共识替代**，观察 1-2 周（信号=HybridLoader issue 修复/HF likes 增长/教程或官方默认采用）
- **scottmudge 主观推荐 = block 25-49**（与 smhfacct b25-49 一致，双验证）；其 preset 默认不动 final_layer（保持 fl2va），与 smhfacct 做法相同
- **b20-49 放弃下载**（用户决策 2026-08-15）：hf-mirror 整体限速 0.5MB/s（单连接 60s 512KB、并发连接被挂起、fl2va_int8 同慢，与 VPN 开关无关；代理 0.9MB/s、HF 直连超时、Modelscope 无源），20GB 需 11h+ 不可接受；且 b20 与 b25 系窄渐变（README: not uniformly better），已清理 768MB 半成品 part
- **任务拆分**：Hybrid 深度测试（参考忠实度/写实/身份一致性 + 社区观察）→ 独立任务 T-20260815-09（TODO 已登记，agent 未认领）

## 下一步
✅ 本线全部完成（T-20260815-07 收口）：四类新发现均实测定论——加速策略（params.md Sage 默认/Sol 弃用）+ 六块文字（块5必要+块6提升）+ turnaround（仅动漫）+ Hybrid（拆 T-20260815-09）
- 接力：链B T1 社区技巧调研收口；Hybrid 深度测试 T-20260815-09 未认领

## 关键链接
- 索引：https://github.com/MiniMax-AI/awesome-minimax-h3-integration
- Hybrid：https://huggingface.co/smhfacct/MiniMax-H3-fl2va-ref2va-hybrid-models
- Sol-Attn：https://github.com/kijai/ComfyUI-SolAttn_triton
- 六块结构：https://www.atlascloud.ai/zh/blog/tips/minimax-h3-prompt-guide
- 现有参数/工作流：.pi/skills/comfyui/references/{params,workflows}.md
