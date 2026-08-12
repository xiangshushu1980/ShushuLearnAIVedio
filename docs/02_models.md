# 02 模型与下载

> 最后更新：2026-08-12 — 全面盘点（ComfyUI v0.32.0 更新时发现文档与磁盘脱节，逐目录核对修正）
> ⚠️ 本清单以磁盘实况为准。新增/删除模型后请同步更新本文件。

## 磁盘实况（2026-08-12 盘点）

### 视频生成（MiniMax H3，主力）
| 文件 | 位置 | 大小 | 用途 |
|------|------|------|------|
| minimax_h3_fl2va_pruned_fp8_scaled.safetensors | models/diffusion_models/ | 20GB | H3 FL2VA（首/尾帧→视频+音频，fp8）|
| minimax_h3_fl2va_pruned_int8_convrot.safetensors | models/diffusion_models/ | 20GB | H3 FL2VA int8（速度/显存更优）|
| minimax_h3_ref2va_pruned_int8_convrot.safetensors | models/diffusion_models/ | 20GB | H3 Ref2VA（视频+音频参考→视频+音频）|
| qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors | models/text_encoders/ | 15GB | H3 文本编码器（Qwen3-VL-32B nvfp4_awq 官方推荐）|
| minimax_h3_video_vae_fp16.safetensors | models/vae/ | 4.9GB | H3 视频 VAE |
| minimax_h3_audio_vae_fp32.safetensors | models/vae/ | 578MB | H3 音频 VAE（32kHz 立体声）|

H3 LoRA（models/loras/）：
| 文件 | 大小 | 用途 |
|------|------|------|
| minimax_h3_fl2v_turbo_8step_v1.0_comfyui_bf16.safetensors | 1.9GB | 8 步 Turbo（成片档 v4-600EMA 搭档，备选）|
| minimax_h3_fl2v_turbo_4step_v1.0_768p_comfyui_bf16.safetensors | 1.9GB | 4 步 v1.0（淘汰档，仅留档）|
| minimax_h3_fl2v_lightx2v_turbo_4step_v0.1_comfy_resized_avg_rank_21_bf16.safetensors | 301MB | 4 步 v0.1（淘汰档，仅留档）|
| minimax_h3_turbo_v4_step600_ema.safetensors | 744MB | **成片档主力**（v4-600EMA 8步@1024，用户决策 2026-08-11）|
| minimax_h3_turbo_4step_ckpt500_pruned_comfyui.safetensors | 592MB | 4 步试点 ckpt500（淘汰档）|
| minimax_h3_turbo_4step_ema_ckpt850_pruned_comfyui.safetensors | 592MB | 4 步试点 ckpt850（淘汰档）|

### 生图（ANIMA + KREA）
| 文件 | 位置 | 大小 | 用途 |
|------|------|------|------|
| anima-base-v1.0.safetensors | models/diffusion_models/ | 3.9GB | ANIMA 动漫生图 |
| qwen_3_06b_base.safetensors | models/text_encoders/ | 1.2GB | ANIMA 文本编码器（2026-08-10 从 HF circlestone-labs/Anima 补回，曾误清）|
| krea2_turbo_fp8.safetensors | models/diffusion_models/ | 13GB | KREA 2 turbo 生图 |
| qwen3vl_4b_fp8_scaled.safetensors | models/text_encoders/ | 4.9GB | KREA 文本编码器 |
| qwen_image_vae.safetensors | models/vae/ | 243MB | ANIMA/KREA VAE |

### 生图（ACE 栈，2026-08-12 盘点补记，此前文档未收录）
| 文件 | 位置 | 大小 |
|------|------|------|
| acestep_v1.5_xl_turbo_bf16.safetensors | models/diffusion_models/ | 9.3GB |
| qwen_4b_ace15.safetensors | models/text_encoders/ | 7.9GB |
| qwen_0.6b_ace15.safetensors | models/text_encoders/ | 1.2GB |
| ace_1.5_vae.safetensors | models/vae/ | 322MB |

### 图像编辑/超分
| 文件 | 位置 | 大小 | 用途 |
|------|------|------|------|
| BiRefNet_toonout.safetensors | models/RMBG/BiRefNet/ | 844MB | 抠图（ComfyUI-RMBG 节点）|
| 4x-ClearRealityV1.pth | models/upscale_models/ | 8.6MB | 超分 4x（768→3072 实测 3.3s）|

> ⚠️ **Bernini-R 模型缺失（2026-08-12 确认）**：`wan2.2_bernini_r_{high,low}_noise_int8_convrot.safetensors`（14.5GB×2）及 fp8 版、蒸馏 LoRA `lightx2v_T2V_14B_cfg_step_distill_v2_lora_rank64_bf16.safetensors`、配套 TE `umt5_xxl_fp8_e4m3fn_scaled.safetensors`（6.3GB）磁盘均不存在（模板/蓝图/测试视频仍在）。用户记得曾下载，待确认位置或重下。下载指引见下方 Bernini-R 节 + docs/06_extras_install.md。

