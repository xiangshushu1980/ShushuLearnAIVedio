# Comfy-ops 项目约定（所有会话自动加载）

> 通用的记忆、远程任务和多 Agent 协作纪律以用户级 AGENTS.md 及对应全局 skill 为准；本文件只规定 comfy-ops 专属入口和边界。

## 会话入口与任务判断

- **续接**：有 T-ID 先运行 `task-center info <T-ID>`；无 ID 时按标题/关键词查找，只有无法唯一定位才询问用户。读取描述、状态、checkpoint、`metadata.contextRefs` 和引用资料；progress 等长档案用 `incdoc` 定位。写回前确认本会话持有 controller/generation；本地 progress 不是任务状态。
- **自由会话**：从 `docs/INDEX.md` 按主题进入文档；没有续接、状态或冲突信号时不查 Task Center，也不为获取资料创建任务。
- **新工作**：有明确执行范围时先查 Task Center，检查重复任务和活跃冲突；只有用户明确要求立项才创建。Task Center 是任务真源，项目文档只保存证据与恢复上下文。查询遇到 `fetch failed`、timeout、连接拒绝或 5xx 时停止任务操作并报告，不能当作任务不存在；明确 404 也须用户授权后才能新建。
- **项目技能**：任务匹配 `.pi/skills/` 时显式读取 `SKILL.md` 和必要 references；宿主 catalog 未列出不代表技能未安装。按 `docs/INDEX.md` 的回退顺序检索未覆盖主题。
- **H3/ComfyUI 专题**：涉及节点、模型、依赖、VAE、采样加速、工作流升级或外部调研时，先读最新 `docs/dev/comfyui_node_update_*.md`、`.pi/ledger/h3-speed.md`、`.pi/ledger/h3-models.md`（涉及音频再读 `h3-audio.md`）、专题文档和最近实验。外部资料用于核对上游变化；本地证据和运行时决定实装与验证状态。
- 正常 Agent 只通过 `task-center` 操作远程任务；不调用 Hivemind 后端、Pi Web、PTY、Codex 会话接口或 `hive-task start`。Hivemind 调试必须显式设置 `HIVEMIND_AGENT_DEBUG=1`。

## ComfyUI 权限边界

- ComfyUI 的访问与操作权限完全由当前会话环境设置及宿主审批流程决定；本项目不另设沙箱、全局权限或逐项授权门槛。若宿主针对某项操作要求审批，按宿主流程向用户请求；获批后继续，不绕过审批。
- ComfyUI 是共享单实例服务。操作前检查 Hive0 服务状态及共享队列；不得切换数据库或创建第二实例。需要启动或关闭服务时，统一通过 `http://hive0.localhost` 的 ComfyUI 服务卡片操作，使其与 Hive0 使用同一 `comfyui.service` 生命周期入口；不要另走 systemctl、wrapper 或脚本启动第二条管理路径。
- ComfyUI MCP 已由 CLI/HTTP API 工作流替代；程序化访问的共享接口契约见用户级 `comfyui` skill 的 `references/api.md`。图片任务入口仍见该 skill 的图片流程。规范服务地址为 `http://comfy.localhost`；已有 CLI 可继续使用 IP+端口。本项目不再配置或启动 `comfyui-mcp`。

## 模型清理与恢复（Sean 决策，2026-10-11）

- 已删除 H3 FL2VA FP8 scaled、H3 Ref2VA Turbo 主模型残片，以及 ACE-Step 1.5 XL Turbo 本地模型栈。缺少这些文件时不要自动重新下载；仅在 Sean 明确要求恢复时下载。
- `scripts/h3_promptor_p1.py` 和 `scripts/h3_gap_runner.py` 仍默认引用已删除的 H3 FP8 scaled 模型。下次运行前先修改这两个脚本，改用届时确认可用的本地模型；不要为满足旧默认值而恢复下载。
- `scripts/ace_t2i_probe.py` 仍引用已删除的 ACE-Step 模型文件；运行前需先修改脚本或由 Sean 明确恢复模型，不得自动重下。
- 本地配乐优先评估 H3 Music 和现有备选方案；不要把 ACE-Step 作为默认恢复项。

## 增量档案检索（incdoc）

- 查历史任务/实验结论、较长 `progress.md`、`done/` 归档或追加日志时，用 `incdoc grep <文件> <关键词>` 按条目取原文；小于 100 行的文件直接读，JSON 等结构化文件不适用。incdoc 覆盖有限，关键结论需核对命中原文。

## ComfyUI 服务管理

- ComfyUI 共享实例仍由用户级 `comfyui.service` 承载；统一经 `http://hive0.localhost` 的 ComfyUI 服务卡片启停和查看状态，该入口与 Hivemind 共用同一服务生命周期。Agent 不直接调用 systemctl，不用 `scripts/comfy-stack.sh`、`start.sh`、`nohup` 或其他脚本另行管理服务。
- CLI/HTTP API 客户端连接现有共享实例，不由服务 unit 或其他 wrapper 再启动 ComfyUI；规范服务地址为 `http://comfy.localhost`，已有 CLI 可继续使用 IP+端口。
- `hive-resource` 只负责资源预检、`service:comfyui` 服务登记和生成任务的 GPU lease；不把长驻 ComfyUI 当作短 TTL 的 GPU 独占 lease，也不把资源 lease 当作进程单例锁。
- 生成任务按 hive-resource 规则申请 lease、heartbeat、observe 和 release；服务启停仍统一走 Hive0 服务卡片。

