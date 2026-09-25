#!/usr/bin/env python3
"""H3 批量测试 runner（2026-08-05 正式版，替代 /tmp/patch_runner.py）
用法: python3 h3_batch_runner.py <cases.json> [--interval 15]
case 字段:
  name: 任务名（日志标识）
  unet: 模型文件名（默认 fl2va int8）
  steps: 采样步数（默认 20）
  mc: true 启用 MotionCache
  mc_warmup / mc_threshold / mc_maxskip: MC 参数（默认 4/0.15/2）
  mc_verbose: 输出 MC 跳步日志
  width/height/length: 分辨率与帧数（默认 1024×576×124）
  seed: 噪声种子（默认 20260805）
  image: fl2va 首帧图（"start/xxx.png"）
  refs: ref2va 参考图列表（与 image 二选一）
  prompt: 提示词
  prefix: 输出路径（SaveVideo filename_prefix）
  audio: 外部音频路径（可选；启用 H3 Native Audio Lock）
  pdd: PDD Acc 文件名（可选；文件位于 models/pdd_acc，使用专用 Euler/SIGMA）
  vdn: true 启用 ApplyVDNH3（与 pdd 二选一）
  low_vram_attention: true 启用 KJNodes MiniMaxLowVRAMAttention
  sage_attention: true 启用 KJNodes MiniMax H3 Memory Efficient Sage Attention Patch
  chunk_feedforward: true 启用 KJNodes MiniMaxChunkFeedForward
  head_chunks / ff_chunks / ff_seq_threshold: KJNodes 分块参数
  h3_memory_optimization: true 启用 H3-Optimizations H3MemoryOptimization
  h3_chunk_rows / h3_precision_mode / h3_qkv_streaming_mode: H3 优化参数
  release_before_decode: true 采样后用 KJ VRAM Debug 卸载模型
  tiled_vae: true 使用视频 VAEDecodeTiled（音频仍用普通解码）
输出: <cases.json>.results.json（含每条耗时/错误）+ stdout 汇总

设计要点（吸取 2026-08-05 补测批踩坑）：
- 提交后确认 prompt_id 出现在队列（running 或 pending）再进入轮询，防重启过渡期误判"完成"
- 串行执行，耗时 = 提交到出队时间差（含加载/排队，无并行干扰）
"""
import json, sys, time, urllib.request, urllib.error

