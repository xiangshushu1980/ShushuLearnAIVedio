"""Project-side Conductor adapter boundary.

Only this module knows Conductor REST paths.  Project callers deal in a Run
reference and review decisions; Artifact/Provider contracts stay independent
of the orchestrator implementation.
"""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any


@dataclass(frozen=True)
class RunRef:
    run_id: str
    workflow_name: str
    workflow_version: int


class ConductorAdapter:
    def __init__(self, base_url: str = "http://127.0.0.1:18080") -> None:
        self.base_url = base_url.rstrip("/")

    def _request(self, method: str, path: str, body: Any = None) -> Any:
        payload = None if body is None else json.dumps(body).encode("utf-8")
        request = urllib.request.Request(
            self.base_url + path,
            data=payload,
            method=method,
            headers={"Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(request, timeout=20) as response:
                raw = response.read()
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode(errors="replace")
            raise RuntimeError(f"Conductor {method} {path}: HTTP {exc.code}: {detail}") from exc
        if not raw:
            return None
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return raw.decode("utf-8")

    def start_run(self, workflow_name: str, topic: dict[str, Any]) -> RunRef:
        workflow = self._request("GET", f"/api/metadata/workflow/{workflow_name}")
        version = int(workflow.get("version", 1))
        run_id = str(self._request("POST", f"/api/workflow/{workflow_name}", {"topic": topic}))
        return RunRef(run_id, workflow_name, version)

    def get_run(self, run: RunRef) -> dict[str, Any]:
        value = self._request("GET", f"/api/workflow/{run.run_id}")
        if not isinstance(value, dict):
            raise RuntimeError("Conductor returned a non-object workflow status")
        return value

    def approve(self, run: RunRef, decision: str, reason: str = "", task_ref: str = "approval") -> None:
        if decision not in {"approved", "rejected"}:
            raise ValueError("decision must be approved or rejected")
        # HUMAN task output is deliberately kept as a project ReviewDecision.
        self._request("POST", f"/api/tasks/{run.run_id}/{task_ref}/COMPLETED/sync", {
            "decision": decision,
            "reason": reason,
        })

    @staticmethod
    def review_decision(run: RunRef, decision: str, reason: str, actor: str) -> dict[str, Any]:
        if decision not in {"approved", "rejected"}:
            raise ValueError("decision must be approved or rejected")
        return {"run_id": run.run_id, "decision": decision, "reason": reason,
                "actor": actor, "at": datetime.now(timezone.utc).isoformat()}

    def rerun_from(self, run: RunRef, task_id: str) -> str:
        """Create a Conductor partial rerun and return its workflow id."""
        value = self._request("POST", f"/api/workflow/{run.run_id}/rerun", {
            "reRunFromWorkflowId": run.run_id,
            "reRunFromTaskId": task_id,
        })
        return str(value)
