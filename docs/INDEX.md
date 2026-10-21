# Comfy-ops 文档入口

> Owner: Sean。本文件只负责定位权威资料；详细参数、步骤、实验过程按需读取。
> 环境基线：Ubuntu 24.04 / WSL2 / RTX 4090 24GB / Python 3.13 / CUDA 13。
> 最后更新：2026-10-14。

## 按问题找入口

有 T-ID 先读 Task Center 的 checkpoint 和 `metadata.contextRefs`；自由会话从下表开始。只读匹配主题的正文。

| 问题 | 入口 |
|---|---|
| 环境、模型、节点、升级 | [ComfyUI 项目研究索引（comfyui-ops）](../.pi/skills/comfyui-ops/INDEX.md) · [环境](01_environment.md) · [模型](02_models.md) · [升级](44_comfyui_h3_upgrade_runbook.md) |
| 生图、Qwen、三视图、Krea2、质检 | [共享生图入口（用户级 comfyui）](/home/sean/.pi/agent/skills/comfyui/SKILL.md) · [图像索引](../.pi/skills/comfyui-ops/references/image/README.md) · [Krea2](40_krea2_prompt_and_identity_pipeline.md) · [VL 质检](24_vl_qc_api.md) |
| H3 生成、提示词、参数 | [Ref2VA 日常生成](34_ref2va_generation_guide.md) · [提示词 skill](../.pi/skills/h3-prompt-writing/SKILL.md) · [历史测试证据（不作配置依据）](09_h3_test_plan.md) |
| 长视频、音频、数字人 | [MC 工程](33_h3_mc_engineering.md) · [Breeze TTS](breeze-tts-standard.md) · [数字人研究](h3-digital-human-research/) |
| 参考图、多视图、FaceRefine | [Reference 主题导航](reference/README.md) · [Reference 手册](45_ref_asset_handbook.md) · [多视图研究](46_multiview_consistency_research.md) · [FaceRefine 现状](43_h3_facerefine_current_state.md) |
| Reference 创建与编辑 | [主题导航](reference/README.md) · [创建/编辑流程](48_h3_reference_creation_editing_flow.md) · [实现前架构](49_h3_reference_workspace_architecture.md) |
| 视频生产系统与 Web 工具 | [服务架构](31_daily_video_service_architecture.md) · [拍摄本看板](22_shotlist_web_tool.md) |
| 素材、工作流、实验、旧方案 | [视频素材](07_video_material.md) · [工作流索引](../.pi/skills/comfyui-ops/references/workflows/README.md) · [实验索引](../experiments/INDEX.md) · [归档](archive/README.md) |

未命中时，先查下方完整目录，再用 `rg -n '<关键词>' docs .pi/skills .pi/ledger experiments/INDEX.md` 搜索；大档案按 `incdoc` 检索。任务状态看 Task Center，经验查 Mem0，历史定论查 [ledger](../.pi/ledger/README.md)。

## 完整目录

- **基础、图像与素材**：[01_environment](<01_environment.md>) · [02_models](<02_models.md>) · [06_extras_install](<06_extras_install.md>) · [07_video_material](<07_video_material.md>) · [24_vl_qc_api](<24_vl_qc_api.md>) · [qwen-chart-aesthetics-baseline](<qwen-chart-aesthetics-baseline.md>)
- **ComfyUI 图像节点实测**：[Qwen Image 2.1 nodes and Tiny VAE preview](<50_qwen_image_2_1_nodes_and_tiny_vae.md>)
- **提示词、制作与验收**：[08_h3_prompt_agent](<08_h3_prompt_agent.md>) · [09_h3_test_plan](<09_h3_test_plan.md>) · [10_h3_batch_optimization](<10_h3_batch_optimization.md>) · [11_h3_case_library](<11_h3_case_library.md>) · [12_speech_to_video_pipeline](<12_speech_to_video_pipeline.md>) · [17_h3_prompt_writing_rules](<17_h3_prompt_writing_rules.md>) · [19_h3_dual_track_gap_test](<19_h3_dual_track_gap_test.md>) · [21_pipeline_acceptance](<21_pipeline_acceptance.md>) · [26_music3_audio_quality](<26_music3_audio_quality.md>)
- **H3 视频、音频与人脸**：[33_h3_mc_engineering](<33_h3_mc_engineering.md>) · [34_ref2va_generation_guide](<34_ref2va_generation_guide.md>) · [35_vdn_h3_ref2va_route](<35_vdn_h3_ref2va_route.md>) · [36_h3_audio_driven_dubbing_research](<36_h3_audio_driven_dubbing_research.md>) · [39_h3_latent_upscale_face_research](<39_h3_latent_upscale_face_research.md>) · [40_h3_far_face_second_pass_strategy](<40_h3_far_face_second_pass_strategy.md>) · [42_h3_face_preanalysis_external_research](<42_h3_face_preanalysis_external_research.md>) · [43_h3_facerefine_current_state](<43_h3_facerefine_current_state.md>) · [44_comfyui_h3_upgrade_runbook](<44_comfyui_h3_upgrade_runbook.md>)
- **参考图与 Krea2**：[Reference 主题导航](<reference/README.md>) · [23_refimage_system](<23_refimage_system.md>) · [40_krea2_prompt_and_identity_pipeline](<40_krea2_prompt_and_identity_pipeline.md>) · [41_h3_character_reference_test_plan](<41_h3_character_reference_test_plan.md>) · [45_ref_asset_handbook](<45_ref_asset_handbook.md>) · [46_multiview_consistency_research](<46_multiview_consistency_research.md>) · [47_h3_reference_workbench_redesign](<47_h3_reference_workbench_redesign.md>) · [48_h3_reference_creation_editing_flow](<48_h3_reference_creation_editing_flow.md>) · [49_h3_reference_workspace_architecture](<49_h3_reference_workspace_architecture.md>)
- **系统、产品与治理**：[14_skill_governance](<14_skill_governance.md>) · [22_shotlist_web_tool](<22_shotlist_web_tool.md>) · [31_daily_video_service_architecture](<31_daily_video_service_architecture.md>)

