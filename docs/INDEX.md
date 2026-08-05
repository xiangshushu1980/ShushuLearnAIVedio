# ComfyUI 项目文档索引

> 本机环境：Ubuntu 24.04 (WSL2, mirror 网络模式) / RTX 4090 24GB / Python 3.13 / CUDA 13
> 最后更新：2026-08-05

## 📚 文档导航（按需加载）

| 文档 | 用途 | 何时加载 |
|------|------|----------|
| [01_environment.md](01_environment.md) | 环境/启动/维护/API/客户端（01+03 合并） | 环境出问题 / 重启服务 / 脚本化调用 |
| [02_models.md](02_models.md) | 已下载模型清单（含 RMBG/ClearReality/Bernini/H3）、下载源、显存参考 | 下新模型 / 下载慢 / 查模型 |
| [04_bernini_int8_findings.md](04_bernini_int8_findings.md) | Bernini int8 调研/下载/实测快照（结果已同步 06 + Mem0） | 查 int8 来龙去脉/下载源时 |
| [05_session_handoff.md](05_session_handoff.md) | ~~会话交接~~ **已归档**（2026-08-05 起状态迁移至 mem0 [STATE] + `.pi/agents/` progress，git 历史可查） | 新会话开场按 AGENTS.md 流程（progress → INDEX → recall [STATE]） |
| [06_extras_install.md](06_extras_install.md) | 图像编辑/超分/Bernini 手册（经验已迁 Mem0） | 涉及这些能力时加载 |
| [07_video_material.md](07_video_material.md) | 视频素材库索引（Pexels 原片/Bernini 预处理版/命名规则） | 找 v2v 编辑素材 / 素材管线 |
| [08_h3_prompt_agent.md](08_h3_prompt_agent.md) | H3 提示词增强方案（官方六段式 + 自建智能体） | 提示词智能体落地时 |
| [09_h3_test_plan.md](09_h3_test_plan.md) | H3 系统化测试全量数据（速度矩阵/steps/提示词/量化/MC） | 查 H3 实测数据 / 参数定论依据 |
| [10_h3_batch_optimization.md](10_h3_batch_optimization.md) | H3 fl2va 机制/TE 加载成本/缓存/两阶段批量方案 | 批量优化 / 理解 80s TE 开销 |
| [11_h3_case_library.md](11_h3_case_library.md) | H3 提示词案例库（A-G 分组 + 目视反馈） | 写提示词参考案例时 |

> agent 操作手册（模型栈/参数/踩坑/工作流档案）在 `.pi/skills/comfyui/SKILL.md` 及其 `references/` 分册；共享记忆/经验检索在 Mem0（`memory_recall`）。

## 🔑 快速速览

### 启动 ComfyUI
```bash
cd /home/sean/projects/ComfyUI
./start.sh          # 后台: nohup ./start.sh > /tmp/comfyui_start.log 2>&1 &
```
界面: http://localhost:8188 （WSL mirror 模式下 Windows 浏览器可直接访问）

### 模型栈（全部就位）
- **视频（快速）**：MiniMax H3（fl2va/ref2va int8 + qwen3vl-32B nvfp4_awq TE + 双 VAE）— 1024×576×20步 ≈ 5min/条，受提示词控制
- **视频（老栈）**：Wan2.2 I2V Lightning — GGUF Hi/Lo Q4_K_S + lightx2v 4步 LoRA（480²×33帧 ≈ 10-16s）
- **图像编辑**：Bernini-R int8_convrot（v2v 快 21% 画质无损）+ Wan2.1 I2V fp8（对照）
- **生图**：ANIMA（动漫线稿/高饱和）+ KREA 2 turbo（平滑/写实）+ Alya/Yuki LoRA
- 完整清单与下载源见 [02_models.md](02_models.md)

### 主力工作流
- `workflows/minimax_h3_i2v_api.json` / `minimax_h3_t2v_api.json` — H3 图/文生视频（当前主力）
- `workflows/wan2.2_i2v_lightning_test.json` — Wan2.2 图生视频（480²×33帧×4步，~14s/次）
- `workflows/anima_alya_768_t2i.json` — Alya 角色 768² 起始图（I2V 标准）
- `workflows/video_bernini_r_v2v_test.json` — Bernini v2v 编辑（int8 已切默认）

### 资源规范（2025-08-01 起沿用）
- `output/` 按模型/用途分子目录：anima / krea / compare / video / review / img_* / res_test
- `input/start/` 公用 I2V 起始图（语义命名，用原图分辨率直接跑）；`input/test/` 测试素材；`input/material(_b)/` v2v 素材（见 07）
- SaveImage/SaveVideo 的 filename_prefix 直接带子目录，生成即落位

## 📁 目录结构

```
/home/sean/projects/ComfyUI/          # ComfyUI 本体
├── main.py / start.sh                # 入口与启动（--enable-assets --use-sage-attention 已固化）
├── models/                           # 模型（unet/diffusion_models/text_encoders/vae/loras...）
├── custom_nodes/                     # 自定义节点（Manager、browser、GGUF、WanVideoWrapper 等 8 个）
├── input/                            # 输入（start/ 公用起始图，test/ 测试，material(_b)/ v2v 素材）
├── output/                           # 生成结果（anima/ krea/ compare/ video/ review/ img_*/ res_test/）
└── user/                             # 用户数据（workflows/ comfyui.db assets 索引）

/home/sean/projects/comfy-ops/        # 本项目（工作流/文档/脚本）
├── docs/                             # 本文档体系（01-11）
├── workflows/                        # 工作流 JSON（API 格式）
├── .pi/skills/comfyui/               # agent 手册（SKILL.md + references/ 分册）
├── run_workflow.py                   # 工作流运行脚本
└── comfy_client.py                   # API 客户端示例
```
