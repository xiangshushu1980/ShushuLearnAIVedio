# 任务进度：h3-params（H3 语境下的参数技巧与放大讨论）

## 任务
- 目标：社区 H3 专项技巧调研 + 在 MiniMax H3 语境下讨论放大/参数技巧（用户决策 2026-08-07：**主力模型是 H3 非 Wan2.2**；H3 成片 2 分钟/条，5 秒+ 更有优势）
- 当前状态：🟡 进行中（首次对话已沉淀，等待新对话继续）
- 模式：讨论型任务——目的=给 Agent 积累经验 + 用户理解概念，不赶工

## 首次对话成果（2026-08-07，已 retain Mem0）

### 1. 放大路线社区调研结论（B站 + Reddit）
- **H3 框架 + LTX-2 放大 = 社区验证路线**（Reddit aurelm 87 赞：Wan 720p→LTX-2 时空双重放大→1440p，去伪影）
- LTX-2 参数铁律：**denoise ≤ 0.15**；高分辨率首帧重新注入潜空间效果更好；LTX 只做放大工具不做主生成；两步跑防 OOM；音频 25fps
- SeedVR2 = 精修备选（tile 逐帧、不魔化、慢）；Bernini 放大无社区背书（定位=编辑）
- **用户决策**：Wan3/LTX3.3 开源前不投入实装，先攒知识

### 2. 架构讨论结论（用户认同 2026-08-07）
- **不做自定义节点**：走"参数化模板 + 程序化组装"路线（API JSON 模板 + workflow_builder 组装层）
- 子单元粒度**待定**（能力级 vs 业务级，持续讨论）
- 契约文档放 docs（16 号位预留），模板资产在 workflows/templates/

### 3. 概念学习（用户感兴趣：潜空间/编码/条件注入）
- 关键认知：所有现代扩散模型在**潜空间**去噪（VAE encode 入场/decode 出场）；像素域=事后加工，潜空间=创作中干预
- 会淘汰：补丁类技巧（hires fix/九宫格/分段采样——模型内化）；不会淘汰：框架类（VAE/潜空间/编排思维/条件注入）
- 学习策略：框架概念值得学、参数甜点走 params.md/Mem0；Wan3 开源后社区沉淀 2-4 周再学新玩法

## 社区进展快照（2026-08-07 新增，临时会话调研落盘）

### 🔥 4 步加速 LoRA 今日发布（lightX2V 出品）
- `lightx2v/Minimax-h3-Turbo` v0.1（HF 08-07 14:45 UTC）：`minimax_h3_fl2v_turbo_4step_v0.1.safetensors`
- Kijai 同日转 ComfyUI 版（15:18 UTC）：`Kijai/MiniMax-H3_comfy/loras/`，含 `resized_avg_rank_21_bf16` 低显存版
- **Kijai README 参数铁律：4 步 + 0.75 强度 + er_sde/sa_solver 采样器；噪输出降强度**
- 官方仓库无新 LoRA（08-06 仅 README 更新）；"官方加速lora"标题党

### 社区实测（今天视频，结论分歧）
- 乐观派：刘悦 BV1LPu46ZE9J（3923播放）4 步 lora 支持所有裁剪模型+KJ 新节点，4060 6 步 ~100s；larryvrh 社区版 Turbo LoRA 已到 0.85 权重（GitHub 08-07 10:17 更新）
- 冷静派 Aiden_0 BV19Yu86eE6t：809s→200s+ 但**4 步音频有问题/重影/提示词遵循差；不能用多参 Ref 模型（只能 fl2va）**；建议等优化
- 预览派惊尘 BV1QBu86cEJZ：0.7 权重+10 步音频正常点，画面略过拟合

### 三重加速组合拳（Sol-Attn+SageAttention+EasyCache，BV1K1ut6UEHB）
- T2V 7:12→3:34、I2V 10:49→3:19（~3.2x）、Ref2V 8:05→3:41
- EasyCache 已入 ComfyUI 原生；Sol-Attn 是 KJ 新扩展；我们已有 sage，两者可叠加试点

### 对任务线意义
- 4 步 lora 可能重估速度甜点（基线 14 步 75s/条 → 6 步或 ~30-40s），但音频/Ref 不支持需实测验证，暂不直接上生产
- Sol-Attn + EasyCache 低风险试点增量

## 下一步（新对话入口）

### T1. 社区 H3 技巧调研（B 站 BV 清单，已定位未深挖）
- `BV1zMMf6nEYM`（1.8 万播放）H3 5 倍加速+超强画质"小技巧"
- `BV1efMm62EeR`（1.3 万）官方提示词 skill 安装使用心得
- `BV171Mo67EBb`（7201）必备使用技巧 + 提示词自动反推工作流
- `BV1T7uP6SEC2`（1.4 万）8GB 显存 15 秒视频 + 2K 画质 + 24FPS
- `BV1ZeuF6HE3Y`（3041）本地测试 2：参数及细节（参考生视频/视频编辑）
- `BV15Bun6gEvX`（2742）加速 LoRA 完整使用技巧
- `BV1McMy6ZEUY`（2253）实战技巧：提示词与多模态参考解析
- `BV12Zuw6CE42`（9393）多参多宫格导演台 3.0（插件+工作流+手册）

### T2. H3 语境放大参数讨论（新对话）
- 把 LTX-2 放大铁律搬到 H3 语境：H3 输出 1024×576@16fps → 放大目标/denoise/首帧注入在 H3 上怎么设
- H3 自带音频 → 与 LTX 音频 25fps 规则的衔接
- 等 Wan3/LTX3.3 开源后：新模型上验证原理迁移

### 其他遗留
- T3. TTS 方案调研（context-opt 遗留）
- T4. 模型源调研（context-opt 遗留）

## 关键链接
- 放大调研全文：本对话记录 + Mem0（agent_id=h3-params）
- H3 既有实测：docs/09_h3_test_plan.md、docs/10_h3_batch_optimization.md、params.md
- 子单元架构：docs/15 未建（契约文档预留位）
