---
name: comfyui
description: ComfyUI 项目操作手册 — Wan2.2 I2V Lightning 快速视频栈、ANIMA/KREA 生图、MCP 工具用法、参数经验与踩坑。做 ComfyUI 视频生成/工作流编辑/参数调优时加载。分册：nodes/params/workflows/troubleshooting/learning 见 references/。
---

# ComfyUI 项目手册

## 环境
- 服务器: http://127.0.0.1:8188（WSL2 mirror / RTX 4090 24GB / torch 2.13+cu130 / py3.13 / ComfyUI 0.32.0，2026-08-12 更新）
- 启动: `cd /home/sean/projects/ComfyUI && ./start.sh`，日志 `/tmp/comfyui_start.log`
- venv python: `./venv/bin/python`（非系统 python）
- MCP: pi-mcp-adapter + 项目级 `.mcp.json` → comfyui server（comfyui-mcp v0.48+，181 工具，mcp({search}) 按需发现）
- comfy-cli: **1.13.0 已装进 ComfyUI 工作区 venv**（`/home/sean/projects/ComfyUI/venv/bin/comfy`），解锁 MCP 内 8 个 `comfy_cli_*` 桥接工具（status/server/jobs/search_nodes/workflow/transfer/models/skills）；comfyui-mcp 探测顺序 PATH → COMFY_CLI_PATH → 工作区 `.venv`/`venv`，装在 venv 里最稳（不依赖 spawn env）
- 目录: ComfyUI 本体在 `/home/sean/projects/ComfyUI`；工作流/文档/脚本在 `/home/sean/projects/comfy-ops`

## 模型栈（2026-08-12 盘点后实况；完整清单见 docs/02_models.md）

**主力 = MiniMax H3 视频生成**（FL2VA/Ref2VA + Qwen3-VL-32B TE + H3 双 VAE + turbo LoRA 系列；成片档 v4-600EMA 8步@1024）
| 组件 | 文件 | 位置 |
|------|------|------|
| H3 扩散 | minimax_h3_{fl2va|ref2va}_pruned_{fp8_scaled|int8_convrot} | diffusion_models/ |
| H3 TE | qwen3vl_32b_minimax_h3_nvfp4_awq | text_encoders/ |
| H3 VAE | minimax_h3_{video,audio}_vae | vae/ |
| H3 LoRA | minimax_h3_turbo_v4_step600_ema（成片档）等 6 个 | loras/ |
| ANIMA 生图 | anima-base-v1.0 + qwen_3_06b_base + qwen_image_vae | diffusion_models/ |
| KREA 2 生图 | krea2_turbo_fp8 + qwen3vl_4b_fp8_scaled + qwen_image_vae | diffusion_models/ |
| ACE 生图 | acestep_v1.5_xl_turbo + qwen_{0.6b,4b}_ace15 + ace_1.5_vae | diffusion_models/ + text_encoders/ + vae/ |
| 角色 LoRA | alisa(Alya)×3 / yuki_suou_v1120706 / anima-highres / anima-turbo-v0.2 | models/loras/ |
| 抠图 | BiRefNetRMBG 节点（ComfyUI-RMBG，1038lab）+ BiRefNet_toonout | custom_nodes/ + models/RMBG/ |
| 超分 | 4x-ClearRealityV1 | models/upscale_models/ |
| 编辑 ⚠️ | **Bernini-R 模型缺失**（2026-08-12 盘点确认磁盘无 int8/fp8/蒸馏 LoRA/umt5 TE；待确认或重下，指引 docs/02）| diffusion_models/ |

- ~~Wan2.2 GGUF 快速栈~~ **已整体清理（用户确认 2026-08-12 有意清理）**：unet GGUF×2、umt5 GGUF、lightx2v LoRA×2 全部删除；`wan_2.1_vae` 已补回（243MB，兜底保留）

