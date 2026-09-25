#!/usr/bin/env python3
"""End-to-end check for the project-side Conductor adapter."""

from __future__ import annotations

import argparse
import json
import time
import urllib.request

from conductor_adapter import ConductorAdapter


def complete_task(base: str, task: dict, run_id: str, worker: str) -> None:
    name = task["taskType"]
    output = {"stage": name, "artifact_ref": f"artifact://adapter/{name}"}
    body = {"taskId": task["taskId"], "workflowInstanceId": run_id,
            "workerId": worker, "status": "COMPLETED",
            "outputData": {"result": output}}
    request = urllib.request.Request(base + "/api/tasks", data=json.dumps(body).encode(),
                                     method="POST", headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(request, timeout=10):
        pass


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="http://127.0.0.1:18080")
    args = parser.parse_args()
    adapter = ConductorAdapter(args.base_url)
    run = adapter.start_run("t32_framework_probe", {"title": "Adapter E2E"})
    worker = "t32-project-adapter-probe"
    task_types = ("t32_source", "t32_director", "t32_render")
    for _ in range(100):
        status = adapter.get_run(run).get("status")
        if status in {"COMPLETED", "FAILED", "TERMINATED", "TIMED_OUT"}:
            break
        for task_type in task_types:
            request = urllib.request.Request(f"{args.base_url}/api/tasks/poll/{task_type}?workerid={worker}")
            with urllib.request.urlopen(request, timeout=10) as response:
                raw = response.read()
            task = json.loads(raw) if raw else {}
            if task.get("taskId"):
                complete_task(args.base_url, task, run.run_id, worker)
        time.sleep(0.2)
    final = adapter.get_run(run)
    print(json.dumps({"run_id": run.run_id, "workflow_version": run.workflow_version,
                      "status": final.get("status")}, ensure_ascii=False))
    return 0 if final.get("status") == "COMPLETED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
