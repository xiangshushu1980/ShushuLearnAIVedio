# Comfy-ops 项目约定（所有会话自动加载）

> 通用的记忆、TODO 和多 Agent 协作纪律以用户级 AGENTS.md 及对应全局 skill 为准；本文件只规定 comfy-ops 专属入口和边界。

## 新会话开场（每会话自动执行）

1. 读 `docs/INDEX.md` 定位当前任务的权威文档，不把索引当作操作手册。
2. 任务匹配 `.pi/skills/` 下的项目 skill 时，显式读取其 `SKILL.md`；再按任务读取所需 references。宿主 catalog 未列出项目 skill 不代表已加载。
3. 开始任务：新任务一律在远程 Task Center 创建/领取；本地 TODO 仅用于迁移兼容或历史检索，不作为新任务入口。

## ComfyUI 权限边界

- 禁止在沙箱权限下启动、重启、停止或直接操作 ComfyUI；也不要把沙箱内访问不到 `127.0.0.1:8188`、GPU、进程或模型目录解释为 ComfyUI 离线。
- 需要查询、提交生成、读取队列/模型、访问 GPU 或操作 `/home/sean/projects/ComfyUI` 时，先请求宿主提供全局权限；权限不足就暂停并等待用户授权，不在沙箱内绕过或尝试替代启动。
- ComfyUI 默认视为共享单实例服务：先检查共享 Agent 状态和队列，禁止擅自重启、切换数据库或创建第二实例。
- 该规则只约束操作纪律，不授予权限；实际权限由 Codex 宿主/会话的 approval policy 和 sandbox profile 决定。

## ComfyUI 唯一启动入口

- ComfyUI 共享实例的唯一启动入口是 `scripts/comfy-stack.sh`：
  `start`、`stop`、`status`、`restart`；禁止直接使用 `start.sh`、`nohup` 或另一个脚本拉起第二个实例。
- `comfy-stack.sh` 使用本地 `flock`、8188 健康检查和精确 PID 校验实现单实例；发现已有健康实例时必须复用，发现端口或进程异常占用时必须停止并报告，不能盲目启动。
- Agent/MCP 由客户端根据项目 `.mcp.json` 管理；`comfy-stack.sh` 不启动 `comfyui-mcp`，避免 Agent 自己启动的 MCP 与手工启动的 MCP 重复。Agent 只连接现有 `http://127.0.0.1:8188`。
- `hive-resource` 只负责资源预检、`service:comfyui` 服务登记和生成任务的 GPU lease；不把长驻 ComfyUI 当作短 TTL 的 GPU 独占 lease，也不把资源 lease 当作进程单例锁。
- 启动前可由 wrapper 展示 `hive-resource occupancy`；具体生成任务仍按 hive-resource 规则申请 lease、heartbeat、observe 和 release。

## H3 测试与提示词硬规则

- 任何 MiniMax H3 视频测试、生成、提示词编写、修改或审查，**先读 `.pi/skills/h3-prompt-writing/SKILL.md`、对应模式的参考文件和 `docs/17_h3_prompt_writing_rules.md`**。先判定 T2VA、I2VA、FL2VA、L2VA 或 Ref2VA；字段、标签、顺序和时间线以该模式官方参考为准。
- Ref2VA 默认采用 skill 的六段式；参考图、视频、音频的标签及角色跨段一致。NativeAudioLock 是外部音频锁定链路，不能当作普通 `ref_audio` 音色参考；外部对白以输入音频为真值，prompt 不重复编写未经核对的台词。
- 只有用户明确要求的快速对照实验，才允许使用简化 prompt；此类文件和结果必须明确标注为 `simplified`/`quick comparison`，不得作为默认 H3 测试或生产基线。
- 20 秒及更长本地实验可以继续执行，但必须记录其超出官方 H3 skill 4–15 秒目标范围的扩展条件；时长扩展不改变提示词格式要求。

## 内容落盘（项目专属位置）

- 原始实验数据与产物 → `experiments/`；当前模型清单、工作流结构、参数基线和安装步骤 → `docs/`；跨任务的稳定操作方法 → `.pi/skills/comfyui/`。同一事实只保留一处权威正文，其余位置链接引用。
- **实测定论**（参数值、加速比、可行性、选型）→ 现行值及适用条件写 `docs/`，演进史、覆盖链和证据锚 append 到 `.pi/ledger/`（见 `.pi/ledger/README.md`）。任务收尾按 `multi-agent-collab` 的远程流程执行；本地 progress/ledger 只保存证据和上下文，会话结束 retain 的实测定论打标 `[定论候选]`（见 mem0 skill）。
- 动态经验、踩坑、偏好 → Mem0 池 `comfy-ops`（跨界 → `global`）

## Sean 新增内容标签

- 本项目后续由 Sean 新增的脚本、节点、工作流、实验、manifest 和文档，必须带 `Sean` 所有者标签；不要为了加标签改名已有文件。
- 代码/节点文件使用模块注释或节点显示名 `Owner: Sean` / `[Sean] ...`；实验与缓存文件在 metadata/manifest 中写 `owner: Sean`，机器文件名可使用 `sean_` 前缀。
- 新增 ComfyUI 节点的 UI 名称优先使用 `[Sean] ...`，新增实验输出/manifest 的 prefix 优先使用 `sean_...`；历史文件和外部模型不追溯改名。

## Skill 划分纪律（多 skill 维护）

- 三层：**共享层**（跨所有 skill 的稳定契约，只写一份用引用不复制）/ **核心能力 skill**（框架层：安装+理解+节点+通用工作流）/ **特定用例 skill**（业务层：组装核心）
- 动态经验先进入 Mem0（按池隔离）；只有验证稳定且标明适用条件，才蒸馏为 docs 或 skill 的当前基线。
- 宿主边界必须写清：`h3-prompt-writing`、`comfyui`、`breeze-tts` 是本地可执行能力；依赖 MiniMax Hub canvas、choice cards 或 `hub_*` 工具的用例 skill 只在 Hub 宿主执行，其他宿主只能交付策划/提示词且必须显式说明降级
- 建 skill 前先读 `docs/14_skill_governance.md` 决定建哪种/经验放哪，再调 skill-creator 写文件
