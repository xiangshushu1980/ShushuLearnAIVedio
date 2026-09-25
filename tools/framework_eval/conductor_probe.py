#!/usr/bin/env python3
"""Small Conductor OSS probe: register and run a Python-worker pipeline."""

from __future__ import annotations

import argparse
import json
import time
import urllib.error
import urllib.request
import uuid
from pathlib import Path


TASKS = ["t32_source", "t32_director", "t32_render"]
WORKFLOW = "t32_framework_probe"


def request(base: str, method: str, path: str, body: object | None = None) -> object:
    data = None if body is None else json.dumps(body).encode()
    req = urllib.request.Request(base.rstrip("/") + path, data=data, method=method, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=20) as response:
            raw = response.read()
            if not raw:
                return None
            try:
                return json.loads(raw)
            except json.JSONDecodeError:
                return raw.decode()
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode(errors="replace")
        raise RuntimeError(f"{method} {path}: HTTP {exc.code}: {detail}") from exc


def register(base: str) -> None:
    defs = [{
        "name": task,
        "description": "T-32 framework evaluation task",
        "retryCount": 2,
        "timeoutSeconds": 120,
        "responseTimeoutSeconds": 30,
        "retryLogic": "EXPONENTIAL_BACKOFF",
        "retryDelaySeconds": 1,
    } for task in TASKS]
    request(base, "POST", "/api/metadata/taskdefs", defs)
    workflow = {
        "name": WORKFLOW,
        "description": "T-32 Source -> Director -> Render probe",
        "version": 1,
        "schemaVersion": 2,
        "restartable": True,
        "timeoutSeconds": 600,
        "inputParameters": ["topic"],
        "tasks": [{
            "name": task,
            "taskReferenceName": task,
            "type": "SIMPLE",
            "workflowTaskType": "SIMPLE",
            "inputParameters": {"topic": "${workflow.input.topic}"},
        } for task in TASKS],
        "outputParameters": {"last_output": "${t32_render.output.result}"},
    }
    try:
        request(base, "POST", "/api/metadata/workflow", workflow)
    except RuntimeError as exc:
        if "HTTP 409" not in str(exc):
            raise
        request(base, "PUT", "/api/metadata/workflow", [workflow])


def run_worker(base: str, workflow_id: str, out: Path) -> list[dict]:
    events: list[dict] = []
    worker_id = f"t32-probe-{uuid.uuid4().hex[:8]}"
    while True:
        status = request(base, "GET", f"/api/workflow/{workflow_id}")
        if isinstance(status, dict) and status.get("status") in {"COMPLETED", "FAILED", "TERMINATED", "TIMED_OUT"}:
            return events
        for task in TASKS:
            polled = request(base, "GET", f"/api/tasks/poll/{task}?workerid={worker_id}")
            if not isinstance(polled, dict) or not polled.get("taskId"):
                continue
            task_id = polled["taskId"]
            input_data = polled.get("inputData") or {}
            result = {"stage": task.removeprefix("t32_"), "topic": input_data.get("topic"), "artifact_ref": f"artifact://conductor-probe/{task}"}
            event = {"task": task, "task_id": task_id, "status": "COMPLETED", "result": result}
            request(base, "POST", "/api/tasks", {
                "taskId": task_id,
                "workflowInstanceId": workflow_id,
                "workerId": worker_id,
                "status": "COMPLETED",
                "outputData": {"result": result},
            })
            events.append(event)
            out.mkdir(parents=True, exist_ok=True)
            (out / f"{task}.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
        time.sleep(0.25)


def main() -> int:
    global TASKS, WORKFLOW
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="http://127.0.0.1:18080")
    parser.add_argument("--out", type=Path, default=Path("/tmp/t32-conductor-probe"))
    args = parser.parse_args()
    suffix = uuid.uuid4().hex[:8]
    TASKS = [f"t32_{stage}_{suffix}" for stage in ("source", "director", "render")]
    WORKFLOW = f"t32_framework_probe_{suffix}"
    register(args.base_url)
    started = request(args.base_url, "POST", f"/api/workflow/{WORKFLOW}", {"topic": "Conductor Python Worker 验证"})
    workflow_id = str(started)
    events = run_worker(args.base_url, workflow_id, args.out)
    final = request(args.base_url, "GET", f"/api/workflow/{workflow_id}")
    manifest = {"workflow_id": workflow_id, "workflow": WORKFLOW, "events": events, "final": final}
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"workflow_id": workflow_id, "status": final.get("status") if isinstance(final, dict) else None, "events": len(events)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
