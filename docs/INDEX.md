# ComfyUI 项目文档索引

> 本机环境：Ubuntu 24.04 (WSL2, mirror 网络模式) / RTX 4090 24GB / Python 3.13 / CUDA 13
> 最后更新：2026-08-11（docs 体系整理：13→12、04→06、20→21 合并；09/19 瘦身；维护规则见文末）

## 📚 文档导航（按需加载）

| 文档 | 用途 | 何时加载 |
|------|------|----------|
| [01_environment.md](01_environment.md) | 环境/启动/维护/API/客户端（01+03 合并） | 环境出问题 / 重启服务 / 脚本化调用 |
| [02_models.md](02_models.md) | 已下载模型清单（含 RMBG/ClearReality/Bernini/H3）、下载源、显存参考 | 下新模型 / 下载慢 / 查模型 |
| [06_extras_install.md](06_extras_install.md) | 图像编辑/超分/Bernini 手册（含 int8 选型背景、遗留 FLClash 脚本） | 涉及这些能力时加载 |
| [07_video_material.md](07_video_material.md) | 视频素材库索引（Pexels 原片/Bernini 预处理版/16:9 首帧图库/ref_lib） | 找 v2v 编辑素材 / 素材管线 |
| [08_h3_prompt_agent.md](08_h3_prompt_agent.md) | H3 提示词增强方案（官方 IR API 为主路径 + 接入细则） | IR API 调用 / 提示词智能体落地 |
| [09_h3_test_plan.md](09_h3_test_plan.md) | H3 系统化测试全量数据（速度矩阵/steps/提示词/量化/MC/sage/底图库） | 查 H3 实测数据 / 参数定论依据 |
| [10_h3_batch_optimization.md](10_h3_batch_optimization.md) | H3 fl2va 机制/TE 加载成本/缓存/两阶段批量方案 | 批量优化 / 理解 80s TE 开销 |
| [11_h3_case_library.md](11_h3_case_library.md) | H3 提示词案例库（C01-C24 / D / E 批 + 目视反馈） | 写提示词参考案例时 |
| [12_speech_to_video_pipeline.md](12_speech_to_video_pipeline.md) | 音频+文字→视频管线（whisper→分镜→生图→动画→合成→字幕→BGM/混音/音效） | 演讲稿/旁白转视频 / BGM 制作 |
| [14_skill_governance.md](14_skill_governance.md) | Skill 治理框架（三层划分/经验→mem0 原则/蒸馏管道/升级路径） | 建新 skill / 组织多 skill 时 |
| [16_prompt_generator_plan.md](16_prompt_generator_plan.md) | 提示词生成器计划（分层管线/控制面/工具形态/收集清单） | 生成器开发时 |
| [17_h3_prompt_writing_rules.md](17_h3_prompt_writing_rules.md) | H3 提示词写作规则手册（模式契约/镜头/声音/六段式/七维增强） | 写提示词 / 工具 B 合成时 |
| [18_ir_sample_teardown.md](18_ir_sample_teardown.md) | IR 输出样本拆解（结构规律/声音三层/词汇库附录待建） | 学习 IR 输出 / 查词汇 |
| [19_h3_dual_track_gap_test.md](19_h3_dual_track_gap_test.md) | H3 双轨盲区补测（快/慢车道矩阵/帧链 SSIM 负面结论） | 双轨参数 / 帧链可靠性 |
| [21_pipeline_acceptance.md](21_pipeline_acceptance.md) | 新管线全链路验收（F 批/首帧锚定规律/工具链 vs IR/无 BGM 版） | 管线验收 / 首帧规范 |

**已归档**（内容已并入他处，git 历史可查）：03（→01）、04（→06）、05（→mem0 [STATE]）、13（→12）、20（→21）

> agent 操作手册（模型栈/参数/踩坑/工作流档案）在 `.pi/skills/comfyui/SKILL.md` 及其 `references/` 分册；共享记忆/经验检索在 Mem0（`memory_recall`）。

## 🔑 快速速览

### 启动 ComfyUI
```bash
cd /home/sean/projects/ComfyUI
./start.sh          # 后台: nohup ./start.sh > /tmp/comfyui_start.log 2>&1 &
```
界面: http://localhost:8188 （WSL mirror 模式下 Windows 浏览器可直接访问）

