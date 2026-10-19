# 编排框架横向评估计划

> 任务：T-comfy-ops-32；版本：v0.1；日期：2026-09-07。
> 目的：用同一条最小 Fake Pipeline 体验候选框架，再决定每日视频系统的编排底座。本文记录方法和证据，不提前拍板。

## 1. 当前结论

继续在 `comfy-ops` 评估是合适的：候选框架要直接连接本项目已有的 `daily_video_poc`、ComfyUI/H3/Breeze Provider、Artifact 契约和 `hive-resource`。未来若编排器成为独立产品，再把稳定的协议和运行服务拆出。

首批候选：

| 候选 | 主要验证问题 | 初步定位 |
|---|---|---|
| Conductor OSS | JSON/HTTP 编排、语言无关 Worker、审批、重试、Replay 是否完整 | 最可能的总编排器候选 |
| Temporal | Durable Execution、跨天等待、崩溃恢复和代码式工作流体验 | 可靠性上限候选 |
| Kestra | 画布、YAML、人工暂停/审批、执行历史和操作体验 | 可视化编排候选 |

Windmill 暂列第二批：它很适合 Python/TypeScript 脚本、内部工具和自动生成 UI，但需单独评估 AGPLv3 及其“平台”属性。Prefect 作为 Python-first 对照，不作为第一轮总底座。

Temporal 对照使用官方 `temporalio/auto-setup` + PostgreSQL，Python SDK 使用临时依赖目录，不污染项目运行环境；测试暂使用镜像自带的 `temporal-system` namespace，避免把 namespace 初始化误判为编排能力问题。

## 2. 统一测试流程

```text
Fake Source → Fake Director → Human Approval → Fake Render
```

每个框架都用相同的输入和输出：

- 输入：`topic.json`；
- 中间产物：`evidence.json`、`script.json`、`timeline.json`；
- 审批：接受 / 拒绝并附修改原因；
- 输出：`preview.mp4` 占位文件、QC JSON、事件记录；
- Worker 至少两种语言：Python 和 Node.js；
- Worker 之间只传结构化 JSON 和 `artifact_ref`，不传共享内部目录。

## 3. 必测能力

| 编号 | 能力 | 通过条件 |
|---|---|---|
| E1 | 外部 API/CLI 创建运行 | Web/Pi 可不依赖框架 UI 启动任务 |
| E2 | 多语言 Worker | Python、Node.js Worker 都能领取并回报 Job |
| E3 | 人工审核 | 流程持久化暂停，提交决定后从原节点继续 |
| E4 | 失败重试 | 只重试失败节点，保留 attempt 和错误 |
| E5 | Replay | 从中间节点重新运行，不覆盖旧 Run/Artifact |
| E6 | 服务重启恢复 | 编排器/Worker重启后状态、队列和审批仍在 |
| E7 | 并发与资源标签 | 能限制 H3 类 Worker 独占 GPU/队列 |
| E8 | 事件和审计 | 能取得输入、输出、耗时、日志、失败和人工决定 |
| E9 | 版本语义 | 修改流程后旧 Run 仍按旧版本可追溯 |
| E10 | 接入成本 | Docker 启动、最小流程和本项目 Provider 适配耗时可记录 |

## 4. 架构判断标准

编排器只负责 Workflow、Task、Dependency、State、Retry、Approval、Event 和 Worker 调度；它不拥有 Evidence、Script、Timeline 和媒体文件的业务真相。业务真相仍由本项目 Artifact/Manifest 契约保存。

服务连接优先使用 HTTP/JSON + OpenAPI；需要实时状态时使用 WebSocket/SSE；只有在测出吞吐或类型约束不足后才引入 gRPC。Pi 和 WebUI 都作为外部客户端调用编排器 API，不能把会话状态当成任务状态。

## 5. 启动顺序

1. Conductor：Docker 单容器 + Python/Node Worker + JSON workflow。
2. Temporal：官方 Docker/Compose + Python/TypeScript workflow/worker。
3. Kestra：官方 Docker/Compose + HTTP/Python task + approval。
4. 用同一张评分表记录启动复杂度、操作体验、恢复证据、资源路由和许可证。
5. 将结果追加到本文；只有通过 E1–E9 且没有关键阻塞，才进入正式架构选型。

## 6. 当前环境

