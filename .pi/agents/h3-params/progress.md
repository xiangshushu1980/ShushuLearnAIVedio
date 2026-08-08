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

## 社区反应深挖（2026-08-07 晚，临时会话二轮调研落盘）

### B 站反应：怀疑观望派为主
- 高赞直指标题党刷流量（"300%加速/王炸"封面党）；"等等党胜利"、一天几更等稳定
- 实测负面：4 步爆音（er_sde 0.75/4 步）、重影/糊、提示词遵循差、动作变慢；**低于 24fps 音频易出问题**；**pruned 模型用 unpruned lora 有兼容大问题**；爆显存（20 系/8G）；EasyCache 劣化严重 + 音频问题（与 4 步 lora 二选一）；多参 Ref 不支持只能 fl2va
- 实测正面：lightx2v lora 8 步"完美"R2V 可（紫韵）；只挂 lora 8 步 480p≈150s；4060 6 步≈100s（刘悦）；5070ti 15s 1080 370s；**sage 最稳（~30% 提速画质影响最小）**

### Reddit：权威参数与作者定调
- **larryvrh Turbo LoRA 热帖 1550 分**：video sigma shift=12 / audio=4-6；8-10 步(EMA) / 6-8 步(ckpt500)；**res_multistep 采样器**；strength 0.8-1.8；可叠 sage/Sol-Attn/Gradient；**禁与 cache 同用**；音频修复用其自定义采样器（GitHub Larryvrh/ComfyUI-MiniMax-H3-Turbo）；官方承认 undertrained
- **Kijai PR #15243 已合并进 ComfyUI**（Fix sampler issues for audio with minimax）→ **nightly 已修复 4 步 lora 爆音**（Jota_be 实测：nightly+Kijai loader+sage+4 步 lora(500 ckpt pruned) 音频完美清晰）
- **comfyanonymous 定调**（tips 帖 65 赞）：sage+easycache 好；**GGUF/VRAM清理节点/tiled VAE 完全避免**；省内存用 `--fast-disk`；推荐 `MiniMaxH3MemoryEfficientSageAttentionPatch` 专用节点；OPTIMIZE_FOR_SPEED=1 + expandable_segments
- **Spectrum 节点**（551 分，斯坦福+字节）：~1.5x 提速（Euler -34%），作者诚实标注**非无损**（快速运动眼睛/手指劣化）；不与 EasyCache 同用；位置=loader→lora→sigma shift→Spectrum→guider
- **Ostris 在训练 4 步 turbo lora**（374 分，期待极高）；官方 X 发推夸社区 4 天做出实验室级成果
- 环境要点：CUDA 30+ 原生 int8 convrot（旧 CUDA 软模拟慢）；INT4 TE 可用（Merserk 量）；--fast-disk 后 16GB RAM 即可（峰值 11GB）

### 结论：当前最佳选择（用户待拍板）
1. **本周立即**：ComfyUI 更新到最新 nightly（PR 15243 音频修复已合）；生产维持 sage 不动（最稳）
2. **试点（新任务线）**：4 步 lora 用 **Kijai 转换的 pruned 兼容版（resized_avg_rank_21_bf16）**，参数起点 larryvrh（res_multistep + sigma shift 12/4-6 + 8 步），音频作 gate；预期 75s→45-50s（8 步）/→30-35s（4 步）
3. **观望 1-2 周**：Ostris lora、lightx2v 修复版（UP 自曝明天修）、ComfyUI 正式版合入 PR
4. **不做**：EasyCache/Sol-Attn 上生产（劣化+音频报告多）、GGUF/清理节点/tiled VAE（作者明令）、多参 Ref+4 步 lora（不支持）、4 步档出成品

## 社区进展快照 v3（2026-08-07 深夜，三轮调研落盘）

### 官方级重磅：lightx2v + ModelTC 发布 4 步 Turbo LoRA v0.1（今日 UTC 12:59）
- `minimax_h3_fl2v_turbo_4step_v0.1.safetensors`（1.3GB，FL2V 蒸馏；HF 147 likes/8 小时）
- **Kijai 1 小时内出 ComfyUI 转换 ×2**：`minimax_h3_fl2v_lightx2v_turbo_4step_v0.1_comfy.safetensors` + `_comfy_resized_avg_rank_21_bf16.safetensors`（都在 Kijai/MiniMax-H3_comfy）
- **无需自定义节点**：丢 models/loras/ + 原生 LoraLoader 即可；Kijai 测试笔记参数：**0.75 strength + 4 步 + er_sde 或 sa_solver**
- 社区实测好参数（Reddit 11 赞）：**er_sde + beta57 + shift 12/10 + strength 1.0**
- 踩坑：普通采样器（euler simple）→ 音频完全毁（必须 er_sde）；**只支持 T/I2V，Ref2V 不可用**（roadmap 有 Ref2V 蒸馏）；8GB VRAM 可跑（传闻）；Diffusers 与 ComfyUI 音频有差异（nightly 已修 = Kijai PR #15243）
- 团队自述：v0.1 仅预览，**未来几天出更新版**

### larryvrh v4-600 EMA（今晚更新，434 likes，~744MB bf16）
- 推荐 `minimax_h3_turbo_v4_step600_ema.safetensors`：静帧/小动作大提升、微细节（脸/手指/纹理）更好、v1 过锐塑料感解决
- trade-off：仅 4 步 + 大快速运动 → motion-smear/trailing（作者修中）；6-8 步基本消除
- **步骤范围改为 4-8**（超 8 步过锐伪影无益）；**strength 固定 1.0**（ghosting→1.05-1.2；过锐→0.8-0.95）；**scheduler 用 simple**；4 步重动作场景 v1-850 仍更友好
- 节点自动适配 pruned base（pruned_int8/fp8 均支持，我们 pruned fp8 ✓）；low_vram off 应用最锐
- 音频仍待改进

### Ostris 状态
- 8/4 X：turbo time LoRA 训练中，**音频算法未解决（borked）** + 数据集（慢动作问题）生成中；未发布 → lightx2v 抢先

### B 站动态
- 标题党整合包潮继续（900%/350%/45% 封面党）；8g显存小黑 106s 出片实测（整活向无参数细节）
- 官方 vllm_project：**vLLM-Omni day-0 支持 MiniMax H3**（34 分钟）→ 推理服务赛道铺路（本地线不受影响，仅记录）
- 安仔先生「双时钟加速版」新概念待考证（可能指 video/audio 双调度）

### 对我们的意义（行动清单更新）
1. **立即试点 lightx2v v0.1**：无节点依赖、官方团队背书；Kijai resized bf16 转换；4 步 + er_sde + beta57 + shift 12/10 + strength 0.75 与 1.0 两档；沿用写实泳池首帧同 seed；音频作 gate
2. **同步换 larryvrh v4-600 EMA**：替换 ckpt500/850 旧档；6 步 + strength 1.0 + simple；4 步重动作留 v1-850 作对照
3. 观望：lightx2v v0.2（几天内）、Ref2V turbo（roadmap）、Ostris DMD

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
