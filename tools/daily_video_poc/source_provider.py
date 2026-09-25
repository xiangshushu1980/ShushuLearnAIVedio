"""Provider-neutral Source implementation for the first real input boundary."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse
from urllib.request import Request, urlopen


MANIFEST = {
    "capability": "source",
    "version": "source-json@0.1",
    "input_schema": "daily-video/topic.v1",
    "output_schema": "daily-video/evidence.v1",
    "resources": {"cpu": 1, "gpu": False},
    "retryable": True,
    "failure_classes": ["invalid_input", "fetch_failed", "unsupported_source"],
}


def _load(source: str) -> dict[str, Any]:
    parsed = urlparse(source)
    if parsed.scheme in {"http", "https"}:
        request = Request(source, headers={"Accept": "application/json", "User-Agent": "comfy-ops-source/0.1"})
        with urlopen(request, timeout=20) as response:
            value = json.loads(response.read())
    else:
        value = json.loads(Path(source).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("source payload must be a JSON object")
    return value


def collect(source: str, topic: str | None = None) -> dict[str, Any]:
    """Normalize a JSON topic/evidence pack and attach collection provenance."""
    value = _load(source)
    if not value.get("topic") and not topic:
        raise ValueError("source payload requires topic")
    if not isinstance(value.get("evidence"), list) or not value["evidence"]:
        raise ValueError("source payload requires a non-empty evidence list")
    result = dict(value)
    result["schema_version"] = "daily-video/evidence.v1"
    result["topic"] = value.get("topic") or topic
    result["collection"] = {"provider": MANIFEST["version"],
                             "source": source,
                             "captured_at": datetime.now(timezone.utc).isoformat()}
    return result
