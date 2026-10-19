# 开源流程编排、可视化、审计与资源监控调研

> T-comfy-ops-32，2026-09-07。本文只记录官方文档/官方仓库可确认的能力，暂不做安装和最终选型。
> 当前使用目标：先人工逐阶段完成每日话题视频；每阶段可查看、审核、修改、重做，并保留可审计产物。

## 1. 先给结论

没有一个现成开源项目同时做好：

```text
资料研究 + Agent 编排 + 人工审核 + 媒体时间线 + GPU 资源监控 + 完整审计
```

候选项目实际分为五类：

| 层 | 代表项目 | 主要解决的问题 |
|---|---|---|
| 流程执行 | Kestra、Windmill、Prefect、Temporal、Dagster | 状态、暂停、重试、并行、执行记录 |
| AI 流程 UI | Dify、Flowise、Langflow | Agent/LLM 节点、工具、Prompt、调试 |
| 媒体工作台 | OpenKlip、OpenChatCut、Remotion、OTIO、Kitsu、ResourceSpace | 素材、脚本、时间线、人工审阅、版本 |
| Agent 审计 | OpenTelemetry、Phoenix、Langfuse、MLflow | LLM/tool/retrieval trace、成本、延迟、评估 |
| 资源监控 | Prometheus、Grafana、NVIDIA DCGM、Ray Dashboard、Flower | GPU、CPU、队列、worker、任务状态 |

因此 LangGraph 不是整体方案的“最佳选择”。它更准确的定位是：为复杂、有状态的 Agent 子流程提供运行时；它不提供完整的媒体项目管理、时间线审阅和 GPU 运维 UI。

## 2. 工作流执行候选

### LangGraph

