#!/usr/bin/env python3
"""Framework-neutral baseline for the T-32 orchestrator evaluation."""

from __future__ import annotations

import argparse
import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    data = json.loads(args.input.read_text(encoding="utf-8"))
    args.out.mkdir(parents=True, exist_ok=True)
    run_id = f"run_eval_{uuid.uuid4().hex[:10]}"
    events: list[dict] = []
    artifacts: list[dict] = []
    fail_stage = os.getenv("FAKE_FAIL_STAGE")
    approval = os.getenv("FAKE_APPROVAL", "approved")

    def emit(stage: str, status: str, **extra: object) -> None:
        events.append({"at": now(), "run_id": run_id, "stage": stage, "status": status, **extra})

    def artifact(kind: str, value: object, producer: str) -> str:
        artifact_id = f"art_{kind}_{len(artifacts) + 1:02d}"
        path = args.out / f"{artifact_id}.json"
        path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")
        artifacts.append({"artifact_id": artifact_id, "kind": kind, "uri": str(path), "producer": producer, "status": "candidate"})
        return artifact_id

    for stage in ("source", "director"):
        emit(stage, "started")
        if fail_stage == stage:
            emit(stage, "failed", failure_class="fixture_failure")
            break
        if stage == "source":
            source_ref = artifact("evidence", data, "fake_source@1")
        else:
            script = {"topic": data.get("topic"), "evidence_ref": source_ref, "text": "这是一个可审核的测试脚本。"}
            script_ref = artifact("script", script, "fake_director@1")
        emit(stage, "succeeded")
    else:
        emit("approval", "blocked", decision_required=True)
        emit("approval", approval, reason="fixture decision")
        if approval == "approved":
            timeline_ref = artifact("timeline", {"script_ref": script_ref, "duration_s": 5.0}, "fake_render@1")
            emit("render", "succeeded", output_ref=timeline_ref)
        else:
            emit("run", "rejected")

    manifest = {"schema_version": "daily-video/framework-eval-run.v1", "run_id": run_id, "events": events, "artifacts": artifacts}
    (args.out / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"run_id": run_id, "event_count": len(events), "artifact_count": len(artifacts)}, ensure_ascii=False))
    return 0 if not fail_stage else 1


if __name__ == "__main__":
    raise SystemExit(main())
