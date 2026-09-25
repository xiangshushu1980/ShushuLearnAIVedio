import tempfile
import time
import unittest

from .coordinator import CoordinatorError, CoordinatorStore


class CoordinatorTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile(suffix=".sqlite3")
        self.store = CoordinatorStore(self.tmp.name, lease_seconds=1, token="secret")
        self.store.create_task("t1", {"kind": "demo"})

    def tearDown(self):
        self.store.close(); self.tmp.close()

    def test_lifecycle_and_idempotency(self):
        lease = self.store.claim("worker-a", "t1", "claim-1")
        self.assertEqual(lease["generation"], 1)
        self.assertEqual(self.store.claim("worker-a", "t1", "claim-1"), lease)
        renewed = self.store.mutate("heartbeat", "t1", "worker-a", 1, lease["fencing_token"], {}, "hb-1")
        self.assertEqual(renewed, self.store.mutate("heartbeat", "t1", "worker-a", 1, lease["fencing_token"], {}, "hb-1"))
        self.store.mutate("checkpoint", "t1", "worker-a", 1, lease["fencing_token"], {"checkpoint": {"step": 2}}, "cp-1")
        finished = self.store.mutate("finish", "t1", "worker-a", 1, lease["fencing_token"], {"result": {"ok": True}}, "finish-1")
        self.assertEqual(finished["status"], "finished")
        self.assertEqual(self.store.get_task("t1")["checkpoint"], {"step": 2})

    def test_expiry_fences_old_worker_and_reclaims(self):
        old = self.store.claim("worker-a", "t1")
        time.sleep(1.05)
        new = self.store.claim("worker-b", "t1")
        self.assertEqual(new["generation"], 2)
        with self.assertRaisesRegex(CoordinatorError, "stale"):
            self.store.mutate("finish", "t1", "worker-a", old["generation"], old["fencing_token"], {})

    def test_auth_and_idempotency_conflict(self):
        with self.assertRaisesRegex(CoordinatorError, "invalid bearer"):
            self.store.authenticate("wrong")
        self.store.claim("worker-a", "t1", "same")
        with self.assertRaisesRegex(CoordinatorError, "another request"):
            self.store.claim("worker-b", "t1", "same")


if __name__ == "__main__":
    unittest.main()
