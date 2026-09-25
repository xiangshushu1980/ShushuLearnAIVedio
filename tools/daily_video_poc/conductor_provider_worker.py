#!/usr/bin/env python3
"""Run local daily-video Providers behind Conductor SIMPLE tasks."""

from __future__ import annotations

import argparse
import json
import time
from datetime import datetime, timezone
import urllib.request
from pathlib import Path

from audio_provider import synthesize
from director_provider import direct
from poc import make_claims, make_storyboard, make_timeline, write_srt
from qc_provider import check
from render_provider import render
from source_provider import collect


STAGES = {"daily_video_source", "daily_video_director", "daily_video_tts", "daily_video_render", "daily_video_qc"}


class Worker:
    def __init__(self, base: str, root: Path, worker_id: str) -> None:
        self.base, self.root, self.worker_id = base.rstrip("/"), root, worker_id
        self.events: list[dict] = []

    def event(self, workflow_id: str, stage: str, status: str, **extra: object) -> None:
        self.events.append({"at": datetime.now(timezone.utc).isoformat(), "run_id": workflow_id,
                            "stage": stage, "status": status, **extra})

    def request(self, path: str, method: str = "GET", body: object | None = None) -> object:
        data = None if body is None else json.dumps(body, ensure_ascii=False).encode()
        req = urllib.request.Request(self.base + path, data=data, method=method, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=20) as response:
            raw = response.read()
        if not raw:
            return None
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return raw.decode(errors="replace")

    def poll(self, task: str) -> dict:
        value = self.request(f"/api/tasks/poll/{task}?workerid={self.worker_id}")
        return value if isinstance(value, dict) else {}

    def complete(self, task: dict, result: dict) -> None:
        self.request("/api/tasks", "POST", {"taskId": task["taskId"], "workflowInstanceId": task["workflowInstanceId"],
                     "workerId": self.worker_id, "status": "COMPLETED", "outputData": result})

    def fail(self, task: dict, error: Exception) -> None:
        self.request("/api/tasks", "POST", {"taskId": task["taskId"], "workflowInstanceId": task["workflowInstanceId"],
                     "workerId": self.worker_id, "status": "FAILED",
                     "reasonForIncompletion": str(error),
                     "outputData": {"failure_class": type(error).__name__, "message": str(error)}})

    def execute(self, task: dict) -> None:
        task_type = task["taskType"]
        workflow_id = task["workflowInstanceId"]
        self.event(workflow_id, task.get("referenceTaskName", task_type), "started")
        run_dir = self.root / task["workflowInstanceId"]
        run_dir.mkdir(parents=True, exist_ok=True)
        inputs = task.get("inputData") or {}
        if task_type == "daily_video_source":
            evidence = collect(str(inputs.get("source", "tools/daily_video_poc/example_topic.json")), inputs.get("topic"))
            (run_dir / "evidence.json").write_text(json.dumps(evidence, ensure_ascii=False, indent=2), encoding="utf-8")
            result = {"evidence": evidence, "artifact_ref": str(run_dir / "evidence.json")}
        elif task_type == "daily_video_director":
            evidence = json.loads((run_dir / "evidence.json").read_text(encoding="utf-8"))
            script = direct(evidence)
            timeline = make_timeline(script)
            (run_dir / "script.json").write_text(json.dumps(script, ensure_ascii=False, indent=2), encoding="utf-8")
            (run_dir / "timeline.json").write_text(json.dumps(timeline, ensure_ascii=False, indent=2), encoding="utf-8")
            (run_dir / "claims.json").write_text(json.dumps(make_claims(evidence), ensure_ascii=False, indent=2), encoding="utf-8")
            (run_dir / "storyboard.json").write_text(json.dumps(make_storyboard(script, timeline), ensure_ascii=False, indent=2), encoding="utf-8")
            write_srt(script, timeline, run_dir / "subtitles.srt")
            result = {"script": script, "timeline": timeline, "artifact_ref": str(run_dir / "script.json")}
        elif task_type == "daily_video_tts":
            script = json.loads((run_dir / "script.json").read_text(encoding="utf-8")); timeline = json.loads((run_dir / "timeline.json").read_text(encoding="utf-8"))
            result = {"audio": synthesize(script, timeline, run_dir / "audio.wav"), "artifact_ref": str(run_dir / "audio.wav")}
        elif task_type == "daily_video_render":
            script = json.loads((run_dir / "script.json").read_text(encoding="utf-8")); timeline = json.loads((run_dir / "timeline.json").read_text(encoding="utf-8"))
            video = render(script, timeline, run_dir / "audio.wav", run_dir / "preview.mp4")
            (run_dir / "render.json").write_text(json.dumps(video, ensure_ascii=False, indent=2), encoding="utf-8")
            result = {"video": video, "artifact_ref": str(run_dir / "preview.mp4")}
        elif task_type == "daily_video_qc":
            script = json.loads((run_dir / "script.json").read_text(encoding="utf-8")); timeline = json.loads((run_dir / "timeline.json").read_text(encoding="utf-8"))
            result = {"qc": check(run_dir, script, timeline), "artifact_ref": str(run_dir / "qc.json")}
            (run_dir / "qc.json").write_text(json.dumps(result["qc"], ensure_ascii=False, indent=2), encoding="utf-8")
        else:
            return
        self.complete(task, result)
        self.event(workflow_id, task.get("referenceTaskName", task_type), "completed", artifact_ref=result.get("artifact_ref"))

    def run_until(self, workflow_id: str, timeout: float = 300) -> dict:
        deadline = time.time() + timeout
        while time.time() < deadline:
            state = self.request(f"/api/workflow/{workflow_id}")
            approval = next((t for t in state.get("tasks", []) if t.get("referenceTaskName") == "approval"), None)
            if approval and approval.get("status") in {"IN_PROGRESS", "COMPLETED"}:
                status = "blocked" if approval["status"] == "IN_PROGRESS" else "completed"
                previous = next((e for e in reversed(self.events) if e["stage"] == "approval"), None)
                if not previous or previous["status"] != status:
                    self.event(workflow_id, "approval", status,
                               decision=(approval.get("outputData") or {}).get("decision"))
            if state.get("status") in {"COMPLETED", "FAILED", "TERMINATED", "TIMED_OUT"}:
                run_dir = self.root / workflow_id
                run_dir.mkdir(parents=True, exist_ok=True)
                manifest = {"schema_version": "daily-video/conductor-run.v1", "run_id": workflow_id,
                            "workflow_status": state.get("status"), "events": self.events,
                            "artifacts": sorted(p.name for p in run_dir.iterdir() if p.is_file())}
                (run_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
                return state
            for task in STAGES:
                item = self.poll(task)
                if item.get("taskId") and item.get("workflowInstanceId") == workflow_id:
                    try:
                        self.execute(item)
                    except (OSError, ValueError, RuntimeError, KeyError) as error:
                        self.event(workflow_id, item.get("referenceTaskName", task), "failed",
                                   failure_class=type(error).__name__, message=str(error))
                        self.fail(item, error)
            time.sleep(0.2)
        raise TimeoutError(workflow_id)


def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("workflow_id"); parser.add_argument("--base-url", default="http://127.0.0.1:18080"); parser.add_argument("--root", type=Path, default=Path("/tmp/t32-conductor-provider-runs")); args = parser.parse_args()
    state = Worker(args.base_url, args.root, "t32-provider-worker").run_until(args.workflow_id)
    print(json.dumps({"workflow_id": args.workflow_id, "status": state.get("status")}, ensure_ascii=False)); return 0 if state.get("status") == "COMPLETED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
