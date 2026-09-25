# 每日话题视频生产系统服务架构

> 任务：T-comfy-ops-32；版本：v0.1；日期：2026-09-07。
> 本文是进入服务化开发前的架构基线，重点定义边界、契约、状态和验收方式；不承诺当前立刻部署所有服务。

## 1. 目标与非目标

系统目标是把每日话题生产做成可持续演进的节目生产平台，而不是一次性“主题→MP4”脚本：

- 同一套核心对象支持新闻、主持、博客、对谈、访谈、娱乐和真人出镜等 `Format Profile`；
- Source、Director、TTS、Host、B-roll、Music/SFX、Render、QC 都可以替换；
- 每个阶段可查看输入输出、暂停审核、拒绝、局部重试和从失败点恢复；
- 每个结论、脚本段、媒体产物和最终成片都能追溯到输入、版本和人工决定。

第一阶段不做：完整无人值守每日调度、分布式多 GPU、通用视频编辑器、自动替用户发布到外部平台。先用本地文件和 Fake Provider 验证稳定契约，再逐个替换真实 Provider。

## 2. 总体边界

```text
                 ┌─────────────────────────────┐
                 │         Unified WebUI        │
                 │ project / evidence / review  │
                 │ timeline / runs / resources  │
                 └──────────────┬──────────────┘
                                │ API/events
┌───────────────┐        ┌──────▼────────────────┐        ┌─────────────────┐
│ Source/Media  │───────▶│ Workflow Orchestrator │───────▶│ Artifact Store  │
│ Provider(s)   │        │ DAG/state/retry/review│        │ JSON/media/hash │
└───────────────┘        └──────┬────────────────┘        └─────────────────┘
                                │ Job + resource lease
                 ┌──────────────▼──────────────┐
                 │ Provider workers             │
                 │ Director / Breeze / H3 /     │
                 │ Music / Render / QC          │
                 └──────────────┬──────────────┘
                                │
                        ┌───────▼────────┐
                        │ hive-resource  │
                        │ GPU/CPU/port   │
                        └────────────────┘
```

三层职责必须分开：

| 层 | 负责 | 不负责 |
|---|---|---|
| WebUI | 项目、证据、素材、时间线、审核和运行可视化 | 直接调用 H3、保存流程真相 |
| Orchestrator | 依赖图、状态、Job、暂停/恢复、重试、审核门、事件和 provenance | TTS、H3、FFmpeg 或模型内部逻辑 |
| Provider | 一个明确能力的输入→Artifact 生产 | 读取其他服务内部目录、决定全局流程 |

ComfyUI 继续作为媒体生成 worker/API；Breeze、H3 和音乐模型可以先以本地 Provider 适配器实现，之后再进程化。服务间只传 `artifact_ref` 和结构化 JSON，不传共享目录路径作为隐式接口。

## 3. 稳定对象

平台对象不可变或事件化更新。重新生成产生新版本，不覆盖旧 Artifact。

### 3.1 Project、Format Profile、Run

```json
{
  "project_id": "proj_20260907_001",
  "topic": {"title": "话题", "keywords": ["..."], "time_range": "24h"},
  "format_profile": "news_brief@1",
  "target_duration_s": {"min": 30, "max": 90},
  "status": "draft|running|blocked|review|approved|delivered",
  "run_id": "run_..."
}
```

`Format Profile` 是版本化数据，不是 Director Prompt 内的隐含分支。它定义段落结构、默认节奏、证据门槛、主持人/素材比例、审核规则和允许的 Provider 类型。

### 3.2 Job、Artifact、Event

```json
{
  "job_id": "job_...",
  "run_id": "run_...",
  "provider": "breeze_tts",
  "kind": "tts",
  "input_refs": ["art_..."],
  "parameters": {"voice": "default", "seed": 123},
  "resources": {"gpu": "optional", "vram_mb": 6000},
  "status": "queued|running|paused|retrying|failed|succeeded|cancelled",
  "attempt": 1,
  "failure_class": null
}
```

```json
{
  "artifact_id": "art_...",
  "kind": "evidence|script|audio|video|timeline|qc|delivery",
  "uri": "artifacts/run_.../audio/seg_01.wav",
  "content_hash": "sha256:...",
  "media": {"duration_s": 4.2, "width": 1280, "height": 720, "fps": 25},
  "input_refs": ["art_..."],
  "producer": {"provider": "breeze_tts", "version": "adapter@0.1", "model": "breeze-tts-2", "prompt_version": "tts@1"},
  "status": "candidate|approved|rejected|superseded"
}
```

