#!/usr/bin/env python3
"""Ref2VA 测试 runner（2026-08-14 h3-ref2v-pilot 任务线）

用法: python3 h3_ref2v_runner.py <cases.json> [--interval 15]
case 字段:
  ref_images: [本地图路径(相对 ComfyUI/input 或 input 内路径)] 1-3 张
  prompt: 六段式（subject_definitions/summary/retention_analysis/
          detailed_description/overall_soundscape/non_diegetic_music）
  ref_image_size: "match"(默认) | "max"
  unet(默认 ref2va_pruned_int8_convrot) / lora(可选 ref2v turbo) /
  steps(默认 20) / sampler: "res"(res_multistep, 官方20步) | "euler"(turbo 4步)
  pdd(可选 PDD Acc 文件名): 启用 PDD 8-step 快车道（自动 euler + 节点 sigmas）
          pdd_nfe(默认8) / pdd_partition / pdd_lora_strength / pdd_head_strength
  shift_video(默认12) / shift_audio(默认3) / width / height / length /
  seed / prefix
输出: <cases.json>.results.json（耗时/错误）
"""
import json, sys, time, urllib.request, urllib.error

HOST = "http://127.0.0.1:8188"
DEFAULT_UNET = "minimax_h3_ref2va_pruned_int8_convrot.safetensors"
CLIP = "qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors"

def api(path, data=None, timeout=30):
    url = f"{HOST}{path}"
    if data is not None:
        req = urllib.request.Request(url, data=json.dumps(data).encode(),
            headers={"Content-Type": "application/json"})
    else:
        req = urllib.request.Request(url)
    return json.load(urllib.request.urlopen(req, timeout=timeout))

def queue_pids():
    q = api("/queue")
    return ([x[1] for x in q["queue_running"]], [x[1] for x in q["queue_pending"]])

