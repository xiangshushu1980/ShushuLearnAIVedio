# ComfyUI 项目文档索引

> 本文件只做导航和当前入口提示；详细参数、步骤、实验过程按需加载。
> 环境基线：Ubuntu 24.04 / WSL2 / RTX 4090 24GB / Python 3.13 / CUDA 13。
> 最后更新：2026-09-05。

## 📚 文档导航（按需加载）

| 文档 | 用途 | 何时加载 |
|------|------|----------|
| [01_environment.md](01_environment.md) | 环境/启动/维护/API/客户端（01+03 合并） | 环境出问题 / 重启服务 / 脚本化调用 |
| [02_models.md](02_models.md) | 已下载模型清单（含 RMBG/ClearReality/Bernini/H3）、下载源、显存参考 | 下新模型 / 下载慢 / 查模型 |
| [06_extras_install.md](06_extras_install.md) | 图像编辑/超分/Bernini 手册（含 int8 选型背景、遗留 FLClash 脚本） | 涉及这些能力时加载 |
| [07_video_material.md](07_video_material.md) | 视频素材库索引（Pexels 原片/Bernini 预处理版/16:9 首帧图库/ref_lib） | 找 v2v 编辑素材 / 素材管线 |
| [08_h3_prompt_agent.md](08_h3_prompt_agent.md) | H3 提示词增强方案（官方 IR API 为主路径 + 接入细则） | IR API 调用 / 提示词智能体落地 |
| [09_h3_test_plan.md](09_h3_test_plan.md) | H3 系统化测试全量数据（速度矩阵/steps/提示词/量化/MC/sage/底图库） | 查 H3 实测数据 / 参数定论依据 |
| [10_h3_batch_optimization.md](10_h3_batch_optimization.md) | H3 fl2va 机制/TE 加载成本/缓存/两阶段批量方案（已落地 CondCache 节点） | 批量优化 / 理解 TE 加载成本（冷 ~11s/热 ~4s） |
| [11_h3_case_library.md](11_h3_case_library.md) | H3 提示词案例库（C01-C24 / D / E 批 + 目视反馈） | 写提示词参考案例时 |
| [12_speech_to_video_pipeline.md](12_speech_to_video_pipeline.md) | 音频+文字→视频管线（whisper→分镜→生图→动画→合成→字幕→BGM/混音/音效） | 演讲稿/旁白转视频 / BGM 制作 |
| [14_skill_governance.md](14_skill_governance.md) | Skill 治理框架（三层划分/经验→mem0 原则/蒸馏管道/升级路径） | 建新 skill / 组织多 skill 时 |
| [16_prompt_generator_plan.md](16_prompt_generator_plan.md) | 提示词生成器计划（分层管线/控制面/工具形态/收集清单） | 生成器开发时 |
| [17_h3_prompt_writing_rules.md](17_h3_prompt_writing_rules.md) | H3 提示词写作规则手册（模式契约/镜头/声音/六段式/七维增强） | 写提示词 / 工具 B 合成时 |
| [18_ir_sample_teardown.md](18_ir_sample_teardown.md) | IR 输出样本拆解（结构规律/声音三层/词汇库附录待建） | 学习 IR 输出 / 查词汇 |
| [19_h3_dual_track_gap_test.md](19_h3_dual_track_gap_test.md) | H3 双轨盲区补测（快/慢车道矩阵/帧链 SSIM 负面结论） | 双轨参数 / 帧链可靠性 |
| [21_pipeline_acceptance.md](21_pipeline_acceptance.md) | 新管线全链路验收（F 批/首帧锚定规律/工具链 vs IR/无 BGM 版） | 管线验收 / 首帧规范 |
| [22_shotlist_web_tool.md](22_shotlist_web_tool.md) | 拍摄本看板 Web 工具设计（全 TS 单栈/三段式/实体系统/标色/输入源） | 看板工具开发 / 工具 A/B 重写 |
| [23_refimage_system.md](23_refimage_system.md) | 设定图体系设计（角色/场景/道具/技能四类设定图形态/主次/重点控制/自动推导 + 工具 C 决策树） | 生成设定图 / 工具 A/B/C 落地设定图逻辑时 |
| [24_vl_qc_api.md](24_vl_qc_api.md) | 出图质检线上 VL API 选型与用法（qwen3-vl-flash 最省档/质检 prompt 模板/费用实测） | ComfyUI 出图客观质检（内容/文字/崩图/比例） |
| [25_h3c_study.md](25_h3c_study.md) | antirez h3.c（h3-metal）架构研究：垂直切片顺序/Metal 内存策略/优化方法论/H3 模型知识 | 借鉴无依赖推理架构思路 / 查 H3 参数坑（帧对齐/RoPE/音频 batch 折叠） |
| [26_music3_audio_quality.md](26_music3_audio_quality.md) | MiniMax Music 3 音质与 Prompt 探索定论（高频持续音杂音规律/台词坑修复/超分+母带链路/产出清单） | 写 Music3 prompt / 处理 Music3 音频 / 生成纯器乐曲子时 |
| [27_DUIX_Avatar_数字人评估.md](27_DUIX_Avatar_数字人评估.md) | DUIX-Avatar 开源自托管数字人评估（架构/硬件/API/粤语/与LongCat·InfiniteTalk·H3定位对比） | 选本地数字人/口拨分身引擎时 |
| [28_数字人在线方案_对比与价位.md](28_数字人在线方案_对比与价位.md) | 在线数字人方案对比（LongCat HF Space免费看效果/硅基元镜每日5分钟/HeyGen/可灵0.12元s/D-ID） | 想在线便宜看数字人效果/选按量API时 |
| [h3-digital-human-research/](h3-digital-human-research/) | MiniMax H3 数字人调查资料：官方事实、开源方案、社区实测、技术推论、未解析线索 | 研究 H3 数字人、长时主持、口型、角色参考和 InfiniteTalk 对照时 |
| [project/project-handoff.md](project/project-handoff.md) | 项目交接总览：调研、视频生成工作流、数字人方案、代码索引和打包边界 | 项目交接与打包时 |
| [archive/README.md](archive/README.md) | 历史技术、实验样本和旧交接资料索引 | 遇到旧技术或需要追溯研究细节时 |

