# 文档、ledger 与 Mem0 联合维护实施记录

Owner: Sean。实施日期：2026-10-21。

## 设计与部署

- 当前配置与操作在项目手册；ledger 是结论历史层，保留证据和覆盖链；Mem0 是可检索经验。任务状态只在远程 Task Center。
- 统一工具及运行手册：`/home/sean/.pi/agent/tools/document-health/README.md`；源码 `health.py`，项目注册表 `projects.json`。项目配置见 [本项目配置](../../.document-health.json)。
- 云端原 `mem0-l0-audit.timer` 每日北京时间 05:00 保持既有 L0 自动处理范围，新增 ideas 池。新增只读桥接 `/home/ubuntu/app/mem0/document_health_review.py`，读取最近非 dry-run 的 L0 报告与项目/global 记忆，使用现有 DeepSeek 凭证作一致性审阅。没有重启 Mem0。
- 本地 `document-health.timer` 初次部署为每日 05:30；同日按用户开机不规律的实际情况改为 WSL 用户服务启动约 3 分钟后执行，持续在线每 24 小时再执行；失败后每 5 分钟有限重试，45 分钟内最多 3 次。实际 unit 环境已运行成功。开机指 WSL／用户服务启动，不会自动拉起尚未启动的 WSL 发行版。
- 检查器只读项目与记忆，不自动修文、提交、推送或建任务。通知体现为变化时的服务日志；私有报告在 `~/.local/share/document-health/`，未接入额外外部通知渠道。原有 L0 的自动去重等权限没有扩展到文档事实裁决。

## 验证后再推广

1. image-gen：2 份 Markdown。清除旧 TODO/本地任务状态入口，为旧价格表补历史和未核验边界，移除把路线图当当前待办的表述；项目无远端，不猜上传目标。复查无待报问题。提交 `24debb7`。
2. ideas：10 份 Markdown。从索引去除重复状态/日期，只保留定位；想法与来源正文不修改，既有未跟踪 idea-006/007 保持原样。试跑曾发现模型越界建议改创意正文，因此改成程序强制不向语义模型发送受保护正文，只做本地引用检查。复查无待报问题。提交 `bb405d7`。
3. comfy-ops：73 份文档纳入首轮结构检查与分批语义初筛；17 份大文件仅作明确标注的节选/变更上下文审阅，未宣称全文事实核验。未递归扫描整个 experiments、媒体或模型目录。待审文件队列可跨批次保留。

## comfy-ops 已采用的修订

- 清除 nodes 的强制 CPU 残留；docs/09 和旧 params 明确历史范围，H3 分册不再将旧参数与新手册并列为配置依据。
- 撤销批次前无条件重启建议，环境、Breeze 与排错手册对齐共享 comfyui.service。
- 旧量化、Wan、Bernini、ANIMA 工作流标注已清理或历史版本，禁止按旧模板自动恢复模型。
- 更新 ledger 分工，撤销 TODO/[STATE] 作为任务状态源；去掉 ledger 维护说明中的重复旧文件清单。
- 新增 C-H3MODELS-20261021-01（固定 CPU 建议撤销）、C-COLLAB-20261021-01（远程任务唯一状态源）、C-H3AUDIO-20261021-01（RTF 与跨场景设备比较边界），补旧结论指向新结论。
- FaceRefine 旧参数标为历史档位，任务地图移除本地生命周期投影；Motion Context 历史链与当前 Continuum 路线区分。
- 保留旧实验数字，不为纠正文档而新增生成或操作 ComfyUI/GPU。

## 效果与限制

- 14 项自动测试覆盖失败重试、未提交/删除、依赖重查、锚点、无源文件写入、受保护内容隔离、分批队列、重复通知和有哈希约束的误报裁决等。
- 注入三条已退役指令（强制 CPU、无条件重启、旧 FP8 推荐）均能检出；修订后的三处源文均不触发。既有项目 docs_check 在修订后通过。
- 语义模型曾把 RTF 方向读反、把未提供的上下文当缺失，以及对历史已撤销语句再次报警。未照单执行；新增缺上下文只能算覆盖限制的约束和本地 C-ID 位置映射，保留人工裁决。模型仍可能误报，不能把其候选数当真实缺陷数。
- 首轮消除了已确认的高风险执行指令。剩余格式、重复、证据范围和跨主题候选保存在私有报告；没有把所有候选标成已修复，也没有宣称所有文档内容正确。
- 云端今日 L0 报告成功，1 个候选、0 个待处理；今日旧报告尚不含新注册 ideas 池，新池在下一次 05:00 运行纳入。

## Git 与恢复

各项目配置均为 auto_commit=false、auto_push=false。人工仅 scoped commit；远端与分支未明确时不自动推送，推送前核对全部 ahead 提交。

中央工具提交 `57d0382`、`4aaff4c`；comfy-ops ledger 提交 `b580021`、`a75ed04`。本轮全部未推送。`docs/09_h3_test_plan.md`、`docs/34_ref2va_generation_guide.md`、`.pi/skills/comfyui-ops/references/params.md` 原有未提交改动与本轮修订混合，保留工作树不整文件提交。原有 film-editor、预览实验、工作流及其他用户级修改不纳入本轮提交。

停用每日检查：`systemctl --user disable --now document-health.timer`。云端原 L0 不受此影响；其本轮仅增加扫描池，旧部署备份在 `/home/ubuntu/app/mem0/mem0_l0_maintain.py.pre-document-health-20261021`。文档回退使用本轮各 scoped commit，不执行整树重置，也不把 Git 回退当作 Mem0 回退。

## 同日补充：开机与手动入口

Owner: Sean。新增共享 skill `/home/sean/.pi/agent/skills/document-health/SKILL.md`，Codex 通过同名软链使用。任意项目或子目录可执行 `~/.pi/agent/bin/document-health`，或对 Agent 说“用 document-health 检查当前项目”。未配置目录临时推断范围，仅本地结构检查，不写项目配置、不注册后台、不发云端。当前共 18 项自动测试通过，配置项目子目录与临时无 Git 目录均已实测；skill 格式与 systemd unit 校验通过。
