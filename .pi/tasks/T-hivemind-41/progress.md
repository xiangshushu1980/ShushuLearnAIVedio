# T-hivemind-41：远端轻量任务协调器与本地 Worker 分离控制面 POC

## 范围

- 远端 Coordinator API：claim/renew/release/checkpoint/finish/heartbeat。
- SQLite 持久化、Bearer 认证、幂等键、generation/fencing token、断线/租约过期语义。
- 本地 `HiveAgentAdapter`；保留本地 TODO、progress 与 `[STATE]`，不迁移既有 Hive CLI。
- 明确不做 Web 看板、Codex/Pi/ComfyUI 迁移、远端 shell/PTY/本机服务控制。

## 已完成

- `tools/hivemind/coordinator.py`：持久化任务状态机与事件日志。
- `tools/hivemind/server.py`：标准库 HTTP API，支持 bearer token。
- `tools/hivemind/adapter.py`：本地 Worker 客户端及显式 append-only progress helper。
- `tools/hivemind/test_coordinator.py`：生命周期、幂等、认证、租约过期、旧 token fencing 测试。
- `tools/hivemind/test_http_adapter.py`：真实 HTTP Server + `HiveAgentAdapter` 集成测试，覆盖重启、断线过期、并发 claim、认证和 progress 保留。
- 稳定性补充：覆盖显式 release 后旧 lease fencing、HTTP 层幂等键冲突；POST 先认证再解析 body，未认证畸形请求不会泄露为业务解析错误。
- `tools/hivemind/README.md`：接口与断线语义说明。

## 设计定论

- 断线不立即取消任务；lease 到期后才可被新 Worker claim。
- 每次新 claim 递增 generation 并生成新 fencing token；旧 worker 的所有写操作拒绝。
- 幂等键重复且请求相同返回原响应；相同键请求不同返回冲突。
- adapter 不改 TODO、不会重建/删除 progress 或 `[STATE]`；checkpoint 是否追加到 progress 由调用方显式决定。

## 验证

- `PYTHONPATH=tools python3 -m unittest tools.hivemind.test_coordinator`：3 tests passed。
- `python3 -m compileall -q tools/hivemind`：通过。
- 临时 HTTP 冒烟（Bearer auth）：create → claim → heartbeat with invalid fencing token；最后一步按预期返回 HTTP 409 `fenced`。
- `PYTHONPATH=tools python3 -m unittest tools.hivemind.test_coordinator tools.hivemind.test_http_adapter`：8 tests passed；覆盖真实 HTTP、adapter 生命周期、幂等重试、SQLite 重启恢复、断线过期与旧 token fencing、并发 claim、认证和 append-only progress。
- 最新 `PYTHONPATH=tools python3 -m unittest -q tools.hivemind.test_coordinator tools.hivemind.test_http_adapter`：10 tests passed；新增 release fencing 与 HTTP 幂等冲突验证。
- 默认沙箱禁止绑定 localhost socket；HTTP 集成测试使用临时宿主权限执行，测试本身无失败。
- 未启动 ComfyUI、未访问远端 shell/PTY、未修改或迁移本地 TODO/[STATE]。
