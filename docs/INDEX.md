# ComfyUI 项目文档索引

> 本机环境：Ubuntu 24.04 (WSL2, mirror 网络模式) / RTX 4090 24GB / Python 3.13 / CUDA 13
> 最后更新：2025-08-01

## 📚 文档导航（按需加载）

| 文档 | 用途 | 何时加载 |
|------|------|----------|
| [01_install.md](01_install.md) | 安装、启动、目录结构 | 环境出问题 / 需要重启服务 |
| [02_models.md](02_models.md) | 已下载模型清单、下载源、网络加速经验 | 需要下新模型 / 下载慢 |
| [03_api.md](03_api.md) | API 客户端用法、自动化调用 | 做远程服务 / 脚本化调用 |
| [04_workflows.md](04_workflows.md) | 工作流索引、主力工作流速览 | 编辑/运行工作流 |
| [05_session_handoff.md](05_session_handoff.md) | 会话交接（2025-08-01）：环境状态/成果/待办 | 新对话起点，无缝续接 |
| [06_extras_install.md](06_extras_install.md) | 图像编辑/超分工具安装（RMBG/ClearReality）+ Bernini-R 状态 | 涉及这些能力时加载 |

> agent 操作手册（参数/踩坑/工作流档案/学习记录）在 `.pi/skills/comfyui/SKILL.md` 及其 `references/` 分册。

## 🔑 快速速览

### 启动 ComfyUI
```bash
cd /home/sean/projects/ComfyUI
./start.sh          # 后台: nohup ./start.sh > /tmp/comfyui_start.log 2>&1 &
```
界面: http://localhost:8188 （WSL mirror 模式下 Windows 浏览器可直接访问）

### 模型栈（全部就位）
- **视频**：Wan2.2 I2V Lightning — GGUF Hi/Lo Q4_K_S + lightx2v 4步 LoRA（480²×33帧 ≈ 10-16s）
- **生图**：ANIMA（动漫线稿/高饱和）+ KREA 2 turbo（平滑/写实）
- **角色**：Alya(alisa) / Yuki(yuki) LoRA + ANIMA 高清/加速 LoRA
- 对照：Wan2.1 I2V fp8（20 步 ~3 分钟）
- 完整清单与下载源见 [02_models.md](02_models.md)

### 主力工作流
- `workflows/wan2.2_i2v_lightning_test.json` — Wan2.2 图生视频（480²×33帧×4步，~14s/次）
- `workflows/anima_alya_768_t2i.json` — Alya 角色 768² 起始图（I2V 标准）
- `workflows/anima_t2i_test.json` / `krea2_t2i_test.json` — ANIMA/KREA 生图

### 资源规范（2025-08-01 起沿用）
- `output/` 按模型/用途分子目录：anima / krea / compare / video / img_* / res_test
- `input/start/` 公用 I2V 起始图（语义命名，用原图分辨率直接跑）；`input/test/` 测试素材
- SaveImage/SaveVideo 的 filename_prefix 直接带子目录，生成即落位

## 📁 目录结构

```
/home/sean/projects/ComfyUI/          # ComfyUI 本体
├── main.py / start.sh                # 入口与启动（--enable-assets 已固化）
├── models/                           # 模型（unet/diffusion_models/text_encoders/vae/loras...）
├── custom_nodes/                     # 自定义节点（Manager、browser、GGUF、WanVideoWrapper 等 8 个）
├── input/                            # 输入（start/ 公用起始图，test/ 测试）
├── output/                           # 生成结果（anima/ krea/ compare/ video/ img_*/ res_test/）
└── user/                             # 用户数据（workflows/ comfyui.db assets 索引）

/home/sean/projects/comfy-ops/        # 本项目（工作流/文档/脚本）
├── docs/                             # 本文档体系
├── workflows/                        # 工作流 JSON（API 格式）
├── .pi/skills/comfyui/               # agent 手册（SKILL.md + references/ 分册）
├── run_workflow.py                   # 工作流运行脚本
└── comfy_client.py                   # API 客户端示例
```