`Event` 是追加式记录，至少包含 `run_id/job_id/stage/status/at/input_refs/output_refs/message`，并可附 `duration_s/resource_snapshot/review_decision/failure_class`。运行真相来自对象状态加事件流，不来自 WebUI 的临时状态。

## 4. Provider 契约

每个 Provider 必须声明 `ProviderManifest`：能力名、输入/输出 schema、版本、资源需求、是否可取消/重试/checkpoint、估算耗时和失败类别。统一 HTTP 形态为：

```text
POST /jobs
GET  /jobs/{job_id}
POST /jobs/{job_id}/cancel
POST /jobs/{job_id}/retry
GET  /jobs/{job_id}/artifacts
GET  /jobs/{job_id}/events
GET  /manifest
```

`POST /jobs` 只接收结构化参数和 Artifact 引用，返回 `job_id`；Provider 完成后登记不可变 Artifact 和事件。同步 Fake Provider 可以实现同一接口的内存/文件版本，不能另设一套只适用于 POC 的字段。

首批 Provider 类型：

| 类型 | 输入 | 输出 | 首阶段实现 |
|---|---|---|---|
| `source` | Topic/渠道策略 | raw、normalized、evidence、media manifest | Fake JSON → 真实渠道 |
| `director` | Evidence Pack + Format Profile | claims、script、storyboard | Fake 模板 → Director skill |
| `tts` | ScriptSegment | WAV + timing metadata | Fake tone → Breeze |
| `host` | WAV + identity/motion refs | 主持人视频片段 | Fake video → H3 |
| `broll` | Shot spec + refs | 视频/图片 | 占位 → H3/Source |
| `music_sfx` | Segment/Timeline cues | 分轨音频 | 占位 → Music/音效 |
| `render` | Timeline + media refs | preview/delivery + SRT | FFmpeg POC → OTIO/Remotion/FFmpeg |
| `qc` | 全部候选 Artifact | QC report + review gate | 规则检查 → ASR/OCR/VLM |

当前已加入 `tools/daily_video_poc/source_provider.py` 作为 Source Provider 第一版：输入本地或 HTTP JSON，校验 Topic/Evidence 契约，补充 `collection` provenance 后输出 `daily-video/evidence.v1`；它不依赖 Conductor，也不读取其他 Provider 的内部目录。

`tools/daily_video_poc/director_provider.py` 是 Director Provider 第一版：接收 Evidence Pack 与 Format Profile，输出带 `evidence_ids`、`fact_status` 和 producer provenance 的 `daily-video/script.v1`；当前使用确定性模板，后续可替换为 LLM Director 而不改变下游契约。

`tools/daily_video_poc/audio_provider.py` 是 TTS Provider 第一版：接收 `script.v1 + timeline.v1`，输出 WAV 和音频 metadata；当前用确定性 tone 验证时间轴，未来可替换 Breeze-TTS。音频必须以 Timeline duration 为真值，不能由各段文本时长自行漂移。

`render_provider.py` 和 `qc_provider.py` 负责最后两个边界：Render 只接 Script/Timeline/Audio 并输出 MP4；QC 只读取运行 Artifact，检查证据覆盖、Artifact 集、正时长和媒体时长一致性。两者均声明 manifest，不承担编排状态。

`vertical_slice_verify.py` 是可重复验收入口：检查五个 Provider Manifest 必需字段、验证 workflow 的批准分支拓扑，运行 Source → Director → TTS → Render → QC，并验证 11 个 Artifact、5 个阶段事件和 QC 全部通过。

`workflow_definition.py` 将同一切片声明为可注册的 Conductor 拓扑：Source → Director → TTS → HUMAN Approval → Decision(approved) → Render → QC；拒绝分支不进入 Render。`register_workflow.py` 负责校验并注册定义，Provider 实现仍不嵌入 workflow 文件。

`conductor_provider_worker.py` 是第一版 Provider Worker：轮询并执行五个 SIMPLE task，按 workflow ID 隔离本地运行目录；HUMAN task 不由 Worker 越权完成，必须由审核 API 恢复。

Worker 结束时写入 `daily-video/conductor-run.v1` Manifest，汇总每个 task 的 started/completed、审核 blocked/completed、最终 workflow 状态和本地 Artifact 文件清单。

Provider 异常由 Worker 回报为 `FAILED`，不等待 task 超时；Conductor 的 retry policy 负责重新调度，失败分类和原因写入事件与 task output。

## 5. 编排状态图

```text
created → collecting → researched → scripted → media_pending
   → audio_ready → visuals_ready → timeline_ready → rendering
   → qc_pending → human_review → approved → delivered
                         │             │
                         └─ retry ◀────┘
任何状态 ── cancel ──▶ cancelled
失败 ──▶ failed ──(retry/replay/修正输入)──▶ queued
```