HOST = "http://127.0.0.1:8188"
DEFAULT_UNET = "minimax_h3_fl2va_pruned_int8_convrot.safetensors"
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
    if c.get("image"):  # fl2va I2V
        wf["5"] = {"class_type": "LoadImage", "inputs": {"image": c["image"]}}
        wf["6"] = {"class_type": "MiniMaxH3ImageToVideo", "inputs": {
            "clip": ["2",0], "vae": ["3",0],
            "prompt": c["prompt"], "width": c.get("width",1024), "height": c.get("height",576),
            "length": c.get("length",124), "first_frame": ["5",0]}}
    else:  # ref2va
        wf["6"] = {"class_type": "MiniMaxH3ReferenceToVideo", "inputs": {
            "clip": ["2",0], "vae": ["3",0], "audio_vae": ["4",0],
            "prompt": c["prompt"], "width": c.get("width",1024), "height": c.get("height",576),
            "length": c.get("length",124), "ref_image_size": c.get("ref_image_size","match")}}
        nid = 100
        for j, ref in enumerate(c.get("refs", [])):
            wf[str(nid)] = {"class_type": "LoadImage", "inputs": {"image": ref}}
            wf["6"]["inputs"][f"ref_images.ref_image_{j}"] = [str(nid), 0]
            nid += 1
    model_ref = ["1", 0]
    if c.get("vdn"):
        wf["18"] = {"class_type": "ApplyVDNH3", "inputs": {
            "model": ["1", 0], "vdn_checkpoint": c.get("vdn_checkpoint", "vdn-minimax-h3-int8-convrot-comfyui"),
            "apply_turbo_adapter": True, "strength": c.get("vdn_strength", 1.0),
            "lora_mode": "merge", "branch_weights": c.get("vdn_branch_weights", "stream"),
            "retain_buffers": c.get("vdn_retain_buffers", "off"), "verbose": True,
            "attention_backend": c.get("vdn_attention_backend", "grouped")}}
        model_ref = ["18", 0]
    if c.get("pdd"):
        # PDD must be applied before any KJ/H3 model patches.  Keeping it
        # separate from the sigma output lets the patched model drive both
        # scheduler and guider while PDD supplies its dedicated sigmas.
        wf["18"] = {"class_type": "MiniMaxH3PDDAccApply", "inputs": {
            "model": model_ref, "pdd_file": c["pdd"], "nfe": str(c.get("pdd_nfe", 8)),
            "lora_strength": c.get("pdd_lora_strength", 1.0), "head_strength": c.get("pdd_head_strength", 1.0),
            "on_off_grid": "error"}}
        model_ref = ["18", 0]
    # Optional KJNodes memory patches. Keep them after VDN so the test verifies
    # whether the patched model path remains compatible with ApplyVDNH3.
    if c.get("low_vram_attention"):
        wf["19"] = {"class_type": "MiniMaxLowVRAMAttention", "inputs": {
            "model": model_ref, "head_chunks": int(c.get("head_chunks", 4))}}
        model_ref = ["19", 0]
    if c.get("chunk_feedforward"):
        wf["20"] = {"class_type": "MiniMaxChunkFeedForward", "inputs": {
            "model": model_ref, "chunks": int(c.get("ff_chunks", 4)),
            "seq_threshold": int(c.get("ff_seq_threshold", 4096))}}
        model_ref = ["20", 0]
    if c.get("h3_memory_optimization"):
        wf["22"] = {"class_type": "H3MemoryOptimization", "inputs": {
            "model": model_ref, "fused_qkv": "auto",
            "mlp_memory": c.get("h3_mlp_memory", "auto"),
            "chunk_rows": int(c.get("h3_chunk_rows", 4096)),
            "preserve_precision": True,
            "precision_mode": c.get("h3_precision_mode", "Preserve native"),
            "qkv_streaming_mode": c.get("h3_qkv_streaming_mode", "Auto"),
            "embedding_memory_mode": c.get("h3_embedding_memory_mode", "Auto"),
            "kitchen_v_memory_mode": c.get("h3_kitchen_v_memory_mode", "Standard")}}
        model_ref = ["22", 0]
    wf["7"] = {"class_type": "KSamplerSelect", "inputs": {"sampler_name": "euler" if c.get("pdd") else "res_multistep"}}
    wf["8"] = {"class_type": "BasicScheduler", "inputs": {"model": model_ref, "scheduler": "simple", "steps": c.get("steps",20), "denoise": 1}}
    wf["9"] = {"class_type": "BasicGuider", "inputs": {"model": model_ref, "conditioning": ["6",0]}}
    wf["10"] = {"class_type": "RandomNoise", "inputs": {"noise_seed": c.get("seed",20260805)}}
    wf["11"] = {"class_type": "SamplerCustomAdvanced", "inputs": {
        "noise": ["10",0], "guider": ["9",0], "sampler": ["7",0],
        "sigmas": ["18",1] if c.get("pdd") else ["8",0], "latent_image": ["6",1]}}
    # Apply the H3-specific KJ Sage patch after the optional H3 optimization
    # patch.  This is deliberately separate from the global PyTorch attention
    # backend: the test must prove that the workflow uses SageAttention.
    if c.get("sage_attention"):
        wf["23"] = {"class_type": "MiniMaxH3MemoryEfficientSageAttentionPatch", "inputs": {
            "model": model_ref}}
        model_ref = ["23", 0]
        wf["8"]["inputs"]["model"] = model_ref
        wf["9"]["inputs"]["model"] = model_ref
    if c.get("audio"):
        # Lock an externally prepared soundtrack; only the video branch is denoised.
        wf["16"] = {"class_type": "LoadAudio", "inputs": {"audio": c["audio"]}}
        wf["17"] = {"class_type": "MiniMaxH3NativeAudioLock", "inputs": {
            "model": model_ref, "av_latent": ["6",1], "audio_vae": ["4",0], "audio": ["16",0]}}
        wf["9"]["inputs"]["model"] = ["17",0]
        wf["11"]["inputs"]["latent_image"] = ["17",1]
        model_ref = ["17", 0]
    latent_ref = ["11", 0]
    if c.get("release_before_decode"):
        wf["21"] = {"class_type": "VRAM_Debug", "inputs": {
            "empty_cache": True, "gc_collect": True, "unload_all_models": True,
            "any_input": ["11", 0], "model_pass": model_ref}}
        latent_ref = ["21", 0]
    if c.get("tiled_vae"):
        wf["12"] = {"class_type": "VAEDecodeTiled", "inputs": {
            "samples": latent_ref, "vae": ["3",0],
            "tile_size": c.get("vae_tile_size", 512), "overlap": c.get("vae_overlap", 64),
            "temporal_size": c.get("vae_temporal_size", 64), "temporal_overlap": c.get("vae_temporal_overlap", 8)}}
    else:
        wf["12"] = {"class_type": "VAEDecode", "inputs": {"samples": latent_ref, "vae": ["3",0]}}
    wf["13"] = {"class_type": "VAEDecodeAudio", "inputs": {"samples": latent_ref, "vae": ["4",0]}}
    wf["14"] = {"class_type": "CreateVideo", "inputs": {"images": ["12",0], "fps": 24, "audio": ["13",0], "bit_depth": 8}}
    wf["15"] = {"class_type": "SaveVideo", "inputs": {"video": ["14",0], "filename_prefix": c["prefix"], "format": "mp4", "codec": "auto"}}
    if c.get("mc"):
        wf["200"] = {"class_type": "MiniMaxH3MotionCache", "inputs": {
            "model": ["17",0] if c.get("audio") else ["1",0], "reuse_threshold": c.get("mc_threshold", 0.15), "motion_strength": 1,
            "warmup_steps": c.get("mc_warmup", 4), "max_consecutive_skips": c.get("mc_maxskip", 2),
            "start_percent": 0.15, "end_percent": 0.95, "subsample_factor": 8,
            "verbose": bool(c.get("mc_verbose", False))}}
        wf["8"]["inputs"]["model"] = ["200",0]
        wf["9"]["inputs"]["model"] = ["200",0]
    return wf

