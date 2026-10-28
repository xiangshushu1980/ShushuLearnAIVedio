# 02 模型与下载

> 最后全面盘点：2026-08-12（ComfyUI v0.32.0 更新时发现文档与磁盘脱节，逐目录核对修正）
> Owner: Sean。2026-10-03 增补 Motion Booster REF2VA 与当前 Civitai 凭证入口；2026-10-11 局部记录 H3 模型清理。
> ⚠️ 本清单以磁盘实况为准。新增/删除模型后请同步更新本文件。

## 2026-10-11 H3 本地模型清理提醒

- `models/diffusion_models/minimax_h3_fl2va_pruned_fp8_scaled.safetensors` 已删除。后续运行脚本时**不要自动重新下载**；只有 Sean 明确要求时才恢复下载。
- `scripts/h3_promptor_p1.py` 和 `scripts/h3_gap_runner.py` 仍把上述 FP8 scaled 文件设为默认模型。下次运行这两个脚本前，先直接修改它们的默认模型配置，使用届时确认可用的本地模型；不要为满足旧默认值而重下 FP8 模型。
- `models/diffusion_models/minimax_h3_ref2va_pruned_turbo_int8_convrot.dl` 也已删除。
- ACE-Step 本地 XL Turbo 栈已整体删除（主模型、两个文本编码器、VAE，合计约 18.5 GiB）。后续**不要自动重新下载**；配乐优先考虑 H3 Music 和其他现有方案。`scripts/ace_t2i_probe.py` 仍引用这些文件，运行前需先改脚本或明确决定恢复模型。

## 磁盘实况（2026-08-12 盘点）

### 视频生成（MiniMax H3，主力）
| 文件 | 位置 | 大小 | 用途 |
|------|------|------|------|
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
| ref2VA_Motion_v2.safetensors | 147.9 MiB | Motion Booster V0.2 REF2VA；Civitai 2840146 / version 3246346；触发 `dynv2`；兼容与生成已验证；目标比例横幅在已测0.7可全幅，1.0同图转体重现近方形内容与黑边（竖图0.7/0.8曾有白边）；长发动态时机/轨迹变化，飘带/根须未见稳定增益，暂不改变默认配置；[初测与白边诊断](../experiments/sean_h3_motion_booster_ref2va_20261002/README.md)、[长发/根须/飘带0/0.7/1.0](../experiments/sean_h3_motion_booster_secondary_20261003/README.md) |

### Qwen Image 2.1（BF16 + Fun Control）
| 文件 | 位置 | 大小 | 用途 |
|------|------|------|------|
| qwen_image_2.1_bf16.safetensors | models/diffusion_models/ | 14.2GB | Qwen Image 2.1 BF16 主模型；Character Sheet LoRA 配方现用底模 |
| qwen_image_2.1_fun_controlnet_union_bf16.safetensors | models/model_patches/ | 7.55GB | Qwen Image 2.1 Fun Control Union BF16 模型补丁；2026-10-24 与 BF16 主模型完成单视图加载及生成验证；Character Sheet LoRA 组合未测，见[试验记录](../experiments/qwen_fun_control_bf16_side_view_20261024/QC.md) |
| qwen_image_2.1_fun_controlnet_union_int8_convrot.safetensors | models/model_patches/ | 3.78GB | Qwen Image 2.1 Fun Control Union INT8 ConvRot 模型补丁；已下载并被 ComfyUI ModelPatchLoader 枚举，尚未验证加载/生成 |
| character-sheet-qwen-image-2.1-edit-lora-e9.safetensors | models/loras/ | 42MB | Character Sheet BF16 LoRA；仍与 BF16 主模型配用，Fun Control 组合待实测 |

Fun Control 两个补丁来自 ModelScope `Comfy-Org/Qwen-Image-2.1` 的 `model_patches/`。两个文件头均可解析；2026-10-24 的单视图试跑确认 BF16 主模型 + BF16 补丁可在本机 RTX 4090 上以 768×1024、25 步完成生成（试验未叠加 Character Sheet LoRA）。该组合约 21.8GB（十进制）权重，需要 ComfyUI offload；已观测的显存读数为阶段性样本，不是峰值。Character Sheet LoRA 组合、更高分辨率及 INT8 ConvRot 补丁配方仍未验证。详见[试验记录](../experiments/qwen_fun_control_bf16_side_view_20261024/QC.md)。

### 生图（ANIMA + KREA）
| 文件 | 位置 | 大小 | 用途 |
|------|------|------|------|
| anima-base-v1.0.safetensors | models/diffusion_models/ | 3.9GB | ANIMA 动漫生图 |
| qwen_3_06b_base.safetensors | models/text_encoders/ | 1.2GB | ANIMA 文本编码器（2026-08-10 从 HF circlestone-labs/Anima 补回，曾误清）|
| krea2_turbo_fp8.safetensors | models/diffusion_models/ | 13GB | KREA 2 turbo 生图 |
| qwen3vl_4b_fp8_scaled.safetensors | models/text_encoders/ | 4.9GB | KREA 文本编码器 |
| qwen_image_vae.safetensors | models/vae/ | 243MB | ANIMA/KREA VAE |

