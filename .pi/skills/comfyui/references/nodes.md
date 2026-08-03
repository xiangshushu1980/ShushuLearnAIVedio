# 节点速查（本项目实际用过的节点）

> 记录每个用过的节点：干什么（语义）→ 官方/社区推荐（出处+理由）→ 本地实测（4090 24GB）。
> 用途：搭工作流前先查本表，避免重复查源码；新节点首次落地后必须补录（流程见 learning.md §3.5）。

## 来源标注约定
- `[官方]`：模型作者/官方模板/官方文档，标注出处；**理由比数值重要**（懂理由才知道什么偏离安全）
- `[社区]`：社区来源（CivitAI/reddit/讨论帖），标注来源+适用配置；**非 4090 或不同栈的经验慎用，需实跑验证**
- `[本地实测]`：本机 4090 实测，标注日期；无标签默认即本地实测

---

## A. 加载类

### UNETLoader / UnetLoaderGGUF / DiffusionModelLoader
- 作用：加载扩散主模型（safetensors / GGUF 量化）
- 参数：`unet_name`（模型文件名）、`weight_dtype`（GGUF 不需要，safetensors 可 fp8 等）
- 官方/社区：
  - `[官方]` Wan 2.2 I2V 官方模板即用 fp8_scaled（高/低噪双模型），见 `blueprints/Image to Video (Wan 2.2).json`
  - `[社区]` GGUF Q4_K_S 是 4090 24GB 跑 A14B 的主流量化（kijai 生态）；Q8 更准但 24GB 放不下 Hi+Lo 双模型
- 本地实测：Hi+Lo 双 GGUF Q4_K_S 共存可行；切换模型重载 ~45s

### CLIPLoader / CLIPLoaderGGUF
- 作用：加载文本编码器；`type` 参数决定编码器家族（wan / minimax / krea2 / ...），**填错必报错**
- 参数：`clip_name`、`type`、`device`
- 本地实测：
  - Wan 系用 `umt5-xxl-encoder-Q5_K_S.gguf`（type=wan）
  - MiniMax H3 用 `qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors`（type=minimax）
  - KREA 用 `qwen3vl_4b_fp8_scaled.safetensors`（type=krea2）
  - ANIMA 用 `qwen_3_06b_base`（type 对应模型卡要求）

### VAELoader
- 作用：加载 VAE（图像/视频）。一个模型可能对应多个 VAE（如 H3 有 video VAE + audio VAE 两个节点）

### LoadImage
- 作用：加载输入图。`image` 参数**支持子目录路径**（`start/alya_768.png` 已验证 ✅）
- 本地实测：起始图分辨率直接用原图（1024-1792²），越大视频越清晰（见 params.md 分辨率节）

---

## B. 采样类

### KSampler / KSamplerAdvanced
- 作用：核心采样器。KSamplerAdvanced 可分段控制去噪步数区间（start_at_step/end_at_step + add_noise）
- 官方/社区：
  - `[官方]` Wan2.1 标准模式：20 步 / cfg 3.5 / shift 8（官方模板）；lightx2v 蒸馏版：4 步 / 无 cfg（BasicGuider）
  - `[官方]` lightx2v 蒸馏卡明确 4-step；LoRA rank 64 = 原版质量（Banodoco 仓库），rank 48 ≈ 27% 重建误差 / rank 32 ≈ 40%
- 本地实测：
  - Hi/Lo 双段：Hi 0-2 段加噪，Lo 2-4 段不加噪（4 步总）
  - 6 步 vs 4 步几乎不增耗时，质量小幅提升 → 日常 6 步，对比/求快 4 步

### ModelSamplingSD3（shift）
- 作用：调整时间步分布（shift），影响去噪节奏。**Wan 系必配**
- 官方/社区：
  - `[官方]` Wan 2.2 I2V 官方 blueprint 子图：**shift = 5**（刚挖到的权威值，LoRA@1.0）
  - `[官方]` Wan2.1 标准模式官方 shift = 8
  - `[社区]` WanVideoWrapper 生态用 shift 42（artokun-flow 等），那是 kijai 包装器的体系，**勿混用**
- 本地实测：lightning 版用 shift 5，cfg 1.0（见 wan2.2_i2v_lightning_test.json）

