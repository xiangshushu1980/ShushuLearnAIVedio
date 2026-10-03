# 应用内 Agent 接入手册 v1

Owner: Sean。2026-10-03。适用：Node 24、Pi SDK 0.86.0、本机单用户应用。当前用例是 Reference 项目创作与场景空间助手；后续人物、声音等流程复用本手册的运行、上下文和工具契约。实施过程与版本注意事项单独保存在 [Agent 接入经验记录](../../.pi/ledger/reference-agent.md)。

## 分层与复用

```text
业务页面 → Agent Workspace 服务 → Pi Runtime 适配器 → 已配置模型
                  ↓
          项目资料 / 会话 / 运行快照 / 事件 / 候选提案
                  ↓ 用户应用与确认
             Reference 场景空间版本 → 既有只读 manifest 导出
```

- `server/pi-agent-runtime.mjs`：SDK、模型/认证、受限资源加载、会话恢复。未来可以增加同契约的 Codex 适配器，业务界面不直接依赖其协议。
- `server/agent-profiles.mjs`：用途 ID、名称、提示词版本、方法包/skill 版本。当前 project-authoring 与 scene-spatial，共用项目核心提示词，各有方法包；不生成多个自主协作 Agent。
- `server/project-workspace.mjs`：项目介绍、成员、实体剧情作用和项目剧情关系的业务真源。
- `server/agent-workspace.mjs`：会话、运行快照、工具、提案、版本冲突及业务持久化。
- `src/SceneAgentPanel.jsx`：选图、对话、提案、人工复核；在管理和创建流程共用的空间编辑器中打开。

运行框架与模型分开。Pi 不限定一个模型提供方，但第一版只列出当前可用且声明支持图片输入的模型。可用凭据不代表真实推理已验证；工具调用质量与图片理解需通过实际讨论验收。

## 模型与凭据配置

服务默认使用应用 `.data/agent/` 下自己的配置与缓存，不自动读取全局 Pi 的提示词、AGENTS、skill、扩展、设置或聊天，不借用 Hivemind 的会话/PTY。

| 环境变量 | 默认 | 作用 |
| --- | --- | --- |
| REFERENCE_AGENT_PROVIDER | 未限制 | 限制可选提供方，如 openai 或 openai-codex |
| REFERENCE_AGENT_MODEL | 未限制 | 限制模型 ID；必须支持图片输入 |
| REFERENCE_AGENT_AUTH_FILE | 数据目录/agent/auth.json | Pi 格式凭据文件；服务端使用，不返回网页 |
| REFERENCE_AGENT_MODELS_FILE | 数据目录/agent/models.json | Pi 格式自定义模型配置 |
| 模型提供方标准 API key 环境变量 | 未设置 | 由 Pi ModelRuntime 解析，如 OPENAI_API_KEY；不要写入聊天/工程资料 |

使用已有 Pi 登录时，推荐复制凭据到应用自己的数据目录，并限制文件权限。OAuth 刷新写入应用副本，不更新原有 Pi 用户文件。凭据不会随 Git 或工程上下文导出。复制后账号退出、权限变化或 token 过期，可能需要更新副本/重新登录。

本次用户已选择复用 Pi。已复制 auth.json、models.json、models-store.json，并只从 settings.json 提取默认 provider/model 到应用 preferences.json；原文件不改动。目录权限 700、复制文件权限 600。能力接口成功读取两项可选模型，列表优先使用原 Pi 的默认模型；没有提交真实推理请求。

```bash
cd /home/sean/projects/comfy-ops/reference-workspace
mkdir -p .data/agent
chmod 700 .data/agent
# 仅在用户选择复用当前 Pi 登录时执行；不要输出文件内容。
cp ~/.pi/agent/auth.json .data/agent/auth.json
chmod 600 .data/agent/auth.json
npm ci
npm run build
npm start
```

