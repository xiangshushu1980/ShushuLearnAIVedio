"""Contract-level QC Provider for the first vertical slice."""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path
from typing import Any


MANIFEST = {"capability": "qc", "version": "basic-qc@0.1", "input_schema": "daily-video/run.v1", "output_schema": "daily-video/qc.v1", "resources": {"cpu": 1, "gpu": False}}


def check(out: str | Path, script: dict[str, Any], timeline: dict[str, Any]) -> dict[str, Any]:
    root = Path(out)
    evidence_covered = all(s.get("evidence_ids") or s.get("review", {}).get("fact_status") != "supported" for s in script["segments"])
    files = ["evidence.json", "claims.json", "script.json", "storyboard.json", "timeline.json", "subtitles.srt", "audio.wav", "render.json", "preview.mp4"]
    media_ok = False
    ffprobe = shutil.which("ffprobe")
    if ffprobe and (root / "preview.mp4").exists():
        raw = subprocess.check_output([ffprobe, "-v", "error", "-show_entries", "format=duration", "-of", "json", str(root / "preview.mp4")])
        media_ok = abs(float(json.loads(raw)["format"]["duration"]) - float(timeline["duration_s"])) < 0.1
    checks = {"artifact_set_complete": all((root / name).exists() for name in files),
              "supported_script_segments_have_evidence": evidence_covered,
              "timeline_has_positive_duration": timeline["duration_s"] > 0,
              "render_duration_matches_timeline": media_ok}
    return {"schema_version": "daily-video/qc.v1", "status": "pass" if all(checks.values()) else "warn", "checks": checks, "producer": MANIFEST["version"]}
