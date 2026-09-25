# T-comfy-ops-32：自动生成每日话题视频流程方案与 POC

## 状态

- 2026-09-07：用户确认新开任务，开始方案讨论与落盘。
- 当前阶段：方案基线已记录，尚未进入完整端到端实现。

## 用户目标

建立一个自动生成每日话题视频的流程，单条节目约 30–90 秒：

1. Source 抓取指定话题的文本、图片、视频和声音原料。
2. 导演 skill 根据资料设计每日视频节目和完整脚本。
3. H3 数字人主持人负责主持人口播/对谈和相关视频素材；Breeze TTS 负责本地中文语音生成；H3/Music 生成补充视频、音乐、专场和音效素材。
4. 将主持人、抓取素材、AI 生成素材、音乐和音效按脚本拼接成片。

## 当前方案基线

### A. Source 资料层

- 输入：主题、关键词、时间范围、语言和平台范围。
- 输出：文本事实、来源链接、图片、视频片段、声音/采访素材，以及每项素材的来源、时间、授权/可用性和内容摘要。
- 后续重点：深入确定各渠道抓取方式、去重、可信度分层、版权与引用保留。

### B. 导演/脚本层

- 将资料整理为 30–90 秒节目结构，而不是直接把搜索结果拼接起来。
- 产出：节目标题、核心结论、段落节奏、主持人角色、镜头/素材需求、口播稿或多人对谈稿、情绪标注、字幕稿、音乐/音效提示。
- 需要区分事实、推断、观点和待核实内容，避免导演 skill 自行补写未经来源支持的事实。

### C. 音视频生成层

- 主持人：H3 数字人，最终外部音频作为音频真值；H3 用音频条件驱动口型和表演。
- 语音：Breeze TTS 2 本地中文生成；当前实测保守口播基线为 `cfg_scale=1.5`、固定 seed、自然口播指令。情绪通过段落级指令和少量 vocal event 控制，避免短句割裂逻辑。
- 补充画面：按素材缺口调用 H3 生成视频素材；保持角色、画面比例和风格约束。
- 声音：根据节目节奏补充音乐、专场/转场和音效；音乐与人声分轨，便于混音。

### D. 合成层

- 按节目时间线拼接抓取素材、H3 主持人段落、AI 补充镜头、音乐、音效和字幕。
- 需要统一处理：画幅、帧率、音量、响度、字幕时间轴、转场、素材引用/署名和最终导出。
- 验收：事实可追溯、口播与字幕一致、画面与口播匹配、数字人口型可接受、音频无突变、素材版权状态明确。

## 已有可复用能力

- Breeze TTS skill：`.pi/skills/breeze-tts/`
- Breeze 正式模型：`models/breeze-tts-2`
- Breeze 代码：`tools/breeze-tts`
- H3 数字人和外部音频锁定经验：`docs/h3-digital-human-research/`
- Source 检索工具和渠道手册：`~/.codex/skills/sources/`，项目已有 source 相关经验和脚本。
- 语音→视频总体管线参考：`docs/12_speech_to_video_pipeline.md`

## 下一步讨论/POC

1. 选一个固定话题，定义 30–45 秒最小节目格式。
2. 设计 Source normalized/raw/evidence 数据结构和素材清单。
3. 定义导演 skill 的输入、输出 JSON 和事实引用契约。
4. 用一条完整稿件测试 Breeze 段落级情绪标注，再接 H3 主持人。
5. 明确音乐、音效和抓取素材的混音与版权记录格式。
6. 端到端跑通一条样片后，再决定是否开发 Web 看板/自动化编排器。

## 当前未决问题

- 每日话题来源和抓取平台的优先级。
- 事实核验的最低标准和引用展示方式。
- 主持人单人播报还是双人/多人对谈为默认节目形态。
- H3 主持人段落的时长、分段和长视频续接策略。
- Breeze 音色情绪控制的自动标注格式。
- 音乐/音效生成工具和商用授权边界。
- 成片是本地批处理、Web 编排，还是两者结合。

## 2026-09-07 当前完整流程盘点

### 已完成或已有可靠基础