使用专用 API 配置时，在启动服务的环境中设置对应 key；不要求通过聊天传递 key。环境变量须在启动前设置，修改配置后需重启 Reference 服务。不得因此操作 ComfyUI。应用不会发起登录、安装全局扩展或后台预热模型。

首次使用：在项目工作区新建/选择项目 → 加入或新建实体 → 打开通用创作助手，或从场景打开空间模式 → 选择模型、新建对话 → 发送讨论要求。空间模式需要参考图，通用模式无需图片。模型配置缺失显示说明，其余实体功能不受阻。

## 工程上下文与会话

项目结构、字段、成员与关系归属、索引和迁移的当前契约见 [项目工作区 v2](project-workspace-v2.md)，不在本手册重复定义。

会话按 projectId + 可空 entityId + purpose 隔离，并固定创建时的 provider/model；更换模型通过新建对话表达。浏览器只记项目 ID，资料与讨论保存在 SQLite。不同用途继承同一项目的最新资料，各自保存讨论记录。

每轮保存：请求 UUID、用户消息、当前工程/实体/空间/参考图的修订哈希、提示词/skill 版本、模型与创建时间。`agent_run_contexts` 保存送给工具的上下文快照：当前场景完整资料，其他工程实体的简短说明和修订。工程有大量资料时不把所有其他实体的长文和所有历史会话送入模型。所有可见对话和 Pi 的 compaction-aware 会话条目分别持久化；中断恢复继续使用最后完整的轮次记录，未完成回复在 UI 中明确显示。

不把模型生成的会话摘要当权威设定。工程决定、实体版本和来源仍由应用管理。服务正常退出会取消运行并保存；异常退出后将旧 running 标为 interrupted，不自动重新计费/重发用户请求。

## 受控工具与方法包

当前工具仅四个：

| 工具 | 范围 |
| --- | --- |
| get_project_context | 自动注入项目设置后，读取本轮捕获的共用上下文及用户消息 |
| get_project_entity | 读取项目内一个实体的完整资料，补充默认索引摘要 |
| propose_project_review | 保存带实体 ID、覆盖范围和来源版本的检查报告，不改事实 |
| propose_project_update | 通用创作模式提出项目资料修改，网页逐字段审阅并应用 |
| get_scene_context | 当前运行捕获的工程资料、当前场景空间、用户消息 ID、最近候选提案 |
| view_reference_image | 用户本轮选定的当前实体图片 ID，验证归属/内容哈希，缩放供模型观察 |
| load_authoring_skill | 读取当前用途登记的方法包 ID/版本；不接受任意路径 |
| propose_scene_spatial | 严格 schema 校验候选文档和来源，保存候选提案 |

SDK `noTools:'builtin'` 加显式工具 allowlist；ResourceLoader 关闭全局/项目自动发现。没有 shell、文件编辑、网络浏览、确认事实、生成图片或任意文件读取工具。提供方错误只显示通用提示，避免原始错误泄露 key/内部路径。模型工具参数也经业务层再次校验。

方法包当前通过用途配置和受控 load 工具按需装入。未来扩展为独立 skill 文件时，增加明确注册表和版本；不要直接开放本机所有开发 skill，或赋予方法包默认文件执行权限。

第一版界面显示文本回答与工具活动，不暴露推理内部文本。SSE 事件保存整数 seq，并支持 Last-Event-ID；刷新/重连以持久化消息为准，不盲目叠加重放文本。每会话同时一轮，整个服务同时至多两轮；每轮最多 8 张选图、24 次工具调用、5 分钟，提供方自动重试关闭、缓存预热关闭。会话压缩可调用模型，属于当前用户触发的运行。

## 提案、来源与确认

候选提案包含完整 spatial document、summary、最多三个关键问题、修改差异、sources 和依据哈希。已知 frame/element/link/route 必须有来源：

- image：实际查看过的本轮图片 assetId。
- user：本会话的用户消息 ID。
- existing：原空间中已知条目路径。