- Docker 29.1.3；Docker Compose 2.40.3；Node.js v24.18.0；Python 3.12.3。
- 本机没有 Java；Conductor 评估使用官方 Docker 镜像，不在主机安装 JVM。
- 评估任务不申请 GPU，不占用 H3/Breeze 生成队列。

## 7. 尚未拍板

- Conductor 与 Temporal 的最终选择；
- 是否需要 Kestra 的画布作为运营入口；
- Windmill 是否因脚本平台体验进入第二轮；
- Artifact Store、认证、租户和生产部署拓扑。

## 8. 实际执行记录

- 2026-09-07：本机 Docker/Compose 可用，但 Docker daemon 拉取 `conductoross/conductor:latest` 多次均因 Docker Hub TLS handshake timeout 失败；宿主机 `curl` 可收到 Docker Registry 的 HTTP 401，`docker info` 显示 daemon 的 HTTP/HTTPS proxy 为空，判断为 Docker daemon 网络路径未继承 VPN/代理；这只记录为环境网络阻塞，不作为框架能力结论。
- 2026-09-07：新增 `tools/framework_eval/` 统一夹具和本地基线，先验证输入、Artifact、Approval、Failure Event 的测试语义；待镜像可拉取后复用同一夹具接入候选框架。
- 2026-09-07：用户已提供运行中的 Conductor 容器，映射 `127.0.0.1:18080`；`/health` 返回 200，`/api-docs` 返回 OpenAPI 3.1。
- 2026-09-07：`tools/framework_eval/conductor_probe.py` 以 Python Worker 通过 REST poll/complete 驱动唯一命名的 `Source → Director → Render` 流程，最终 `COMPLETED`，3 个阶段各完成一次；输出 Artifact ref 和 manifest。证明 E1（外部 API）、E2（Python Worker）、基础 E4（任务完成回报）可行。
- 2026-09-07：首次调试的旧 Run 被 Worker 领取，暴露出测试 Worker 必须处理任务隔离/幂等；已清理两个本次产生的测试 Run，并改为每次运行生成唯一 workflow/task 名，干净复跑无串扰。
- 2026-09-07：Node.js 24 Worker 探针通过同一 REST poll/complete 契约跑通单任务 workflow，最终 `COMPLETED`，证明 E2 的 Python/Node 跨语言接入可行。
- 2026-09-07：HUMAN 探针先进入 `IN_PROGRESS`，再通过 `/api/tasks/{workflowId}/approval/COMPLETED/sync` 外部提交决定，同一 Run 恢复并 `COMPLETED`，证明 E3 的持久化人工审核门可行；官方 HUMAN task 适合作为 WebUI/Pi 审核入口。
- 2026-09-07：对已完成的 Node workflow 调用 `/api/workflow/{workflowId}/restart`，重新领取并完成任务，证明从头 Restart 可行。
- 2026-09-07：故意将一次 SIMPLE task 标记为 `FAILED`，Conductor 生成 `retryCount=1` 的新 task；第二次完成后 Run 为 `COMPLETED`，证明基础 E4 可行。未显式设置 `retryDelaySeconds` 时默认延迟约 60 秒，H3/长任务必须显式配置 retry delay、response timeout 和 total timeout。
- 2026-09-07：对已完成 Run 从 Director task 调用 `rerun`，只重新领取 Director→Render，原 Run 最终 `COMPLETED`，证明 E5 的中间节点 Rerun 可行。
- 2026-09-07：HUMAN 任务进入 `IN_PROGRESS` 后重启 Conductor 容器，健康检查恢复后任务仍为 `IN_PROGRESS`；外部完成审批后原 Run `COMPLETED`，证明 E6 的服务重启恢复可行。
- 2026-09-07：SIMPLE TaskDef 的 `isolationGroupId`/`executionNameSpace` 等字段可承载 Worker 路由元数据，但 Conductor 不知道 GPU/VRAM 的真实租约；E7 仍需由 Provider Worker 对接 `hive-resource`，不能把 Conductor 标签当作资源中心。
- 2026-09-07：同一 workflow 注册 v2 后，新 Run 使用 `workflowVersion=2`，既有 Run 仍保留 `workflowVersion=1` 且不受影响，证明 E9 的运行版本隔离可行。
- 2026-09-07：Temporal Python 探针通过 `temporal-system` namespace 跑通 Source → Director → Approval Signal → Render；Director 故意首次失败后第二次成功，结果 `director_attempts=2`，证明 Durable Execution、活动重试和持久化 Signal 可用。Temporal 的 auto-setup 默认 namespace 初始化仍需单独整理。
- 2026-09-07：Kestra 镜像已启动并完成本地 H2 初始化，但当前 `server local` 的 API 始终返回 `401`；按官方配置尝试文件、环境变量和全新数据库卷仍未取得可用 API 身份，故 Kestra 只记为“环境启动、最小流程待认证配置解决”，不据此否定编排能力。