官方定位是长时间运行、有状态 Agent 的底层编排运行时，核心能力包括 durable execution、持久化、人工介入和流式执行。[官方 Overview](https://docs.langchain.com/oss/python/langgraph/overview)

适合：

- Source Planner → 多路检索 → Claim/Evidence → Director 的动态 Agent 流程；
- 条件分支、循环核验、evaluator-optimizer；
- 需要保存 Agent 状态并从 checkpoint 恢复的流程。

不足：

- 不是媒体资产管理系统；
- 不是视频时间线编辑器；
- 不是 GPU/ComfyUI 队列调度器；
- 可视化重点是 Agent graph，不是节目资料、镜头和素材审阅工作台。

### Temporal

Temporal 是通用 durable execution 平台，目标是让工作流在进程崩溃、网络故障或基础设施重启后继续运行，并提供重试、任务队列和持久状态。[官方文档](https://docs.temporal.io/)

适合：

- 后期无人值守的每日生产；
- H3、TTS、渲染等长时间外部任务；
- 任务级重试、超时、恢复和长期等待。

不足：

- 工程和部署重量大；
- 内容编辑、人工审阅和素材关系仍需自行开发。

### Kestra

Kestra 对当前“每阶段可视化、审核、重来”的匹配度很高：支持 UI 中暂停/恢复、查看日志和输出、人工审批；任务支持重试；还区分 restart（同一执行重试失败任务）与 replay（从任意节点创建新执行）。[Pause/Resume](https://kestra.io/docs/how-to-guides/pause-resume)、[Retries/Replay](https://kestra.io/docs/workflow-components/retries)

特别有价值的是：暂停状态会持久化在数据库中，服务器重启后仍可等待人工恢复。[Human-in-the-loop](https://kestra.io/docs/use-cases/approval-processes)

不足：

- YAML/插件/服务体系较重；
- 媒体素材、时间线和内容对象仍需外部工作台；
- 对 Python 本地脚本、ComfyUI 队列和 GPU 独占需要自行封装 worker。

### Windmill

Windmill 是开源 workflow engine + developer platform，支持 Python、TypeScript、Go 等脚本；Flow 支持分支、循环、审批和重试，也可以构建 React/Svelte UI。[官方 Getting Started](https://www.windmill.dev/docs/getting_started/how_to_use_windmill)

它的人工审批支持暂停、恢复、取消、超时和审批输入，并可通过 UI 或 webhook 恢复。[Suspend & Approval](https://www.windmill.dev/docs/flows/flow_approval)

适合：

- 用现有 Python/TS 脚本拼工作流；
- 自定义阶段 UI；
- 手动执行和审批；
- 以后再接定时、Webhook 和队列。

不足：

- 更像开发者平台和脚本工作流，不是媒体编辑器；
- AGPLv3 和自托管边界需单独评估。[官方 GitHub](https://github.com/windmill-labs/windmill)

### Prefect

Prefect 适合 Python 优先的工作流：有 UI 查看 flow runs、任务级重试、超时，并支持暂停/恢复和交互式人工输入。[Flows](https://docs.prefect.io/latest/tutorial/flows)、[Interactive Workflows](https://docs.prefect.io/v3/advanced/interactive)、[Retries](https://docs.prefect.io/v3/how-to-guides/workflows/retries)

适合：

- 复用已有 Python source、媒体分析和渲染脚本；
- 先用代码定义流程，UI 看运行结果；
- 不想立即维护一套 YAML/节点插件系统。

不足：

- 流程画布和内容工作台能力弱于专门的可视化工具；
- 资料、脚本、素材和时间线仍需自定义。

### Dagster

Dagster 是以资产为中心的数据编排器，强调 lineage、observability、testability；Asset Checks 可以在 UI 中查看资产质量结果，并阻塞下游执行。[官方 Overview](https://docs.dagster.io/)、[Asset Checks](https://master.dagster.dagster-docs.io/concepts/assets/asset-checks)

适合：

- 把 raw、normalized、evidence、transcript、script、render 当作可追溯资产；
- 质量检查、依赖关系和数据血缘。

不足：

- 原生思路偏数据平台；
- 人工内容审核和媒体时间线不是其主要 UX；
- H3 生成任务仍要包装成外部 asset/job。

## 3. AI 流程和可视化 UI 候选

### Dify

Dify 提供自部署的 Agentic Workflow Studio、知识库、插件和监控面板。[官方主页](https://dify.ai/)

适合：

- 资料分析、RAG、Director Agent、工具调用和人工审核原型；
- 快速让用户观察 AI 节点输入输出。

不足：

- 核心对象是 AI 应用，不是媒体资产/时间线；
- ComfyUI/H3/Breeze 需要自定义工具或服务；
- 很难直接表达“某个脚本句对应某个镜头和证据”的编辑 UX。

### Flowise

Flowise 是开源的 Agent/LLM workflow 平台，包含 Assistant、Chatflow、Agentflow 三种可视化构建器，以及 tracing、evaluation、human-in-the-loop 等能力。[官方文档](https://docs.flowiseai.com/)

适合快速试验 Agent 和工具链；不应直接当作完整媒体工作台。

### Langflow

Langflow 通过可视化编辑器搭建组件流，支持 Playground、日志、API、导入导出和自定义组件；官方还区分 IDE（编辑/调试）与 headless runtime（生产执行）。[Visual Editor](https://docs.langflow.org/concepts-overview)、[Deployment Architecture](https://docs.langflow.org/deployment-architecture)

适合：

- 组件化的 Source/Research/Director 流程原型；
- 快速测试自定义 Python 组件。

不足：

- 对话/AI flow 语义比媒体生产语义强；
- 自定义组件可能带来版本与安全治理问题；
- 需要自己补素材库、审核队列和时间线。

### React Flow

React Flow 是 MIT 开源的 React 节点图 UI 库，支持自定义节点、保存/恢复、校验、撤销重做、缩放和协作等基础能力。[官方 Examples](https://reactflow.dev/examples)

它不是执行引擎，但最适合成为项目自己的“阶段图/证据图/资产关系图”前端底座。执行、状态和审计必须接外部 runner。

## 4. 媒体工作台与时间线

### OpenKlip / OpenChatCut

OpenKlip 是 MIT、local-first 的 Agent-native 视频工具：Agent 或 CLI 修改项目，浏览器审阅同一个 `project.json`，支持 transcript cuts、字幕、overlay 和导出。[OpenKlip](https://openklip.com/)

OpenChatCut 强调本地、可编辑、可撤销的多轨时间线；Agent 的每次修改都保留在真实时间线中，而不是只生成不可编辑 MP4。[OpenChatCut](https://openchatcut.com/about)

这两个项目对 T-32 的启发最直接：

- Agent 修改结构化项目；
- 人在浏览器中审阅；
- 每个动作可撤销或继续编辑；
- 预览和最终导出分离。

需要实际验证平台、许可证、媒体格式和是否能容纳我们的 Evidence/Claim 关系。

### Remotion

Remotion 用 React/代码生成视频，支持浏览器预览、逐帧拖动、数据驱动、批量渲染和构建视频编辑器。[官方主页](https://www.remotion.dev/)

适合：

- 将结构化 Timeline 渲染成可预览的节目；
- 做字幕、标题卡、来源标记和固定节目模板；
- 后续做自定义可视化编辑器。

它不是工作流状态机、素材库或 GPU 队列系统。

### OpenTimelineIO

OTIO 是 editorial cut information 的 API 和交换格式，支持 clip、track、transition、marker、metadata，并通过 adaptor 对接其他剪辑工具；媒体文件本身由外部引用，不嵌在 OTIO 内。[官方文档](https://opentimelineio.readthedocs.io/en/latest/)

适合作为 T-32 内部 Timeline 的长期抽象，避免把时间线写死在某条 FFmpeg 命令里。

### ComfyUI

ComfyUI 已经提供生成阶段所需的队列、历史、系统状态、WebSocket 进度、取消和内存释放 API：`/prompt`、`/queue`、`/history`、`/system_stats`、`/ws`、`/interrupt`、`/free` 等。[官方 Server Routes](https://docs.comfy.org/development/comfyui-server/comms_routes)

因此 ComfyUI 适合作为 Media Provider/Worker，不适合作为整个节目生产工作台。

## 5. 审计与可观测性

### OpenTelemetry

应作为底层 trace/metric/log 协议，不把审计格式绑定在 LangGraph、Dify 或某个 UI 上。

建议每个阶段记录：

```text
run_id
stage_id
input_artifact_ids
output_artifact_ids
skill_version
tool_version
model/prompt version
start/end/duration
resource snapshot
review action
failure class
```

### Phoenix

Phoenix 是开源、自托管的 AI observability/evaluation 平台，基于 OpenTelemetry/OpenInference，可记录 LLM、retriever、tool、agent、evaluator 等 span，并支持 tracing、datasets、experiments 和 prompt 评估。[Phoenix GitHub](https://github.com/Arize-ai/phoenix)

适合：

- 审计 Source Agent、导演 Agent、事实核验 Agent；
- 检查检索结果、模型输入输出、耗时、Token、错误和评估。

### Langfuse / MLflow

Langfuse 的 trace/observation 模型适合 LLM/Agent 调用树；MLflow 的 OpenTelemetry tracing 可以记录输入输出、延迟、span 类型、Token 和模型名。[MLflow LLM Tracing](https://mlflow.org/llm-tracing)、[MLflow/Phoenix Integration](https://mlflow.org/docs/latest/genai/tracing/integrations/listing/arize/)

这些工具解决的是“为什么 Agent 这样做”，不能替代“这个媒体文件如何审阅和重做”。

## 6. 资源、GPU 和队列监控

### ComfyUI 自身

先利用 ComfyUI 已有的 `/queue`、`/history`、`/system_stats` 和 WebSocket，不要重复造生成队列。[ComfyUI API](https://docs.comfy.org/development/comfyui-server/comms_routes)

### Prometheus + Grafana + DCGM Exporter

NVIDIA DCGM Exporter 将 GPU telemetry 暴露为 Prometheus metrics，可用 Grafana 展示 GPU 利用率、显存、温度和功耗等。[DCGM Exporter](https://docs.nvidia.com/datacenter/dcgm/latest/gpu-telemetry/dcgm-exporter.html)

这适合记录：

- 哪个阶段占用 GPU；
- H3/Breeze/视频理解的显存峰值；
- 队列等待时间与实际运行时间；
- OOM、温度和功耗异常。

### Ray Dashboard

Ray Dashboard 提供 jobs/tasks、日志、CPU/内存/GPU 分配和 Prometheus/Grafana 指标视图。[官方 Dashboard](https://docs.ray.io/en/latest/ray-core/ray-dashboard.html)

它适合多 worker/多 GPU 批处理，但当前单机 4090 手动生产阶段未必需要引入 Ray。

### Flower / Celery

如果以后用 Celery 处理 CPU/媒体任务，Flower/Celery events 可观察 worker、队列和任务历史。[Celery Monitoring](https://docs.celeryq.dev/en/stable/userguide/monitoring.html)

## 7. 按当前“手动逐阶段”目标的候选组合

### 组合 A：最小、贴近现有项目

```text
pi
  + project files / JSON artifacts
  + ComfyUI existing UI/API
  + OpenKlip 或 OpenChatCut（媒体审阅）
  + Remotion/FFmpeg（Timeline render）
  + OpenTelemetry JSON 或 Phoenix（Agent audit）
  + nvidia-smi/DCGM later（资源）
```

优点：不引入重型 workflow server，先把人工审阅体验做对。

### 组合 B：现成的人机审批/重跑优先

```text
Windmill 或 Kestra
  + Python/TS stage scripts
  + 自定义 artifact/project UI
  + ComfyUI API
  + Phoenix/OpenTelemetry
  + Prometheus/Grafana/DCGM
```

优点：暂停、审批、恢复、重试、执行日志现成；比较符合“每阶段审核和重来”。

代价：引入服务、权限、数据库和部署复杂度。

### 组合 C：Agent 图和复杂研究优先

```text
LangGraph
  + 自定义 Web UI / React Flow
  + ComfyUI API
  + OTEL/Phoenix
  + Prometheus/Grafana/DCGM
```

优点：最适合动态研究、循环核验、Agent 分支和 checkpoint。

代价：几乎所有资料、媒体、审核、时间线和资源页面都要自己补。

## 8. LangGraph 是否最好

结论：不是整体最优；它只在“复杂 Agent 决策图”这一层有明显优势。

当前阶段排序建议：

1. 先不选 LangGraph 作为总平台；用 pi + 文件型项目 + ComfyUI UI/API + 媒体审阅工具验证人工流程。
2. 如果最痛的是人工审批、暂停、恢复、局部重做，优先试 Kestra 或 Windmill。
3. 如果最痛的是 Python 编排和运行记录，试 Prefect。
4. 如果最痛的是复杂研究 Agent 的状态、循环和 checkpoint，再试 LangGraph。
5. 如果未来进入无人值守、多天等待、严肃可靠性，再评估 Temporal。

“可视化流程”不等于“一个大画布”：

- 流程图：看阶段和依赖；
- 证据图：看来源→Claim→脚本→镜头；
- 素材库：看媒体语义和版权；
- 时间线：看音视频编排；
- 运行面板：看日志、失败、重试和资源。

任何单一项目都不应被强行用来承载全部这些视图。

## 9. 下一步验证顺序

这次只做手动验证，不做自动化生产：

1. 用 ComfyUI API/UI 验证一个 H3 片段任务的提交、进度、历史、取消和重做。
2. 用 OpenKlip/OpenChatCut 评估“Agent 修改项目 + 人在浏览器审核”的体验和平台限制。
3. 用 Kestra 或 Windmill 做一个三阶段假流程：资料→脚本→渲染，每阶段暂停人工，支持 reject/retry/replay。
4. 用 Phoenix 或 Langfuse 记录一轮 Source/Director 调用。
5. 用 Prometheus/Grafana/DCGM 记录一次 H3 的 GPU/显存/耗时。
6. 对比上述体验后，再决定是否需要 LangGraph。
