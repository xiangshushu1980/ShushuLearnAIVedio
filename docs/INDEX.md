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
| [29_daily_video_system.md](29_daily_video_system.md) | 每日话题视频系统分层、Format Profile、证据/脚本/时间线契约和 POC 边界 | 每日视频系统设计与 POC 时 |
| [30_open_source_workflow_ui_research.md](30_open_source_workflow_ui_research.md) | 开源流程编排、媒体工作台、审计和资源监控调研 | 选编排器 / 工作台 / 观测方案时 |
| [31_daily_video_service_architecture.md](31_daily_video_service_architecture.md) | 每日视频生产系统服务边界、Provider/Job/Artifact/Event 契约、状态图和实施顺序 | 开始编排器或 Provider 开发前 |
| [32_orchestrator_framework_evaluation.md](32_orchestrator_framework_evaluation.md) | Conductor、Temporal、Kestra 横向体验测试方法、评分矩阵和当前环境 | 评估任务编排框架时 |
| [33_h3_mc_engineering.md](33_h3_mc_engineering.md) | H3 Ref2VA + NativeAudioLock + MC 工程流程、帧网格、音频时间线和验收 | 进行 MC 长视频续接或排查音画不同步时 |
| [34_ref2va_generation_guide.md](34_ref2va_generation_guide.md) | H3 普通 Ref2VA 唯一日常入口：首次生成清单、资源、路线分流、4090 基线、验收与排错 | 普通 Ref2VA 日常生成；专题细节按文内链接进入 |
| [35_vdn_h3_ref2va_route.md](35_vdn_h3_ref2va_route.md) | VDN-H3 Ref2VA 路线、资源、4090 参数、社区证据与验收矩阵 | VDN-H3 下载、测试与后续维护 |
| [36_h3_audio_driven_dubbing_research.md](36_h3_audio_driven_dubbing_research.md) | 豆包 Audio 连续表演音频、Ref2VA 输入音频、NativeAudioLock、MC/Extender 配音研究 | 研究音频优先短剧配音、角色声线、口型和连续音效 |
| [37_hyperflow_4090_ref2va_research.md](37_hyperflow_4090_ref2va_research.md) | HyperFlow 在 RTX 4090 上的 Ref2VA 研究：完整 non-pruned 路线、pruned 社区路线、生产边界与 smoke 门槛 | 评估 HyperFlow 是否适合本机 4090 Ref2VA 生产 |
| [38_h3_selflift_ref2va_4090_research.md](38_h3_selflift_ref2va_4090_research.md) | H3 SelfLift + Ref2VA 的社区证据、4090 可行性边界与暂停结论 | 判断是否继续 SelfLift 前沿测试 |
| [39_h3_latent_upscale_face_research.md](39_h3_latent_upscale_face_research.md) | H3 远景人脸的像素局部修复与完整视频 latent 二采复核、第一优先测试记录 | 测试 H3 latent 两阶段放大与远景脸稳定性 |
| [40_h3_far_face_second_pass_strategy.md](40_h3_far_face_second_pass_strategy.md) | H3 远景小脸第二阶段局部重绘与 VOSR2/人物跟踪路线研究 | 远景小脸二次处理、人物跟踪和第二阶段策略 |
| [40_krea2_prompt_and_identity_pipeline.md](40_krea2_prompt_and_identity_pipeline.md) | Krea2 官方/社区提示词、Identity Edit 三模式和 H3 人物参考图管线 | Krea2 人物头像、风格化脸、人物参考图和 Ref2VA 前置准备 |
| [41_h3_character_reference_test_plan.md](41_h3_character_reference_test_plan.md) | H3 人物 reference 组织方式系统测试：独立多图、角色混合板、双人物板和复杂多对象条件竞争 | 开展 H3 人物 reference A/B 测试前 |
| [42_h3_face_preanalysis_external_research.md](42_h3_face_preanalysis_external_research.md) | H3 人脸预分析、multi-reference、缓存和现有节点外部方案研究 | 继续 T47 通用两阶段人脸预分析管线时 |
| [breeze-tts-standard.md](breeze-tts-standard.md) | Breeze TTS 当前正式入口、BF16/多人配置、环境分工和跨 Agent 读取规则 | 制作 Breeze 声音/配音时 |
| [h3-digital-human-research/](h3-digital-human-research/) | MiniMax H3 数字人调查资料：官方事实、开源方案、社区实测、技术推论、未解析线索 | 研究 H3 数字人、长时主持、口型、角色参考和 InfiniteTalk 对照时 |
| [project/project-handoff.md](project/project-handoff.md) | 项目交接总览：调研、视频生成工作流、数字人方案、代码索引和打包边界 | 项目交接与打包时 |
| [archive/README.md](archive/README.md) | 历史技术、实验样本和旧交接资料索引 | 遇到旧技术或需要追溯研究细节时 |

**已归档或保留编号**：03（→01）、04（→06）、05（→mem0 历史记录）、13（→12）、20（→21）；15 从未创建，保留编号避免重用。具体历史资料见 [archive/README.md](archive/README.md)。

> agent 操作手册入口在 `.pi/skills/comfyui/INDEX.md`：按任务目的路由到 core/image/video/workflows/troubleshooting 分册；共享记忆/经验检索在 Mem0（`memory_recall`）；定论的演进史/覆盖链在 `.pi/ledger/`（结论谱系，append-only）。

## 当前入口

- 当前主线：MiniMax H3 本地视频/数字人，优先看 `09`、`10`、`17` 及 `h3-digital-human-research/`。
- 当前 Breeze 入口：[`breeze-tts-standard.md`](breeze-tts-standard.md)；默认使用 ComfyUI Breeze 节点，Docker 仅用于隔离和 Flash Attention 实验。
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
