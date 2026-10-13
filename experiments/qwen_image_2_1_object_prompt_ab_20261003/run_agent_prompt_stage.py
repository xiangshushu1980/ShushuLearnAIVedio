#!/usr/bin/env python3
"""[Sean] Generate per-object prompts with the local Qwen3-VL 8B model."""
from __future__ import annotations

import json
import hashlib
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import run_prompt_ab as runner  # noqa: E402


def main() -> None:
    manifest_path = ROOT / "manifest.json"
    manifest = json.loads(manifest_path.read_text())
    lease_id = None
    try:
        runner.queue_empty()
        lease_id = runner.acquire_lease()
        runner.LEASE_ID = lease_id
        runner.sample_vram()
        for case in runner.CASES:
            case_id = case["id"]
            final = ROOT / "prompts" / f"agent_qwen3vl_{case_id}.txt"
            if final.is_file() and final.read_text().strip():
                continue
            local = ROOT / "inputs" / case["reference"]
            remote = f"{runner.PREFIX}_{case_id}_agent_reference.png"
            runner.upload(local, remote)
            result = runner.run_graph(runner.agent_graph(remote, case_id), "text", f"agent_qwen3vl_{case_id}")
            generated = (ROOT / result["output"]).read_text().strip()
            if "</think>" in generated:
                generated = generated.partition("</think>")[2].strip()
            elif "<think>" in generated:
                generated = generated.partition("<think>")[2].strip()
            final.write_text(generated + "\n")
            manifest.setdefault("results", []).append({
                "stage": "agent_prompt", "case": case_id,
                "model": "qwen3vl_8b_int8_convrot.safetensors",
                "instruction": f"prompts/{case['agent_instruction']}",
                "prompt": f"prompts/{final.name}", **result,
            })
            manifest.setdefault("references", {})[case_id] = {
                "file": f"inputs/{case['reference']}",
                "sha256": hashlib.sha256(local.read_bytes()).hexdigest(),
            }
            manifest["status"] = "agent_prompts_running"
            manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
            source = runner.COMFY_INPUT / remote
            if source.is_file():
                source.unlink()
        manifest["status"] = "agent_prompts_ready_pe_pending"
    except Exception as exc:
        manifest["status"] = "agent_prompt_partial_error"
        manifest["agent_prompt_error"] = repr(exc)
        raise
    finally:
        for remote in runner.UPLOADED:
            source = runner.COMFY_INPUT / remote
            if source.is_file():
                source.unlink()
        runner.sample_vram()
        if lease_id:
            subprocess.run(
                ["hive-resource", "observe", "--resource", "gpu:0", "--job", ROOT.name + "-agent-prompts", "--metrics", json.dumps({"peakVramMb": runner.PEAK_VRAM_MB, "promptCount": sum(1 for c in runner.CASES if (ROOT / "prompts" / f"agent_qwen3vl_{c['id']}.txt").is_file()), "status": manifest["status"]})],
                check=False, capture_output=True, text=True,
            )
            subprocess.run(["hive-resource", "lease", "release", lease_id], check=False, capture_output=True, text=True)
        manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"status": manifest["status"], "prompts": sum(1 for c in runner.CASES if (ROOT / "prompts" / f"agent_qwen3vl_{c['id']}.txt").is_file()), "peakVramMb": runner.PEAK_VRAM_MB}, ensure_ascii=False))


if __name__ == "__main__":
    main()
