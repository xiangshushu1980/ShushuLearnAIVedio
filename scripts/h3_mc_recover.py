#!/usr/bin/env python3
"""MC 验收材料恢复：latent → 视频（不重采样，仅 VAE 解码）。

背景：2026-08-17 发现 output/video/h3_mc* 视频产物丢失，但
output/h3_context、output/h3_ctx_same 的 AV latent 完好。
本脚本把 latent 转成标准 .latent 文件，走 ComfyUI API 解码恢复视频。

用法:
  python3 h3_mc_recover.py            # 恢复 4 条 latent 视频
  python3 h3_mc_recover.py --baseline # 另重跑 same_seg2_baseline（151s）
"""
import json, os, subprocess, sys, time, urllib.request

HOST = "http://127.0.0.1:8188"
INPUT_DIR = "/home/sean/projects/ComfyUI/input"
OUTPUT_DIR = "/home/sean/projects/ComfyUI/output"
VIDEO_VAE = "minimax_h3_video_vae_fp16.safetensors"
AUDIO_VAE = "minimax_h3_audio_vae_fp32.safetensors"
TRIM_FRAMES = 22  # context_length=22，与 mc_cases 一致

# (latent 文件, 输出 prefix, 是否 trim, 名称)
CASES = [
    ("h3_context/clip_00001", "video/h3_mc/agreement_mc_seg1", False, "首批 seg1"),
    ("h3_context/clip_00002", "video/h3_mc/agreement_mc_seg2_ctx22", True, "首批 seg2 MC22"),
    ("h3_ctx_same/clip_00001", "video/h3_mc_same/agreement_same_seg1", False, "批2 seg1"),
    ("h3_ctx_same/clip_00002", "video/h3_mc_same/agreement_same_seg2_chain", True, "批2 chain"),
]


def api(path, data=None, timeout=60):
    url = f"{HOST}{path}"
    if data is not None:
        req = urllib.request.Request(url, data=json.dumps(data).encode(),
                                     headers={"Content-Type": "application/json"})
    else:
        req = urllib.request.Request(url)
    return json.load(urllib.request.urlopen(req, timeout=timeout))


def to_std_latent(src_safetensors, out_base, tag):
    """拆 video/audio 两流 → 两个标准 .latent（带 latent_format_version_0 免缩放）"""
    import safetensors.torch as st
    d = st.load_file(src_safetensors)
    paths = []
    for stream, name in (("video", "video"), ("audio", "audio")):
        t = d[stream]
        p = os.path.join(INPUT_DIR, f"{out_base}_{tag}_{name}.latent")
        t = t.contiguous()
        st.save_file({"latent_tensor": t.clone(),
                      "latent_format_version_0": t}, p)
        paths.append((name, p))
    return paths


def build_decode_wf(video_latent, audio_latent, prefix, do_trim):
    """LoadLatent → VAEDecode/VAEDecodeAudio → (Trim) → CreateVideo → SaveVideo"""
    wf = {
        "1": {"class_type": "VAELoader", "inputs": {"vae_name": VIDEO_VAE}},
        "2": {"class_type": "VAELoader", "inputs": {"vae_name": AUDIO_VAE}},
        "3": {"class_type": "LoadLatent", "inputs": {"latent": os.path.basename(video_latent)}},
        "4": {"class_type": "LoadLatent", "inputs": {"latent": os.path.basename(audio_latent)}},
        "5": {"class_type": "VAEDecode", "inputs": {"samples": ["3", 0], "vae": ["1", 0]}},
        "6": {"class_type": "VAEDecodeAudio", "inputs": {"samples": ["4", 0], "vae": ["2", 0]}},
    }
    nxt = 7
    if do_trim:
        wf["7"] = {"class_type": "MiniMaxH3MotionContextTrim", "inputs": {
            "images": ["5", 0], "trim_frames": TRIM_FRAMES,
            "audio": ["6", 0], "fps": 24.0, "match_tail": True}}
        img, aud = ["7", 0], ["7", 1]
        nxt = 8
    else:
        img, aud = ["5", 0], ["6", 0]
    wf[str(nxt)] = {"class_type": "CreateVideo", "inputs": {
        "images": img, "fps": 24, "audio": aud, "bit_depth": 8}}
    wf[str(nxt + 1)] = {"class_type": "SaveVideo", "inputs": {
        "video": [str(nxt), 0], "filename_prefix": prefix,
        "format": "mp4", "codec": "auto"}}
    return wf


def submit(wf, name):
    r = api("/prompt", {"prompt": wf})
    pid = r["prompt_id"]
    print(f"[{name}] 已提交 {pid}")
    t0 = time.time()
    while True:
        st = api(f"/history/{pid}", timeout=30)
        if pid in st:
            h = st[pid]
            status = h.get("status", {})
            if status.get("completed"):
                outs = h.get("outputs", {})
                vids = []
                for node_id, o in outs.items():
                    for k in ("gifs", "videos"):
                        if k in o:
                            for it in o[k]:
                                if isinstance(it, str):
                                    vids.append(it)
                                elif isinstance(it, dict):
                                    vids.append(it.get("filename", it))
                print(f"[{name}] ✅ {time.time()-t0:.0f}s -> {vids}")
                return vids
            if status.get("status_str") in ("error", "failed") or h.get("status", {}).get("messages"):
                msgs = [m for m in h.get("status", {}).get("messages", []) if m and m[0] in ("execution_error", "execution_interrupted")]
                print(f"[{name}] ❌ {msgs}")
                return None
        time.sleep(3)


def main():
    import safetensors
    recover = "--baseline" not in sys.argv
    if recover:
        for src, prefix, do_trim, name in CASES:
            p = os.path.join(OUTPUT_DIR, src + ".safetensors")
            if not os.path.isfile(p):
                print(f"[{name}] 缺 latent {p}")
                continue
            tag = os.path.basename(src)
            pairs = to_std_latent(p, "h3_mc_recover", tag)
            wf = build_decode_wf(pairs[0][1], pairs[1][1], prefix, do_trim)
            submit(wf, name)
    if "--baseline" in sys.argv:
        print("重跑 same_seg2_baseline（151s）...")
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        import h3_mc_runner as runner
        cases = json.load(open(os.path.join(os.path.dirname(__file__), "..",
                                            "experiments/mc_test/mc_same_cases.json")))
        c = [x for x in cases["cases"] if x["name"] == "same_seg2_baseline"][0]
        wf = runner.build_wf(c)
        r = runner.api("/prompt", {"prompt": wf})
        print("已提交", r["prompt_id"])


if __name__ == "__main__":
    main()
