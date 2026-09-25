"""Deterministic audio Provider; its contract can later be backed by Breeze-TTS."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
from typing import Any


MANIFEST = {
    "capability": "tts",
    "version": "tone-tts@0.1",
    "input_schema": "daily-video/script.v1 + daily-video/timeline.v1",
    "output_schema": "audio/wav + daily-video/audio-metadata.v1",
    "resources": {"cpu": 1, "gpu": False},
    "retryable": True,
    "failure_classes": ["invalid_script", "audio_render_failed"],
}


def synthesize(script: dict[str, Any], timeline: dict[str, Any], output: str | Path) -> dict[str, Any]:
    if script.get("schema_version") != "daily-video/script.v1":
        raise ValueError("audio Provider requires daily-video/script.v1")
    duration = float(timeline.get("duration_s", 0))
    if duration <= 0:
        raise ValueError("audio Provider requires a positive timeline duration")
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise RuntimeError("ffmpeg is required for tone audio Provider")
    path = Path(output)
    path.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run([ffmpeg, "-y", "-f", "lavfi", "-i",
                    f"sine=frequency=220:sample_rate=24000:duration={duration}",
                    "-c:a", "pcm_s16le", str(path)], check=True,
                   stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return {"kind": "audio", "uri": str(path), "format": "wav",
            "duration_s": duration, "producer": MANIFEST["version"]}
