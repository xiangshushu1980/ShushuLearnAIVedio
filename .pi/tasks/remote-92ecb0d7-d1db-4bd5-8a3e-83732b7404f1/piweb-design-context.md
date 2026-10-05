# [Sean] PiWeb 接入设计评审续接

Owner: Sean。2026-10-05。

当前任务 controller：`01a100c6-8f5d-7bd2-b205-ce08d7ac0b92`，generation 18；生命周期以 Task Center 为准。

用户要求设计项目归属、多对话、skill 粒度与动态载入、AI 工具 CLI、任务系统复用、Mem0/文档配合，制定开发测试计划；用户选择先审阅确认再实施。2026-10-05 后续“继续”按继续完成设计评审理解，未视作对尚未展示方案的实施批准。

评审稿：`film-editor/PIWEB_DESIGN.md`；计划：`film-editor/PIWEB_PLAN.md`。已自审，文档链接和 Owner 标签检查通过。没有修改运行代码、用户级文件、Hivemind，未创建 PI 会话/制作任务、未提交 GPU。

建议：独立制作目录 `~/projects/film-production/films/<UUID>`，instanceId+filmProjectId 明确绑定；多个对话一个制作 controller；沿用 Task Center 与现有 SQLite；薄 CLI+身份扩展；四个制作 skill，H3 规范引用现有文件；文档存约定，Mem0 存经验。保留旧助手到新流程验证通过。

关键风险：Hivemind 文档要求远程控制权，检索的 `/api/open` 仍有旧 registry/TODO 逻辑，P0 必须核对实际运行入口。现开发任务已绑定 Codex，不能跨类型换成 PI 制作任务。远程 controller 与 SQLite 无跨系统原子事务，方案写明校验/交接/已接受操作边界，不能宣称严格原子 fencing 已实现。

下一步：用户审阅两份文档并确认设计；批准后依次 P0 宿主契约、P1 业务接口/CLI、P2 绑定、P3 skills、P4 隔离真实文字流程、P5 迁移交付。若宿主需要改变任务协议或大规模重构，应再提交具体方案。

既有交付见 `delivery.md`，代码 73f38f1/511408b/7abdc3b；本轮设计不使旧成果失效。现有影片与进程不变，工作树中 `film-editor/.env.example` 和大量其他项目改动不属于本轮。
