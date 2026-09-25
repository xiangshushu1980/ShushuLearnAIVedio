from __future__ import annotations

import json
import tempfile
import threading
import time
import unittest
import urllib.error
import urllib.request
from pathlib import Path
from http.server import ThreadingHTTPServer

from .adapter import HiveAgentAdapter
from .coordinator import CoordinatorStore
from .server import Handler


class CoordinatorHTTPTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.db = Path(self.tmp.name) / "coordinator.sqlite3"
        self._start_server()

    def tearDown(self) -> None:
        self._stop_server()
        self.tmp.cleanup()

    def _start_server(self) -> None:
        port = getattr(self, "port", 0)
        self.httpd = ThreadingHTTPServer(("127.0.0.1", port), Handler)
        self.httpd.store = CoordinatorStore(self.db, lease_seconds=2, token="secret")
        self.thread = threading.Thread(target=self.httpd.serve_forever, daemon=True)
        self.thread.start()
        self.port = self.httpd.server_port
        self.base = f"http://127.0.0.1:{self.httpd.server_port}"

    def _stop_server(self) -> None:
        self.httpd.shutdown()
        self.thread.join(timeout=2)
        self.httpd.store.close()
        self.httpd.server_close()

    def _request(self, method: str, path: str, body: dict, token: str = "secret", key: str | None = None) -> dict:
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        if key:
            headers["Idempotency-Key"] = key
        request = urllib.request.Request(self.base + path, json.dumps(body).encode(), headers, method=method)
        with urllib.request.urlopen(request, timeout=2) as response:
            return json.loads(response.read())

    def _create(self, task_id: str) -> dict:
        return self._request("POST", "/v1/tasks", {"task_id": task_id, "payload": {"source": "test"}}, key=f"create-{task_id}")

    def test_adapter_lifecycle_and_idempotent_retry(self) -> None:
        self._create("http-1")
        worker = HiveAgentAdapter(self.base, "worker-a", "secret")
        lease = worker.claim("http-1", "claim-http-1")
        self.assertEqual(worker.claim("http-1", "claim-http-1"), lease)
        self.assertEqual(worker.checkpoint(lease, {"step": 1}, "checkpoint-http-1")["checkpoint"], {"step": 1})
        self.assertEqual(worker.heartbeat(lease, "heartbeat-http-1")["status"], "running")
        self.assertEqual(worker.finish(lease, {"artifact": "a1"}, "finish-http-1")["status"], "finished")
        self.assertEqual(self._request("GET", "/v1/tasks/http-1", {})["result"], {"artifact": "a1"})

    def test_restart_preserves_active_lease_and_state(self) -> None:
        self._create("restart-1")
        worker = HiveAgentAdapter(self.base, "worker-a", "secret")
        lease = worker.claim("restart-1")
        self._stop_server()
        self._start_server()
        self.assertEqual(worker.finish(lease, {"after_restart": True})["status"], "finished")
        task = self._request("GET", "/v1/tasks/restart-1", {})
        self.assertEqual(task["generation"], 1)
        self.assertEqual(task["result"], {"after_restart": True})

    def test_disconnect_expiry_reclaims_and_fences_old_adapter(self) -> None:
        self._create("expiry-1")
        old_worker = HiveAgentAdapter(self.base, "worker-old", "secret")
        new_worker = HiveAgentAdapter(self.base, "worker-new", "secret")
        self.httpd.store.lease_seconds = 0.2
        old_lease = old_worker.claim("expiry-1")
        time.sleep(max(0, old_lease.lease_until - time.time() + 0.05))
        new_lease = new_worker.claim("expiry-1")
        self.assertEqual(new_lease.generation, old_lease.generation + 1)
        with self.assertRaisesRegex(RuntimeError, "409"):
            old_worker.finish(old_lease, {"stale": True})
        self.assertEqual(new_worker.finish(new_lease, {"stale": False})["status"], "finished")

    def test_release_reclaims_and_fences_old_adapter(self) -> None:
        self._create("release-1")
        old_worker = HiveAgentAdapter(self.base, "worker-old", "secret")
        new_worker = HiveAgentAdapter(self.base, "worker-new", "secret")
        old_lease = old_worker.claim("release-1")
        self.assertEqual(old_worker.release(old_lease)["status"], "queued")
        new_lease = new_worker.claim("release-1")
        self.assertEqual(new_lease.generation, old_lease.generation + 1)
        with self.assertRaisesRegex(RuntimeError, "409"):
            old_worker.finish(old_lease, {"stale": True})
        self.assertEqual(new_worker.finish(new_lease, {"stale": False})["status"], "finished")

    def test_http_idempotency_conflict_is_rejected(self) -> None:
        self._request("POST", "/v1/tasks", {"task_id": "idem-a", "payload": {}}, key="same-key")
        with self.assertRaisesRegex(urllib.error.HTTPError, "HTTP Error 409"):
            self._request("POST", "/v1/tasks", {"task_id": "idem-b", "payload": {}}, key="same-key")

    def test_concurrent_claim_has_one_winner(self) -> None:
        self._create("race-1")
        results: list[object] = []
        barrier = threading.Barrier(2)

        def claim(worker_id: str) -> None:
            try:
                barrier.wait()
                results.append(HiveAgentAdapter(self.base, worker_id, "secret").claim("race-1"))
            except Exception as exc:  # the losing claim is expected to be an HTTP 409
                results.append(exc)

        threads = [threading.Thread(target=claim, args=(f"worker-{i}",)) for i in range(2)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join(timeout=2)
        self.assertEqual(len(results), 2)
        self.assertEqual(sum(isinstance(item, RuntimeError) for item in results), 1)
        self.assertEqual(sum(hasattr(item, "fencing_token") for item in results), 1)

    def test_auth_and_append_only_progress_bridge(self) -> None:
        self._create("auth-1")
        with self.assertRaisesRegex(urllib.error.HTTPError, "HTTP Error 401"):
            self._request("GET", "/v1/tasks/auth-1", {}, token="wrong")
        progress = Path(self.tmp.name) / "progress.md"
        progress.write_text("existing local truth\n", encoding="utf-8")
        HiveAgentAdapter.append_progress(progress, "auth-1", {"step": 3})
        content = progress.read_text(encoding="utf-8")
        self.assertIn("existing local truth", content)
        self.assertIn('"step": 3', content)


if __name__ == "__main__":
    unittest.main()