## H3 测试与提示词硬规则

- 任何 MiniMax H3 视频测试、生成、提示词编写、修改或审查，**先读 `.pi/skills/h3-prompt-writing/SKILL.md`、对应模式的参考文件和 `docs/17_h3_prompt_writing_rules.md`**。先判定 T2VA、I2VA、FL2VA、L2VA 或 Ref2VA；字段、标签、顺序和时间线以该模式官方参考为准。
- Ref2VA 默认采用 skill 的六段式；参考图、视频、音频的标签及角色跨段一致。NativeAudioLock 是外部音频锁定链路，不能当作普通 `ref_audio` 音色参考；外部对白以输入音频为真值，prompt 不重复编写未经核对的台词。
- 只有用户明确要求的快速对照实验，才允许使用简化 prompt；此类文件和结果必须明确标注为 `simplified`/`quick comparison`，不得作为默认 H3 测试或生产基线。
- 20 秒及更长本地实验可以继续执行，但必须记录其超出官方 H3 skill 4–15 秒目标范围的扩展条件；时长扩展不改变提示词格式要求。

## 内容落盘（项目专属位置）

- 原始实验数据与产物 → `experiments/`；当前模型清单、工作流结构、参数基线和安装步骤 → `docs/`；跨任务的稳定操作方法 → `.pi/skills/comfyui-ops/`。ComfyUI `output` 仅作单次生成的临时落点；实验完成后立即把选定产物、manifest、prompt、QC 和分析文本迁入对应 `experiments/<任务>/`，更新引用后清理本批次 output 文件。Agent 只读取当前任务的 `experiments/<任务>/`，不递归扫描整个 experiments 树。不得将历史实验积累在 `output`，也不得把 `output` 子目录当作长期归档。归档文件放在 ComfyUI 扫描根目录和项目工作区之外，并在 experiments 中保留归档索引。同一事实只保留一处权威正文，其余位置链接引用。
- **实测定论**（参数值、加速比、可行性、选型）→ 现行值及适用条件写 `docs/`，演进史、覆盖链和证据锚 append 到 `.pi/ledger/`（见 `.pi/ledger/README.md`）。任务收尾按 `multi-agent-collab` 的远程流程执行；本地 progress/ledger 只保存证据和上下文，会话结束 retain 的实测定论打标 `[定论候选]`（见 mem0 skill）。
- 动态经验、踩坑、偏好 → Mem0 池 `comfy-ops`（跨界 → `global`）

## Agent 与无线画布协作

- 画布是业务数据真源。Agent 每回合开始时由服务端注入精简 Workflow 框架和字段级待处理差异，不默认注入完整对象快照。服务端先按当前 Workflow 的目标与关联节点筛选变更，再交给 Agent。
- `entity_studio` 的 `context` 是固定按需读取接口。Agent 可指定范围、对象 ID、类型、搜索词和字段；服务端强制限制在当前 Workflow 可见范围内并执行结果分页。除 ExtractEntities 的项目实体搜索外，不扫描整张画布；不得依赖轮询。
- 只在 Agent 成功接收该回合上下文后确认已读游标；传递失败或 Agent 回合开始后产生的画布修改必须留到后续回合。区分 Agent 自己写入的事件，避免将其当成用户新修改重复处理。
- Agent 可按用户意图整理和修改数据，但生成、采用、删除等操作仍遵守各 Workflow 的既有确认边界。
- 用户要求刷新或同步时，只汇报本次检测到的变更及其影响；未变化上下文留在已有对话状态中，只有应用修改需要时才按需读取准确字段。被截断的差异值必须先读取完整字段再用于修改。没有待处理变更时简短说明即可。

## Skill 划分纪律（多 skill 维护）

- 三层：**共享层**（跨所有 skill 的稳定契约，只写一份用引用不复制）/ **核心能力 skill**（框架层：安装+理解+节点+通用工作流）/ **特定用例 skill**（业务层：组装核心）
- 动态经验先进入 Mem0（按池隔离）；只有验证稳定且标明适用条件，才蒸馏为 docs 或 skill 的当前基线。
- 宿主边界必须写清：`h3-prompt-writing`、`comfyui`、`breeze-tts` 是本地可执行能力；依赖 MiniMax Hub canvas、choice cards 或 `hub_*` 工具的用例 skill 只在 Hub 宿主执行，其他宿主只能交付策划/提示词且必须显式说明降级
- 建 skill 前先读 `docs/14_skill_governance.md` 决定建哪种/经验放哪，再调 skill-creator 写文件

## 每日文档维护与 Git

Owner: Sean。扫描范围、权威正文和自动上传开关见 [.document-health.json](.document-health.json)。每日检查只读；当前自动提交、自动推送均关闭，人工维护仅提交本次明确内容，混合工作树不得整文件纳入。推送必须核对远端、目标分支和全部待上传提交。结论变化即时更新手册、ledger 覆盖关系与直接入口，不能等每日检查替代同步。