- Provider-neutral 每日视频 POC：本地 JSON→evidence/claims→script/storyboard→timeline→SRT→QC→preview MP4 闭环已跑通；但媒体 provider 仍是占位/后接入。
- Breeze TTS：中文自然口播、连续长段、局部叹息/肯定/质疑和英文参考音色克隆已完成独立验证；尚未接入每日视频 runner。
- H3 数字人底层能力：外部音频参考、NativeAudioLock、Motion Context、主播身份参考图、FaceRefine 和 16:9 裁切已有节点与实测样本。
- H3 长段摸底：4090 上有 10–15 秒级单段和多段 MC 链成功记录；4 段链约 19 秒成片已生成，外部原始音频复挂和时间线修正方法已明确。
- 旧的音频→分镜→动画→字幕→混音管线已有 ffmpeg/字幕/BGM/音效经验可复用。

### 尚未走完的关键环节

1. **真实 Source 接入**：尚未把每日话题抓取稳定产出为 raw/normalized/evidence/media pack；渠道、去重、事实核验、媒体下载、版权状态还没有接入 T-comfy-ops-32 runner。
2. **导演 Skill 实装**：Format Profile 和 Script/Storyboard JSON 契约已有，但还没有一个能读取真实 Evidence Pack、生成可审阅脚本、标注情绪/镜头/引用并支持修改的导演 skill。
3. **H3 数字人主持生产链**：目前是独立实验，不是 `ScriptSegment→Breeze WAV→H3 host clip→MC continuation→host artifact` 的 provider。尚未完成中文 Breeze 音频驱动的 30–90 秒主持人口播验收，也未确定默认 chunk、接缝和恢复策略。
4. **主持人与 B-roll 时间线绑定**：还没有把主持人口播的句子/音频时间轴自动映射到抓取视频、图片、H3 补充镜头和主持人画面。
5. **抓取素材理解**：ffprobe/ASR/OCR/VLM/镜头切分/人物分析尚未作为真实媒体理解阶段接入，当前不能可靠地从视频原料挑出可用片段。
6. **H3 补充画面 provider**：尚未按 storyboard 自动提交 H3 生成 B-roll、保存 job/artifact 版本并回填 timeline；现有 H3 实验主要集中在数字人。
7. **Music/音效 provider**：Music3/ACE-Step/本地 MusicGen 与转场/专场/环境音尚未按节目段落自动生成、排队、对齐和记录授权。
8. **真实合成与混音**：POC 能渲染占位预览，旧管线能处理局部视频；尚未完成“真实主持人+抓取素材+H3 B-roll+音乐+音效+字幕”的 30–90 秒一键合成。
9. **QC 与人工审核**：事实、引用、口播字幕、口型、画面相关性、响度、版权和失败分类的检查项已有设计，但没有贯穿真实产物的审核门和可恢复重跑。
10. **工作台/自动化编排**：尚未决定并落地 Web 工作台、任务队列、GPU 资源占用、暂停/恢复、单节点重试和每日定时触发。

### H3 主持人下一验收门槛

- 固定一段 30–45 秒中文 Breeze 完整口播；
- 生成 H3 主持人首段并完成音频锁定/口型检查；
- 用 Motion Context 续接到完整时长，按真实帧数裁切并挂回同一 Breeze 母带；
- 检查身份、口型、断句接缝、音画同步、显存、耗时和失败恢复；
- 通过后才把 H3 Host Provider 接入每日视频 POC。

## 2026-09-07 资源调配架构决策

资源调配应独立于 Agent 和具体媒体 Provider，但不再另起一套重复系统。当前已有 `hive-resource daemon`，负责全局资源登记、GPU/端口/服务租约、心跳、释放和运行观测；T-comfy-ops-32 的编排器应通过它申请资源。

推荐三层边界：

```text
Workflow Orchestrator
  └─ Resource Broker / hive-resource
       ├─ GPU/VRAM/CPU/port lease
       ├─ queue + priority + heartbeat + timeout
       └─ worker/service discovery
            ├─ Source/Director worker
            ├─ Breeze worker
            ├─ H3 worker
            ├─ Music/SFX worker
            └─ Render/QC worker
```

资源需求不写死在 Agent Prompt，而写在每个 `GenerationJob`/Provider manifest：

