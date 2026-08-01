# 工作流档案

> 每个工作流的节点结构、用途、参数与已生成结果。工作流 JSON 在 `/home/sean/projects/comfy-ops/workflows/`。

## 1. wan2.2_i2v_lightning_test.json — 主力快速视频（17 节点）

**任务**: 图生视频（起始图 → 动画）｜ **耗时**: 480²×17帧 ≈ 10-16 秒/次（对比 Wan2.1 的 3 分钟）

### 节点结构
```
UnetLoaderGGUF(High) → ModelSamplingSD3(shift=5) → LoraLoaderModelOnly(Hi LoRA) ─┐
UnetLoaderGGUF(Low)  → ModelSamplingSD3(shift=5) → LoraLoaderModelOnly(Lo LoRA) ─┤
CLIPLoaderGGUF(umt5 Q5, wan) → CLIPTextEncode 正/负 ────────────────────────────┤
VAELoader(wan_2.1_vae) ──────────────────────────────────────────────────────────┤
LoadImage(起始图) ───────────────────────────────────────────────────────────────┴→ WanImageToVideo(480×480, 33帧)
                                                                                      → KSamplerAdvanced(Hi: 4步 0-2) 
                                                                                      → KSamplerAdvanced(Lo: 4步 2-4) 
                                                                                      → VAEDecode → CreateVideo(16fps) → SaveVideo
```

### 关键参数
| 参数 | 当前值 | 说明 |
|------|--------|------|
| shift (ModelSamplingSD3) | 5.0 | Lightning 用 5，标准用 8 |
| KSamplerAdvanced | 4-6 步, cfg 1.0, euler, simple | Hi 前段 add_noise / Lo 后段；日常 6 步，对比/求快 4 步 |
| cfg | **1.0-1.5 甜点** | 2.0+ 画面改动过大/过曝 |
| 分辨率 | 480×480（16 倍数）| 384² 更快但糊 |
| 帧数 | **41（4n+1）**| **5 秒标准配置 @ 8fps**（生成 ~24s；81帧@16fps 更流畅但 45s）| 17=1s / 33=2s / 49=3s / 81=5s@16fps |
| fps | **8** | 只影响播放速度；5 秒视频默认 8fps |

### 已生成结果（output/video/）
| 文件 | 内容 |
|------|------|
| alya768_i2v_33f_4step | Alya 768² 起始图 → I2V（2025-08-01 标准产物）|
| anima_i2v_480_33f | ANIMA 生成居中图 → I2V（管线验证 ✓）|
| newimg_kiss_480x480_17f | 基准：夜景居中图 + 飞吻（构图验证 ✓）|
| kiss_33f/49f × 4/6step | 2/3 秒视频步数对比 |
| cfg_cmp_10/20/30/40 | cfg 1.0-4.0 对比（2.0 开始改动大）|
| cfg2_10/12/15 | cfg 1.0/1.2/1.5 细对比（甜点区）|
| restest_512/768 | 分辨率测试成片 |

## 2. wan2.2_i2v_standard_multiaction.json — 标准模式多动作（20 步）

- 去 Lightning LoRA，20 步 cfg 3.5 shift 8（零下载）
- **实测**: 动作幅度大但仅开头单阶段（33/49 帧均如此）→ 多动作序列不可靠
- 已生成: multiaction_standard_33f_20step / 49f_20step

## 3. anima_t2i_test.json — ANIMA 生图（10 节点）

**任务**: 文生图 → 居中动漫图 → 作为 Wan2.2 I2V 起始图

### 加载配置（关键）
| 组件 | 节点 | 文件 | 要点 |
|------|------|------|------|
| 扩散模型 | UNETLoader | anima-base-v1.0.safetensors | weight_dtype default |
| 文本编码器 | CLIPLoader | qwen_3_06b_base.safetensors | **type=stable_diffusion**（非 qwen_image！）|
| VAE | VAELoader | qwen_image_vae.safetensors | 与 wan_2.1_vae 同结构 |
| 加速 | LoraLoaderModelOnly | anima-turbo-lora-v0.1.safetensors | strength 1.0 |

### 参数
- Base 30步 / cfg 4.5 / er_sde/simple（主体突出）；Turbo 12步 / cfg 1.0（快速）
- 输出 prefix: `anima/anima_base_30step`

## 4. anima_alya_768_t2i.json — Alya 角色 768²（I2V 标准起始图）

- alisa LoRA@1.0（触发词 `alisa mikhailovna kujou (roshidere)`），20步/euler/cfg4
- 768×768 → `output/anima/anima_alya_768_00001_.png` → `input/start/alya_768.png`
- 原 1024² 版 prompt 可从 `output/anima/anima_alya_20step_00001_.png` 的 PNG metadata（prompt 字段）恢复

## 5. krea2_t2i_test.json — KREA 2 生图（8 节点）

- UNETLoader krea2_turbo_fp8 / CLIPLoader type=krea2 (qwen3vl_4b_fp8_scaled) / qwen_image_vae
- 8 步 / cfg 1.0 / er_sde/simple → 输出 `krea/krea2_turbo_8step`
- KREA 版 Alya 768²: `krea/krea_alya_768_00001_.png`

## 6. anima_i2v_test.json — ANIMA→I2V 管线

- ANIMA 生图 → input/start/anima_1024.png → WanImageToVideo → Hi/Lo 双通道 4 步
- 已验证 ✓：主体全程居中（center≈167 稳定），帧间差异 22-31 有动作

## 7. wan2.1_i2v_480p.json — Wan2.1 对照（UI 格式）

- 20 步 ~3 分钟，Wan2.1 I2V fp8 + clip_vision（2.1 需要 clip_vision_output）
- 保留作对照用；`comfy_client.py` 内置构建此工作流

## 起始图档案（input/start/）
| 文件 | 内容 | 用途 |
|------|------|------|
| alya_768.png | Alya 768² | I2V 主角色起始图（原图即可，无需降分辨率）|
| aliya_1024.png | Alya 1024²（旧参考）| 备用 |
| anima_1024.png | ANIMA 通用 1024² | 管线测试 |
| night_street_2048.png | 夜景人物居中（原 renemoreno）| 构图基准 |
| resk_{512..1792}.png | 骑士图 5 档分辨率（实验产物）| 分辨率实验保留 |
| gen_2p_leftright / gen_3p_group / gen_2p_talk | ANIMA 自生成多人图 | 多人视频测试 |
| multi_a/b/c, knight, wechat | 用户上传图 | 用户素材 |

> **2025-08-01 修订：起始图直接用原图分辨率**（512→1792² 视频清晰度线性 +82%，不影响动作/耗时）

## 学习中的新管线（MCP 内置 packs）
- `artokun-flow`：角色动作/舞蹈迁移 — **已分析（2025-08-01）**：832×480/81帧/4步，需 WanVideoWrapper 生态（缺 Animate-14B ~16GB + 5 节点），成本高 → 降级方案优先 wan-longer-videos
- `wan-longer-videos`：视频拼接长片（同 GGUF 栈，适配成本低，待评估）
- `wan-pusa-extend`：Pusa 时序续写
- `krea2-combo`：KREA 两遍细化；`krea2-txt2img-json`：区域提示
- 每个 pack 含 workflow.json + manifest.yaml，可用 `comfyui_read_pack_workflow` 读取
- 详细分析见 [learning.md](learning.md)