def build_wf(c):
    wf = {
        "1": {"class_type": "UNETLoader", "inputs": {"unet_name": c.get("unet", DEFAULT_UNET), "weight_dtype": "default"}},
        "2": {"class_type": "CLIPLoader", "inputs": {"clip_name": CLIP, "type": "minimax", "device": "default"}},
        "3": {"class_type": "VAELoader", "inputs": {"vae_name": "minimax_h3_video_vae_fp16.safetensors"}},
        "4": {"class_type": "VAELoader", "inputs": {"vae_name": "minimax_h3_audio_vae_fp32.safetensors"}},
    }
    # 参考图
    ref_inputs = {}
    for i, img in enumerate(c.get("ref_images", [])):
        nid = f"5{i}"
        wf[nid] = {"class_type": "LoadImage", "inputs": {"image": img}}
        ref_inputs[f"ref_image_{i}"] = [nid, 0]
    wf["6"] = {"class_type": "MiniMaxH3ReferenceToVideo", "inputs": {
        "clip": ["2", 0], "vae": ["3", 0], "audio_vae": ["4", 0],
        "prompt": c["prompt"], "width": c.get("width", 960), "height": c.get("height", 544),
        "length": c.get("length", 124),
        "ref_image_size": c.get("ref_image_size", "match"),
        "ref_images": ref_inputs,
    }}
    model_ref = "1"
    if c.get("lora"):
        wf["90"] = {"class_type": "LoraLoaderModelOnly", "inputs": {
            "model": ["1", 0], "lora_name": c["lora"], "strength_model": c.get("lora_strength", 1.0)}}
        model_ref = "90"
    if c.get("sage_attention") or c.get("name", "").startswith("sage_"):
        wf["93"] = {"class_type": "PathchSageAttentionKJ", "inputs": {
            "model": [model_ref, 0], "sage_attention": "auto", "allow_compile": False}}
        model_ref = "93"
    if c.get("pdd"):
        wf["94"] = {"class_type": "MiniMaxH3PDDAccApply", "inputs": {
            "model": [model_ref, 0], "pdd_file": c["pdd"], "nfe": str(c.get("pdd_nfe", 8)),
            "lora_strength": c.get("pdd_lora_strength", 1.0),
            "head_strength": c.get("pdd_head_strength", 1.0),
            "on_off_grid": c.get("pdd_on_off_grid", "error")}}
        if c.get("pdd_partition"):
            wf["94"]["inputs"]["partition"] = c["pdd_partition"]
        model_ref = "94"
    if c.get("shift_video") is not None:
        wf["91"] = {"class_type": "MiniMaxH3SigmaShift", "inputs": {
            "model": [model_ref, 0],
            "shift_video": c.get("shift_video", 12.0), "shift_audio": c.get("shift_audio", 3.0)}}
        model_ref = "91"
    if c.get("sparse_attention"):
        wf["92"] = {"class_type": "BlockSparseAttention", "inputs": {
            "model": [model_ref, 0],
            "selection": "sol-attn", "selection.tau": c.get("sparse_tau", 1.3),
            "start_percent": c.get("sparse_start", 0.2), "end_percent": c.get("sparse_end", 1.0),
            "dense_blocks": "", "min_tokens": c.get("sparse_min_tokens", 12288),
            "extra_tokens": 256, "sink_conditioning": "exact_kv_and_rows", "verbose": True}}
        model_ref = "92"
    # Optional external audio lock.  Keep it after the LoRA/model modifiers so
    # the ordinary Ref2VA comparison uses the same accelerated model path.
    audio_lock = c.get("audio_lock")
    base_model = [model_ref, 0]
    base_latent = ["6", 1]
    if audio_lock:
        wf["19"] = {"class_type": "LoadAudio", "inputs": {"audio": audio_lock}}
        wf["20"] = {"class_type": "MiniMaxH3NativeAudioLock", "inputs": {
            "model": base_model, "av_latent": ["6", 1], "audio_vae": ["4", 0], "audio": ["19", 0]}}
        base_model = ["20", 0]
        base_latent = ["20", 1]

    default_sampler = "euler" if c.get("pdd") else "res_multistep"
    wf["7"] = {"class_type": "KSamplerSelect", "inputs": {"sampler_name": c.get("sampler", default_sampler)}}
    if c.get("pdd"):
        sigmas_ref = ["94", 1]   # PDD Apply 的 sigmas 输出（PDD 关节）
    else:
        sigmas_ref = ["8", 0]
        wf["8"] = {"class_type": "BasicScheduler", "inputs": {"model": base_model, "scheduler": "simple", "steps": c.get("steps", 20), "denoise": 1}}
    wf["9"] = {"class_type": "BasicGuider", "inputs": {"model": base_model, "conditioning": ["6", 0]}}
    fresh_seed = 20260914 if c.get("name", "").endswith("d05_1344x768") else c.get("seed", 20260814)
    wf["10"] = {"class_type": "RandomNoise", "inputs": {"noise_seed": fresh_seed}}
    wf["11"] = {"class_type": "SamplerCustomAdvanced", "inputs": {"noise": ["10", 0], "guider": ["9", 0], "sampler": ["7", 0], "sigmas": sigmas_ref, "latent_image": base_latent}}
    wf["12"] = {"class_type": "VAEDecode", "inputs": {"samples": ["11", 0], "vae": ["3", 0]}}
    wf["13"] = {"class_type": "VAEDecodeAudio", "inputs": {"samples": ["11", 0], "vae": ["4", 0]}}
    wf["14"] = {"class_type": "CreateVideo", "inputs": {"images": ["12", 0], "fps": 24, "audio": ["13", 0], "bit_depth": 8}}
    wf["15"] = {"class_type": "SaveVideo", "inputs": {"video": ["14", 0], "filename_prefix": c["prefix"], "format": "mp4", "codec": "auto"}}
    return wf

def main():
    cases = json.load(open(sys.argv[1]))
    interval = 5
    if "--interval" in sys.argv:
        interval = int(sys.argv[sys.argv.index("--interval") + 1])
    results = []
    for c in cases:
        pid = api("/prompt", {"prompt": build_wf(c)})["prompt_id"]
        t0 = time.time()
        exec_ms = None
        while True:
            time.sleep(interval)
            running, pending = queue_pids()
            hist = api("/history/" + pid, timeout=10)
            if pid in hist:
                st = hist[pid]["status"]
                status = "success" if st.get("completed") else ("error" if st.get("status_str") == "error" else "running")
                if status != "running":
                    msgs = hist[pid].get("status", {}).get("messages", [])
                    exec_ms = [m[1] for m in msgs if m[0] == "execution_success" and isinstance(m[1], dict)]
                    results.append({"name": c["name"], "status": status, "secs": round(time.time() - t0, 1),
                                    "pid": pid, "exec_ms": exec_ms[-1] if exec_ms else None, **c})
                    print(f"[{c['name']}] {status} {round(time.time()-t0,1)}s {exec_ms[-1] if exec_ms else ''}", flush=True)
                    break
            if time.time() - t0 > 3600:
                results.append({"name": c["name"], "status": "timeout", "secs": 3600, "pid": pid, **c})
                break
    out = sys.argv[1] + ".results.json"
    json.dump(results, open(out, "w"), ensure_ascii=False, indent=1)
    print("results ->", out)

if __name__ == "__main__":
    main()
