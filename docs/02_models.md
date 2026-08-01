# 02 模型与下载

> 最后更新：2025-08-01 — 已切换到 Wan2.2 Lightning 快速视频栈 + ANIMA/KREA 生图

## 已下载模型（全部就位）

### 视频生成（Wan2.2 I2V Lightning，主力）
| 文件 | 位置 | 大小 | 用途 |
|------|------|------|------|
| Wan2.2-I2V-A14B-HighNoise-Q4_K_S.gguf | models/unet/ | 8.7GB | 高分岔 UNet |
| Wan2.2-I2V-A14B-LowNoise-Q4_K_S.gguf | models/unet/ | 8.7GB | 低分岔 UNet |
| umt5-xxl-encoder-Q5_K_S.gguf | models/text_encoders/ | — | Wan 文本编码器 |
| wan2.2_i2v_lightx2v_4steps_lora_v1_{high,low}_noise.safetensors | models/loras/ | 1.2GB×2 | 4 步蒸馏 LoRA |
| wan_2.1_vae.safetensors | models/vae/ | 243MB | Wan VAE |

### 生图（ANIMA + KREA）
| 文件 | 位置 | 大小 | 用途 |
|------|------|------|------|
| anima-base-v1.0.safetensors | models/diffusion_models/ | 4.18GB | ANIMA 动漫生图 |
| qwen_3_06b_base.safetensors | models/text_encoders/ | — | ANIMA 文本编码器 |
| krea2_turbo_fp8.safetensors | models/diffusion_models/ | 12.9GB | KREA 2 turbo 生图 |
| qwen3vl_4b_fp8_scaled.safetensors | models/text_encoders/ | 5.24GB | KREA 文本编码器 |
| qwen_image_vae.safetensors | models/vae/ | — | ANIMA/KREA VAE（与 wan_2.1_vae 同结构）|

### LoRA（CivitAI）
| 文件 | 说明 |
|------|------|
| alisa_mikhailovna_kujou-roshidere-ana-soralz.safetensors | 角色 Alya（840 张量）|
| yuki_suou-roshidere-ana-soralz.safetensors | 角色 Yuki（840 张量）|
| anima-highres-aesthetic-boost.safetensors | ANIMA 高清/美学增强 |
| anima-turbo-lora-v0.1 / v0.2.safetensors | ANIMA 加速（v0.2 更新）|

### 对照（Wan2.1，保留）
| 文件 | 位置 | 大小 | 用途 |
|------|------|------|------|
| wan2.1_i2v_480p_14B_fp8_e4m3fn.safetensors | models/diffusion_models/ | 16GB | Wan2.1 I2V（20 步 ~3 分钟，对照）|
| umt5_xxl_fp8_e4m3fn_scaled.safetensors | models/text_encoders/ | 6.3GB | 2.1 文本编码器 |
| clip_vision_h.safetensors | models/clip_vision/ | 1.2GB | CLIP Vision（2.1 I2V 需要；2.2 不需要）|

## 下载源

### Wan2.2 GGUF（Comfy-Org 或 city96）
- Wan2.2 GGUF 系列：HuggingFace `city96/Wan2.2-I2V-A14B-GGUF`
- LoRA（lightx2v 4steps）：HuggingFace 搜 `wan2.2_i2v_lightx2v_4steps_lora`

### Wan2.1（Comfy-Org 打包版，无需授权）
```
https://huggingface.co/Comfy-Org/Wan_2.1_ComfyUI_repackaged/tree/main/split_files
```

### ANIMA / KREA
- ANIMA：CivitAI / HF `circlestone-labs`
- KREA 2：HF 搜 `krea2_turbo_fp8`；编码器 `qwen3vl_4b_fp8_scaled`

### CivitAI（需 token）
- 角色/风格 LoRA：civitai.com 搜索，token 在 `.mcp.json`（**pi MCP 不读新增 env → 用 curl 绕行下载**，见 SKILL troubleshooting）

## ⚠️ 关键经验

### 1. 不要下载 diffusers 分片格式
- `Wan-AI/Wan2.1-I2V-14B-480P` 仓库是 fp32 分片（7 个文件共 61GB）
- **ComfyUI 的 UNETLoader 不支持分片文件夹加载** → 浪费 61GB
- 直接下 Comfy-Org 的**单文件**版本（fp16 28GB / fp8 16GB）
- 4090 用 fp8 更省显存更快，fp16 画质略好

### 2. 网络加速（WSL + FLClash VPN）
下载慢的根因：**VPN TUN 模式劫持所有流量**（含国内域名），DNS 返回 fake-ip (198.18.0.x)。

FLClash 脚本配置（已设置，未来重装需恢复）：
```javascript
const main = (config) => {
  config.tun.mtu = 1500;
  if (!config.rules) config.rules = [];
  config.rules.unshift('DOMAIN-SUFFIX,xethub.hf.co,DIRECT');
  config.rules.unshift('DOMAIN-SUFFIX,hf-mirror.com,DIRECT');
  config.rules.unshift('DOMAIN-SUFFIX,modelscope.cn,DIRECT');
  if (!config.dns) config.dns = {};
  if (!config.dns['fake-ip-filter']) config.dns['fake-ip-filter'] = [];
  config.dns['fake-ip-filter'].push('+.xethub.hf.co');
  config.dns['fake-ip-filter'].push('+.hf-mirror.com');
  config.dns['fake-ip-filter'].push('+.modelscope.cn');
  return config;
};
```
- hf-mirror.com 302 重定向到 `cas-bridge.xethub.hf.co`（CloudFront CDN）→ 必须直连
- 部分文件重定向到 `us.aws.cdn.hf.co`（也需直连，可加进规则）

### 3. 下载命令（带续传）
```bash
TOKEN="<HF_TOKEN>"
wget -c --timeout=120 --tries=0 \
  --header="Authorization: Bearer $TOKEN" \
  -O models/diffusion_models/<文件名> \
  "https://hf-mirror.com/<repo>/resolve/main/<路径>/<文件名>"
```

## 显存参考（RTX 4090 24GB）
- Wan2.2 GGUF Q4_K_S（Hi+Lo 双加载）: ~13-16GB，流畅
- Wan2.1 480P fp8: ~13-16GB；fp16: ~18-20GB 紧张
- KREA 2 fp8: ~12.9GB 模型，生图 16s 加载
- Wan2.2 (48通道) 未量化: 24GB+，不建议
