"""Small immutable JSON Artifact Store used by the first vertical slice."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


class ArtifactStore:
    def __init__(self, root: str | Path) -> None:
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def put_json(self, run_id: str, kind: str, value: Any, producer: str,
                 supersedes: str | None = None) -> dict[str, Any]:
        payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
        digest = hashlib.sha256(payload).hexdigest()
        artifact_id = f"art_{kind}_{digest[:12]}"
        path = self.root / run_id / f"{artifact_id}.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists() and path.read_bytes() != payload:
            raise RuntimeError(f"immutable artifact collision: {artifact_id}")
        path.write_bytes(payload)
        result = {"artifact_id": artifact_id, "run_id": run_id, "kind": kind, "uri": str(path),
                  "content_hash": f"sha256:{digest}", "producer": producer,
                  "status": "candidate"}
        if supersedes:
            result["supersedes"] = supersedes
        return result

    def revise_json(self, previous: dict[str, Any], value: Any, producer: str) -> dict[str, Any]:
        """Write a changed immutable version while preserving the old Artifact."""
        run_id = previous.get("run_id") or Path(previous["uri"]).parent.name
        return self.put_json(run_id, previous["kind"], value,
                             producer, supersedes=previous["artifact_id"])

    def read_json(self, artifact: dict[str, Any]) -> Any:
        return json.loads(Path(artifact["uri"]).read_text(encoding="utf-8"))