**已归档**（内容已并入他处，git 历史可查）：03（→01）、04（→06）、05（→mem0 [STATE]）、13（→12）、20（→21）；具体历史资料见 [archive/README.md](archive/README.md)。

> agent 操作手册（模型栈/参数/踩坑/工作流档案）在 `.pi/skills/comfyui/SKILL.md` 及其 `references/` 分册；共享记忆/经验检索在 Mem0（`memory_recall`）；定论的演进史/覆盖链在 `.pi/ledger/`（结论谱系，append-only）。

## 当前入口

- 当前主线：MiniMax H3 本地视频/数字人，优先看 `09`、`10`、`17` 及 `h3-digital-human-research/`。
- 当前数字人链路：FL2VA/PDD → Motion Context → NativeAudioLock；任务记录见 `.pi/tasks/T-comfy-ops-28/progress.md`。
- 环境、启动、API：[`01_environment.md`](01_environment.md)。
- 模型和磁盘清单：[`02_models.md`](02_models.md)。
- 项目交接和打包边界：[`project/project-handoff.md`](project/project-handoff.md)。
- 历史实验与归档资料：[`archive/README.md`](archive/README.md)。

## 📐 文档维护规则（等幂纪律，2026-08-11 起）

1. **编号连续**：新文档用下一个空号；`scripts/docs_check.sh` 检查编号缺口与引用断裂（已归档号除外）
2. **归档流程**：内容并入他处（docs 或 mem0）→ 删除文件（git 保留历史）→ 本 INDEX「已归档」行登记 → 清理全仓引用 → 跑 `scripts/docs_check.sh` 验证
3. **经验不进 docs**：实测/踩坑/偏好 → mem0（判定树见用户级 AGENTS.md）；docs 只留手册/参考/数据记录
4. **合并先问**：跨任务线动文件前，read 最新版 + `git status` 查 WIP + recall [STATE] 确认无活跃占用
5. **引用即同步**：改文件名/合并时 grep 全仓（docs/.pi 全部 .md）；删除后立即验证
6. **单写者 + scoped commit**：每个文档一个任务线负责；改动只 `git add <自己的文件>`（禁止 -A）
