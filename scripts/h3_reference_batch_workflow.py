#!/usr/bin/env python3
"""[Sean] Plan and validate isolated single-object H3 reference jobs.

This tool deliberately does not submit generation jobs. It validates the batch
contract and prints the review gates. A later executor may consume the same
manifest only after the corresponding gate is explicitly approved.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ALLOWED_TYPES = {"character", "scene", "prop", "spell"}
GATES = ("main_review", "h3_review", "package_review")


def load(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    jobs = data.get("jobs")
    if not isinstance(jobs, list) or not jobs:
        raise ValueError("jobs must be a non-empty list")
    ids = set()
    errors = []
    for job in jobs:
        object_id = job.get("object_id")
        if not object_id or object_id in ids:
            errors.append(f"duplicate or missing object_id: {object_id}")
        ids.add(object_id)
        if job.get("object_type") not in ALLOWED_TYPES:
            errors.append(f"{object_id}: invalid object_type")
        if not job.get("main_image"):
            errors.append(f"{object_id}: main_image is required")
        if job.get("allow_other_objects") is not False:
            errors.append(f"{object_id}: allow_other_objects must be false")
        if not job.get("frame_roles"):
            errors.append(f"{object_id}: frame_roles is required")
        if not job.get("prompt_file"):
            errors.append(f"{object_id}: prompt_file is required")
    if len(ids) != len(jobs):
        errors.append("object_id values must be unique")
    if errors:
        raise ValueError("; ".join(errors))
    return data


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--stage", choices=("plan",) + GATES, default="plan")
    args = parser.parse_args()
    try:
        data = load(args.manifest)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({"status": "error", "error": str(exc)}, ensure_ascii=False, indent=2))
        return 1

    root = data.get("output_root")
    jobs = []
    for job in data["jobs"]:
        jobs.append({
            "object_id": job["object_id"],
            "object_type": job["object_type"],
            "main_image": job["main_image"],
            "main_exists": Path(job["main_image"]).is_file(),
            "prompt_file": job["prompt_file"],
            "output_dir": f"{root}/{job['output_dir']}",
            "frame_roles": job["frame_roles"],
            "isolated": job["allow_other_objects"] is False,
        })
    print(json.dumps({
        "status": "valid",
        "stage": args.stage,
        "generation_submitted": False,
        "batch_id": data.get("batch_id"),
        "review_gates": list(GATES),
        "jobs": jobs,
        "invariants": [
            "one main image per job",
            "one object per H3 turnaround job",
            "no cross-object reference input",
            "H3 video review precedes extraction",
            "package review precedes canonical promotion",
        ],
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
