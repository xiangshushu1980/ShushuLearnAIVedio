"""Conductor workflow definition for the provider-neutral daily-video slice."""

from __future__ import annotations

from typing import Any


TASKS = ("source", "director", "tts", "approval", "route")


def build(name: str = "daily_video_poc", version: int = 1) -> dict[str, Any]:
    return {
        "name": name,
        "description": "Provider-neutral daily video vertical slice",
        "version": version,
        "schemaVersion": 2,
        "restartable": True,
        "timeoutSeconds": 3600,
        "inputParameters": ["topic", "source"],
        "tasks": [
            {"name": "daily_video_source", "taskReferenceName": "source", "type": "SIMPLE", "workflowTaskType": "SIMPLE",
             "inputParameters": {"topic": "${workflow.input.topic}", "source": "${workflow.input.source}"}},
            {"name": "daily_video_director", "taskReferenceName": "director", "type": "SIMPLE", "workflowTaskType": "SIMPLE",
             "inputParameters": {"evidence": "${source.output.evidence}"}},
            {"name": "daily_video_tts", "taskReferenceName": "tts", "type": "SIMPLE", "workflowTaskType": "SIMPLE",
             "inputParameters": {"script": "${director.output.script}", "timeline": "${director.output.timeline}"}},
            {"name": "daily_video_approval", "taskReferenceName": "approval", "type": "HUMAN", "workflowTaskType": "HUMAN",
             "inputParameters": {"script": "${director.output.script}", "audio": "${tts.output.audio}"}},
            {"name": "daily_video_route", "taskReferenceName": "route", "type": "DECISION", "workflowTaskType": "DECISION",
             "caseValueParam": "decision", "inputParameters": {"decision": "${approval.output.decision}"}, "decisionCases": {"approved": [
                 {"name": "daily_video_render", "taskReferenceName": "render", "type": "SIMPLE", "workflowTaskType": "SIMPLE",
                  "inputParameters": {"script": "${director.output.script}", "timeline": "${director.output.timeline}", "audio": "${tts.output.audio}"}},
                 {"name": "daily_video_qc", "taskReferenceName": "qc", "type": "SIMPLE", "workflowTaskType": "SIMPLE",
                  "inputParameters": {"run": "${render.output.video}"}}
             ]}},
        ],
        "outputParameters": {"qc": "${qc.output.qc}", "video": "${render.output.video}"},
    }


def validate(workflow: dict[str, Any]) -> None:
    refs = [task["taskReferenceName"] for task in workflow["tasks"]]
    if refs != list(TASKS):
        raise ValueError(f"unexpected task topology: {refs}")
    if workflow["tasks"][3]["type"] != "HUMAN":
        raise ValueError("approval must remain a HUMAN task")
    if workflow["tasks"][4].get("caseValueParam") != "decision":
        raise ValueError("approval decision must control the render branch")
    branch = workflow["tasks"][4]["decisionCases"]["approved"]
    if [task["taskReferenceName"] for task in branch] != ["render", "qc"]:
        raise ValueError("approved branch must render then QC")
