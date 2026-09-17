#!/usr/bin/env python3
"""WOW 概念风格探针：固定案例，逐个注入一个 KREA2 风格 LoRA。

默认只做 dry-run；实际提交前先用 --case SP03_FIRE_SHAPING --candidate ... 做单例 smoke test。
"""
from __future__ import annotations

import argparse
import copy
import json
import os
import time
import urllib.request
from pathlib import Path

import yaml

SERVER = "http://127.0.0.1:8188"
ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "projects/wow-mage-survival/fixtures/style_probe_v1.yaml"


def load_fixture():
    return yaml.safe_load(FIXTURE.read_text())


def build_workflow(
    base_path: Path,
    case: dict,
    candidate: dict,
    strength: float,
    fixed_world_block: str,
) -> dict:
    wf = json.loads(base_path.read_text())
    prompt = case["prompt"].replace("{fixed_world_block}", fixed_world_block)
    trigger = " ".join(candidate.get("trigger_words", []))
    if trigger:
        prompt = f"{trigger}, {prompt}"

    # KREA2 test workflow is deliberately tiny. Add exactly one model-only LoRA.
    wf["9"] = {
        "class_type": "LoraLoaderModelOnly",
        "inputs": {
            "model": ["1", 0],
            "lora_name": candidate["file"],
            "strength_model": strength,
        },
    }
    wf["6"]["inputs"]["model"] = ["9", 0]
    for node in wf.values():
        if node["class_type"] == "CLIPTextEncode":
            node["inputs"]["text"] = prompt
        elif node["class_type"] == "SaveImage":
            node["inputs"]["filename_prefix"] = (
                f"wow_style_probe/{case['id']}/{candidate['id']}_s{strength:g}"
            )
    return wf


def submit(workflow: dict) -> str:
    body = json.dumps({"prompt": workflow, "client_id": "wow-style-probe"}).encode()
    req = urllib.request.Request(
        f"{SERVER}/prompt", data=body, headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=30) as response:
        return json.load(response)["prompt_id"]


def wait_queue(timeout: int = 300):
    deadline = time.time() + timeout
    while time.time() < deadline:
        with urllib.request.urlopen(f"{SERVER}/queue", timeout=10) as response:
            queue = json.load(response)
        if not queue.get("queue_running") and not queue.get("queue_pending"):
            return
        time.sleep(3)
    raise TimeoutError(f"queue did not drain within {timeout}s")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--case", default="SP03_FIRE_SHAPING")
    parser.add_argument("--candidate", help="candidate id; default: all downloaded candidates")
    parser.add_argument("--strength", type=float, default=0.8)
    parser.add_argument("--submit", action="store_true")
    args = parser.parse_args()

    fixture = load_fixture()
    cases = {item["id"]: item for item in fixture["cases"]}
    candidates = {
        item["id"]: item
        for item in fixture["candidates"]
        if item.get("local_status") == "downloaded_verified"
    }
    if args.case not in cases:
        parser.error(f"unknown case: {args.case}; choose from {', '.join(cases)}")
    selected = [candidates[args.candidate]] if args.candidate else list(candidates.values())
    if args.candidate and args.candidate not in candidates:
        parser.error(f"candidate is not downloaded_verified: {args.candidate}")

    base_path = ROOT / fixture["base"]["workflow"]
    for candidate in selected:
        wf = build_workflow(
            base_path,
            cases[args.case],
            candidate,
            args.strength,
            fixture["fixed_world_block"],
        )
        if not args.submit:
            print(
                f"[dry-run] {args.case} × {candidate['id']} "
                f"strength={args.strength:g} prompt_len="
                f"{len(next(n for n in wf.values() if n['class_type'] == 'CLIPTextEncode')['inputs']['text'])}"
            )
            continue
        prompt_id = submit(wf)
        print(f"[submitted] {candidate['id']} pid={prompt_id}", flush=True)
        wait_queue()
    print("ALL DONE")


if __name__ == "__main__":
    main()
