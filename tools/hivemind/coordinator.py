from __future__ import annotations

import hashlib
import json
import secrets
import sqlite3
import threading
import time
from pathlib import Path
from typing import Any


class CoordinatorError(Exception):
    def __init__(self, code: str, message: str, status: int = 409):
        super().__init__(message)
        self.code, self.message, self.status = code, message, status


def _now() -> float:
    return time.time()


class CoordinatorStore:
    """Durable task/lease state machine used by the HTTP coordinator."""

    def __init__(self, db_path: str | Path = ":memory:", lease_seconds: int = 30,
                 token: str | None = None):
        self.db_path, self.lease_seconds, self.token = str(db_path), lease_seconds, token
        self._lock = threading.RLock()
        self.db = sqlite3.connect(self.db_path, check_same_thread=False)
        self.db.row_factory = sqlite3.Row
        self.db.execute("PRAGMA journal_mode=WAL")
        self.db.executescript("""
        CREATE TABLE IF NOT EXISTS tasks (
          task_id TEXT PRIMARY KEY, payload TEXT NOT NULL, status TEXT NOT NULL,
          generation INTEGER NOT NULL DEFAULT 0, worker_id TEXT, fencing_token TEXT,
          lease_until REAL, checkpoint TEXT, result TEXT, updated_at REAL NOT NULL
        );
        CREATE TABLE IF NOT EXISTS idempotency (
          idem_key TEXT PRIMARY KEY, request_hash TEXT NOT NULL, response TEXT NOT NULL,
          status INTEGER NOT NULL, created_at REAL NOT NULL
        );
        CREATE TABLE IF NOT EXISTS events (
          id INTEGER PRIMARY KEY AUTOINCREMENT, task_id TEXT NOT NULL, event TEXT NOT NULL,
          generation INTEGER, worker_id TEXT, detail TEXT, at REAL NOT NULL
        );
        """)
        self.db.commit()

    def close(self) -> None:
        self.db.close()

    def authenticate(self, supplied: str | None) -> None:
        if self.token is not None and not secrets.compare_digest(self.token, supplied or ""):
            raise CoordinatorError("unauthorized", "invalid bearer token", 401)

    def _event(self, task_id: str, event: str, generation: int | None = None,
               worker_id: str | None = None, detail: Any = None) -> None:
        self.db.execute("INSERT INTO events(task_id,event,generation,worker_id,detail,at) VALUES(?,?,?,?,?,?)",
                        (task_id, event, generation, worker_id,
                         json.dumps(detail, ensure_ascii=False) if detail is not None else None, _now()))

    def _task(self, task_id: str) -> sqlite3.Row:
        row = self.db.execute("SELECT * FROM tasks WHERE task_id=?", (task_id,)).fetchone()
        if row is None:
            raise CoordinatorError("not_found", f"unknown task {task_id}", 404)
        return row

    def _idem(self, key: str | None, body: Any) -> dict[str, Any] | None:
        if not key:
            return None
        digest = hashlib.sha256(json.dumps(body, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
        row = self.db.execute("SELECT * FROM idempotency WHERE idem_key=?", (key,)).fetchone()
        if row:
            if row["request_hash"] != digest:
                raise CoordinatorError("idempotency_conflict", "key was already used with another request", 409)
            return json.loads(row["response"])
        return {"_new": digest, "_key": key}

    def _save_idem(self, marker: dict[str, Any] | None, response: dict[str, Any], status: int = 200) -> None:
        if marker and "_new" in marker:
            self.db.execute("INSERT INTO idempotency VALUES(?,?,?,?,?)",
                            (marker["_key"], marker["_new"], json.dumps(response), status, _now()))

    def create_task(self, task_id: str, payload: dict[str, Any] | None = None,
                    idem_key: str | None = None) -> dict[str, Any]:
        with self._lock:
            request = {"task_id": task_id, "payload": payload or {}}
            marker = self._idem(idem_key, request)
            if marker and "_new" not in marker:
                return marker
            try:
                self.db.execute("INSERT INTO tasks(task_id,payload,status,updated_at) VALUES(?,?,?,?)",
                                (task_id, json.dumps(payload or {}, ensure_ascii=False), "queued", _now()))
            except sqlite3.IntegrityError:
                raise CoordinatorError("already_exists", f"task {task_id} already exists", 409)
            self._event(task_id, "created", detail=payload or {})
            self.db.commit()
            response = self.get_task(task_id)
            self._save_idem(marker, response); self.db.commit()
            return response

    def get_task(self, task_id: str) -> dict[str, Any]:
        with self._lock:
            row = self._task(task_id)
            data = dict(row)
            for key in ("payload", "checkpoint", "result"):
                data[key] = json.loads(data[key]) if data[key] else None
            return data

    def claim(self, worker_id: str, task_id: str | None = None, idem_key: str | None = None) -> dict[str, Any]:
        body = {"worker_id": worker_id, "task_id": task_id}
        with self._lock:
            marker = self._idem(idem_key, body)
            if marker and "_new" not in marker:
                return marker
            now = _now()
            where, args = ("task_id=?", (task_id,)) if task_id else ("1=1", ())
            row = self.db.execute(f"SELECT * FROM tasks WHERE {where} AND (status='queued' OR (status='running' AND lease_until<?)) ORDER BY updated_at LIMIT 1",
                                  args + (now,)).fetchone()
            if row is None:
                raise CoordinatorError("no_task", "no claimable task", 409)
            generation = int(row["generation"]) + 1
            lease = secrets.token_urlsafe(32)
            self.db.execute("UPDATE tasks SET status='running',generation=?,worker_id=?,fencing_token=?,lease_until=?,updated_at=? WHERE task_id=?",
                            (generation, worker_id, lease, now + self.lease_seconds, now, row["task_id"]))
            self._event(row["task_id"], "claimed", generation, worker_id,
                        {"lease_until": now + self.lease_seconds})
            response = {"task_id": row["task_id"], "payload": json.loads(row["payload"]),
                        "generation": generation, "fencing_token": lease,
                        "lease_until": now + self.lease_seconds}
            self._save_idem(marker, response); self.db.commit(); return response

    def _lease(self, task_id: str, worker_id: str, generation: int, fencing_token: str) -> sqlite3.Row:
        row = self._task(task_id)
        if row["worker_id"] != worker_id or row["generation"] != generation or row["fencing_token"] != fencing_token:
            raise CoordinatorError("fenced", "stale or invalid generation/fencing token", 409)
        if row["status"] != "running" or (row["lease_until"] or 0) < _now():
            raise CoordinatorError("lease_expired", "worker lease has expired", 409)
        return row

    def mutate(self, action: str, task_id: str, worker_id: str, generation: int,
               fencing_token: str, body: dict[str, Any] | None = None,
               idem_key: str | None = None) -> dict[str, Any]:
        body = body or {}
        request = {"action": action, "task_id": task_id, "worker_id": worker_id,
                   "generation": generation, "fencing_token": fencing_token, "body": body}
        with self._lock:
            marker = self._idem(idem_key, request)
            if marker and "_new" not in marker:
                return marker
            row = self._lease(task_id, worker_id, generation, fencing_token)
            now = _now()
            if action in {"renew", "heartbeat"}:
                until = now + self.lease_seconds
                self.db.execute("UPDATE tasks SET lease_until=?,updated_at=? WHERE task_id=?", (until, now, task_id))
                response = {"task_id": task_id, "status": "running", "generation": generation, "lease_until": until}
            elif action == "checkpoint":
                checkpoint = body.get("checkpoint", body)
                self.db.execute("UPDATE tasks SET checkpoint=?,updated_at=? WHERE task_id=?",
                                (json.dumps(checkpoint, ensure_ascii=False), now, task_id))
                response = {"task_id": task_id, "status": "running", "generation": generation, "checkpoint": checkpoint}
            elif action == "finish":
                result = body.get("result", body)
                self.db.execute("UPDATE tasks SET status='finished',result=?,lease_until=NULL,updated_at=? WHERE task_id=?",
                                (json.dumps(result, ensure_ascii=False), now, task_id))
                response = {"task_id": task_id, "status": "finished", "generation": generation, "result": result}
            elif action == "release":
                self.db.execute("UPDATE tasks SET status='queued',worker_id=NULL,fencing_token=NULL,lease_until=NULL,updated_at=? WHERE task_id=?",
                                (now, task_id))
                response = {"task_id": task_id, "status": "queued", "generation": generation}
            else:
                raise CoordinatorError("bad_action", action, 400)
            self._event(task_id, action, generation, worker_id, body)
            self._save_idem(marker, response); self.db.commit(); return response

    def events(self, task_id: str) -> list[dict[str, Any]]:
        with self._lock:
            self._task(task_id)
            rows = self.db.execute("SELECT * FROM events WHERE task_id=? ORDER BY id", (task_id,)).fetchall()
            return [{**dict(r), "detail": json.loads(r["detail"]) if r["detail"] else None} for r in rows]