### 角色 LoRA（CivitAI，models/loras/）
| 文件 | 说明 |
|------|------|
| alisa_mikhailovna_kujou_roshidere.safetensors | 角色 Alya（2026-08-10 重下 civitai 28695，73MB）|
| alisa_mikhailovna_kujou_tokidoki.safetensors | 角色 Alya（civitai 557213，39MB）|
| alisa_mikhailovna_kujou_ayra.safetensors | 角色 Alya（civitai 955584，110MB）|
| yuki_suou_v1120706.safetensors | 角色 Yuki（civitai 1000015，110MB）|
| anima-highres-aesthetic-boost.safetensors | ANIMA 高清/美学增强（133MB）|
| anima-turbo-lora-v0.2.safetensors | ANIMA 加速 v0.2（143MB）|

### 遗留（无主栈）
- `wan_2.1_vae.safetensors`（models/vae/，243MB）：**2026-08-12 补回**（hf-mirror，Comfy-Org/Wan_2.1_ComfyUI_repackaged）。Wan 栈已清但 VAE 与 ANIMA 同结构、体积小，保留兜底
- `clip_vision_h.safetensors`（models/clip_vision/，1.2GB）：Wan2.1 遗留，当前无栈使用，未清

## 已清理记录（用户确认 2026-08-12 有意清理）

| 模型 | 原大小 | 说明 |
|------|--------|------|
| Wan2.2-I2V-A14B-High/LowNoise-Q4_K_S.gguf | 8.7GB×2 | Wan2.2 快速视频栈整栈清理（给 H3 腾空间）|
| umt5-xxl-encoder-Q5_K_S.gguf | — | 同上（Wan 文本编码器）|
| wan2.2_i2v_lightx2v_4steps_lora_v1_{high,low}_noise.safetensors | 1.2GB×2 | 同上（4 步蒸馏 LoRA）|
| wan2.1_i2v_480p_14B_fp8_e4m3fn.safetensors | 16GB | Wan2.1 对照栈（同批清理）|
| umt5_xxl_fp8_e4m3fn_scaled.safetensors | 6.3GB | 同上（Bernini 配套 TE，随 Bernini 缺失一并失效）|
| yuki_suou-roshidere-ana-soralz.safetensors | — | 角色 Yuki 旧版（840 张量）|
| anima-turbo-lora-v0.1.safetensors | — | 被 v0.2 取代 |
| lightx2v_T2V_14B_cfg_step_distill_v2_lora_rank64_bf16.safetensors | 630MB | Bernini 蒸馏 LoRA（与 Bernini 模型同批清理）|

> ⚠️ 影响：`workflows/wan2.2_i2v_lightning_test.json` 及全部 `wan2.2*`/`wan2.1*`/`bernini*`/`pipeline_wan22_*` 工作流当前不可用（引用已清模型）。将来 LTX/Wan3/FLUX 开源测试时注意区分。

## 下载源

### Bernini-R int8_convrot（待重下时用）
- **源**：`https://hf-mirror.com/Comfy-Org/Bernini-R/resolve/main/diffusion_models/wan2.2_bernini_r_{high,low}_noise_int8_convrot.safetensors`（各 14.54GB，revision e5674fad）
- **命令**：`wget -c --tries=0 --timeout=30`（断点续传+无限重试）
- **网络实测**：hf-mirror 直连 ~8.6MB/s；**开 VPN 后大幅提速**（18 分钟下完 29GB）；GitHub 直连时通时不通（7890 代理未监听，勿依赖）
- **完整性校验（三重）**：① 字节数精确等于目标 14535868680；② safetensors header（190464 字节）可解析；③ wget rc=0 正常收尾
- int8 选型背景与平台差异见 docs/06 §三

### H3（Comfy-Org/MiniMax-H3）
- 下载源：`Comfy-Org/MiniMax-H3`（hf-mirror，需 `HF_HUB_DISABLE_XET=1` 绕过 Xet 401）

### ANIMA / KREA
- ANIMA：CivitAI / HF `circlestone-labs`
- KREA 2：HF 搜 `krea2_turbo_fp8`；编码器 `qwen3vl_4b_fp8_scaled`

### CivitAI（需 token）
- 角色/风格 LoRA：civitai.com 搜索，token 在 `.mcp.json`（**pi MCP 不读新增 env → 用 curl 绕行下载**，见 SKILL troubleshooting）

## ⚠️ 关键经验

### 1. 不要下载 diffusers 分片格式
- `Wan-AI/Wan2.1-I2V-14B-480P` 仓库是 fp32 分片（7 个文件共 61GB）
- **ComfyUI 的 UNETLoader 不支持分片文件夹加载** → 浪费 61GB
- 直接下 Comfy-Org 的**单文件**版本

### 2. 网络加速

> 网络权威配置以用户级 AGENTS.md（Clash Rule + TUN）与 docs/06 §五 为准；遗留 FLClash 全劫持脚本（重装参考）见 docs/06 §五。

### 3. 下载命令（带续传）
```bash
TOKEN="<HF_TOKEN>"
wget -c --timeout=120 --tries=0 \
  --header="Authorization: Bearer $TOKEN" \
  -O models/diffusion_models/<文件名> \
  "https://hf-mirror.com/<repo>/resolve/main/<路径>/<文件名>"
```

## 显存参考（RTX 4090 24GB）
- H3 FL2VA/Ref2VA int8：扩散 ~14GB + 6.1GB offload；nvfp4 文本编码器可全量入显存
- KREA 2 fp8：~13GB 模型，生图 16s 加载
- ANIMA：轻量，生图流畅
- （Wan2.2 GGUF Q4_K_S Hi+Lo 双加载 ~13-16GB / Wan2.1 fp8 ~13-16GB 为历史参考，模型已清）