def main():
    cases = json.load(open(sys.argv[1]))
    interval = 15
    if "--interval" in sys.argv:
        interval = int(sys.argv[sys.argv.index("--interval")+1])
    # 前置健康检查：ComfyUI 必须就绪（防过渡期误判）
    try:
        st = api("/system_stats")
        print(f"ComfyUI 就绪: {st['devices'][0]['name']}", flush=True)
    except Exception as e:
        print(f"❌ ComfyUI 不可用: {e}"); sys.exit(1)

    results = []
    for c in cases:
        t0 = time.time()
        try:
            pid = api("/prompt", {"prompt": build_wf(c), "client_id": "h3-batch"})["prompt_id"]
        except urllib.error.HTTPError as e:
            print(f"[{c['name']}] ❌ 提交失败: {e.read().decode()[:150]}", flush=True)
            results.append({"name": c["name"], "error": "submit failed"}); continue
        # 提交确认：prompt_id 必须出现在队列（防重启过渡期假完成）
        seen = False
        for _ in range(20):
            time.sleep(5)
            run, pend = queue_pids()
            if pid in run or pid in pend:
                seen = True; break
            h = api(f"/history/{pid}")
            if pid in h:  # 已在 history（执行过快或失败）
                seen = True; break
        if not seen:
            print(f"[{c['name']}] ⚠️ 提交后 100s 未见队列/历史，跳过", flush=True)
            results.append({"name": c["name"], "error": "not seen in queue"}); continue
        # 轮询完成
        while True:
            time.sleep(interval)
            run, pend = queue_pids()
            if pid not in run and pid not in pend:
                break
        t1 = time.time()
        h = api(f"/history/{pid}")
        msgs = h.get(pid, {}).get("status", {}).get("messages", [])
        errs = [m[1].get("exception_message","") for m in msgs if m[0]=="execution_error"]
        interrupted = any(m[0] == "execution_interrupted" for m in msgs)
        if interrupted and not errs:
            errs = ["execution_interrupted"]
        ok = not errs
        print(f"[{c['name']}] {t1-t0:.0f}s {'❌ '+errs[0][:100] if errs else '✅'}", flush=True)
        results.append({"name": c["name"], "seconds": round(t1-t0), "error": errs[0] if errs else None})

    out = sys.argv[1] + ".results.json"
    json.dump(results, open(out, "w"), indent=1, ensure_ascii=False)
    print(f"\n结果: {out}")

if __name__ == "__main__":
    main()
