#!/usr/bin/env python3
"""[Sean] Retry the prop and scene cases with a cleaner reference and stricter view semantics."""
import json
import os
import re
import subprocess
import sys
from pathlib import Path

os.environ.setdefault("HIVE_LEASE_ID", "pending")
import run_validation as base

ROOT = base.ROOT
RETRY_SEEDS = {"prop_katana_sheathed": [2026100370, 2026100371, 2026100372], "scene_shrine_v2": [2026100380, 2026100381, 2026100382]}
lease_id = None
manifest = json.loads(base.MANIFEST_PATH.read_text())
manifest.setdefault("retries", [])

def persist():
    base.save_manifest(manifest)

try:
    acquired = subprocess.run(
        ["hive-resource", "lease", "acquire", "--owner", "Agent", "--resources", "gpu:0", "--pid", str(os.getpid()), "--ttl", "600000"],
        check=True, capture_output=True, text=True,
    )
    match = re.search(r"租约 ([0-9a-f-]+) 已授予", acquired.stdout)
    if not match:
        raise RuntimeError("Could not parse lease ID: " + acquired.stdout)
    lease_id = match.group(1)
    os.environ["HIVE_LEASE_ID"] = lease_id
    base.LEASE = lease_id

    retry_source = ROOT / "inputs/prop_katana_sheathed_source.png"
    source_graph = json.loads((base.BASE / "api_workflows/source_fullbody.json").read_text())
    source_graph["5"]["inputs"]["prompt"] = (ROOT / "prompts/source_katana_sheathed.txt").read_text().strip()
    source_graph["7"]["inputs"]["seed"] = 2026100369
    source_graph["9"]["inputs"]["filename_prefix"] = f"{base.PREFIX}/retry/prop_katana_sheathed/source"
    result = base.run_graph(source_graph, retry_source, "prop_katana_sheathed_source")
    manifest["results"].append(result)
    persist()

    for case, source, prompt_file in [
        ("prop_katana_sheathed", retry_source, "prop_katana_sheathed.txt"),
        ("scene_shrine_v2", ROOT / "inputs/scene_shrine_source.png", "scene_shrine_v2.txt"),
    ]:
        remote = f"{base.PREFIX}_{case}_reference.png"
        base.upload(source, remote)
        for offset, seed in enumerate(RETRY_SEEDS[case], start=1):
            graph = json.loads((base.BASE / "source_workflow_v3/v3_simple_static_adapted_api.json").read_text())
            graph["5"]["inputs"]["prompt"] = (ROOT / "prompts" / prompt_file).read_text().strip()
            graph["7"]["inputs"]["seed"] = seed
            graph["9"]["inputs"]["filename_prefix"] = f"{base.PREFIX}/retry/{case}/sheet_{offset}"
            graph["10"]["inputs"]["image"] = remote
            out = ROOT / "outputs/retry" / case / f"seed_{seed}.png"
            result = base.run_graph(graph, out, f"{case}_sheet_{offset}")
            result["seed"] = seed
            manifest["retries"].append(result)
            persist()
        uploaded = base.COMFY_INPUT / remote
        if uploaded.is_file():
            uploaded.unlink()

    shield_source = ROOT / "inputs/prop_shield_source.png"
    shield_graph = json.loads((base.BASE / "api_workflows/source_fullbody.json").read_text())
    shield_graph["5"]["inputs"]["prompt"] = (ROOT / "prompts/source_shield.txt").read_text().strip()
    shield_graph["7"]["inputs"]["seed"] = 2026100390
    shield_graph["9"]["inputs"]["filename_prefix"] = f"{base.PREFIX}/prop_shield/source"
    result = base.run_graph(shield_graph, shield_source, "prop_shield_source")
    manifest["results"].append(result)
    persist()
    remote = f"{base.PREFIX}_prop_shield_reference.png"
    base.upload(shield_source, remote)
    for offset, seed in enumerate([2026100391, 2026100392, 2026100393], start=1):
        graph = json.loads((base.BASE / "source_workflow_v3/v3_simple_static_adapted_api.json").read_text())
        graph["5"]["inputs"]["prompt"] = (ROOT / "prompts/prop_shield.txt").read_text().strip()
        graph["7"]["inputs"]["seed"] = seed
        graph["9"]["inputs"]["filename_prefix"] = f"{base.PREFIX}/prop_shield/sheet_{offset}"
        graph["10"]["inputs"]["image"] = remote
        out = ROOT / "outputs/prop_shield" / f"seed_{seed}.png"
        result = base.run_graph(graph, out, f"prop_shield_sheet_{offset}")
        result["seed"] = seed
        manifest["retries"].append(result)
        persist()
    uploaded = base.COMFY_INPUT / remote
    if uploaded.is_file():
        uploaded.unlink()
    manifest["retry_status"] = "generated_qc_pending"
except Exception as exc:
    manifest["retry_status"] = "partial_error"
    manifest["retry_error"] = repr(exc)
    raise
finally:
    for remote in base.UPLOADED:
        remote_path = base.COMFY_INPUT / remote
        if remote_path.is_file():
            remote_path.unlink()
    persist()
    if lease_id:
        subprocess.run(
            ["hive-resource", "observe", "--resource", "gpu:0", "--job", ROOT.name + "-retries", "--metrics", json.dumps({"runs": len(manifest["retries"]), "status": manifest.get("retry_status", "error"), "peakVramMeasured": False})],
            check=False, capture_output=True, text=True,
        )
        released = subprocess.run(["hive-resource", "lease", "release", lease_id], check=False, capture_output=True, text=True)
        if released.returncode:
            print(f"lease release warning: {released.stderr or released.stdout}", file=sys.stderr)

print(json.dumps({"status": manifest.get("retry_status"), "retry_runs": len(manifest["retries"])}, ensure_ascii=False))
