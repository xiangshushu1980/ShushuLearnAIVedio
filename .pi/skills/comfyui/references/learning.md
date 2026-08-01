# 学习记录（高质量工作流来源 + 学习闭环）

> 本册记录：① 高质量工作流从哪来、如何把关 ② 学习如何落地 ③ 已学习案例。
> 原则：**官方示例 + MCP 内置 packs 是"可信基线"**（有维护者背书），社区来源必须过质量门禁。

## 1. 高质量工作流来源（三层）

| 层级 | 来源 | 质量特征 | 使用方式 |
|------|------|---------|---------|
| 官方/核心开发者 | Comfy-Org example_workflows（GitHub）、官方 blueprints/（本地 80+）、官方 templates（本地 506）、kijai（WanVideoWrapper）、city96 | 与模型同步更新、参数已验证 | 直接拉取，本地已缓存模板 |
| 社区策展 | CivitAI 高赞工作流（token 已配）、comfyui-browser Sources（Git 订阅）、MCP list_packs（56 个专家包）| 有评分/使用量背书 | 按需订阅，实跑验证 |
| 自研沉淀 | 我们实测调优过的工作流（anima_alya_768、wan2.2_lightning）| 有本机实测数据 | 逐步成为主力 |

### MCP 内置 56 个 packs（重要资源）
- 位置：`~/.npm/_npx/*/node_modules/comfyui-mcp/packs/<name>/`（workflow.json + manifest.yaml + pack.yaml）
- 与本机栈相关：`artokun-flow`（角色动作迁移）、`wan-longer-videos*`（长视频）、`wan-pusa-extend`（续写）、`wan-animate*`（v2v）、`wan-multitalk`（对口型）、`krea2-*`、`anima-*`
- 另有 35 个 plugin/skills 主题文档（comfyui-core / troubleshooting / prompt-engineering / workflow-layout 等）

## 2. 质量门禁（每个新拉取工作流过四关）
1. `comfyui_validate_workflow` — graph health 检查
2. `comfyui_check_workflow_runtime` — 模型/节点兼容性
3. 与本机栈对比 — 模型文件名、LoRA、分辨率/帧数约束（16 倍数 / 4n+1）
4. **实跑一次 + 量化验证** — PIL 分析（清晰度/中心比/饱和度/帧差），或用户目视确认

## 3. 学习闭环（拉取 → 沉淀）
```
拉取 → analyze 结构（comfyui_analyze_workflow / visualize）→ 适配本机栈 → 实跑 → 量化对比
        ├─ workflows/适配版.json（资产）
        ├─ workflows.md（节点结构/参数档案）
        └─ 踩坑/结论 → troubleshooting.md 或 params.md
```
- 文档三层分工：`docs/`=环境事实（不常变）；`SKILL` 主体+references=操作经验（高频）；`workflows/`=案例资产（可复用）
- 本册 learning.md = 来源管道 + 案例记录

## 4. 已学习案例

### Wan2.1 Fun Camera（2025-08-01 验证通路）
- 来源：Comfy-Org example_workflows（官方）`video/wan/fun-camera/v1.1/wan2.1_fun_camera_14B.json`
- 结构：15 节点，新增 `WanCameraImageToVideo` + `WanCameraEmbedding`（相机运镜控制：Zoom/Pan/Tilt 等 10+ 预设 + fx/fy 焦距参数）
- 拉取验证：✅ 完整解析 + 校验（仅提示缺模型 `wan2.1_fun_camera_v1.1_14B_bf16.safetensors`）
- 与本机栈差异：需下载 fun_camera 专用模型（~30GB），暂未适配
- 参考价值：Wan 系相机控制工作流的范例；若将来需要"推拉摇移"运镜，这是模板

### artokun-flow 深度分析（2025-08-01 学习闭环示范）

**定位**: 角色动作/舞蹈迁移（v2v）— 交接文档点名的多动作问题潜在解

**结构**（19 顶层节点 + 7 子图）:
```
VHS_LoadVideo(驱动视频, 30fps) ─┐
LoadImage×3(角色多视角 ref) ────┤→ PREPROCESS(pose检测+clip-vision+uni3c+text-embeds)
                                 │    → WanVideoAnimateEmbeds(832×480, 81帧)
                                 │    → WanVideoSampler(4步,cfg5,shift42,dpm++_sde)
                                 │    → DECODE·COLOR → TSVideoCombine(30fps)
```

**关键参数**: 832×480 / 81帧 / 4步 / cfg 5 / shift 42 / dpm++_sde / 驱动视频 30fps（frame_load_cap 81）
**LoRA 栈**: light@1.0 + wan.reworked@0.3 + WanPusa@0.9 + WanFun.reworked@0.5
**双模式**（REPLACEMENT MODE 子图）:
- OFF（默认）: 全角色动画 — 角色+背景跟随驱动视频动作（"让角色跳这支舞"）
- ON: 换脸到真实视频 — SAM3 分割驱动视频人物，角色画入遮罩区（保持真实背景/光照）
**增强链**: ReActor 首帧身份锁定 + TSColorMatch 调色 + 可选 Upscale4x-RIFE-1080p（SeedVR2+RIFE）

**可行性评估**:
- ✅ 与本机栈共享: umt5_xxl 编码器、clip_vision_h、wan VAE（wan_2.1_vae 同源替代）
- ❌ 缺核心: ComfyUI-WanVideoWrapper（未装）+ Wan2.2-Animate-14B fp8（~16GB）
- ❌ 缺辅助: Uni3C controlnet / SAM3 / ViTPose+YOLO onnx / ReActor / RIFE / SeedVR2（可选）
- 💰 成本: ~30GB 模型 + 5+ 个新自定义节点（WanVideoWrapper 需 SageAttention/Triton）
- ⏱️ 单次推理: 81帧@832×480 预计 1-3 分钟（4步蒸馏 + 双模型）

**结论**: artokun-flow 能解决多动作（驱动视频自带动作），但生态独立（WanVideoWrapper 体系），安装成本高。**建议降级方案优先**: wan-longer-videos（同 GGUF 栈，适配成本低，长视频拼接实现多动作）→ 先评估此路线，artokun-flow 作为进阶预留。

### MCP packs 分析（2025-08-01 摸底）
- `artokun-flow`：人物舞蹈/动作迁移 — **多动作问题的潜在解**（交接文档点名），需 24GB+，未测
- `wan-longer-videos-i2v`：GGUF 双 UNet + extend 链拼接长片 — 与现有栈同模型系，适配成本低

## 5. 待学习（按优先级）
1. ~~artokun-flow 工作流结构~~ ✅ 已完成分析（见上）：缺 WanVideoWrapper 生态，成本高，**建议降级到 wan-longer-videos**
2. wan-longer-videos-i2v 结构（同 GGUF 栈，适配成本低）→ 评估多动作可行性
3. CivitAI 高赞 Wan 工作流 1-2 个（练质量门禁流程）
4. 官方 templates 里 `api_wan_image_to_video.json` 与现有 lightning 版对比
