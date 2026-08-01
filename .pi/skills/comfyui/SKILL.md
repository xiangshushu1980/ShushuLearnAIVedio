---
name: comfyui
description: ComfyUI 项目操作手册 — Wan2.2 I2V Lightning 快速视频生成栈（GGUF Hi/Lo + 4步LoRA）、ANIMA/KREA 生图、MCP 工具用法、速度/质量参数经验、操作流程与踩坑记录。使用 ComfyUI 视频生成、工作流编辑、参数调优、agent 测试循环时加载。分册：references/params.md（参数经验）、references/workflows.md（工作流档案）、references/troubleshooting.md（踩坑）、references/learning.md（学习记录）。
---

# ComfyUI 项目手册

## 环境
- 服务器: http://127.0.0.1:8188（WSL2 mirror / RTX 4090 24GB / torch 2.13+cu130 / py3.13 / ComfyUI 0.29）
- 启动: `cd /home/sean/projects/ComfyUI && ./start.sh`，日志 `/tmp/comfyui_start.log`
- venv python: `./venv/bin/python`（非系统 python）
- MCP: pi-mcp-adapter + 项目级 `.mcp.json` → comfyui server（181 工具，mcp({search}) 按需发现）
- 目录: ComfyUI 本体在 `/home/sean/projects/ComfyUI`；工作流/文档/脚本在 `/home/sean/projects/comfy-ops`

## 模型栈（快速视频生成）
| 组件 | 文件 | 位置 |
|------|------|------|
| UNet High | Wan2.2-I2V-A14B-HighNoise-Q4_K_S.gguf | models/unet/ |
| UNet Low | Wan2.2-I2V-A14B-LowNoise-Q4_K_S.gguf | models/unet/ |
| Text encoder | umt5-xxl-encoder-Q5_K_S.gguf | models/text_encoders/ |
| LoRA ×2 | wan2.2_i2v_lightx2v_4steps_lora_v1_{high,low}_noise.safetensors | models/loras/ |
| VAE | wan_2.1_vae.safetensors | models/vae/ |
| ANIMA 生图 | anima-base-v1.0 + qwen_3_06b_base + qwen_image_vae | diffusion_models/ |
| KREA 2 生图 | krea2_turbo_fp8 + qwen3vl_4b_fp8_scaled + qwen_image_vae | diffusion_models/ |
| 角色 LoRA | alisa(Alya) / yuki(Yuki) / anima-highres / anima-turbo-v0.2 | models/loras/ |
| 抠图 | BiRefNetRMBG 节点（ComfyUI-RMBG，1038lab）+ BiRefNet_toonout | custom_nodes/ + models/RMBG/ |
| 超分 | 4x-ClearRealityV1 | models/upscale_models/ |
| 编辑(下载中) | Bernini-R 双 fp8（Wan2.2 renderer，重打光/重风格化/插主体）| diffusion_models/ |

- 图像编辑/超分安装细节与 Bernini 状态见 docs/06_extras_install.md

- Wan2.1 I2V fp8 模型也在（20 步 ~3 分钟，对照用）
- 聪明档：同一 GGUF 去掉 Lightning LoRA + 20 步 cfg 3.5 shift 8 = 原版模式（多动作可行，零下载）

## 测试工作流（comfy-ops/workflows/）
- `wan2.2_i2v_lightning_test.json`（API 格式 17 节点）— 主力快速视频
  - 结构：UnetLoaderGGUF×2 → ModelSamplingSD3(shift=5) → LoraLoaderModelOnly(Hi/Lo LoRA) → CLIPLoaderGGUF(umt5,wan) → CLIPTextEncode 正/负 → WanImageToVideo → KSamplerAdvanced(Hi: 0-2 add_noise) → KSamplerAdvanced(Lo: 2-4 no_add_noise) → VAEDecode → CreateVideo → SaveVideo
  - 起始图：`input/start/*.png`（语义命名，用原图分辨率直接跑，越大越清晰）
  - WanImageToVideo **不需要** clip_vision_output（Wan 2.2 I2V 内部处理，2.1 才需要）
- `anima_t2i_test.json` / `anima_alya_768_t2i.json`（ANIMA 生图，10 节点）
- `krea2_t2i_test.json`（KREA 生图，8 节点）
- 各工作流详细档案见 [references/workflows.md](references/workflows.md)

## 操作流程
1. 提交：`comfyui_enqueue_workflow`（API 格式）
2. 批量参数对比：`comfyui_submit_batch`（base workflow + sweep: `[{"steps":6,"filename_prefix":"video/x"}, ...]`，key 自动匹配所有含该 input 的节点）
3. 轮询：`curl http://127.0.0.1:8188/history/<prompt_id>`，解析 execution_start/success 时间戳算耗时
4. 查看：`http://localhost:8188/view?filename=<名>&subfolder=<子目录>&type=output`（Output 浏览器也行）
5. **文件名规范**：SaveVideo 的 filename_prefix 直接写内容标识（`video/动作_分辨率_帧数`），生成时命名，**绝不要事后重命名**
6. 验证工作流：`comfyui_validate_workflow`（graph health 检查）
7. 本地 CLI（bash 直连，无需 MCP）：`python3 run_workflow.py workflows/<文件>.json` 提交现成工作流；`python3 comfy_client.py "prompt" [--image 图] [--steps N]` 快速 Wan I2V 生成

## 资源分类规范（之后沿用）
- **output/ 生成物直接落子目录**：`anima/`(ANIMA 生图) `krea/`(KREA 生图) `compare/`(对比拼图) `video/`(视频) `img_anima|img_krea/`(题材测试集) `res_test/`(分辨率测试)
- **input/ 公用素材**：`start/`(I2V 公用起始图，语义命名如 alya_768.png) `test/`(测试素材)
- **SaveImage/SaveVideo 的 filename_prefix 直接带子目录**（如 `anima/xxx`、`video/xxx`），生成时命名绝不再 mv
- **LoadImage 的 image 参数支持子目录路径**（已验证 `start/alya_768.png` ✅）
- **移动文件后需重启 ComfyUI**：asset_seeder(prune_first=True) 自动软删除旧路径记录(is_missing=1)，API 层自动过滤

## 分册导航（按需加载）
- [params.md](references/params.md) — 参数经验全量：速度表、cfg 甜点、分辨率、多动作边界、帧数约束
- [workflows.md](references/workflows.md) — 工作流档案：每个工作流节点结构/用途/参数/已生成结果
- [troubleshooting.md](references/troubleshooting.md) — 踩坑全量：Assets/history/下载/token/队列
- [learning.md](references/learning.md) — 高质量来源管道 + 学习闭环 + 已学习案例记录