> Krea2 人物身份三模式和 Raw/Turbo 选择见 [40_krea2_prompt_and_identity_pipeline.md](40_krea2_prompt_and_identity_pipeline.md)。当前本机只登记/安装 Turbo；`krea2_raw_fp8_scaled.safetensors` 尚未下载，因此 `identity_remove` 只能做配置校验，不能作为已实测基线。

### 图像编辑/超分
| 文件 | 位置 | 大小 | 用途 |
|------|------|------|------|
| BiRefNet_toonout.safetensors | models/RMBG/BiRefNet/ | 844MB | 抠图（ComfyUI-RMBG 节点）|
| 4x-ClearRealityV1.pth | models/upscale_models/ | 8.6MB | 超分 4x（768→3072 实测 3.3s）|

> ⚠️ **Bernini-R 模型缺失（2026-08-12 确认）**：`wan2.2_bernini_r_{high,low}_noise_int8_convrot.safetensors`（14.5GB×2）及 fp8 版、蒸馏 LoRA `lightx2v_T2V_14B_cfg_step_distill_v2_lora_rank64_bf16.safetensors`、配套 TE `umt5_xxl_fp8_e4m3fn_scaled.safetensors`（6.3GB）磁盘均不存在（模板/蓝图/测试视频仍在）。**用户决策 2026-08-12：暂不找回，后续需要时再下载**（指引见下方 Bernini-R 节 + docs/06_extras_install.md）。

### 角色 LoRA（CivitAI，models/loras/）
| 文件 | 说明 |
|------|------|
| alisa_mikhailovna_kujou_roshidere.safetensors | 角色 Alya（2026-08-10 重下 civitai 28695，73MB）|
| alisa_mikhailovna_kujou_tokidoki.safetensors | 角色 Alya（civitai 557213，39MB）|
| alisa_mikhailovna_kujou_ayra.safetensors | 角色 Alya（civitai 955584，110MB）|
| yuki_suou_v1120706.safetensors | 角色 Yuki（civitai 1000015，110MB）|
| anima-highres-aesthetic-boost.safetensors | ANIMA 高清/美学增强（133MB）|
| anima-turbo-lora-v0.2.safetensors | ANIMA 加速 v0.2（143MB）|

### KREA 2 风格 LoRA（T-comfy-ops-37，2026-09-17 下载并 SHA256 核验）
| 文件 | 位置 | 来源/版本 | 用途 |
|------|------|------|------|
| Jibs_Krea_2_Midjourney_Fantasy_Style_V1.safetensors | models/loras/ | CivitAI 1276784 / version 3176271 | Jibs Midjourney Fantasy Style；trigger `M1djourneyArtStyle`；建议 0.75–1.5 |
| KREA_MIDJ_1.safetensors | models/loras/ | CivitAI 2751419 / version 3095398 | KREA2 Midjourney；建议 0.7–1.0 |
| aumirageV2.safetensors | models/loras/ | CivitAI 2744307 / version 3148897 | Gemlight Beyond the veil；trigger `m1V8`；建议 0.8–1.0 |

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

### 默认下载规则（2026-10-14）
- 模型仓库优先使用 ModelScope；只在 ModelScope 没有**同一权重/同一版本**时，才保留原始来源（如 Hugging Face 或 CivitAI）。不要用相近模型替换同名权重。
- 通过仓库根目录的 `download_models.sh` 下载 ModelScope 指定文件；必须列出仓库内文件路径，避免误下整个大仓库。公开仓库可匿名下载；私有/受限仓库仍需相应授权。
- 本轮已对 H3、ANIMA、Krea 2、Qwen3-VL、Bernini-R、ClearReality 和 BiRefNet ToonOut 的 ModelScope 文件执行 HTTP Range 实际取样；均返回文件字节（206）。ToonOut 的 ModelScope SHA256 与原 HF 文件一致；ClearReality 9 MB 文件完成全量下载，并与 ModelScope API 提供的大小和 SHA256 完全一致。该验证证明文件可下载，不等于全量大模型下载、权重加载或生成已验证。

示例（按需下载，不表示恢复已清理模型）：
```bash
./download_models.sh Comfy-Org/MiniMax-H3 ./models \
  diffusion_models/minimax_h3_fl2va_pruned_int8_convrot.safetensors
./download_models.sh circlestone-labs/Anima ./models \
  split_files/diffusion_models/anima-base-v1.0.safetensors
./download_models.sh Comfy-Org/Krea-2 ./models \
  diffusion_models/krea2_turbo_fp8_scaled.safetensors
./download_models.sh Comfy-Org/Qwen3-VL ./models \
  text_encoders/qwen3vl_4b_fp8_scaled.safetensors
./download_models.sh 1038lab/BiRefNet ./models/RMBG/BiRefNet \
  BiRefNet_toonout.safetensors
```