其他入口：[Breeze TTS](breeze-tts-standard.md) · [数字人研究](h3-digital-human-research/) · [项目交接](project/project-handoff.md) · [归档](archive/README.md) · [实验索引](../experiments/INDEX.md)。

**已归档或保留编号**：03（→01）、04（→06）、05（→mem0 历史记录）、13（→12）、16（→h3-prompt-writing skill）、18（→17）、20（→21）、25（归档）、27（归档）、28（归档）、29（→31）、30（→31/32）、32（归档）、37（归档）、38（归档）；15 从未创建，保留编号避免重用。具体历史资料见 [archive/README.md](archive/README.md)。

## H3/ComfyUI 更新调研必读顺序

凡涉及 H3、ComfyUI、custom node、模型、依赖、VAE、采样加速或工作流升级/更新：

1. 先读 [`节点来源与更新记录`](dev/comfyui_node_update_20260912.md) 中的最新记录。
2. 再读相关 `.pi/ledger/`：至少 `h3-speed.md`、`h3-models.md`；涉及音频或 NativeAudioLock 时加读 `h3-audio.md`。
3. 读取当前任务对应的专题文档和 `experiments/` 中最近实测。
4. 最后进行外部 sources 调研，核对上游是否有新变化。

“已实装 / 已验证 / 待验证”的判断以本地 experiments、ledger 和当前运行时为准；外部来源不能覆盖本地实测结论。

## 📐 文档维护规则（等幂纪律，2026-08-11 起）

### 历史编号例外

- `40` 被历史上的 [H3 远景脸二采策略](40_h3_far_face_second_pass_strategy.md) 与 [Krea2 身份管线](40_krea2_prompt_and_identity_pipeline.md) 共用。保留文件名以免断链；新增文档不得复用编号，引用时使用主题标题和完整路径。

1. **编号与索引**：新文档用未占用编号；`scripts/docs_check.sh` 检查顶层文档是否入索引、重复编号是否登记，以及本地 Markdown 链接和 Ledger ID 映射
2. **归档流程**：内容并入他处（docs 或 mem0）→ 删除文件（git 保留历史）→ 本 INDEX「已归档」行登记 → 清理全仓引用 → 跑 `scripts/docs_check.sh` 验证
3. **经验不进 docs**：实测/踩坑/偏好 → mem0（判定树见用户级 AGENTS.md）；docs 只留手册/参考/数据记录
4. **合并先问**：跨任务线动文件前，读最新版、检查工作树，并查询远程 Task Center 的 controller/generation 确认活跃任务；不以记忆作为占用状态
5. **引用即同步**：改文件名/合并时 grep 全仓（docs/.pi 全部 .md）；删除后立即验证
6. **单写者 + scoped commit**：每个文档一个任务线负责；改动只 `git add <自己的文件>`（禁止 -A）

## 文档与 Git 维护

Owner: Sean。每日增量检查的范围、权威正文、退役指令和 Git 开关统一见 [项目维护配置](../.document-health.json)。当前自动检查只读，不自动提交或推送；原有混合改动保留，推送前核对全部待上传提交。结论变化时同步现行手册、ledger 替代关系与直接引用，每日检查只作漏项兜底。
