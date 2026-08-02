# 06 图像编辑/超分工具安装记录（2025-08-01 本会话新增）

> 本文件记录 ComfyUI 图像处理能力的补装（RMBG 抠图 + ClearReality 超分）与 Bernini-R 安装状态。
> 由独立会话维护，避免与 05 交接/SKILL 重构写冲突。

## 一、RMBG 抠图（✅ 已装可用）

- **节点**：`ComfyUI-RMBG`（仓库 `github.com/1038lab/ComfyUI-RMBG`，不是 kijai 的！kijai 仓库不存在）
- **模型**：`models/RMBG/BiRefNet/BiRefNet_toonout.safetensors`（884MB，hf-mirror 源）
- **依赖**：venv 补装 `onnxruntime-gpu` / `opencv-python-headless` / `timm`（timm 缺失会报 `No module named 'timm'`）
- **验证**：`comfyui_remove_background` 实测成功 → `output/ComfyUI_cutout_00001_.png`（768² RGBA，背景 68% 全透明、四角干净、中心主体 97.8% 保留）
- **使用**：`remove_background` 工具（先 upload/stage 图片）或 `wan-transparent` pack 的 BiRefNetRMBG 节点（透明背景动画）
- ⚠️ 装节点用 git clone 需走代理：`git clone -c http.proxy=http://127.0.0.1:7890 ...`（GitHub git 端点直连被墙）

## 二、ClearReality 超分（✅ 已装可用）

- **模型**：`models/upscale_models/4x-ClearRealityV1.pth`（9MB，源 `hf-mirror.com/Aitrepreneur/FLX/resolve/main/4x-ClearRealityV1.pth`，comfyui-mcp wan-longer pack 同款）
- **验证**：`comfyui_upscale_image` 实测 768²→3072²（4x，3.3s）
- **用法**：`upscale_image` 工具（scale 2/4），或视频 480/720p 生成 → 超分 → 1080p 成品
- 配合 RIFE 补帧（Frame-Interpolation 节点已装）：生成低帧数 → 补帧提流畅 → 超分提分辨率

## 三、Bernini-R（⏳ 下载中，由另一 Agent 负责测试）

- **定位**：ByteDance 的 Wan 2.2 renderer-only 编辑模型（重打光/重风格化/主体插入/多任务 t2v/v2v/rv2v/r2v/img/ads2v），非 Wan2.1 替代品
- **模型**（fp8_scaled 版，4090 推荐）：
  - `diffusion_models/wan2.2_bernini_r_high_noise_fp8_scaled.safetensors`（~15.5GB，✅ 已完整）
  - `diffusion_models/wan2.2_bernini_r_low_noise_fp8_scaled.safetensors`（~15.5GB，下载中）
  - `loras/lightx2v_T2V_14B_cfg_step_distill_v2_lora_rank64_bf16.safetensors`（✅ 已下 13:51，630MB）
  - 源：`hf-mirror.com/Comfy-Org/Bernini-R`；text encoder 用现有 `umt5_xxl_fp8_e4m3fn_scaled.safetensors`（✅ 已有，注意**不是 GGUF 版**）；VAE 用现有 `wan_2.1_vae`
- **workflow 模板**：`comfy-ops/workflows/video_bernini_r_{image_editing,video_editing}.json`（UI 格式，Comfy-Org 官方）；**可用 API 版：`comfy-ops/workflows/video_bernini_r_test.json`**（官方子图反编译，已验证）
- **节点**：用 ComfyUI 0.29 内置节点（**BerniniConditioning** + SamplerCustom×2 + SplitSigmas + KSamplerSelect(res_multistep)）
- **推荐工作流**：Wan2.2 生成 → Bernini 编辑；可编辑任意来源视频（含 Wan2.1/云端，需符合 Wan 帧数 4n+1/分辨率 16 倍数）
- **✅ 测试完成（2025-08-01）**：图像编辑（重打光）实测成功，官方管线 `official_relight_00001_.png`（928×1280）效果优秀，用户满意

