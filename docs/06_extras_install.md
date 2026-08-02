# 06 图像编辑/超分与 Bernini 手册（2025-08-02 精简版）

> ⚠️ **经验迁移**：本文件的实测数据/踩坑实例/提炼认知已迁至 **Mem0 共享记忆**（`memory_recall` 可检索，如"Bernini 用什么采样器""超分多快"）。本文件只留**手册类内容**（安装/模型/管线/参数/规则），经验类内容不再追加。

## 一、RMBG 抠图（✅ 可用）

- **节点**：`ComfyUI-RMBG`（仓库 `github.com/1038lab/ComfyUI-RMBG`——kijai 的仓库不存在）
- **模型**：`models/RMBG/BiRefNet/BiRefNet_toonout.safetensors`（884MB，hf-mirror）
- **依赖**：venv 需装 `onnxruntime-gpu` / `opencv-python-headless` / `timm`（缺 timm 报 `No module named 'timm'`）
- **使用**：MCP `remove_background` 工具（先 upload/stage 图片），或 `wan-transparent` pack 的 BiRefNetRMBG 节点

## 二、ClearReality 超分（✅ 可用）

- **模型**：`models/upscale_models/4x-ClearRealityV1.pth`（9MB，源 `hf-mirror.com/Aitrepreneur/FLX`）
- **使用**：MCP `upscale_image`（scale 2/4）；推荐"低清生成 → 补帧(RIFE) → 超分 → 1080p"流程

## 三、Bernini-R（编辑手册）

### 定位与模型
- **定位**：Wan2.2 renderer-only **编辑器**（重打光/重风格化/主体插入），in-context 软参考（非 concat 硬锁）→ 生成模式（r2v/t2v）脸部漂移，编辑模式（v2v/i2v）保持好
- **模型**（`models/diffusion_models/` + `models/loras/`）：
  - `wan2.2_bernini_r_{high,low}_noise_fp8_scaled.safetensors`（15.5GB×2，主力）
  - `wan2.2_bernini_r_{high,low}_noise_int8_convrot.safetensors`（14.5GB×2，视频任务快 21% 画质无损，需 ComfyUI 0.29+ convrot）
  - `lightx2v_T2V_14B_cfg_step_distill_v2_lora_rank64_bf16.safetensors`（蒸馏 LoRA）
- **text encoder**：必须完整 fp8 `umt5_xxl_fp8_e4m3fn_scaled`（**不能用 GGUF 版**）；VAE 用 `wan_2.1_vae`

### 工作流（comfy-ops/workflows/）
| 文件 | 任务 |
|------|------|
| `pipeline_wan22_bernini_golden.json` | **推荐主管线**：Wan2.2 I2V → Bernini v2v 编辑 → RIFE×3 → ClearReality×4 |
| `video_bernini_r_image_editing.json` | 图像编辑（官方模板）|
| `video_bernini_r_v2v_test.json` | v2v 视频编辑（已验证）|
| `bernini_static2v_test.json` | 单帧伪装视频技巧 |
| `bernini_rv2v_face_test.json` | 双参考脸部保真 |
| `bernini_int8_cfg10/15_fps16.json` | int8 对比 |

### 官方管线结构（图像 & v2v 通用）
```
CLIPLoader(umt5 fp8, wan) → CLIPTextEncode×2
UNETLoader(high) → LoRA(T2V distill, strength=3.0)
UNETLoader(low)  → LoRA(T2V distill, strength=1.5)
BerniniConditioning(positive, negative, vae, width, height, length, source_video=帧/图)
KSamplerSelect(res_multistep) + BasicScheduler(simple, 6步) + SplitSigmas(3/3)
SamplerCustom(high, add_noise=True, cfg=1.0) → SamplerCustom(low, add_noise=False) → VAEDecode
v2v 时：LoadVideo(input/路径) → GetVideoComponents 拆帧 → 注入 source_video → CreateVideo(fps=8) → SaveVideo(显式 format/codec)
```

### 关键参数
- LoRA Hi=3.0 / Lo=1.5；采样器 **res_multistep**；6 步 split 3/3；**cfg=1.0**
- 分辨率 16 倍数（928×1280、832×480）；帧数 4n+1（length=帧数，41=5秒@8fps）
- 官方质量参数（gradio_demo.py）：832×480/fps16/40步/flow_shift 5.0/APG——ComfyUI 用 Turbo 6 步替代

### 任务类型（BerniniConditioning 连接方式）
| 任务 | 连接 | 保真度 |
|------|------|--------|
| v2v | source_video | 高（真实视频参考）|
| i2i | source_video(单帧) | 高（单帧小改）|
| static2v | 单帧 RepeatImageBatch×N 伪装视频 | 中（风格保持、脸部漂移）|
| rv2v | source_video + reference_images | 高但慢（370s）|
| r2v/t2v | 仅 reference_images / 无 | 低（自由生成，脸部漂移）|

### 踩坑规则
1. **不能用 GGUF text encoder**（必须完整 fp8）
2. **不能用 euler 采样器**（必须 res_multistep）
3. **不能走 img2img VAEEncode 半程去噪**（会花屏）——必须 BerniniConditioning in-context 注入从头采样
4. **WanImageToVideo 不适合**（那是 I2V concat 条件）
5. LoadVideo 只能读 `input/` 下文件；SaveVideo 需显式 format/codec

### 提示词技巧
- image0/image1 引用参考图（每图独立 token）；结构：主体引用 → 外貌保持 → 场景 → 动作序列（start/then/after/throughout）→ 镜头固定
- 负面词加 photorealistic / 3D render / different face / 换脸（防写实漂移）

### int8 vs fp8 对比（2025-08-02）
- 视频任务（81帧）：int8 105.1s/清晰度1023 vs fp8 133.1s/999 → **int8 快21% 略优**；单帧图像 int8 反而慢（加载开销）
- 同 seed 像素差异均值 2.08 → 画质几乎一致；int8 省 1GB 显存
- 详见 `.pi/skills/comfyui/references/params.md`

## 四、MCP 工具状态

| 工具 | 状态 |
|---|---|
| `remove_background` / `upscale_image` | ✅ 可用 |
| `generate_with_ip_adapter` | ❌ 缺 ComfyUI_IPAdapter_plus 节点 |
| train_* | ❌ 需 docker-GPU + HF_TOKEN |
| RunPod / 云端 API | ❌ 不用（用户排除云）|

- ✅ ComfyUI-Manager 已更新（2026-07-30，behind=3），Manager API 可用（`/customnode/installed` 正常响应）；Manager 界面的 node conflict 红标是静态比对噪音（线上仓库声明表互相比对，非本地安装冲突），本地已装扩展 AST 扫描 0 同名冲突，可无视
- ⚠️ CivitAI token 有效但 MCP `download_civitai_model` 不可用 → 用 curl 绕行

## 五、网络（用户权威配置）

- **Clash Rule 模式 + TUN 接管**（无 system proxy）：GitHub 走代理节点、国内直连；默认直连即可，`-x http://127.0.0.1:7890` 仅作失败兜底
- git 报 "could not read Username" = 认证问题，不是网络被墙
- **遇到网络异常，第一时间与用户确认和测试，不擅自改配置**
- HF 下载用 hf-mirror.com；pip 用清华源
