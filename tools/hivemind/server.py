from __future__ import annotations

import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

from .coordinator import CoordinatorError, CoordinatorStore


class Handler(BaseHTTPRequestHandler):
    server_version = "hivemind-coordinator/0.1"

    @property
    def store(self) -> CoordinatorStore:
        return self.server.store  # type: ignore[attr-defined]

    def _json(self, status: int, data: object) -> None:
        raw = json.dumps(data, ensure_ascii=False).encode()
        self.send_response(status); self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(raw))); self.end_headers(); self.wfile.write(raw)

    def _body(self) -> dict:
        length = int(self.headers.get("Content-Length", "0"))
        return json.loads(self.rfile.read(length) or b"{}")

    def _auth(self) -> None:
        value = self.headers.get("Authorization", "")
        self.store.authenticate(value[7:] if value.startswith("Bearer ") else None)

    def _run(self, fn) -> None:
        try:
            self._auth(); self._json(200, fn())
        except CoordinatorError as exc:
            self._json(exc.status, {"error": exc.code, "message": exc.message})
        except (ValueError, KeyError, json.JSONDecodeError) as exc:
            self._json(400, {"error": "bad_request", "message": str(exc)})

    def do_GET(self) -> None:
        path = urlparse(self.path).path
        if path == "/health": return self._json(200, {"ok": True})
        if path.startswith("/v1/tasks/"):
            parts = path.split("/")
            task_id = parts[3] if len(parts) > 3 else ""
            if len(parts) == 5 and parts[4] == "events": return self._run(lambda: self.store.events(task_id))
            return self._run(lambda: self.store.get_task(task_id))
        self._json(404, {"error": "not_found"})

    def do_POST(self) -> None:
        path = urlparse(self.path).path
        try:
            self._auth()
            body = self._body()
        except CoordinatorError as exc:
            return self._json(exc.status, {"error": exc.code, "message": exc.message})
        except (ValueError, json.JSONDecodeError) as exc:
            return self._json(400, {"error": "bad_request", "message": str(exc)})
        idem = self.headers.get("Idempotency-Key")
        if path == "/v1/tasks":
            return self._run(lambda: self.store.create_task(str(body["task_id"]), body.get("payload"), idem))
        if path == "/v1/claims":
            return self._run(lambda: self.store.claim(str(body["worker_id"]), body.get("task_id"), idem))
        parts = path.split("/")
        if len(parts) == 5 and parts[1:3] == ["v1", "tasks"]:
            task_id, action = parts[3], parts[4]
            def mutate():
                return self.store.mutate(action, task_id, str(body["worker_id"]), int(body["generation"]),
                                         str(body["fencing_token"]), body, idem)
            return self._run(mutate)
        self._json(404, {"error": "not_found"})


def serve(host: str = "127.0.0.1", port: int = 8791, db: str = "hivemind.sqlite3",
          token: str | None = None) -> None:
    httpd = ThreadingHTTPServer((host, port), Handler)
    httpd.store = CoordinatorStore(db, token=token)  # type: ignore[attr-defined]
    print(f"hivemind coordinator listening on http://{host}:{port}", flush=True)
    try: httpd.serve_forever()
    except KeyboardInterrupt: pass
    finally: httpd.store.close(); httpd.server_close()


def main() -> None:
    p = argparse.ArgumentParser(); p.add_argument("--host", default="127.0.0.1"); p.add_argument("--port", type=int, default=8791)
    p.add_argument("--db", default="hivemind.sqlite3"); p.add_argument("--token")
    a = p.parse_args(); serve(a.host, a.port, a.db, a.token)


if __name__ == "__main__": main()
