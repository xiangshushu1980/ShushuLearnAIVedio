# Orchestrator framework evaluation fixtures

这些文件是 T-comfy-ops-32 的统一最小测试夹具，不是新的业务运行时。

`fake_pipeline.py` 用本地事件日志模拟：

```text
Source → Director → Approval → Render
```

后续每个框架只需要把四个 stage 映射成自己的 workflow/task/worker，输入输出仍使用同一份 JSON 和 `artifact_ref` 语义。

Conductor 已运行时可执行 Python Worker 探针：

```bash
python3 tools/framework_eval/conductor_probe.py \
  --base-url http://127.0.0.1:18080 \
  --out /tmp/t32-conductor-probe

Node.js Worker：

```bash
node tools/framework_eval/conductor_node_probe.mjs http://127.0.0.1:18080
```
```

人工审核暂停/恢复：

```bash
python3 tools/framework_eval/conductor_human_probe.py
```

容器重启恢复（先运行脚本取得 workflow_id，再重启容器，最后用 `/api/tasks/{workflowId}/approval/COMPLETED/sync` 完成）：

```bash
python3 tools/framework_eval/conductor_restart_probe.py
```
```

Temporal Python 对照：

```bash
PYTHONPATH=/tmp/t32-temporal-packages \
  /home/sean/projects/ComfyUI/venv/bin/python tools/framework_eval/temporal_probe.py
```

运行：

```bash
python3 tools/framework_eval/fake_pipeline.py \
  --input tools/framework_eval/fixtures/topic.json \
  --out /tmp/t32-framework-baseline
```

环境变量 `FAKE_APPROVAL=rejected` 可验证审核拒绝路径；`FAKE_FAIL_STAGE=director` 可验证失败事件路径。

## 项目侧 Provider 垂直切片

本地完整链路和结构审查：

```bash
PYTHONPATH=tools/daily_video_poc \
  python3 tools/daily_video_poc/vertical_slice_verify.py
```

注册 Conductor 拓扑：

```bash
PYTHONPATH=tools/daily_video_poc \
  python3 tools/daily_video_poc/register_workflow.py \
  --name daily_video_poc_t32
```

Provider Worker：

```bash
python3 tools/daily_video_poc/conductor_provider_worker.py <workflow_id>
```

拓扑是 `Source → Director → TTS → HUMAN Approval → Decision → Render → QC`；只有 approved 分支创建 Render/QC。