### 模型栈（全部就位）
- **视频（H3 双轨）**：MiniMax H3 — 快车道 fl2va fp8+turbo / 慢车道 ref2va std14/20（qwen3vl-32B nvfp4_awq TE + 双 VAE）；768×448 5s ≈ 1.6-2min/条（矩阵见 09/19）
- **视频（老栈）**：Wan2.2 I2V Lightning — GGUF Hi/Lo Q4_K_S + lightx2v 4步 LoRA（480²×33帧 ≈ 10-16s）
- **图像编辑**：Bernini-R int8_convrot（v2v 快 21% 画质无损，选型背景见 06）
- **生图**：ANIMA（动漫线稿/高饱和）+ KREA 2 turbo（平滑/写实）+ Alya/Yuki LoRA
- 完整清单与下载源见 [02_models.md](02_models.md)

### 主力工作流
- `workflows/minimax_h3_i2v_api.json` / `minimax_h3_t2v_api.json` — H3 图/文生视频（当前主力）
- `workflows/wan2.2_i2v_lightning_test.json` — Wan2.2 图生视频（480²×33帧×4步，~14s/次）
- `workflows/anima_alya_768_t2i.json` — Alya 角色 768² 起始图（I2V 标准）
- `workflows/video_bernini_r_v2v_test.json` — Bernini v2v 编辑（int8 已切默认）

### 资源规范（2025-08-01 起沿用）
- `output/` 按模型/用途分子目录：anima / krea / compare / video / review / img_* / res_test
- `input/start/` 公用 I2V 起始图（语义命名，用原图分辨率直接跑）；`input/start/169/` H3 首帧 16:9 图库（35 张，规则见 21）；`input/ref_lib/` H3 参考图库（realistic/illustration 121 张）；`input/test/` 测试素材；`input/material(_b)/` v2v 素材（见 07）
- SaveImage/SaveVideo 的 filename_prefix 直接带子目录，生成即落位

## 📁 目录结构

```
/home/sean/projects/ComfyUI/          # ComfyUI 本体
├── main.py / start.sh                # 入口与启动（--enable-assets --use-sage-attention 已固化）
├── models/                           # 模型（unet/diffusion_models/text_encoders/vae/loras...）
├── custom_nodes/                     # 自定义节点（Manager、browser、GGUF、WanVideoWrapper 等 8 个）
├── input/                            # 输入（start/ + start/169/、ref_lib/、test/、material(_b)/）
├── output/                           # 生成结果（anima/ krea/ compare/ video/ review/ img_*/ res_test/）
└── user/                             # 用户数据（workflows/ comfyui.db assets 索引）

/home/sean/projects/comfy-ops/        # 本项目（工作流/文档/脚本）
├── docs/                             # 本文档体系（导航见上表；维护规则见下）
├── workflows/                        # 工作流 JSON（API 格式）
├── scripts/                          # 脚本（docs_check.sh / h3_* / restart_comfyui.sh ...）
├── .pi/skills/comfyui/               # agent 手册（SKILL.md + references/ 分册）
├── run_workflow.py                   # 工作流运行脚本
└── comfy_client.py                   # API 客户端示例
```

## 📐 文档维护规则（等幂纪律，2026-08-11 起）

1. **编号连续**：新文档用下一个空号；`scripts/docs_check.sh` 检查编号缺口与引用断裂（已归档号除外）
2. **归档流程**：内容并入他处（docs 或 mem0）→ 删除文件（git 保留历史）→ 本 INDEX「已归档」行登记 → 清理全仓引用 → 跑 `scripts/docs_check.sh` 验证
3. **经验不进 docs**：实测/踩坑/偏好 → mem0（判定树见用户级 AGENTS.md）；docs 只留手册/参考/数据记录
4. **合并先问**：跨任务线动文件前，read 最新版 + `git status` 查 WIP + recall [STATE] 确认无活跃占用
5. **引用即同步**：改文件名/合并时 grep 全仓（docs/.pi 全部 .md）；删除后立即验证
6. **单写者 + scoped commit**：每个文档一个任务线负责；改动只 `git add <自己的文件>`（禁止 -A）
