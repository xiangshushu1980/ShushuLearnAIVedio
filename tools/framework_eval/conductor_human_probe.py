#!/usr/bin/env python3
"""Verify Conductor HUMAN task pause and external approval completion."""

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
workflow = f"t32_human_probe_{suffix}"
request("/api/metadata/workflow", "POST", {
    "name": workflow, "version": 1, "schemaVersion": 2, "restartable": True,
    "timeoutSeconds": 300, "inputParameters": ["topic"],
    "tasks": [{"name": "approval", "taskReferenceName": "approval", "type": "HUMAN", "workflowTaskType": "HUMAN", "inputParameters": {"topic": "${workflow.input.topic}"}}],
    "outputParameters": {"decision": "${approval.output.decision}"},
})
workflow_id = str(request(f"/api/workflow/{workflow}", "POST", {"topic": "审核暂停验证"}))
task = None
for _ in range(40):
    detail = request(f"/api/workflow/{workflow_id}")
    task = next((x for x in detail.get("tasks", []) if x.get("referenceTaskName") == "approval"), None)
    if task and task.get("status") == "IN_PROGRESS":
        break
    time.sleep(0.25)
if not task or task.get("status") != "IN_PROGRESS":
    raise SystemExit(f"approval did not pause: {detail}")
request(f"/api/tasks/{workflow_id}/approval/COMPLETED/sync", "POST", {"decision": "approved", "approver": "t32-test"})
for _ in range(40):
    detail = request(f"/api/workflow/{workflow_id}")
    if detail.get("status") in {"COMPLETED", "FAILED", "TERMINATED", "TIMED_OUT"}:
        break
    time.sleep(0.25)
print(json.dumps({"workflow": workflow, "workflow_id": workflow_id, "approval_status": task["status"], "final_status": detail.get("status"), "decision": detail.get("output")}, ensure_ascii=False))
