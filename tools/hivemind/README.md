# Hivemind remote coordinator POC

This is a deliberately small control-plane experiment for separating a remote
Coordinator from local Workers. It is not a web dashboard, remote shell, PTY,
ComfyUI controller, or migration of the existing Hive CLI.

Run locally:

```bash
PYTHONPATH=tools python3 -m hivemind --db /tmp/hivemind.sqlite3 --token dev-secret
```

The API is JSON over HTTP:

```text
POST /v1/tasks                         {task_id, payload}
POST /v1/claims                        {worker_id, task_id?}
POST /v1/tasks/{id}/renew              {worker_id, generation, fencing_token}
POST /v1/tasks/{id}/heartbeat          same lease fields
POST /v1/tasks/{id}/checkpoint         same + checkpoint
POST /v1/tasks/{id}/finish             same + result
POST /v1/tasks/{id}/release            same lease fields
GET  /v1/tasks/{id}
GET  /v1/tasks/{id}/events
```

All mutating requests accept `Idempotency-Key`. Reusing a key with a different
request returns `idempotency_conflict`; retrying the same request returns the
original response. Every claim increments `generation` and issues a fresh
opaque `fencing_token`. The old pair cannot renew, checkpoint, finish, or
release after lease expiry or explicit release.

Disconnect semantics are intentionally conservative: a disconnected worker
does not cancel a task. The lease remains valid until its deadline, then a new
worker may claim it. The old worker is fenced even if it later reconnects.

`HiveAgentAdapter` is only the local client boundary. It does not edit
`~/.pi/agent/todo/TODO.md`, recreate `.pi/tasks/<T-ID>/progress.md`, or delete
`[STATE]`. `append_progress()` is an explicit append-only helper for a caller
that wants to record a remote checkpoint in its existing progress file.

Run tests:

```bash
PYTHONPATH=tools python3 -m unittest tools.hivemind.test_coordinator
PYTHONPATH=tools python3 -m unittest tools.hivemind.test_http_adapter
```
