#!/usr/bin/env python3
"""Repeatable acceptance check for the provider-neutral daily-video slice."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

from audio_provider import MANIFEST as AUDIO
from director_provider import MANIFEST as DIRECTOR
from qc_provider import MANIFEST as QC
from render_provider import MANIFEST as RENDER
from source_provider import MANIFEST as SOURCE
from workflow_definition import build, validate as validate_workflow


REQUIRED = {"capability", "version", "input_schema", "output_schema", "resources"}


def main() -> int:
    root = Path(__file__).resolve().parent
    fixture = root / "example_topic.json"
    manifests = [SOURCE, DIRECTOR, AUDIO, RENDER, QC]
    workflow = build("daily_video_acceptance")
    validate_workflow(workflow)
    for manifest in manifests:
        missing = REQUIRED - manifest.keys()
        if missing:
            raise AssertionError(f"{manifest.get('capability')} missing manifest fields: {sorted(missing)}")
    with tempfile.TemporaryDirectory(prefix="daily-video-acceptance-") as tmp:
        out = Path(tmp) / "run"
        subprocess.run([sys.executable, str(root / "poc.py"), str(fixture), "--out", str(out)], check=True)
        manifest = json.loads((out / "manifest.json").read_text(encoding="utf-8"))
        qc = json.loads((out / "qc.json").read_text(encoding="utf-8"))
        assert qc["status"] == "pass", qc
        assert len(manifest["events"]) == 5, manifest["events"]
        assert (out / "preview.mp4").exists()
        print(json.dumps({"status": "pass", "providers": [m["version"] for m in manifests],
                          "workflow_tasks": [t["taskReferenceName"] for t in workflow["tasks"]],
                          "artifacts": len(manifest["artifacts"]), "events": len(manifest["events"]),
                          "qc_checks": qc["checks"]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