### BasicGuider + BasicScheduler + KSamplerSelect + SamplerCustomAdvanced
- 作用：无 cfg 蒸馏管线四件套（CFG-distilled 模型：MiniMax H3、Turbo/Lightning 类）
- 关键参数：BasicScheduler(simple, 20步)；KSamplerSelect(res_multistep)
- 官方/社区：
  - `[官方]` MiniMax H3 官方模板用 simple/res_multistep/20 步；**无 cfg**（BasicGuider 等价 cfg=1，CFG-distilled 不要加 cfg）
  - `[官方]` H3 训练帧范围 124-362 帧（官方文档）
- 本地实测：H3 1344×768×124帧(5.2s)×20步 ≈ 241s I2V / 353s T2V（~9.5s/it）

### LoraLoaderModelOnly
- 作用：只给模型挂 LoRA（不处理文本编码器侧）
- 参数：`lora_name`、`strength_model`
- 官方/社区：`[官方]` Wan2.2 官方模板 strength=1.0；lightx2v 有 high/low noise 两个 LoRA 分别挂 Hi/Lo 两个 UNet
- 本地实测：Alya 角色 alisa@1.0 还原好；anima-highres@0.6 清晰度 +8%

### CLIPTextEncode
- 作用：文本 → 条件向量（正/负 prompt）
- 官方/社区：`[官方]` Wan 官方模板负向 = 色调艳丽/过曝/静态/模糊/多余手指等中文负面词（刚挖到）；英文亦可
- 本地实测：ANIMA 用 Danbooru 标签混合；H3 无负向概念（蒸馏模型通常不需要）

---

## C. Wan 视频管线

### WanImageToVideo
- 作用：Wan I2V 图生视频核心节点
- 参数：`width`、`height`、`length`(帧数)、`batch_size`
- 官方/社区：`[官方]` Wan 2.2 blueprint：640×640、81 帧；**分辨率 16 倍数、帧数 4n+1**（官方约束）
- 本地实测：**不需要 clip_vision_output**（Wan 2.2 内部处理，2.1 才需要）；起始图自动双线性缩放

---

## D. MiniMax H3 管线

### MiniMaxH3ImageToVideo / MiniMaxH3TextToVideo
- 作用：H3 全模态音视频生成（图/文 → 视频+原生音频）
- 参数：clip、vae、prompt、width、height、length(帧)、first_frame/last_frame
- 官方/社区：`[官方]` 官方模板 1344×768、124-362 帧训练范围、20 步 res_multistep、无 cfg；r2v 支持 ≤9 图 + ≤3 视频 + ≤3 音频参考
- 本地实测：124 帧 = 5.2s（24fps）；I2V 241s / T2V 353s；音频 VAE 也要加载（VAELoader audio_vae）

### VAEDecodeAudio
- 作用：解码 H3 音频 latent → 音频（32kHz 立体声）
- 本地实测：输出接 CreateVideo 的 audio 输入，最终 mp4 带 AAC 音轨

---

## E. 图像编辑/超分/抠图

### BiRefNetRMBG（ComfyUI-RMBG，1038lab）
- 作用：抠图（背景移除）
- 依赖：onnxruntime-gpu、opencv-python-headless、timm（缺 timm 报 No module named 'timm'）
- 踩坑：kijai 仓库不存在，正确仓库是 1038lab/ComfyUI-RMBG

### UpscaleModelLoader + ImageUpscaleWithModel
- 作用：模型超分（4x-ClearRealityV1）
- 本地实测：Bernini 成片/起始图超分用；4x 模型 4090 无压力

---

## F. 输出类

### CreateVideo + SaveVideo
- 作用：视频编码保存；SaveVideo 的 `filename_prefix` **直接带子目录**（`video/xxx`），生成时命名，绝不要事后 mv
- 参数：fps（H3 用 24，Wan 默认 16，Bernini 官方默认 16）
- 本地实测：移动文件后需重启 ComfyUI（asset_seeder prune 旧路径）

### SaveImage
- 作用：保存图片；同样支持子目录前缀

---

## 待补录（遇到后补）
- WanVideoWrapper 系（VHS_LoadVideo、WanVideoSampler、WanVideoAnimateEmbeds）— artokun-flow 需要时补
- ModelSamplingAuraFlow / 其他采样 shift 节点
- 社区其他配置（16GB 卡 / 3090 / Apple Silicon）经验：按来源标签补录，**只记有出处的**
