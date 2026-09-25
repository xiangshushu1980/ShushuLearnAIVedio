#!/usr/bin/env python3
"""Register and validate the daily-video workflow topology in Conductor."""

from __future__ import annotations

import argparse
import json
import urllib.error
import urllib.request

from workflow_definition import build, validate


def request(base: str, method: str, path: str, body: object) -> object:
    req = urllib.request.Request(base.rstrip("/") + path, data=json.dumps(body).encode(), method=method,
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=20) as response:
            raw = response.read()
            return json.loads(raw) if raw else None
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode(errors="replace")
        raise RuntimeError(f"HTTP {exc.code}: {detail}") from exc


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="http://127.0.0.1:18080")
    parser.add_argument("--name", default="daily_video_poc")
    args = parser.parse_args()
    workflow = build(args.name)
    validate(workflow)
    all_tasks = list(workflow["tasks"])
    for case_tasks in workflow["tasks"][4].get("decisionCases", {}).values():
        all_tasks.extend(case_tasks)
    task_defs = [{"name": task["name"], "description": "daily-video Provider task",
                  "retryCount": 2 if task["type"] == "SIMPLE" else 0,
                  "timeoutSeconds": 3600 if task["type"] == "SIMPLE" else 0,
                  "responseTimeoutSeconds": 30 if task["type"] == "SIMPLE" else 1,
                  "retryLogic": "FIXED", "retryDelaySeconds": 1} for task in all_tasks]
    request(args.base_url, "POST", "/api/metadata/taskdefs", task_defs)
    try:
        request(args.base_url, "POST", "/api/metadata/workflow", workflow)
    except RuntimeError as exc:
        if "HTTP 409" not in str(exc):
            raise
        request(args.base_url, "PUT", "/api/metadata/workflow", [workflow])
    print(json.dumps({"status": "registered", "workflow": args.name, "tasks": [t["taskReferenceName"] for t in workflow["tasks"]]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