当前矩阵：E1 ✅、E2 ✅（Python/Node）、E3 ✅、E4 ✅、E5 ✅（Restart + 中间节点 Rerun）、E6 ✅、E7 🟡（路由字段可用，真实 GPU 租约待接）、E8 ✅（任务历史/输入输出/失败/审核事件可读）、E9 ✅、E10 ✅（Docker + REST Worker 接入成本可接受）。

## 9. Conductor 第一轮结论

Conductor 已满足当前系统作为通用编排底座的核心验证条件：编排定义与 Worker 语言解耦，支持 Python/Node 接入；HUMAN 可作为 WebUI/Pi 审核门；失败重试、Restart、节点 Rerun、容器重启恢复和 workflow 版本隔离均已实测通过。

它不替代本项目的 Artifact Store、媒体时间线、GPU 资源中心或内容审核 UI。推荐的集成边界是：Conductor 保存流程执行状态；本项目保存 Artifact/Manifest/ReviewDecision；Worker 在领取 H3/Breeze 任务时向 `hive-resource` 申请真实资源租约。

## 10. 当前推进决策

在继续评估其他框架的同时，先把 Conductor 作为第一版 Orchestrator Adapter 的实现基线：它已经满足本项目当前需要的外部启动、Python/Node Worker、持久化审核、重试、局部重跑、重启恢复和版本隔离；Temporal 保留为未来需要跨天 Durable Execution 或更强代码式工作流时的替代实现；Kestra 暂不进入主链路，直到认证与配置加载问题解决并完成同一流程验证。

Adapter 只暴露项目自己的 `Run/Job/ReviewDecision/Event` 契约，Conductor 的 workflow/task ID 只作为外部映射；这样未来替换 Temporal 或其他编排器时，WebUI、Artifact Store、Provider 和 `hive-resource` 不需要改写。

已新增 `tools/daily_video_poc/conductor_adapter.py` 和对应探针。探针通过 Adapter 启动已注册的三段 workflow，再由独立 Worker 完成 Source → Director → Render；本次 Run `e5701600-433a-4fd0-93c2-13c40b007b05` 使用 workflow v1 并最终 `COMPLETED`。

Adapter 控制面又补齐了 HUMAN 审核和 `rerun_from`：审核探针创建 `t32_adapter_human_d6d1ba60`，任务确实进入 `IN_PROGRESS`，Adapter 提交 approved 后原 Run `6b4a2814-3558-4ee6-874d-07ad7305d7db` 恢复为 `COMPLETED`；局部重跑接口也已对已完成 Run 发出并由 Conductor 接受。代码审查发现并修复了空 poll 响应处理，避免无任务时把空响应误当 JSON。

拒绝路径也已实测：Run `54db86e6-0e94-46d3-9397-34b9e56713bf` 在 HUMAN 门提交 `rejected/证据不足` 后以 Conductor `COMPLETED` 结束；项目层必须读取 `ReviewDecision.decision` 再决定进入 `blocked/revise` 分支，不能把编排器的 `COMPLETED` 直接当作内容批准。新增文件 ArtifactStore 以内容哈希写入不可变 JSON，并保存 ReviewDecision 作为 Artifact。

阶段性垂直切片验收已完成：`daily_video_poc` 生成 8 个文件 Artifact、4 个阶段事件和 32 秒可播放 MP4，`ffprobe` 确认 H.264/AAC、1280×720，QC `pass`；框架基线的 rejected 分支也保留审核原因并不生成 Render Artifact。

修改闭环已补齐：`ArtifactStore.revise_json()` 为修改后的 JSON 生成新内容哈希并保留 `supersedes` 指针，旧 Artifact 不覆盖；随后由 `ConductorAdapter.rerun_from()` 从受影响 task 重跑。回归验证确认旧/新 Script Artifact 同时可读，Adapter 和 FFmpeg POC 均通过。

