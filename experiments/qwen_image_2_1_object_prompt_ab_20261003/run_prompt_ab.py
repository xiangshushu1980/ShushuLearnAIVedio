#!/usr/bin/env python3
"""[Sean] Compare Qwen PE-I2I and Qwen3-VL Agent prompts on Qwen Image 2.1 V3."""
from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PROJECT = ROOT.parents[1]
BASE = PROJECT / "experiments/qwen_image_2_1_charactersheet_v3_domain_validation_20261003"
V3 = PROJECT / "experiments/qwen_image_2_1_civitai_character_sheet_20261002/source_workflow_v3/v3_simple_static_adapted_api.json"
COMFY_INPUT = Path("/home/sean/projects/ComfyUI/input")
COMFY_OUTPUT = Path("/home/sean/projects/ComfyUI/output")
API = "http://127.0.0.1:8188"
PREFIX = "sean_qwen_image_2_1_object_prompt_ab_20261003"
PE_NAME = "qwen3.5_9b_qwen_image_2.1_pe_i2i.int8_convrot.safetensors"
LEASE_ID: str | None = None
UPLOADED: list[str] = []
PEAK_VRAM_MB = 0

CASES = [
    {"id": "shield", "reference": "shield_reference.png", "manual": "manual_shield.txt", "agent_instruction": "agent_instruction_shield.txt", "seed_base": 2026100391},
    {"id": "lantern", "reference": "lantern_reference.png", "manual": "manual_lantern.txt", "agent_instruction": "agent_instruction_lantern.txt", "seed_base": 2026100340},
    {"id": "katana", "reference": "katana_sheathed_reference.png", "manual": "manual_katana.txt", "agent_instruction": "agent_instruction_katana.txt", "seed_base": 2026100370},
]
CASE_BY_ID = {case["id"]: case for case in CASES}


def request(path: str, payload=None, data=None, headers=None) -> bytes:
    if payload is not None:
        data = json.dumps(payload).encode()
        headers = {**(headers or {}), "Content-Type": "application/json"}
    req = urllib.request.Request(API + path, data=data, headers=headers or {})
    with urllib.request.urlopen(req, timeout=120) as response:
        return response.read()


def sample_vram() -> None:
    global PEAK_VRAM_MB
    try:
        raw = subprocess.check_output(
            ["nvidia-smi", "--query-gpu=memory.used", "--format=csv,noheader,nounits"],
            text=True, timeout=5,
        ).strip().splitlines()[0]
        PEAK_VRAM_MB = max(PEAK_VRAM_MB, int(raw))
    except Exception:
        pass


def heartbeat() -> None:
    if LEASE_ID:
        subprocess.run(
            ["hive-resource", "lease", "heartbeat", LEASE_ID, "--ttl", "600000"],
            check=True, capture_output=True, text=True,
        )


def queue_empty() -> None:
    queue = json.loads(request("/queue"))
    if queue.get("queue_running") or queue.get("queue_pending"):
        raise RuntimeError("Shared ComfyUI queue is busy; refusing to add this batch")


def upload(source: Path, remote: str) -> None:
    boundary = "----SeanQwenObjectPromptAB20261003"
    content = source.read_bytes()
    fields = [
        (f"--{boundary}\r\nContent-Disposition: form-data; name=\"image\"; filename=\"{remote}\"\r\nContent-Type: image/png\r\n\r\n").encode() + content + b"\r\n",
        (f"--{boundary}\r\nContent-Disposition: form-data; name=\"type\"\r\n\r\ninput\r\n").encode(),
        (f"--{boundary}\r\nContent-Disposition: form-data; name=\"overwrite\"\r\n\r\nfalse\r\n").encode(),
        f"--{boundary}--\r\n".encode(),
    ]
    request("/upload/image", data=b"".join(fields), headers={"Content-Type": f"multipart/form-data; boundary={boundary}"})
    UPLOADED.append(remote)


def wait_for(prompt_id: str, expected: str, start: float, label: str) -> dict:
    last_heartbeat = start
    while time.time() - start < 1800:
        sample_vram()
        hist_all = json.loads(request("/history/" + prompt_id))
        hist = hist_all.get(prompt_id, {})
        status = hist.get("status", {})
        if status.get("status_str") == "error":
            raise RuntimeError(json.dumps(status, ensure_ascii=False))
        outputs = hist.get("outputs", {})
        if expected == "text":
            files = [f for node in outputs.values() for f in node.get("files", [])]
            if files:
                f = files[0]
                query = urllib.parse.urlencode({"filename": f["filename"], "subfolder": f.get("subfolder", ""), "type": f.get("type", "output")})
                data = request("/view?" + query)
                out = ROOT / "generated_prompts" / f"{label}_saved.txt"
                out.parent.mkdir(parents=True, exist_ok=True)
                out.write_bytes(data)
                p = COMFY_OUTPUT / f.get("subfolder", "") / f["filename"]
                if p.is_file():
                    p.unlink()
                return {"prompt_id": prompt_id, "seconds": round(time.time() - start, 2), "output": str(out.relative_to(ROOT)), "sha256": hashlib.sha256(data).hexdigest()}
        else:
            images = [im for node in outputs.values() for im in node.get("images", [])]
            if images:
                im = images[0]
                query = urllib.parse.urlencode({"filename": im["filename"], "subfolder": im.get("subfolder", ""), "type": im.get("type", "output")})
                data = request("/view?" + query)
                out = ROOT / "outputs" / expected
                out.parent.mkdir(parents=True, exist_ok=True)
                out.write_bytes(data)
                p = COMFY_OUTPUT / im.get("subfolder", "") / im["filename"]
                if p.is_file():
                    p.unlink()
                return {"prompt_id": prompt_id, "seconds": round(time.time() - start, 2), "output": str(out.relative_to(ROOT))}
        if time.time() - last_heartbeat > 35:
            heartbeat()
            last_heartbeat = time.time()
        time.sleep(2)
    raise TimeoutError(prompt_id)


