"""FFmpeg Render Provider for timeline + audio artifacts."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
from typing import Any


MANIFEST = {
    "capability": "render",
    "version": "ffmpeg-render@0.1",
    "input_schema": "daily-video/timeline.v1 + audio/wav + daily-video/script.v1",
    "output_schema": "video/mp4",
    "resources": {"cpu": 2, "gpu": False},
    "retryable": True,
    "failure_classes": ["invalid_timeline", "missing_audio", "render_failed"],
}


def render(script: dict[str, Any], timeline: dict[str, Any], audio: str | Path, output: str | Path) -> dict[str, Any]:
    if timeline.get("duration_s", 0) <= 0:
        raise ValueError("render Provider requires a positive timeline")
    audio_path = Path(audio)
    if not audio_path.exists():
        raise FileNotFoundError(audio_path)
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise RuntimeError("ffmpeg is required for render Provider")
    destination = Path(output)
    destination.parent.mkdir(parents=True, exist_ok=True)
    title = str(script.get("title", "未命名")).replace(":", "\\:").replace("'", "\\'")
    duration = float(timeline["duration_s"])
    command = [ffmpeg, "-y", "-f", "lavfi", "-i", f"color=c=0x18212f:s=1280x720:r=25:d={duration}",
               "-i", str(audio_path), "-vf", f"drawtext=text='{title}':fontcolor=white:fontsize=52:x=(w-text_w)/2:y=(h-text_h)/2",
               "-map", "0:v:0", "-map", "1:a:0", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", "-shortest", str(destination)]
    subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return {"kind": "video", "uri": str(destination), "format": "mp4",
            "duration_s": duration, "producer": MANIFEST["version"]}