```json
{
  "provider": "h3_host",
  "resources": {"gpu": "exclusive", "vram_mb": 23000, "cpu_ram_mb": 50000},
  "estimated_seconds": 900,
  "checkpointable": true,
  "priority": 4
}
```

本机 4090 的初步调度策略：

- Source、Director、字幕、ffmpeg 合成、QC：CPU/网络 worker，可并行。
- Breeze：单独 GPU job 或常驻服务；可用显存较小，但不要与 H3 默认并行。
- H3：`gpu:0` 独占租约；峰值约 20–23GB 且系统 RAM 压力高，必须串行并支持长租约/心跳。
- Music/SFX：按实际模型选择 CPU 或 GPU 队列，不与 H3 抢卡。
- 每个 job 完成后记录峰值显存、系统内存、耗时、失败类别和 artifact，供后续资源画像。

因此要做的是：扩展现有 resource daemon/CLI 的 job 需求与队列适配，再让统一 WebUI 展示资源状态；不在每个阶段页面里各自实现 GPU 调度。

## 2026-09-07 服务化与开发顺序共识

用户确认回到 T-comfy-ops-32 继续讨论，并接受以下方向：整个每日视频生产系统由多个可替换 Provider 服务、一个统一编排/调度服务和一个统一 WebUI 组成。各阶段可以保留轻量调试页，但不各自建设完整生产工作台，也不各自实现资源调度。

### 统一服务契约

所有 Provider 统一提供 Job 语义：

```text
POST /jobs
GET  /jobs/{job_id}
POST /jobs/{job_id}/cancel
POST /jobs/{job_id}/retry
GET  /jobs/{job_id}/artifacts
GET  /jobs/{job_id}/events
```

核心共享对象：

- `Job`：provider/type/input_refs/parameters/resources/status；
- `Artifact`：不可变产物、URI、hash、媒体元数据、producer/model/version；
- `Event`：started/progress/blocked/retrying/failed/succeeded/approved 等运行事件；
- `ProviderManifest`：能力、输入输出 schema、资源需求、可否 checkpoint/重试；
- `ReviewDecision`：人工批准、拒绝、修改和局部重跑记录。

服务之间只传 `artifact_ref` 和结构化 JSON，不直接依赖其他服务的内部目录。Provider 可以独立部署和替换；Artifact、Event、Job 状态和资源租约由平台层统一记录。

### 编排服务职责

编排服务独立成为服务，负责 DAG/依赖、串并行、状态、失败重试、暂停/恢复、人工审核门、资源租约、artifact provenance 和任务事件；它不实现 TTS、H3、音乐或 ffmpeg 的内部逻辑。

当前已有 `hive-resource daemon` 作为资源租约/观测中心，不再在每日视频系统里复制 GPU 调度。编排器只声明资源需求并申请租约；H3 仍按 GPU 独占 job 调度，Breeze/Music/Render 按各自资源画像排队或并行。

### 开发顺序共识

不采用“先把所有服务完整做完再串”，也不采用“各服务孤立开发最后才对接口”。采用：

```text
统一契约与架构文档
→ 编排骨架
→ Fake Source/Director/TTS/H3/Music/Render/QC 跑通假全链路
→ 逐个替换真实 Provider
→ 每替换一个 Provider 就做阶段验收
```

建议替换顺序：Source → Director → Breeze → Timeline/Render → H3 数字人 → H3 B-roll → Music/SFX → QC/Review/Publish。H3 数字人可由独立任务线开发，但必须实现统一 Host Provider 契约。

### 下一步

先写并 review 正式架构文档（候选：`docs/31_daily_video_service_architecture.md`），再拆分编排器、Source、Director、Breeze、H3、Timeline/Render、QC/Review 等实施任务；在文档 review 通过前不开始大规模服务开发。

## 2026-09-07 方案扩展讨论与调研结论

用户确认目标不是一次性自动生成脚本，而是建设可持续优化的每日节目生产系统：各阶段可扩展、可替换、可观测，并支持新闻/主持/博客/对谈/访谈/娱乐/严肃内容以及真人出镜混合。

已完成三方向独立调研：

