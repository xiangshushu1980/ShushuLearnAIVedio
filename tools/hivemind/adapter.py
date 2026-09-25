from __future__ import annotations

import json
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class Lease:
    task_id: str
    worker_id: str
    generation: int
    fencing_token: str
    lease_until: float
    payload: dict[str, Any]


class HiveAgentAdapter:
    """Remote lease client that leaves local Hive records under local control.

    It never edits TODO.md or deletes/replaces progress/[STATE].  A caller may
    append a human-readable checkpoint to its existing progress file explicitly.
    """
    def __init__(self, base_url: str, worker_id: str, token: str | None = None):
        self.base_url, self.worker_id, self.token = base_url.rstrip("/"), worker_id, token

    def _request(self, method: str, path: str, body: dict[str, Any], idem: str | None = None) -> dict[str, Any]:
        headers = {"Content-Type": "application/json"}
        if self.token: headers["Authorization"] = f"Bearer {self.token}"
        if idem: headers["Idempotency-Key"] = idem
        req = urllib.request.Request(self.base_url + path, json.dumps(body).encode(), headers, method=method)
        try:
            with urllib.request.urlopen(req, timeout=20) as response: raw = response.read()
        except urllib.error.HTTPError as exc:
            detail = json.loads(exc.read() or b"{}"); raise RuntimeError(f"coordinator {exc.code}: {detail}") from exc
        return json.loads(raw or b"{}")

    def claim(self, task_id: str | None = None, idempotency_key: str | None = None) -> Lease:
        body = {"worker_id": self.worker_id};
        if task_id: body["task_id"] = task_id
        value = self._request("POST", "/v1/claims", body, idempotency_key)
        return Lease(value["task_id"], self.worker_id, value["generation"], value["fencing_token"], value["lease_until"], value.get("payload", {}))

    def _lease(self, lease: Lease, action: str, body: dict[str, Any] | None = None, key: str | None = None) -> dict[str, Any]:
        return self._request("POST", f"/v1/tasks/{lease.task_id}/{action}",
                            {"worker_id": lease.worker_id, "generation": lease.generation,
                             "fencing_token": lease.fencing_token, **(body or {})}, key)

    def renew(self, lease: Lease, idempotency_key: str | None = None) -> dict[str, Any]: return self._lease(lease, "renew", key=idempotency_key)
    def heartbeat(self, lease: Lease, idempotency_key: str | None = None) -> dict[str, Any]: return self._lease(lease, "heartbeat", key=idempotency_key)
    def checkpoint(self, lease: Lease, checkpoint: dict[str, Any], idempotency_key: str | None = None) -> dict[str, Any]: return self._lease(lease, "checkpoint", {"checkpoint": checkpoint}, idempotency_key)
    def finish(self, lease: Lease, result: dict[str, Any], idempotency_key: str | None = None) -> dict[str, Any]: return self._lease(lease, "finish", {"result": result}, idempotency_key)
    def release(self, lease: Lease, idempotency_key: str | None = None) -> dict[str, Any]: return self._lease(lease, "release", key=idempotency_key)

    @staticmethod
    def append_progress(progress_file: str | Path, task_id: str, checkpoint: dict[str, Any]) -> None:
        """Append-only bridge; does not rewrite local task truth."""
        path = Path(progress_file); path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as stream:
            stream.write(f"\n## Remote checkpoint {task_id}\n{json.dumps(checkpoint, ensure_ascii=False, indent=2)}\n")
