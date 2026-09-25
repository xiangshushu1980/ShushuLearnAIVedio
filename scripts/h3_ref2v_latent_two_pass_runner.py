#!/usr/bin/env python3
"""Run a native H3 Ref2VA first pass followed by learned full-video latent upscale/refine."""
import json, sys, time, urllib.request, urllib.error
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h3_ref2v_runner as base

HOST = base.HOST

def api(path, data=None, timeout=30):
    try:
        return base.api(path, data, timeout)
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"ComfyUI API {path} HTTP {exc.code}: {body}") from exc

def load_prompt(c):
    if c.get("prompt_file"):
        p = Path(c["prompt_file"])
        if not p.is_absolute():
            p = Path.cwd() / p
        c["prompt"] = p.read_text()
    elif isinstance(c.get("prompt"), str) and c["prompt"].startswith("@"):
        c["prompt"] = Path(c["prompt"][1:]).read_text()

def build_wf(c):
    wf = base.build_wf(c)
    if c.get("source_only"):
        return wf
    model_ref = wf["9"]["inputs"]["model"]
    positive_ref = wf["9"]["inputs"]["conditioning"]

    # First-pass node 11 produces the complete low-resolution H3 AV latent.
    wf["16"] = {"class_type": "RandomNoise", "inputs": {
        "noise_seed": int(c.get("refine_seed", int(c.get("seed", 0)) + 1))}}
    wf["17"] = {"class_type": "BasicScheduler", "inputs": {
        "model": model_ref,
        "scheduler": "simple",
        "steps": int(c.get("refine_steps", 4)),
        "denoise": float(c.get("refine_denoise", 0.4))}}
    wf["18"] = {"class_type": "MinimaxH3LatentUpscaler3DRefineHandoff", "inputs": {
        "latent": ["11", 0],
        "noise": ["16", 0],
        "sampler": ["7", 0],
        "sigmas": ["17", 0],
        "model_name": c.get("latent_upscaler_model", "minimax_h3_latent_upscaler_3d_conv_v1_bf16.safetensors"),
        "mode": "target dimensions",
        "scale": 2.0,
        "width": int(c.get("target_width", 1344)),
        "height": int(c.get("target_height", 768)),
        "megapixels": 1.0,
        "align": 32,
        "keep_proportion": True,
        "lock_audio": True,
        "cfg": 1.0,
        "device": "cuda",
        "precision": c.get("precision", "bf16"),
        "offload_after_upscale": bool(c.get("offload_after_upscale", False)),
        "model": model_ref,
        "positive": positive_ref}}
    wf["12"]["inputs"]["samples"] = ["18", 0]
    wf["13"]["inputs"]["samples"] = ["18", 0]
    return wf

def main():
    cases = json.loads(Path(sys.argv[1]).read_text())
    interval = 5
    results = []
    for c in cases:
        load_prompt(c)
        pid = api("/prompt", {"prompt": build_wf(c)})["prompt_id"]
        t0 = time.time()
        while True:
            time.sleep(interval)
            hist = api("/history/" + pid, timeout=10)
            if pid in hist:
                st = hist[pid]["status"]
                status = "success" if st.get("completed") else ("error" if st.get("status_str") == "error" else "running")
                if status != "running":
                    results.append({"name": c["name"], "status": status, "secs": round(time.time()-t0, 1), "pid": pid, **c})
                    print(f"[{c['name']}] {status} {round(time.time()-t0,1)}s", flush=True)
                    if status == "error":
                        print(json.dumps(st, ensure_ascii=False, indent=2), flush=True)
                    break
            if time.time() - t0 > 3600:
                results.append({"name": c["name"], "status": "timeout", "secs": 3600, "pid": pid, **c})
                break
    out = Path(sys.argv[1]).with_suffix(Path(sys.argv[1]).suffix + ".results.json")
    out.write_text(json.dumps(results, ensure_ascii=False, indent=1))
    print("results ->", out)

if __name__ == "__main__":
    main()