Provider 替换第一步已完成：`source_provider.py` 以 `source-json@0.1` manifest 声明输入/输出 schema、资源和失败类别，可从本地或 HTTP JSON 读取并补充采集 provenance；接入现有 POC 后仍生成预览视频，证明 Source 与编排器、渲染器保持解耦。

Director Provider 已接入同一链路：`director_provider.py` 以 `director-template@0.1` manifest 声明契约，输出带证据引用和事实状态的 `script.v1`；Source → Director → FFmpeg POC 回归生成预览并通过 QC。模板实现仅是当前可验证 Provider，后续可替换为模型调用。

TTS Provider 第一版已接入：`audio_provider.py` 以 `tone-tts@0.1` manifest 接收 Script/Timeline，生成 32 秒 WAV；`ffprobe` 确认 WAV 与 Timeline 同为 32 秒，最终 MP4 为 H.264/AAC 且同长，证明音频母带时间轴契约成立。

Render/QC 已拆出为独立 Provider：`render_provider.py` 使用 `ffmpeg-render@0.1` 输出 MP4，`qc_provider.py` 使用 `basic-qc@0.1` 检查证据引用、Artifact 完整性、正时长和 ffprobe 媒体时长一致性；完整链路当前生成 11 个 Artifact，QC 四项检查全部通过。

新增 `vertical_slice_verify.py` 作为结构审查/回归入口；当前一次验收同时检查五个 Provider Manifest 和 workflow 的 Source/Director/TTS/Approval/Decision 拓扑，输出 11 个 Artifact、5 个阶段事件，QC 四项检查全部为 true。后续替换真实 Provider 时必须保持该入口通过。

编排拓扑已落为 `workflow_definition.py`，并由 `register_workflow.py` 在 Conductor 实例注册成功；Decision task 按 HUMAN 输出的 `decision` 只将 `approved` 路由到 Render/QC，拒绝分支不创建这两个 task。此前直接使用 `${approval.output.decision}` 作为 `caseValueParam` 的结构审查发现其实际 case 为 null，已依据 Conductor 的 `caseValueParam` + `inputParameters` 语义修正并重新注册。

Provider Worker 已完成真实 E2E：Run `5c8f125b-6396-43f7-bcff-6b2cc07c34f1` 中 Source、Director、TTS、Render、QC 均由 `conductor_provider_worker.py` 执行，HUMAN 节点外部提交 approved 后原 Run 最终 `COMPLETED`；Worker 输出目录保留证据、脚本、音频、预览和 QC 文件。期间代码审查发现 Conductor 完成接口可能返回空/纯文本响应，已修复 Worker 的响应解析。

分支修正后的真实验收：批准 Run `0f8275c4-4d6f-4cca-a14d-7a7157fea307` 的 Source/Director/TTS/Approval/Render/QC 全部 `COMPLETED`，QC `pass`、视频 32 秒；拒绝 Run `b367f18d-3745-4e63-aa38-ae0c4f2e2298` 只完成到 route，任务列表没有 Render/QC，workflow 输出 `qc/video=null`。

交付审查补充：统一 README 已补充本地垂直切片、Conductor 注册和 Worker 启动命令；Python 编译、`git diff --check` 和 `vertical_slice_verify.py` 均通过，Provider Worker 已移除未使用依赖。

失败重试已实测：故意让 Source 读取不存在文件，Run `d71e4c11-5bec-4c16-ae3d-7d43e7bbf5f8` 由 Worker 回报 `FileNotFoundError`，Conductor 将 Source 重新调度 2 次，最终 workflow `FAILED`；Manifest 保留三次 started/failed 事件和失败分类。

## 11. T-comfy-ops-32 收尾验收

本任务的小型流程已完成：Provider-neutral 本地切片、Conductor workflow/Worker、持久化人工审核、批准/拒绝分支、Artifact 版本、失败回报与重试、运行 Manifest 和结构验收均有实测证据。真实 Breeze-TTS、H3、外部 Source 渠道和 WebUI 属于后续 Provider/产品任务，不作为本轮完成条件。

Provider Worker 审计补充：Run `b8326300-0dfd-4b21-9745-aca197113a13` 最终 `COMPLETED`，本地 `daily-video/conductor-run.v1` Manifest 汇总 10 个 Artifact 和 task/审核事件；代码审查修复审核从 `blocked` 转为 `completed` 时只记录一次的问题。