def run_graph(graph: dict, expected: str, label: str) -> dict:
    queue_empty()
    (ROOT / "api_workflows" / f"{label}.json").write_text(json.dumps(graph, ensure_ascii=False, indent=2) + "\n")
    pid = json.loads(request("/prompt", {"prompt": graph, "client_id": "sean-qwen-object-prompt-ab-20261003"}))["prompt_id"]
    return wait_for(pid, expected, time.time(), label)


def agent_graph(remote_image: str, case_id: str) -> dict:
    return {
        "1": {"class_type": "CLIPLoader", "inputs": {"clip_name": "qwen3vl_8b_int8_convrot.safetensors", "type": "qwen_image", "device": "default"}},
        "2": {"class_type": "LoadImage", "inputs": {"image": remote_image}},
        "3": {
            "class_type": "TextGenerate",
            "inputs": {
                "clip": ["1", 0], "image": ["2", 0],
                "prompt": (ROOT / "prompts" / CASE_BY_ID[case_id]["agent_instruction"]).read_text().strip(),
                "max_length": 4096,
                "sampling_mode": "on", "sampling_mode.temperature": 0.35, "sampling_mode.top_k": 40, "sampling_mode.top_p": 0.9, "sampling_mode.min_p": 0.0, "sampling_mode.repetition_penalty": 1.05, "sampling_mode.seed": 42, "sampling_mode.presence_penalty": 0.0,
                "thinking": False, "use_default_template": True, "mtp": "auto",
            },
        },
        "4": {"class_type": "SaveText", "inputs": {"text": ["3", 0], "filename_prefix": f"{PREFIX}/agent_prompt/{case_id}", "format": "txt"}},
    }


def pe_graph(remote_image: str, case_id: str) -> dict:
    return {
        "1": {"class_type": "CLIPLoader", "inputs": {"clip_name": PE_NAME, "type": "qwen_image", "device": "default"}},
        "2": {"class_type": "LoadImage", "inputs": {"image": remote_image}},
        "3": {
            "class_type": "QwenImage21_EditPromptRewrite",
            "inputs": {
                "clip": ["1", 0], "image_1": ["2", 0],
                "prompt": (ROOT / "prompts" / f"pe_instruction_{case_id}.txt").read_text().strip(),
                "temperature": 1.0, "top_p": 0.95, "presence_penalty": 0.0,
                "max_length": 24000, "seed": 42,
            },
        },
        "4": {"class_type": "SaveText", "inputs": {"text": ["3", 0], "filename_prefix": f"{PREFIX}/pe_prompt/{case_id}", "format": "txt"}},
    }


def generate_graph(case: dict, remote_image: str, prompt: str, branch: str, seed: int) -> dict:
    graph = json.loads(V3.read_text())
    graph["5"]["inputs"]["prompt"] = prompt
    graph["7"]["inputs"]["seed"] = seed
    graph["9"]["inputs"]["filename_prefix"] = f"{PREFIX}/{branch}/{case['id']}/seed_{seed}"
    graph["10"]["inputs"]["image"] = remote_image
    return graph