- 自动化视频/新闻生产：Pictory、Remotion、OpenKlip/OpenChatCut、Genblaze、OpenMontage 等共同采用脚本与时间线分离、结构化项目和可替换 provider。
- Source→证据→导演：NotebookLM、LangGraph、事实核验研究和视频理解方案表明必须保留 raw/normalized/evidence/analysis，并用 Format Profile 控制节目形态、广度深度和审核策略。
- 工作台/可观测性：Dify、n8n、Temporal、OpenTelemetry/Langfuse、OpenTimelineIO、Kitsu/ResourceSpace 等表明工作台、可靠执行层、观测层要分离；人工审核要可暂停/恢复；素材文件与素材语义要分离。

形成的架构原则：

1. 节目类型是版本化 `Format Profile`，不是导演 Prompt 中的隐含分支。
2. Source、Normalized、Evidence/Claim、Editorial、Script/Storyboard、Media、Timeline、QC、Delivery 为稳定层次。
3. Agent 只生成受约束的结构化中间产物；渲染器执行 Timeline JSON；不让 Agent 直接拼任意 FFmpeg filter graph。
4. 视频素材理解独立成阶段，逐步加入 ffprobe、ASR/WhisperX、OCR、shot detection、VLM 和说话人分析，输出多标签概率与时间定位。
5. 最终音频母带是真实时间轴，数字人/真人视频是视觉层，字幕跟随母带，符合既有 H3 经验。
6. 每个 artifact 记录输入引用、版本、模型/Prompt、状态、事件和失败原因；未来可接 Web 工作台、OpenTelemetry、LangGraph/Temporal、OTIO。

## 2026-09-07 最小闭环 POC

新增 `docs/29_daily_video_system.md`、`tools/daily_video_poc/`。

运行命令：

```bash
python3 tools/daily_video_poc/poc.py \
  tools/daily_video_poc/example_topic.json \
  --out /tmp/daily-video-poc-run \
  --profile news_brief
```

已实测成功：生成 `evidence.json`、`claims.json`、`script.json`、`storyboard.json`、`timeline.json`、`subtitles.srt`、`qc.json`、`run.json`/`manifest.json` 和可播放 `preview.mp4`；六种 profile 均可运行。当前音频是 ffmpeg 占位音轨，Breeze/H3/真实 Source/媒体理解作为后续 provider 接入，不改变主流程契约。

## 2026-09-07 开源编排/UI/审计/资源监控调研

用户明确要求先广泛检索现有开源方案，当前先手动逐阶段完成，不急于自动化。已检索官方资料并形成 `docs/30_open_source_workflow_ui_research.md`。

调研结论：

- LangGraph：适合研究/导演/脚本等动态 Agent 子流程；不应作为整个内容生产系统的总平台，因为它不提供成熟的媒体资产、时间线审阅和 GPU 资源 UI。
- Kestra：流程画布、Pause/Resume、审批、执行历史、重试和 Replay 贴合“每阶段审核/重来”；部署和 YAML/插件体系较重。
- Windmill：Python/TS/Go/Bash 脚本、流程编辑器、Approval/Suspend、分支/重试，最接近“脚本工具组合 + 人工操作”；需评估 AGPL 与内容工作台边界。
- Prefect：Python-first、UI、暂停/恢复/typed input/重试，最适合 Python POC；业务内容审阅 UI 仍需补。
- Temporal：可靠性和长期恢复最强，但当前手动生产阶段过重；未来无人值守/跨天/大规模时再评估。
- Dagster：资产 lineage/质量检查强，偏数据资产，不是节目人工审片首选。
- n8n/Activepieces/Inngest：适合连接器和事件自动化，不建议作为内容生产核心状态真相。
- OpenKlip/OpenChatCut：最接近 Agent 修改项目、浏览器人工审阅、可撤销/可编辑时间线；需实测平台和许可证限制。
- Remotion/OTIO：分别适合程序化渲染和可交换时间线，不是工作流执行器。
- ComfyUI：已有 `/prompt`、`/queue`、`/history`、`/system_stats`、`/ws`、`/interrupt`、`/free`，应继续作为媒体生成 worker/provider。
- 审计和观测需分层：MLflow 或自建 manifest 管内容 Run/Artifact；OpenTelemetry 做标准埋点；Langfuse/Phoenix 选一个做 Agent trace；Prometheus/Grafana/DCGM 做系统/GPU监控。