来源 target 是 frame 或 elements/ID、links/ID、routes/ID。新条目由服务分配 UUID 派生的局部 ID，已有 ID 继续沿用。sources 是依据引用和说明，不声称自动证明文字与图片的语义一致。

提案不修改实体，也不确认事实。只有成功结束的运行提案允许由用户点击“应用为空间草稿”；整次来源检查、空间新版本写入、提案 appliedVersionId 记录在同一事务内。工程资料、任何工程成员资料、空间版本、当前形象、选图内容发生变化时拒绝应用；用户继续讨论当前版本，而不是强制覆盖。

用户再勾选图文一致性并使用原有 spatial/confirm 接口确认。当前主形象必须纳入核对图，至少一个有依据锚点和方向基准；其他未知继续 pending。Agent 没有 confirm 工具。聊天中说“确认”不会触发正式确认。

候选来源记录通过 appliedVersionId 可追溯到空间版本。下游仍只读取已确认 sceneSpatial/promptContext；不导出助手聊天、凭据或 Pi 内部会话。不改已有 manifest 内容，也不自动刷新短片项目快照。

## API

所有路径在 `/api/agents` 下，沿用本机 Host/Origin 边界。错误 400 使用 details.fieldErrors；未知对象 404，冲突 409。

| 方法 | 路径 | 输入 / 响应 |
| --- | --- | --- |
| GET | /capabilities | runtime、profiles、models、configurationIssue；不包含凭据 |
| GET / POST | /projects | 列表 / {name,brief,decisions,entityIds} 新建 |
| PATCH | /projects/:projectId | 上述字段 + expectedRevision |
| GET | /projects/:projectId/context | 只读工程共用资料及实体/关系/空间修订；供后续用途构造上下文 |
| GET | /projects/:projectId/sessions?entityId=UUID | 工程/实体下的对话列表 |
| POST | /sessions | {projectId,entityId,purpose:"scene-spatial",provider,modelId} |
| GET | /sessions/:sessionId | 可见消息、运行状态、来源/差异提案，不含 SDK 内部条目 |
| POST | /sessions/:sessionId/messages | {requestId:UUID,text,referenceAssetIds} → 202 {runId,status} |
| GET | /runs/:runId/events | SSE：text/tool/proposal/usage/done；支持 after 或 Last-Event-ID |
| POST | /runs/:runId/cancel | 停止本轮；已存讨论/候选保留 |
| POST | /proposals/:proposalId/apply | {expectedContentHash} → {versionId,alreadyApplied} |

## 交付状态与验证范围

已完成前端构建和后端静态语法检查，Reference 服务启动成功，能力接口读取配置成功，依赖扫描无已知漏洞。本轮未运行自动化测试、真实模型调用或 ComfyUI；真实看图、工具调用兼容性、连续讨论质量和 PC 浏览器交互仍需验收。不以“有可用凭据”冒充一次真实推理成功。

SDK 0.86.0 的 npm-shrinkwrap 锁定有漏洞的 brace-expansion 5.0.9，普通根 overrides/更新无效。应用直接固定兼容补丁 5.0.12，并在 postinstall 由 `scripts/patch-pi-dependency.mjs` 更新嵌套包及安装库存；不修改 SDK 的功能代码。应用 package-lock 同样登记真实补丁。升级 SDK 时脚本会因版本不符停止，必须重新审视补丁。使用 `npm ci`，不跳过根 postinstall；忽略脚本安装后要显式运行此脚本。重新生成 lock 后应检查嵌套补丁登记和扫描结果，不能只看 overrides。

后续验收建议：读图整理已有锚点 → 用户指定未知入口 → 提案应用与人工确认 → manifest 读取；再检查刷新恢复、取消、资料变更后的 409、另一页面修改工程的 409。此处仅记录步骤，没有执行这些测试。
