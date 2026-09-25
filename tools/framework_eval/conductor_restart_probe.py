#!/usr/bin/env python3
"""Create a durable HUMAN wait used by the container-restart probe."""

from __future__ import annotations

import json
import time
import uuid
from urllib.request import Request, urlopen


BASE = "http://127.0.0.1:18080"


def request(path: str, method: str = "GET", body: object | None = None) -> object:
    data = None if body is None else json.dumps(body).encode()
    req = Request(BASE + path, data=data, method=method, headers={"Content-Type": "application/json"})
    with urlopen(req, timeout=20) as response:
        raw = response.read()
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return raw.decode()


suffix = uuid.uuid4().hex[:8]
workflow = f"t32_restart_probe_{suffix}"
request("/api/metadata/workflow", "POST", {
    "name": workflow, "version": 1, "schemaVersion": 2, "restartable": True,
    "timeoutSeconds": 300, "inputParameters": ["topic"],
    "tasks": [{"name": "approval", "taskReferenceName": "approval", "type": "HUMAN", "workflowTaskType": "HUMAN", "inputParameters": {}}],
})
workflow_id = str(request(f"/api/workflow/{workflow}", "POST", {"topic": "容器重启恢复验证"}))
for _ in range(40):
    detail = request(f"/api/workflow/{workflow_id}")
    task = next((x for x in detail.get("tasks", []) if x.get("referenceTaskName") == "approval"), None)
    if task and task.get("status") == "IN_PROGRESS":
        print(json.dumps({"workflow": workflow, "workflow_id": workflow_id, "task_id": task.get("taskId")}, ensure_ascii=False))
        break
    time.sleep(0.25)
else:
    raise SystemExit(f"HUMAN task did not enter IN_PROGRESS: {detail}")