当前不拍板单一平台。候选验证顺序：

1. 先用 pi + 文件型项目 + ComfyUI 现有 UI/API 手动跑完整流程。
2. 用同一份三阶段假流程分别试 Kestra、Windmill、Prefect：每阶段暂停、查看输出、人工编辑、拒绝、局部重来。
3. 在研究/导演阶段嵌入 LangGraph，对比其 Agent checkpoint/人工修改恢复体验。
4. 再决定是否引入总编排器；不要让编排器内部状态成为内容真相。

## 2026-09-07 架构文档 v0.1

- 新增 `docs/31_daily_video_service_architecture.md`，将当前讨论固化为可 review 的服务架构基线。
- 明确三层边界：统一 WebUI、独立 Workflow Orchestrator、可替换 Provider；ComfyUI 继续作为媒体生成 worker，资源统一复用 hive-resource。
- 固化 `Project/FormatProfile/Run/Job/Artifact/Event/ReviewDecision` 及 ProviderManifest、统一 Job API、Artifact 引用和不可变版本语义。
- 固化编排状态、retry/replay/edit-and-rerun 三种恢复语义、持久化人工审核门、Timeline JSON 与最终音频母带为时间轴真值。
- 开发顺序仍为：架构 review → Fake 全链路 → Source → Director/Breeze → Render/H3 Host → B-roll/Music/QC → WebUI/定时/发布。
- 下一步：对架构文档做 review；review 通过后建立编排骨架和 Fake Provider，先验收暂停/拒绝/重试/replay，再替换真实 Provider。

## 2026-09-07 编排框架评估启动