`BiRefNet_toonout.safetensors` 使用 ModelScope `1038lab/BiRefNet`，并已核对 SHA256 与原 HF 文件一致。CivitAI LoRA 继续从 CivitAI 获取；目前没有确认 ModelScope 上相同版本的副本，不能用相近 LoRA 替换。

### Bernini-R int8_convrot（待重下时用）
- **源**：ModelScope `Comfy-Org/Bernini-R`，文件位于 `diffusion_models/`（当前仍缺失，按用户决定暂不恢复）
- **命令**：`./download_models.sh Comfy-Org/Bernini-R ./models diffusion_models/wan2.2_bernini_r_high_noise_int8_convrot.safetensors diffusion_models/wan2.2_bernini_r_low_noise_int8_convrot.safetensors`
- 旧 HF-Mirror 下载速度记录仅作历史，不再作为默认下载源。
- **完整性校验（三重）**：① 字节数精确等于目标 14535868680；② safetensors header（190464 字节）可解析；③ wget rc=0 正常收尾
- int8 选型背景与平台差异见 docs/06 §三

### H3（Comfy-Org/MiniMax-H3）
- 下载源：ModelScope `Comfy-Org/MiniMax-H3`；ComfyUI 文件保留仓库子目录路径。公开文件下载不需要 HF Token。

### ANIMA / KREA
- ANIMA：ModelScope `circlestone-labs/Anima`；文件在 `split_files/diffusion_models/`、`split_files/text_encoders/`、`split_files/vae/` 子目录。
- KREA 2：ModelScope `Comfy-Org/Krea-2`；`qwen3vl_4b_fp8_scaled.safetensors` 从 `Comfy-Org/Qwen3-VL` 获取。

### CivitAI（需 token）
- 角色/风格 LoRA：civitai.com 搜索。当前 Civitai API Key 保存于 `/home/sean/.config/civitai/api-key`（权限 `600`），下载时从文件读取；密钥值不进入命令行参数、日志或 Git。作者限制登录下载的文件需认证，公开模型元数据可访问不代表文件可匿名下载。

#### Civitai.com / Civitai.red 选择说明（2026-09-18）
- `civitai.red` 是 Civitai 的成人/自由内容入口，不是专门的风格、法术或暗黑奇幻模型库；普通风格、魔法特效、奇幻环境仍优先按底模兼容性和模型实测选择。
- 对黑暗题材，`dark fantasy`、`grimdark`、`horror`、`occult`、`necromancer`、`undead`、`battle damage`、`blood effects` 等方向可能有可用资源，但平台并不保证 `.red` 有独占优势。
- `.red` 也不等于血腥暴力放行区。官方 Safety Center 将 graphic violence、gore、severe injuries、human death 等列为禁止或会被移除的内容；明确肢解、内脏、重度尸体/死亡表现不应作为稳定的 Civitai 资源依赖。
- 接入策略：暂不做独立 Red provider；Civitai provider 保留可配置域名/下载 URL 的扩展位，默认走 `.com`。只有明确需要成人内容检索时才启用 `.red`，并默认关闭 NSFW。
- 参考：[Civitai.red Safety Center](https://civitai.red/safety)、[Civitai 多域名实现说明](https://github.com/civitai/civitai/blob/main/docs/multi-host-domain-aliases.md)、[Civitai API 文档](https://github.com/civitai/civitai-developer-docs)

## ⚠️ 关键经验

### 1. 不要下载 diffusers 分片格式
- `Wan-AI/Wan2.1-I2V-14B-480P` 仓库是 fp32 分片（7 个文件共 61GB）
- **ComfyUI 的 UNETLoader 不支持分片文件夹加载** → 浪费 61GB
- 直接下 Comfy-Org 的**单文件**版本

### 2. 网络加速

> 网络权威配置以用户级 AGENTS.md（Clash Rule + TUN）与 docs/06 §五 为准；遗留 FLClash 全劫持脚本（重装参考）见 docs/06 §五。

### 3. 下载命令（带续传）
```bash
./download_models.sh <ModelScope仓库ID> ./models <仓库内文件路径> [其他文件路径...]
```

## 显存参考（RTX 4090 24GB）
- H3 FL2VA/Ref2VA int8：扩散 ~14GB + 6.1GB offload；nvfp4 文本编码器可全量入显存
- KREA 2 fp8：~13GB 模型，生图 16s 加载
- ANIMA：轻量，生图流畅
- （Wan2.2 GGUF Q4_K_S Hi+Lo 双加载 ~13-16GB / Wan2.1 fp8 ~13-16GB 为历史参考，模型已清）