### Bernini 图像编辑官方管线（API 版，已验证）
```
CLIPLoader(umt5_xxl_fp8_e4m3fn_scaled, wan) → CLIPTextEncode×2
UNETLoader(high_noise fp8) → LoRA(T2V distill, strength=3.0)
UNETLoader(low_noise fp8) → LoRA(T2V distill, strength=1.5)
BerniniConditioning(positive, negative, vae, width=928, height=1280, length=1, source_video=缩放图) → positive/negative/latent
KSamplerSelect(res_multistep) + BasicScheduler(simple, 6步) + SplitSigmas(3/3)
SamplerCustom(high, add_noise=True, cfg=1.0) → SamplerCustom(low, add_noise=False) → VAEDecode → SaveImage
```
- **关键参数**：LoRA Hi=3.0 / Lo=1.5（官方 Turbo）；采样器 `res_multistep`；6 步 split 3/3；cfg=1.0；length=1（单帧图像）；分辨率 16 倍数（928×1280）
- **踩坑**：① 不能用 GGUF text encoder（Q5_K_S），必须完整 fp8（`umt5_xxl_fp8_e4m3fn_scaled`，6.7GB）② 不能用 euler 采样器（官方用 res_multistep）③ 不能走 img2img VAEEncode 半程去噪（会“花”）；必须 BerniniConditioning in-context 注入从头采样 ④ WanImageToVideo 不适合（那是 I2V concat 条件，Bernini 需 BerniniConditioning）
- **产出**：`output/img_bernini/official_relight_00001_.png`（928×1280 重打光）

## 四、MCP 工具可用性更新（本会话盘点结论）

| 工具 | 之前 | 现在 |
|---|---|---|
| `remove_background` | ❌ 缺 RMBG | ✅ 可用 |
| `upscale_image` | ❌ upscale_models 空 | ✅ 可用 |
| `generate_with_ip_adapter` | ❌ 缺节点 | ❌ 仍缺 ComfyUI_IPAdapter_plus |
| `generate_with_controlnet` | ❌ 缺模型 | ❌ 仍缺（通用 controlnet 对视频帮助有限，跳过）|
| 训练 train_* | ❌ docker 无 GPU + 镜像未建 + HF_TOKEN 未设 | ❌ 仍不可用 |
| RunPod / 云端 API 节点 | ❌ 无账号 | ❌ 不用（用户排除云）|

- ⚠️ ComfyUI-Manager 是旧 3.x：comfyui-mcp 的 Manager API 操作（install_custom_node / Manager 下载）不可用 → 装节点用 git clone（走代理）或手动
- ⚠️ Civitai token 有效（curl 带 token 307 / 不带 401），但 MCP `download_civitai_model` 因缺 COMFYUI_PATH + Manager 3.x 不可用 → 下载用 curl 绕行（见 SKILL troubleshooting）

## 五、网络/代理备忘（用户权威配置，2025-08-01 修订）

- **Clash Rule 模式 + TUN 接管**：无 system proxy（无 http_proxy 环境变量），流量被 TUN 透明接管后按规则分流——**GitHub 走代理节点、国内直连**
- **curl/git 默认直连即可**（TUN 接管后自动按规则分流，实测 codeload/raw 直连 200）；显式 `-x http://127.0.0.1:7890`（Clash 端口，WSL2 mirror 下可达）仅在 DNS 污染/节点抖动时作**失败兜底**
- **git 报 "could not read Username" = 认证问题**（仓库不存在/无权限），不是网络被墙
- **遇到无法访问的问题，第一时间与用户确认和测试，不要擅自改配置/反复重试**（网络配置以用户为准）
- HF 模型下载：`hf-mirror.com` 直连可用（不用代理）；pip：清华源 `https://pypi.tuna.tsinghua.edu.cn/simple`
