# [Sean] 短片 Agent、LLM 与真实视频诊断

Owner: Sean。日期：2026-10-04。Task Center：remote-92ecb0d7-d1db-4bd5-8a3e-83732b7404f1。

此实验最初使用独立 SQLite/素材目录 `/tmp/sean-film-pi-real-gjEYqk` 和端口4194；临时目录被清理后从本目录恢复副本续接，目前独立目录为 `/tmp/sean-film-anchor-real-UCUEcQ`。来源项目为5269e95a-d8b7-4c66-b8fd-603be396ef4c revision18；不写用户原项目或 Reference。测试项目70338d49-e494-433f-a753-738fbd3dafc9。Pi使用应用专用配置、DeepSeek远程模型和受限工作流工具，视频由既有共享ComfyUI和资源租约生成。

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

恢复副本保存在本目录 `runtime-data/film.sqlite` 与 `runtime-data/blobs/`，当前SQLite备份integrity_check为ok，revision58、16个终态Agent运行、11个成功视频候选及2条诊断成片及完整素材/会话/版本；初始revision34备份另存film-rev34.sqlite，不含agent凭据目录。仅作为独立数据目录使用，禁止合并主库。可复制到新的FILM_DATA_DIR，在独立端口启动film-editor，配置应用自有模型凭据后续接；GPU操作仍需资源协调。主服务4190继续运行。


## 具体衔接帧对照

方法 v3 将真实前镜尾帧作为最后一个独立 Picture，通过应用自有接口冻结来源与字节，并要求固定 LLM 使用具体开场构图。首轮运行 eeb26bc4-208f-40ab-ac25-38c498e9f8fe 暴露单镜校验隐藏前序上下文的问题，未提交 LLM/GPU，取消后修复并加入回归。证据 `sean_pi_continuity_anchor_first_attempt.json`。

修复后运行 3d074b58-6871-4977-816d-1cb078ca22d8：读取真实 S4 尾帧 → 固定 LLM revision job 1729cefb-3c56-4d07-bfca-7185817fd5e8 → 修复505词警告 → 校验/采用 → 真正生成新 S5 candidate 2ec41dd5-1f33-4f2f-b3cf-10601343667e（12.25秒）。输入含7张真实图片，最后一张来自 S4 candidate414f8436-1205-4a97-95a6-71ec8d9b00b7 的6.433333秒帧，PNG SHA-256 fa0c8b002863d03452f9289b59c8dae8b9d6f62a96d2328d85fc593487ecaa49。完整会话及修订版本见 `sean_pi_continuity_anchor_test.json`，媒体/图片/工作流见 manifest；没有选用新片或重合成。

`collect-video-evidence.mjs` 是只读证据采集器，核对视频/图片字节哈希、保存实际输入/工作流/ffprobe/抽帧，不提交模型或 GPU 请求。`frames/sean_anchor_s05_motion_contact.png` 另保存12个时间点的换装/转身观察；不能用三帧证明完整运动或声音。主服务4190当前由 transient systemd unit恢复，能访问用户项目但不代表配置了开机启动；用户原项目仍revision18。


顺序衔接新增 S2/S3/S4 对照见 `sean_pi_continuity_anchor_s02_test.json`、`sean_pi_continuity_anchor_s03_test.json`、`sean_pi_continuity_anchor_s04_test.json`。已在隔离副本选用新S2/S3，S4尚未选用，S5旧锚点因S4输入变化过期。S1→S4的实际抽帧保留A左/B右、同一主桌/书墙与刀/外套状态链，S4补充六点帧显示拿刀转移及远侧离场；仍需新S5接续当前S4并检查完整运动/音色，不代表全片验收完成。


当前五镜诊断cut53d54489-5189-4300-ac14-80d335af1b3b及四接缝已归档；所有新候选已在隔离副本选用，revision58。`collect-cut-evidence.mjs`只读采集成片/输入哈希、完整流解码与接缝附近帧，不提交LLM/GPU；可安全重复采集同一cut。S5实际新源接续、12点定点观察与诊断选片/合成的真实会话另存sean_pi_continuity_anchor_s05_current_test.json、sean_pi_continuity_anchor_s05_motion_review.json、sean_pi_continuity_anchor_current_cut.json。设计文字对中性桌面物件仍有冲突，S5字幕/开场B与站位/完整动作/声音尚未全片验收；详见QC，不以cut成功结束目标。
