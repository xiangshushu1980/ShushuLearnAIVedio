# 每日话题视频系统设计（T-comfy-ops-32）

> 目标：把“每天一个话题”扩展成可选择节目形态、可替换模型、可追踪证据和可人工介入的内容生产系统。
> 当前阶段：架构讨论 + 最小闭环 POC。

## 1. 核心判断

系统不应是一个从主题直接生成 MP4 的黑箱，而应是一个带版本和状态的生产项目：

```text
Topic / Brief
    ↓
Source Collection → Normalized Sources → Evidence Pack
    ↓                    ↓                  ↓
Media Understanding  Fact Checks       Director / Format Profile
    └──────────────────────────────→ Script + Shot Plan
                                      ↓
                          Voice / Host / B-roll / Music jobs
                                      ↓
                               Timeline + Render
                                      ↓
                         QC + Human Review + Publish Pack
```

每层都通过 JSON 契约连接，模型、平台和生成方式可以替换；每一次运行都有 `run_id`、阶段状态、输入输出哈希、错误和人工决策记录。

## 2. 节目形态不是分支代码，而是 Format Profile

第一版内置 profile：

| profile | 适用场景 | 默认结构 |
|---|---|---|
| `news_brief` | 热点/新闻 | 发生了什么 → 关键事实 → 影响 → 来源 |
| `host_explainer` | 主持人口播 | 钩子 → 背景 → 解释 → 结论 |
| `blog_commentary` | 观点/博客 | 事实 → 观点 → 例子 → 免责声明 |
| `dialogue` | 双人/多人对谈 | 立场 A → 立场 B → 追问 → 共识/分歧 |
| `interview` | 采访 | 问题 → 回答 → 追问 → 重点回收 |
| `entertainment` | 娱乐/轻内容 | 钩子 → 反应 → 信息点 → 包袱/收尾 |

Profile 只规定节目合同、节奏和审核规则，不规定具体模型。真人出镜、H3 数字人和纯素材视频都是 `host` / `visual` provider 的实现选择。

## 3. 四种资料视图

同一批资料需要同时保留四种视图，不能只保存 LLM 最后的摘要：

- `raw`：原网页、字幕、图片、视频、音频和抓取响应。
- `normalized`：统一的标题、作者、发布时间、正文、媒体引用、平台、语言。
- `evidence`：支持某个 claim 的原文片段、定位、来源质量、时间和权限。
- `analysis`：视频/图片/音频的转写、OCR、镜头、人物、主题、情绪、可用片段和模型置信度。

视频素材进入脚本前必须经过 `media_understanding` 阶段。阶段可以先用 ffprobe/字幕，后续接 ASR、VLM、OCR、镜头切分和人物识别；分析结果不能覆盖原始素材，只能产生带模型版本的派生 artifact。

## 4. 稳定契约

最小 `Evidence`：

```json
{
  "id": "ev_001",
  "claim": "可直接进入脚本的事实",
  "source": {"url": "...", "name": "...", "published_at": "...", "captured_at": "..."},
  "quote": {"text": "原文片段", "locator": "paragraph:3"},
  "quality": {"tier": "primary|secondary|community", "confidence": 0.8},
  "rights": {"mode": "link_only|review_required|usable", "note": "..."},
  "media_refs": []
}
```

最小 `ScriptSegment`：

```json
{
  "id": "seg_01",
  "kind": "host|broll|quote|graphic|pause",
  "speaker": "host_01",
  "text": "逐字口播稿",
  "evidence_ids": ["ev_001"],
  "visual_intent": {"role": "host|source|generated|graphic", "asset_query": "..."},
  "delivery": {"tone": "calm", "pace": "normal"},
  "review": {"fact_status": "supported|inferred|opinion|needs_review"}
}
```

## 5. 可观测性与人工介入

每个阶段输出两类数据：

- `artifact`：文件或结构化结果，如 `evidence.json`、`script.json`、`timeline.json`、音频、视频。
- `event`：运行事件，如 `started`、`progress`、`retrying`、`blocked`、`approved`、`failed`。

将来的可视化工作台按五个视图组织：

1. 资料池：来源、证据、媒体缩略图和版权状态。
2. 导演板：节目类型、结构、段落、事实引用和镜头需求。
3. 素材板：每个镜头的候选素材、分析结果和生成任务。
4. 时间线：主持人、真人出镜、B-roll、字幕、音乐、音效和转场。
5. 运行/质检板：队列、GPU、耗时、失败重试、音画/事实/版权检查。

## 6. POC 边界

POC 使用本地 JSON 资料包，支持一个 `news_brief` 或 `host_explainer` profile，产出：

```text
run.json       运行状态和阶段事件
evidence.json  规范化证据
claims.json    从证据派生的可核验主张
script.json    带 evidence_ids 的脚本
storyboard.json 镜头/视觉意图
timeline.json  可执行时间线
subtitles.srt  字幕
qc.json        最小质量检查
preview.mp4    可播放预览
```

POC 的音频可使用已有 WAV；没有音频时用 ffmpeg 生成占位音轨，因此不依赖 GPU 或外部 API 也能验证闭环。Breeze、H3、真实素材分析和 Web 看板都是后续 provider，不改变上述契约。

## 7. 调研得到的设计启示

当前类似方案普遍采用：分阶段导演、可替换 provider、可恢复任务、时间线/画布审阅、生成资产 provenance。Genblaze强调跨供应商 provider 和可验证 provenance；VidForge强调显式状态图、边界重试、成本追踪和可替换层；OpenMontage把生产标准写成 skills/manifests；Scenavo将研究、脚本、素材匹配、生成和发布串成可人工控制的流程；现有 `web-shotlist` 已验证“审阅层和执行层分离”适合本项目。

这些方案可借鉴的是边界和可观测性，不应直接照搬其模型或供应商绑定。
