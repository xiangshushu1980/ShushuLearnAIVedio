# [Sean] 短片 Agent、LLM 与真实视频诊断

Owner: Sean。日期：2026-10-04。Task Center：remote-92ecb0d7-d1db-4bd5-8a3e-83732b7404f1。

此实验使用独立 SQLite/素材目录 `/tmp/sean-film-pi-real-gjEYqk` 和端口4194。来源项目为5269e95a-d8b7-4c66-b8fd-603be396ef4c revision18；不写用户原项目或 Reference。测试项目70338d49-e494-433f-a753-738fbd3dafc9。Pi使用应用专用配置、DeepSeek远程模型和受限工作流工具，视频由既有共享ComfyUI和资源租约生成。

真实操作链：读完整叙事与实体/看场景图 → 固定LLM生成全片空间提案 → 校验提示词格式/绑定并修复 → 明确测试用调度和换装要求 → 采用版本 → 生成五镜 → 看帧 → 选片 → 合成诊断样片。第五镜为换装及转身测试由7秒改为12秒，记录为独立修订版本；对白、角色身份和引用保持。已有基线空间/衣物/刀的偏差，详见 [QC.md](QC.md)，不能当作视觉验收通过。

关键证据：

- `sean_pi_readonly_check.json`：真实PI只读诊断。
- `sean_pi_workflow_check.json`、`sean_spatial_workflow_job.json`：真实固定LLM调用、等待和结果。
- `sean_proposal_format_check.json`、`sean_pi_prepare_check.json`：独立校验发现与修复，版本19→20→21。
- `sean_pi_video_first_pair.json`、`sean_pi_video_second_pair.json`、`sean_pi_video_final_and_cut.json`：五镜实际提交/等待/观察及选片合成。
- `sean_pi_video_feedback_repair.json`：基于实片的第四镜固定LLM反馈、格式修复、采用与再次真实生成；视觉评价有误判，详见QC。
- `sean_pi_fresh_observation.json`：独立只读会话复核同一新候选，部分纠正旧报告，仍有空间观察误判。
- `sean_video_manifest.json`：每个候选原输入、完整prompt、工作流、媒体SHA-256、ffprobe、资源租约和运行指标。
- `sean_test_project.json`：实验项目当前状态；基线合成时revision32。
- `sean_baseline_cut_manifest.json`、`outputs/sean_baseline_cut.mp4`：37.188333秒诊断成片及五镜候选来源。
- `frames/`：按候选ID标记的首/中/尾帧及接触表；三帧不是完整运动或声音评价。
- `references/`、`sean_reference_index.json`：实际参考素材及来源索引。

视频和图片保留本地，代码/文档使用scoped commit。应用专用模型凭据不属于实验交付，不复制进仓库；临时DB不能直接并入主应用DB，因为快照ID与原项目有共同来源。失败基线保留，用后续反馈修订结果作对照。

恢复副本保存在本目录 `runtime-data/film.sqlite` 与 `runtime-data/blobs/`，SQLite备份integrity_check为ok，包含revision34、8个终态Agent运行、完整会话及候选/素材/版本；不含agent凭据目录。仅作为独立数据目录使用，禁止合并主库。可复制到新的FILM_DATA_DIR，在独立端口启动film-editor，配置应用自有模型凭据后续接；GPU操作仍需资源协调。隔离测试服务空闲后停止，主服务4190继续运行。