- 用户确认开始对开源框架做实际体验后再确定底座，当前仍在 `comfy-ops`，因为候选必须直接验证现有 POC、Provider 和 Artifact 契约。
- 新增 `docs/32_orchestrator_framework_evaluation.md`，首批评估 Conductor OSS、Temporal、Kestra；Windmill/Prefect 放第二批对照。
- 统一 Fake Pipeline：Source → Director → Human Approval → Render；要求 Python/Node Worker、暂停恢复、失败重试、Replay、服务重启恢复、资源标签、事件审计和版本语义。
- 本机 Docker/Compose/Node/Python 可用；Java 缺失，Conductor 采用官方 Docker 单容器，不安装主机 JVM；本轮不占 GPU。
- 下一步：启动 Conductor 并完成 E1–E10 第一轮，再用同一测试矩阵验证 Temporal/Kestra。
- Conductor 官方 Docker 镜像拉取两次均因 Docker Hub TLS handshake timeout 失败；未将其记为框架失败。
- VPN 全局模式下重试仍失败；宿主机 curl 能访问 Docker Registry（HTTP 401），但 docker daemon 代理为空，当前更像 daemon 网络路径未继承 VPN/代理。
- 新增 `tools/framework_eval/` 统一 Fake Pipeline 夹具（Source → Director → Approval → Render）和 `framework-eval-run.v1` manifest，用于后续候选框架横向接入。
- 用户已启动 Conductor Docker 容器并映射到 `127.0.0.1:18080`；健康检查 HTTP 200，OpenAPI `/api-docs` 可用。
- 新增 `conductor_probe.py`，用于注册三段 workflow 并由 Python Worker 通过 REST poll/complete，下一步执行并记录结果。
- Conductor Python Worker 探针已干净跑通唯一命名的 Source → Director → Render：最终 `COMPLETED`，3 个阶段各一次，产出 artifact refs 和 manifest。
- 首次调试暴露旧队列任务串扰；已清理本次创建的两个孤儿 Run，并让探针每次使用唯一 workflow/task 名，后续需要补充 Worker 幂等与任务归属策略。
- Node.js Worker 探针已通过同一 REST poll/complete 契约跑通并最终 COMPLETED；HUMAN 探针已验证进入 IN_PROGRESS，外部提交 approved 后同一 Run 恢复并 COMPLETED。
- Conductor 已完成 Restart 测试；故意失败一次后自动生成 retry task，第二次完成后 Run COMPLETED。未设置 retryDelaySeconds 时默认等待约 60 秒，后续 H3 Job 需显式设置超时/重试参数。
- Conductor 中间节点 Rerun 已通过：从 Director task 重新执行到 Render，原 Run 最终 COMPLETED；新增 `conductor_restart_probe.py`，准备测试 HUMAN 等待期间的容器重启恢复。
- HUMAN 等待期间重启 Conductor 容器后任务仍为 IN_PROGRESS，外部审批后原 Run COMPLETED，E6 通过。资源标签可以作为 Worker 路由元数据，但真实 GPU/VRAM 租约仍需接 hive-resource。
- 同一 workflow 注册 v2 后新 Run 使用 v2、旧 Run 保留 v1，E9 通过；Conductor 第一轮 E1-E6/E8-E10 已通过，E7 仅验证路由元数据，真实资源租约仍需接 hive-resource。
- 当前判断：Conductor 可作为通用编排底座候选，不能替代本项目 Artifact Store、媒体时间线、GPU 资源中心和内容审核 UI；下一阶段进入 Temporal/Kestra 对照或先做 Conductor Adapter 骨架，待用户决定优先级。
- Temporal 对照环境已启动：Postgres + `temporalio/auto-setup`，gRPC 映射 `127.0.0.1:17233`；已补最小 dynamic config，下一步运行 Python SDK 的活动重试 + Approval Signal + Render 流程。
- Temporal admin-tools 创建 default namespace 超时，但服务自带 `temporal-system` namespace 且 Docker 网络端口可达；探针改用该 namespace 继续验证，不把初始化工具问题当作 Temporal 编排能力失败。
- Temporal Python 探针已通过：Source → Director → Approval Signal → Render 完成，Director 故意首次失败、第二次成功，`director_attempts=2`；验证 Durable Execution、活动重试和持久化 Signal。
- Kestra 镜像已启动并完成 H2 初始化；尝试官方 basic-auth=false 配置（挂载 YAML、KESTRA_CONFIGURATION、全新卷）后 API 仍返回 401，暂记为认证/启动配置问题，未把它误判为框架能力失败；下一步若继续需专门按 Kestra 1.3.37 的配置加载方式处理。
- 用户确认 `hive-resource` 后续作为独立服务，不并入编排器本体。统一 Fake Pipeline 再跑通一次：`fake_pipeline.py` 输出 `run_eval_cb07d4e48a`，7 个事件、3 个 Artifact。
- 当前推进决策：先以 Conductor 作为第一版 Orchestrator Adapter 基线；Temporal 保留替代路径，Kestra 暂不进入主链路。下一步建立项目侧 Run/Job/ReviewDecision/Event 与 Conductor ID 的映射骨架，保持 Provider/Artifact/WebUI 与编排器解耦。
- 已新增 `tools/daily_video_poc/conductor_adapter.py` 与 `conductor_adapter_probe.py`；真实 Conductor E2E 通过 Adapter 启动并查询 Run，再由独立 Worker 完成三阶段，Run `e5701600-433a-4fd0-93c2-13c40b007b05` 使用 workflow v1 且最终 `COMPLETED`。
- Adapter 已补 `approve()` 与 `rerun_from()`；HUMAN 审核真实验证通过：Run `6b4a2814-3558-4ee6-874d-07ad7305d7db` 进入审核暂停，提交 approved 后 COMPLETED。代码审查发现空 poll 响应未处理，已修复并重新跑通 Adapter E2E（Run `a38c04bc-b69f-495d-b561-5dd59bded3de`）。
- 已新增 `artifact_store.py`（内容哈希、不可变 JSON Artifact）和 `review_decision()`；拒绝路径实测 Run `54db86e6-0e94-46d3-9397-34b9e56713bf` 提交 `rejected/证据不足` 后 Conductor COMPLETED，ReviewDecision Artifact 保存成功。重要约束：业务层必须按 decision 分支，不能把编排器 COMPLETED 等同内容批准。
- 阶段性垂直切片验收通过：`daily_video_poc` 生成 8 个 Artifact 文件、4 个阶段事件和 32 秒 `preview.mp4`；ffprobe 确认 H.264/AAC、1280×720，QC `pass`。Fake Pipeline 的 rejected 分支生成 2 个 Artifact、保留 `证据不足` 类审核结果且不进入 Render。
- 修改闭环已完成：`ArtifactStore.revise_json()` 生成新内容哈希并以 `supersedes` 链接旧 Artifact，旧版本保持可读；结合 `ConductorAdapter.rerun_from()` 形成审核拒绝→修改→局部重跑语义。回归验证旧/新 Script Artifact 均可读，FFmpeg POC 仍生成 32 秒预览。
- Provider 替换开始：新增 `source_provider.py`，以 `source-json@0.1` manifest 声明 Source 输入/输出、资源和失败类别，支持本地/HTTP JSON，补充 collection provenance；接入 daily POC 后仍成功生成预览视频。
- Director Provider 已接入：新增 `director_provider.py`，以 `director-template@0.1` manifest 输出带 evidence_ids、fact_status 和 producer provenance 的 `script.v1`；Source → Director → FFmpeg 回归通过，QC 为 pass。
- TTS Provider 已接入：新增 `audio_provider.py`，以 `tone-tts@0.1` manifest 接收 Script/Timeline 输出 WAV；实测 WAV、Timeline、最终 MP4 均为 32 秒，MP4 为 H.264/AAC，验证音频母带作为时间轴真值。
- Render/QC 已拆出：新增 `render_provider.py`（`ffmpeg-render@0.1`）和 `qc_provider.py`（`basic-qc@0.1`）；完整 Source→Director→TTS→Render→QC 回归生成 11 个 Artifact，证据覆盖、Artifact 完整性、时间轴正时长、媒体时长一致性四项检查全部通过。
- 新增 `vertical_slice_verify.py` 作为可重复结构审查入口；检查五个 Provider Manifest 后运行完整链路，输出 11 个 Artifact、5 个阶段事件，QC 全部通过。
- 结构审查入口已扩展：除五个 Provider Manifest 外，自动验证 workflow 的 Source/Director/TTS/Approval/Decision 拓扑和 approved 分支约束；回归仍通过，输出 11 个 Artifact、5 个事件，QC 四项 true。
- 编排拓扑已落地：新增 `workflow_definition.py`（Source→Director→TTS→HUMAN Approval→Render→QC）和 `register_workflow.py`；已在 Conductor 注册并启动验证，Source 首个 task 进入 SCHEDULED，测试 Run 已精确清理。
- Provider Worker 已完成真实 E2E：新增 `conductor_provider_worker.py`，Run `5c8f125b-6396-43f7-bcff-6b2cc07c34f1` 的 Source/Director/TTS/Render/QC 均由 Worker 执行，外部批准 HUMAN 后 Run COMPLETED；Worker 按 workflow ID 隔离运行目录并输出本地 Artifact。代码审查修复了 Conductor 完成接口纯文本响应解析问题。
- 结构审查发现旧拓扑拒绝后仍可能继续 Render，已新增 Decision route（`caseValueParam=decision`，输入来自 `${approval.output.decision}`），仅 approved 分支包含 Render/QC。批准 Run `0f8275c4-4d6f-4cca-a14d-7a7157fea307` 全部完成且 QC pass；拒绝 Run `b367f18d-3745-4e63-aa38-ae0c4f2e2298` 只到 route，无 Render/QC，分支语义通过。
- 交付审查完成：framework_eval README 补齐垂直切片/Conductor/Worker 命令，Worker 移除未使用依赖；Python 编译、diff check 和结构验收均通过。
- Worker 审计已补齐：结束时写入 `daily-video/conductor-run.v1` Manifest，记录 task/审核事件和 Artifact 清单；Run `b8326300-0dfd-4b21-9745-aca197113a13` COMPLETED，10 个 Artifact。修复审核 blocked→completed 状态转换的事件记录问题。
- Worker 失败回报与重试已验证：故意使用不存在 Source 文件，Run `d71e4c11-5bec-4c16-ae3d-7d43e7bbf5f8` 回报 `FileNotFoundError`，Conductor 重试 Source 2 次后最终 FAILED；Manifest 保留 3 次 started/failed 事件和失败分类。
- 收尾验收：`vertical_slice_verify.py`、Python 编译、diff check、Conductor health 和审计 Manifest 全部通过；本轮小型流程完成。真实 Breeze-TTS/H3/外部 Source/WebUI 作为后续任务，不混入本轮完成条件。
