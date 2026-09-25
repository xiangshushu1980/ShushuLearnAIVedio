#!/usr/bin/env python3
"""Temporal Python probe: retried activities plus a durable approval signal."""

from __future__ import annotations

import asyncio
import os
import uuid
from datetime import timedelta

from temporalio import activity, workflow
from temporalio.client import Client
from temporalio.common import RetryPolicy
from temporalio.worker import Worker


@activity.defn
async def source(topic: str) -> dict:
    return {"stage": "source", "artifact_ref": "artifact://temporal/source", "topic": topic}


_director_attempts = 0


@activity.defn
async def director(source_ref: dict) -> dict:
    global _director_attempts
    _director_attempts += 1
    if _director_attempts == 1:
        raise RuntimeError("intentional T32 retry probe failure")
    return {"stage": "director", "artifact_ref": "artifact://temporal/script", "input": source_ref}


@activity.defn
async def render(script_ref: dict) -> dict:
    return {"stage": "render", "artifact_ref": "artifact://temporal/render", "input": script_ref}


@workflow.defn
class T32TemporalWorkflow:
    approved: bool = False

    @workflow.signal
    async def approve(self, decision: bool) -> None:
        self.approved = decision

    @workflow.run
    async def run(self, topic: str) -> dict:
        retry = RetryPolicy(initial_interval=timedelta(seconds=1), maximum_attempts=2)
        source_ref = await workflow.execute_activity(source, topic, start_to_close_timeout=timedelta(seconds=30), retry_policy=retry)
        script_ref = await workflow.execute_activity(director, source_ref, start_to_close_timeout=timedelta(seconds=30), retry_policy=retry)
        await workflow.wait_condition(lambda: self.approved)
        return await workflow.execute_activity(render, script_ref, start_to_close_timeout=timedelta(seconds=30), retry_policy=retry)


async def main() -> None:
    endpoint = os.getenv("TEMPORAL_ADDRESS", "127.0.0.1:17233")
    client = await Client.connect(endpoint, namespace="temporal-system")
    workflow_id = f"t32-temporal-probe-{uuid.uuid4().hex[:8]}"
    async with Worker(client, task_queue="t32-tasks", workflows=[T32TemporalWorkflow], activities=[source, director, render]):
        handle = await client.start_workflow(T32TemporalWorkflow.run, "Temporal 小型流程验证", id=workflow_id, task_queue="t32-tasks")
        await asyncio.sleep(2)
        await handle.signal(T32TemporalWorkflow.approve, True)
        result = await handle.result()
        print({"workflow_id": workflow_id, "result": result, "director_attempts": _director_attempts})


if __name__ == "__main__":
    asyncio.run(main())