- 图像编辑/超分安装细节与 Bernini 官方管线见 docs/06_extras_install.md
- ⚠️ **Bernini 时长铁律**：源视频时长必须 == 输出时长（10s→5s 会脑补/步伐乱）；cfg 用 1.0 最稳；fps16 官方默认

- ~~Wan2.1/Wan2.2 视频栈~~ **已全部清理（用户确认 2026-08-12 有意清理）**：Wan2.2 GGUF 快速栈 + Wan2.1 fp8 对照栈 + Bernini 配套模型均删除（含 umt5_xxl_fp8 TE，Bernini 必需）

## 测试工作流（comfy-ops/workflows/）
- **H3 系列（主力）**：`minimax_h3_i2v.json` / `minimax_h3_t2v.json` / `minimax_h3_r2v.json` / `minimax_h3_ref2va_img_vid_api.json`（Ref2VA 全链路）/ `h3v1_r2_audio_only.json` / `minimax_h3_t2v_api_nobgm_test.json` 等
- `anima_t2i_test.json` / `anima_alya_768_t2i.json`（ANIMA 生图，10 节点）
- `krea2_t2i_test.json`（KREA 生图，8 节点）
- ~~`wan2.2_i2v_lightning_test.json`~~ **不可用**（模型已清，2026-08-12）；`wan2.1*`/`wan2.2*`/`bernini*`/`pipeline_wan22_*` 同
- 各工作流详细档案见 [references/workflows.md](references/workflows.md)

## 操作流程
1. 提交：`comfyui_enqueue_workflow`（API 格式）
2. 批量参数对比：`comfyui_submit_batch`（base workflow + sweep: `[{"steps":6,"filename_prefix":"video/x"}, ...]`，key 自动匹配所有含该 input 的节点）
3. 轮询：`curl http://127.0.0.1:8188/history/<prompt_id>`，解析 execution_start/success 时间戳算耗时
4. 查看：`http://localhost:8188/view?filename=<名>&subfolder=<子目录>&type=output`（Output 浏览器也行）
5. **文件名规范**：SaveVideo 的 filename_prefix 直接写内容标识（`video/动作_分辨率_帧数`），生成时命名，**绝不要事后重命名**
6. 验证工作流：`comfyui_validate_workflow`（graph health 检查）
7. 本地 CLI（bash 直连，无需 MCP）：`python3 run_workflow.py workflows/<文件>.json` 提交现成工作流；~~`python3 comfy_client.py`~~ 已过时（Wan2.1 式工作流，模型已清，勿用）

## 资源分类规范（之后沿用）
- **output/ 生成物直接落子目录**：`anima/`(ANIMA 生图) `krea/`(KREA 生图) `compare/`(对比拼图) `video/`(视频) `img_anima|img_krea/`(题材测试集) `res_test/`(分辨率测试)
- **input/ 公用素材**：`start/`(I2V 公用起始图，语义命名如 alya_768.png) `test/`(测试素材)
- **SaveImage/SaveVideo 的 filename_prefix 直接带子目录**（如 `anima/xxx`、`video/xxx`），生成时命名绝不再 mv
- **LoadImage 的 image 参数支持子目录路径**（已验证 `start/alya_768.png` ✅）
- **移动文件后需重启 ComfyUI**：asset_seeder(prune_first=True) 自动软删除旧路径记录(is_missing=1)，API 层自动过滤

## 分册导航（按需加载）
- [nodes.md](references/nodes.md) — 节点速查：用过的节点语义/关键参数/官方与社区推荐（含出处理由）/本地实测；**搭新工作流先查本表**
- [params.md](references/params.md) — 参数经验全量：速度表、cfg 甜点、分辨率、多动作边界、帧数约束（官方/社区/本地实测分层标注）
- [workflows.md](references/workflows.md) — 工作流档案：每个工作流节点结构/用途/参数/已生成结果
- [troubleshooting.md](references/troubleshooting.md) — 踩坑全量：Assets/history/下载/token/队列
- [learning.md](references/learning.md) — 高质量来源管道 + 学习闭环（含**新节点落地流程**）+ 已学习案例记录
