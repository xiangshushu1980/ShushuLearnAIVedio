# 06 图像编辑/超分工具安装记录（2025-08-01 本会话新增）

> ⚠️ **经验迁移（2025-08-02）**：本文件的实测数据/踩坑实例/提炼认知已迁移至 **Mem0 共享记忆**（用 `memory_recall` 检索，如“Bernini 用什么采样器”“超分多快”）。本文件保留手册类内容（安装/模型/管线结构）；后续精简由文档维护会话统一处理，**经验类内容不再追加到这里**。

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
- **模型**（4090 实测，2025-08-02）：
  - **int8_convrot 版**（`wan2.2_bernini_r_{high,low}_noise_int8_convrot.safetensors`，各 14.54GB，✅ 已下载）——**视频任务甜点：比 fp8 快 21%（105s vs 133s/81帧）且画质无损**（清晰度 1023 vs 999，一致性持平）→ **默认用它**
  - fp8_scaled 版（`wan2.2_bernini_r_{high,low}_noise_fp8_scaled.safetensors`，各 15.57GB，✅ 已下载）：单帧图像编辑仍可用（int8 单帧因加载开销反而慢 18%），或作 int8 对比基线
  - int8 注意事项：int8_convrot 需 ComfyUI 0.29+（convrot 支持）；RTX 40 系是 int8 收益最大区间；Ampere/ROCm 有坑（与 4090 无关）

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

### Bernini 视频编辑 v2v（✅ 已测成功 2025-08-02）
```
LoadVideo(源视频, input/ 路径) → GetVideoComponents(拆帧) → BerniniConditioning(source_video=帧, length=41, 480²) → SamplerCustom×2 → CreateVideo(fps=8) → SaveVideo
```
- **结构**：与图像编辑同管线，源视频经 GetVideoComponents 拆帧注入 source_video
- **参数**：LoRA Hi=3.0/Lo=1.5、res_multistep、6步 split 3/3、cfg=1.0、length=帧数（41=5秒@8fps）
- **效果**：整段一致性重打光，动作保留（14.1→15.6），主体保持
- **产出**：`output/video/bernini_v2v_alya_golden_00001_.mp4`（Alya 金色时刻 5 秒）
- **工作流**：`workflows/video_bernini_r_v2v_test.json`
- **踩坑**：LoadVideo 只能读 input/ 下文件（不能用 output/ 路径）；SaveVideo 需显式 format/codec

### Bernini 深度研究（2025-08-02，官方仓库 bytedance/Bernini 分析 + 实测）

**任务类型**（由 BerniniConditioning 连了什么决定）：
| 任务 | 连接 | 用途 | 状态 |
|------|------|------|------|
| t2v | 什么都不连 | 纯文本→视频 | ✅ 但一致性弱 |
| v2v | source_video | 视频→视频编辑 | ✅ 保持好 |
| rv2v | source_video + reference_images | 视频编辑+参考图 | ✅ 脸部保真加强 |
| r2v | 只 reference_images | 参考图→视频 | ⚠️ 风格难保 |
| i2i | source_video(单帧) | 图像编辑 | ✅ 保持好 |
| ads2v | source_video + reference_video | 广告插入 | 未测 |

**核心发现：Bernini 是“编辑器”不是“生成器”**
- Wan2.2 I2V 是 **concat 硬锁**（第一帧噪声=0，必须重建）→ 脸部保真天然好
- Bernini 是 **in-context 软参考**（VAE 编码 token，模型“参考”但不锁定）→ 从静态图生成新内容会重绘细节（脸部漂移）
- 保真度排序：骑士 i2i（单帧小改）≈ v2v（有真实视频参考）> static2v（静态帧无运动）> r2v/t2v（自由生成）

**✅ 最终管线（已验证，推荐）**：`workflows/pipeline_wan22_bernini_golden.json`
```
参考图(任意风格) → Wan2.2 I2V（第一帧锁定，脸部/风格保真）→ Bernini v2v（编辑：重打光/风格化）→ RIFE补帧×3 → ClearReality超分×4
```
- 实测：Wan2.2 I2V 10s 视频 → Bernini 金色时刻编辑，脸部/动作/风格全保持，120s
- 耗时对比：v2v（120s）< static2v（230s）< rv2v 双参考（370s）——v2v 单参考 2 次 forward 最快

**static2v 技巧（单图伪装视频）**：`workflows/bernini_static2v_test.json`
- 单帧 → RepeatImageBatch×81 → source_video → 模型当“编辑目标”处理（风格保持二次元✅ 动作自然✅ 但脸部有漂移）

**rv2v 脸部保真**：`workflows/bernini_rv2v_face_test.json`
- source_video(静态帧) + reference_images(同图) 双参考 + 脸部细节提示词 + “换脸/变脸”负面词 → 脸部保持✅ 但慢（370s）

**官方参数**（gradio_demo.py，质量模式）：width=832 height=480（16:9 横屏）fps=16 max_image_size=624 40步 flow_shift=5.0 引导 APG（ComfyUI 无法完全复刻链式 APG，用 Turbo 6 步 + cfg1 + LoRA 3.0/1.5 替代）

**提示词技巧**（官方 testcase 案例）：
- 用 image0/image1 引用参考图（每张图独立 token）
- 结构：主体引用 → 外貌保持描述 → 场景 → 动作序列（start/then/after/throughout）→ 镜头固定+一致性保证
- 负面词加 photorealistic/3D render/different face/换脸（防写实漂移）

### Bernini 量化选型（int8 vs fp8，2025-08-02 实测）
- **int8_convrot 双模型**：`wan2.2_bernini_r_{high,low}_noise_int8_convrot.safetensors`（各 14.54GB）✅ 已下载（hf-mirror，约 18 分钟）
- **甜点**：视频任务 int8 快 21%（105s vs 133s/81帧）画质无损（清晰度 1023 vs 999）→ **默认用 int8**；图像单帧 int8 加载开销主导反而慢 18% → 单帧可留 fp8
- 需 ComfyUI 0.29+（convrot 支持）；RTX 40 系是 int8 收益最大区间；Ampere/ROCm 有坑（与 4090 无关）
- 对比图 `output/compare/bernini_fp8_vs_int8.png`；完整结论 `bernini_int8_findings.md`

### 10s 视频组合管线（2025-08-02 验证，时长匹配铁律）
**工作流**：`wan22_alya_10s_f16.json`（Wan2.2 161帧@16fps 832×480，280s）+ `bernini_v2v_10s_f16.json`（Bernini int8 编辑同帧率，1310s）
- ⚠️ **铁律：源视频时长必须 == Bernini 输出时长**（10s→10s 匹配则自然连贯；10s 压 5s 会脑补/步伐混乱）
- 效果：脸部/动作/风格全保持，清晰度 732→870（+19%），用户目视确认自然连贯
- ⚠️ **161帧@832×480 非线性爆炸**：1310s ≈ 81帧@480²（110s）的 12 倍——长序列成本非线性 + 显存压力
- **耗时预算**：5s 编辑 ≈ 110s；10s 编辑 ≈ 22 分钟（除非降分辨率 640×360 待测）
- 10s 产物：`output/video/wan22_alya_10s_f16_00001_.mp4` / `bernini_v2v_10s_f16_00001_.mp4`


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