def save_manifest(manifest: dict) -> None:
    (ROOT / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")


def acquire_lease() -> str:
    occupancy = json.loads(subprocess.check_output(["hive-resource", "occupancy", "--json"], text=True))
    if occupancy.get("leases") or occupancy.get("occupied"):
        raise RuntimeError(f"GPU lease conflict: {occupancy}")
    acquired = subprocess.run(
        ["hive-resource", "lease", "acquire", "--owner", ROOT.name, "--resources", "gpu:0", "--pid", str(os.getpid()), "--ttl", "600000"],
        check=True, capture_output=True, text=True,
    )
    match = re.search(r"租约 ([0-9a-f-]+) 已授予", acquired.stdout)
    if not match:
        raise RuntimeError("Could not parse GPU lease: " + acquired.stdout)
    return match.group(1)


def main() -> None:
    global LEASE_ID
    manifest_path = ROOT / "manifest.json"
    manifest = json.loads(manifest_path.read_text())
    if manifest.get("status") not in ("preparing", "partial_error", "agent_prompts_ready_pe_pending", "agent_prompt_partial_error"):
        raise RuntimeError(f"Unexpected manifest state: {manifest.get('status')}")
    manifest["status"] = "running"
    manifest.setdefault("results", [])
    save_manifest(manifest)
    try:
        queue_empty()
        LEASE_ID = acquire_lease()
        sample_vram()
        remote_by_case = {}
        for case in CASES:
            local = ROOT / "inputs" / case["reference"]
            remote = f"{PREFIX}_{case['id']}_reference.png"
            upload(local, remote)
            remote_by_case[case["id"]] = remote

        prompt_files = {case["id"]: {"manual": case["manual"]} for case in CASES}
        agent_available = True
        for case in CASES:
            case_id = case["id"]
            final = ROOT / "prompts" / f"agent_qwen3vl_{case_id}.txt"
            if final.is_file() and final.read_text().strip():
                prompt_files[case_id]["agent_qwen3vl"] = final.name
                continue
            try:
                agent = run_graph(agent_graph(remote_by_case[case_id], case_id), "text", f"agent_qwen3vl_{case_id}")
                generated = (ROOT / agent["output"]).read_text().strip()
                if "</think>" in generated:
                    generated = generated.partition("</think>")[2].strip()
                elif "<think>" in generated:
                    generated = generated.partition("<think>")[2].strip()
                final.write_text(generated + "\n")
                prompt_files[case_id]["agent_qwen3vl"] = final.name
                manifest["results"].append({"stage": "agent_prompt", "case": case_id, "model": "qwen3vl_8b_int8_convrot.safetensors", "instruction": f"prompts/{case['agent_instruction']}", "prompt": f"prompts/{final.name}", **agent})
                save_manifest(manifest)
            except Exception as exc:
                agent_available = False
                manifest.setdefault("errors", []).append({"stage": "agent_prompt", "case": case_id, "error": repr(exc)})
                save_manifest(manifest)
                break

        pe_available = True
        for case in CASES:
            case_id = case["id"]
            try:
                pe = run_graph(pe_graph(remote_by_case[case_id], case_id), "text", f"pe_i2i_{case_id}")
                rewritten = (ROOT / pe["output"]).read_text().strip()
                final = ROOT / "prompts" / f"pe_i2i_{case_id}.txt"
                final.write_text(rewritten + "\n")
                prompt_files[case_id]["pe_i2i"] = final.name
                manifest["results"].append({"stage": "pe_prompt", "case": case_id, "checkpoint": PE_NAME, "instruction": f"prompts/pe_instruction_{case_id}.txt", "prompt": f"prompts/{final.name}", "parse": "positive_prompt output from QwenImage21_EditPromptRewrite", **pe})
                save_manifest(manifest)
            except Exception as exc:
                pe_available = False
                manifest.setdefault("errors", []).append({"stage": "pe_prompt", "case": case_id, "error": repr(exc)})
                save_manifest(manifest)
                break

        for case in CASES:
            remote = remote_by_case[case["id"]]
            for offset in range(3):
                seed = case["seed_base"] + offset
                prompt_specs = [(branch, file_name) for branch, file_name in prompt_files[case["id"]].items() if branch != "manual"]
                for branch, prompt_file in prompt_specs:
                    prompt = (ROOT / "prompts" / prompt_file).read_text().strip()
                    filename = f"{branch}/{case['id']}/seed_{seed}.png"
                    result = run_graph(generate_graph(case, remote, prompt, branch, seed), filename, f"{branch}_{case['id']}_seed_{seed}")
                    result.update({"case": case["id"], "branch": branch, "seed": seed, "prompt": f"prompts/{prompt_file}"})
                    manifest["results"].append(result)
                    save_manifest(manifest)
        for remote in remote_by_case.values():
            remote_path = COMFY_INPUT / remote
            if remote_path.is_file():
                remote_path.unlink()
        manifest["status"] = "generated_qc_pending" if agent_available and pe_available else "partial_error_qc_pending"
    except Exception as exc:
        manifest["status"] = "partial_error"
        manifest["fatal_error"] = repr(exc)
        raise
    finally:
        for remote in UPLOADED:
            p = COMFY_INPUT / remote
            if p.is_file():
                p.unlink()
        sample_vram()
        if LEASE_ID:
            subprocess.run(
                ["hive-resource", "observe", "--resource", "gpu:0", "--job", ROOT.name, "--metrics", json.dumps({"peakVramMb": PEAK_VRAM_MB, "generatedRuns": sum(1 for x in manifest.get("results", []) if x.get("branch")), "status": manifest.get("status")})],
                check=False, capture_output=True, text=True,
            )
            subprocess.run(["hive-resource", "lease", "release", LEASE_ID], check=False, capture_output=True, text=True)
        save_manifest(manifest)
    print(json.dumps({"status": manifest["status"], "results": len(manifest["results"]), "peakVramMb": PEAK_VRAM_MB, "manifest": str(manifest_path)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