编排器维护节点状态和依赖，不修改 Artifact 内容。三种恢复语义必须区分：

- `retry`：同一输入和参数再次执行失败 Job；
- `replay`：从指定节点创建新 Run，保留旧 Run 作为证据；
- `edit-and-rerun`：人工修改结构化输入后，创建新版本并从受影响节点重跑。

人工审核是持久化的 `review_gate` 节点。拒绝时必须写 `ReviewDecision`（原因、修改目标、操作者、时间、相关 Artifact），不能只把状态改回 pending。

## 6. 事实、媒体和时间线契约

- `Evidence` 保留来源 URL、抓取时间、原文定位、质量层级、置信度、版权状态和媒体引用；`Claim` 必须反向引用一个或多个 Evidence。
- `ScriptSegment` 保留逐字文本、speaker、`evidence_ids`、delivery、visual intent 和 `fact_status`（supported/inferred/opinion/needs_review）。
- 媒体理解是独立 Provider，输出带时间定位的 ASR、OCR、shot、speaker、VLM 标签及置信度；不得覆盖原始媒体。
- Timeline 是可执行的结构化对象，至少包括轨道、时间区间、Artifact 引用、ScriptSegment 引用、字幕和混音 cue。Agent 只生成 Timeline JSON，渲染器执行它。
- 最终音频母带是时间轴真值；主持人/真人视频是视觉层；字幕跟随母带时间，避免以不同段落输入音频名义时长推算成片轴。
- 长期内部抽象可映射 OTIO，但首阶段保留 POC `timeline.v1`，通过 adapter 输出 FFmpeg/OTIO。

## 7. 资源、审计与观测

Provider manifest 申明资源需求，Orchestrator 向现有 `hive-resource` 申请租约、心跳和释放，不在业务页面复制 GPU 调度。实际命令可通过 `scripts/hive_resource_run.sh` 托管：一次 acquire，由同一进程后台 heartbeat，命令退出时自动 release，避免编排器或 Agent 为每次续约单独发起调用。4090 初始策略：H3 独占 GPU；Breeze/Music 按画像排队；Source/Director/Render/QC 可并行 CPU；同一张卡默认不与 H3 并行。

每个 Job 记录排队时间、运行耗时、峰值显存、系统内存、租约和失败类别。内容审计采用 `run.json/manifest.json + Artifact/Event` 起步；之后可接 OpenTelemetry，Agent trace 再选择 Phoenix 或 Langfuse，系统/GPU 监控接 Prometheus/Grafana/DCGM。观测系统不能成为内容真相。

## 8. 交付顺序与验收门

按以下垂直切片开发，每完成一项都用同一套 Artifact 契约验收：

1. 架构文档与 schema review；
2. 编排骨架 + 文件 Artifact Store + Fake Source/Director/TTS/Host/B-roll/Music/Render/QC；
3. 一条 30–45 秒假全链路，验证暂停、拒绝、单节点重试、replay、事件和 manifest；
4. 替换真实 Source，验收 raw/normalized/evidence/media pack；
5. 替换 Director 与 Breeze，验收证据引用、音频时长和字幕；
6. 替换 Render，再接入 H3 Host，验收外部母带、口型、MC 续接和失败恢复；
7. 接入 B-roll、Music/SFX、媒体理解和 QC/review；
8. 最后做统一 WebUI、定时触发和发布包。

最小 POC 的通过条件：给定一个 Topic/Evidence JSON，生成完整 Artifact 集和可播放 MP4；任一节点失败可分类并重试；人工审核可持久化暂停并恢复；旧版本仍可追溯；没有 Provider 直接依赖另一个 Provider 的内部目录。当前 Fake/FFmpeg POC 已实测生成 32 秒、1280×720、H.264/AAC 的 `preview.mp4`，QC 为 `pass`；Conductor Adapter 已实测批准和拒绝审核门；`ArtifactStore.revise_json()` 已实测保留旧版本并以 `supersedes` 链接新版本，配合 `ConductorAdapter.rerun_from()` 形成修改后局部重跑闭环。

## 9. 当前明确决策与待验证项

已确定：Provider-neutral 分层、独立 Orchestrator、统一 WebUI、Artifact/Event provenance、hive-resource 复用、Fake 全链路优先、H3 Host 独立 Provider、Format Profile 版本化。

待验证而不在本文拍板：Kestra/Windmill/Prefect 是否引入；LangGraph 是否只用于研究/导演子图；WebUI 采用 React Flow/Remotion/OTIO 的具体组合；Artifact Store 是本地目录、对象存储还是数据库；Phoenix 与 Langfuse 的选择；真实 Source 渠道和版权策略。
