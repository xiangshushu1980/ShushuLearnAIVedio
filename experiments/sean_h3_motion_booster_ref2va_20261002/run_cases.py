#!/usr/bin/env python3
"""Owner: Sean. Resume the matched Motion Booster cases under an existing GPU lease."""
import argparse
import hashlib
import json
import pathlib
import re
import shutil
import subprocess
import time
import urllib.error
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent
HOST = "http://127.0.0.1:8188"
OUTPUT = pathlib.Path("/home/sean/projects/ComfyUI/output")


def api(path, body=None):
    request = urllib.request.Request(HOST + path)
    if body is not None:
        request.data = json.dumps(body).encode()
        request.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.load(response)
    except urllib.error.HTTPError as error:
        raise RuntimeError(error.read().decode()) from None


def save(manifest):
    (ROOT / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")


def command(*args):
    return subprocess.check_output(args, text=True).strip()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--lease", required=True)
    parser.add_argument("--case", action="append", choices=["motion_07", "motion_08", "motion_07_no_ref_latent", "motion_07_fullwidth_prompt", "motion_07_landscape_ref"])
    args = parser.parse_args()
    manifest = json.loads((ROOT / "manifest.json").read_text())
    model = pathlib.Path(manifest["model_download"]["path"])
    if hashlib.sha256(model.read_bytes()).hexdigest().upper() != manifest["expected_sha256"]:
        raise RuntimeError("Model hash mismatch")
    names = api("/object_info/LoraLoaderModelOnly")["LoraLoaderModelOnly"]["input"]["required"]["lora_name"][0]
    if model.name not in names:
        raise RuntimeError("Installed model not listed by existing ComfyUI; do not restart automatically")
    manifest.update(status="running", gpu_lease_id=args.lease, gpu_lease_released=False)
    save(manifest)
    batch_peak = 0
    try:
        for case in manifest["cases"]:
            if case["id"] == "baseline" or (args.case and case["id"] not in args.case):
                continue
            if case["status"] == "success":
                continue
            queue = api("/queue")
            if queue["queue_running"] or queue["queue_pending"]:
                raise RuntimeError("Shared queue occupied; stopped before submission")
            workflow = json.loads((ROOT / case["workflow"]).read_text())
            start = time.time()
            result = api("/prompt", {"prompt": workflow, "client_id": "sean-motion-booster"})
            pid = result["prompt_id"]
            case.update(status="running", prompt_id=pid, submitted_at=start)
            save(manifest)
            print(json.dumps({"case": case["id"], "prompt_id": pid, "status": "submitted"}), flush=True)
            last_update = 0
            peak = 0
            while True:
                elapsed = time.time() - start
                if elapsed > 1200:
                    raise RuntimeError("Generation wait exceeded 1200s; active job requires inspection")
                gpu = command("/usr/lib/wsl/lib/nvidia-smi", "--query-gpu=memory.used,utilization.gpu", "--format=csv,noheader,nounits")
                peak = max(peak, int(gpu.split(",")[0]))
                batch_peak = max(batch_peak, peak)
                history = api(f"/history/{pid}")
                if pid in history:
                    entry = history[pid]
                    (ROOT / f"{case['id']}_history.json").write_text(json.dumps(entry, ensure_ascii=False, indent=2) + "\n")
                    case.update(status=entry["status"]["status_str"], completed_at=time.time(), peak_vram_mib=peak)
                    save(manifest)
                    if case["status"] != "success":
                        raise RuntimeError(f"Execution failed; see {case['id']}_history.json")
                    break
                if elapsed - last_update >= 25:
                    command("hive-resource", "lease", "heartbeat", args.lease, "--ttl", "600000")
                    print(f"{case['id']} running {elapsed:.0f}s GPU {gpu} peak {peak} MiB", flush=True)
                    last_update = elapsed
                time.sleep(3)
            item = entry["outputs"]["15"]["images"][0]
            source = (OUTPUT / item["subfolder"] / item["filename"]).resolve()
            if not source.is_relative_to(OUTPUT.resolve()):
                raise RuntimeError("Unexpected output path")
            target = ROOT / f"{case['id']}.mp4"
            shutil.copy2(source, target)
            digest = hashlib.sha256(target.read_bytes()).hexdigest()
            if hashlib.sha256(source.read_bytes()).hexdigest() != digest:
                raise RuntimeError("Output copy verification failed")
            source.unlink()
            probe = json.loads(command("ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(target)))
            (ROOT / f"{case['id']}_ffprobe.json").write_text(json.dumps(probe, ensure_ascii=False, indent=2) + "\n")
            timestamps = {kind: data["timestamp"] for kind, data in entry["status"]["messages"] if "timestamp" in data}
            seconds = (timestamps["execution_success"] - timestamps["execution_start"]) / 1000
            logs = command("journalctl", "--user", "-u", "comfyui.service", "--since", f"@{int(start)}", "--no-pager", "-o", "cat")
            (ROOT / f"{case['id']}_runtime.log").write_text(logs + "\n")
            not_loaded = re.findall(r"(?:lora key not loaded|NOT LOADED diffusion_model)[^\n]*", logs, flags=re.IGNORECASE)
            case.update(output=target.name, sha256=digest, comfy_seconds=seconds, output_cleaned=True,
                        lora_unmatched_log_count=len(not_loaded), lora_matching_status="unmatched_keys_reported" if not_loaded else "no_unmatched_key_warnings_in_runtime_log")
            manifest["results"] = [v for v in manifest["results"] if v["case"] != case["id"]]
            manifest["results"].append({"case": case["id"], "status": "success", "output": target.name, "comfy_seconds": seconds, "peak_vram_mib": peak})
            save(manifest)
            print(json.dumps(case, ensure_ascii=False), flush=True)
        manifest["status"] = "awaiting_qc"
        save(manifest)
    finally:
        queue = api("/queue")
        own_ids = {c.get("prompt_id") for c in manifest["cases"]}
        own_running = any(item[1] in own_ids for item in queue["queue_running"] + queue["queue_pending"])
        if own_running:
            print("Own generation remains active; lease retained for inspection", flush=True)
        else:
            command("hive-resource", "observe", "--resource", "gpu:0", "--job", "sean_h3_motion_booster_ref2va_20261002", "--metrics", json.dumps({"peakVramMb": batch_peak}))
            command("hive-resource", "lease", "release", args.lease)
            manifest["gpu_lease_released"] = True
            save(manifest)
            print("GPU lease released", flush=True)


if __name__ == "__main__":
    main()
