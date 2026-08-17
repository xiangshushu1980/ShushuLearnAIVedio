#!/usr/bin/env python3
"""P1 视频级实测：FL2VA 单镜 vs 多镜 AB + T8 案例锚点 AB（T-comfy-ops-03）
- FL2VA：2 组首尾帧素材 × {单镜, 多镜}，同 seed 同参数（8 步 turbo, 960×544, 5s）
- T8 锚点：净水器广告 T2V 8s {基础版, 锚点版}
用法：python3 scripts/h3_promptor_p1.py [--submit] [--dry-run]
"""
import argparse, json, time, urllib.request
from pathlib import Path

HOST = "http://127.0.0.1:8188"
CLIP = "qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors"
LORA = "minimax_h3_turbo_4step_ema_ckpt850_pruned_comfyui.safetensors"
UNET = "minimax_h3_fl2va_pruned_fp8_scaled.safetensors"
SEED = 20260817
PREFIX = "video/h3_promptor_p1"

# ---------------- 提示词（17 号规则风格，英文） ----------------

P_FL2VA_ALYA_SINGLE = """How the reference pictures align with the target video — Picture 1 (from Shot 1) aligns with the 0.00-second mark of the target video; Picture 2 (from Shot 1) aligns with the 5.00-second mark of the target video.

integrated_multimodal_description: [Shot 1] Live-action, cinematic, a single continuous shot. The young woman with short black hair in the red dress, exactly as shown in <Picture 1>, stands in the warm sunlit room, preserving her appearance, clothing, and spatial position. The camera pushes in with small amplitude at slow speed as she turns her head toward the camera, lifts her gaze, and shifts her posture through fluid intermediate motion, finally settling into the exact pose, angle, and composition established by <Picture 2>.

overall_soundscape: Soft fabric rustle as she turns, beneath gentle room ambience.

non_diegetic_music: N/A"""

P_FL2VA_ALYA_MULTI = """How the reference pictures align with the target video — Picture 1 (from Shot 1) aligns with the 0.00-second mark of the target video; Picture 2 (from Shot 2) aligns with the 5.00-second mark of the target video.

integrated_multimodal_description: [Shot 1] Live-action, cinematic, the young woman with short black hair in the red dress, exactly as shown in <Picture 1>, stands in the warm sunlit room, preserving her appearance, clothing, and spatial position. The camera holds a static shot as she begins to turn her head toward the camera.
[Shot 2] At 00:02.500, the camera cuts to a closer angle as she completes the turn, lifts her gaze, and settles into the exact pose, angle, and composition established by <Picture 2>.

overall_soundscape: Soft fabric rustle as she turns, beneath gentle room ambience.

non_diegetic_music: N/A"""

P_FL2VA_2P_SINGLE = """How the reference pictures align with the target video — Picture 1 (from Shot 1) aligns with the 0.00-second mark of the target video; Picture 2 (from Shot 1) aligns with the 5.00-second mark of the target video.

integrated_multimodal_description: [Shot 1] Live-action, cinematic, a single continuous shot. Two young people, the man in a dark jacket and the woman in a light top, stand separated as shown in <Picture 1>, preserving their appearance, positions, and the interior space. The camera trucks right with small amplitude at slow speed as both turn toward each other, step closer, and settle into the face-to-face conversation pose and composition established by <Picture 2>.

overall_soundscape: Quiet indoor ambience with two light footsteps as they step closer.

non_diegetic_music: N/A"""

P_FL2VA_2P_MULTI = """How the reference pictures align with the target video — Picture 1 (from Shot 1) aligns with the 0.00-second mark of the target video; Picture 2 (from Shot 2) aligns with the 5.00-second mark of the target video.

integrated_multimodal_description: [Shot 1] Live-action, cinematic, two young people, the man in a dark jacket and the woman in a light top, stand separated as shown in <Picture 1>, preserving their appearance, positions, and the interior space. The camera holds a static shot as they begin to turn toward each other.
[Shot 2] At 00:02.500, the camera cuts to a medium shot as both step closer and settle into the face-to-face conversation pose and composition established by <Picture 2>.

overall_soundscape: Quiet indoor ambience with two light footsteps as they step closer.

non_diegetic_music: N/A"""

P_T8_BASE = """integrated_multimodal_description: [Shot 1] Live-action, cinematic, a portable water purifier bottle in matte white and blue stands on a wooden table beside a mountain stream. The camera slowly pushes in, showing the bottle's smooth surface, the clear plastic window, and the filter cap, with soft daylight and green forest bokeh in the background.

overall_soundscape: Gentle stream water flowing, light birdsong in the distance.

non_diegetic_music: N/A"""

P_T8_ANCHOR = """integrated_multimodal_description: [Shot 1] Live-action, cinematic, a hiker drinks clean clear water from the portable purifier bottle and smiles with relief, the visible result of the product. [Shot 2] At 00:02.000, the camera cuts to a macro shot of the bottle's filter cross-section, showing layered white and blue filter membranes, as a visible proof state. [Shot 3] At 00:04.000, the camera cuts to a wide shot of muddy brown stream water being poured into the bottle, then flowing out crystal clear into a glass, a second visible proof state. [Shot 4] At 00:06.000, the camera cuts to the hiker using the bottle at a campsite, refilling and drinking, then ends on a stable product close-up as the final proof and action.

overall_soundscape: Stream water flowing, pouring and dripping water sounds, light birdsong.

non_diegetic_music: N/A"""

# ---------------- 任务定义 ----------------

def fl2va_task(name, prompt, first, last, frames=120):
    return {"name": name, "prompt": prompt, "first": first, "last": last, "frames": frames}

def t2v_task(name, prompt, frames=192):
    return {"name": name, "prompt": prompt, "first": None, "last": None, "frames": frames}

TASKS = [
    fl2va_task("fl2va_alya_single", P_FL2VA_ALYA_SINGLE, "start/alya_169.png", "start/alya_1024.png"),
    fl2va_task("fl2va_alya_multi",  P_FL2VA_ALYA_MULTI,  "start/alya_169.png", "start/alya_1024.png"),
    fl2va_task("fl2va_2p_single",   P_FL2VA_2P_SINGLE,   "start/gen_2p_leftright.png", "start/gen_2p_talk.png"),
    fl2va_task("fl2va_2p_multi",    P_FL2VA_2P_MULTI,    "start/gen_2p_leftright.png", "start/gen_2p_talk.png"),
    t2v_task("t8_water_base",   P_T8_BASE),
    t2v_task("t8_water_anchor", P_T8_ANCHOR),
]

def build_wf(t):
    wf = {
        "1": {"class_type": "UNETLoader", "inputs": {"unet_name": UNET, "weight_dtype": "default"}},
        "2": {"class_type": "CLIPLoader", "inputs": {"clip_name": CLIP, "type": "minimax", "device": "default"}},
        "3": {"class_type": "VAELoader", "inputs": {"vae_name": "minimax_h3_video_vae_fp16.safetensors"}},
        "4": {"class_type": "VAELoader", "inputs": {"vae_name": "minimax_h3_audio_vae_fp32.safetensors"}},
        "90": {"class_type": "MiniMaxH3TurboLoRA", "inputs": {"model": ["1", 0], "lora_name": LORA, "strength": 1.0, "low_vram": False}},
        "7": {"class_type": "MiniMaxH3TurboSampler", "inputs": {}},
        "8": {"class_type": "BasicScheduler", "inputs": {"model": ["90", 0], "scheduler": "simple", "steps": 8, "denoise": 1}},
        "9": {"class_type": "BasicGuider", "inputs": {"model": ["90", 0], "conditioning": ["6", 0]}},
        "10": {"class_type": "RandomNoise", "inputs": {"noise_seed": SEED}},
        "11": {"class_type": "SamplerCustomAdvanced", "inputs": {"noise": ["10", 0], "guider": ["9", 0], "sampler": ["7", 0], "sigmas": ["8", 0], "latent_image": ["6", 1]}},
        "12": {"class_type": "VAEDecode", "inputs": {"samples": ["11", 0], "vae": ["3", 0]}},
        "13": {"class_type": "VAEDecodeAudio", "inputs": {"samples": ["11", 0], "vae": ["4", 0]}},
        "14": {"class_type": "CreateVideo", "inputs": {"images": ["12", 0], "fps": 24, "audio": ["13", 0], "bit_depth": 8}},
        "15": {"class_type": "SaveVideo", "inputs": {"video": ["14", 0], "filename_prefix": f"{PREFIX}/{t['name']}", "format": "mp4", "codec": "auto"}},
    }
    i6 = {"class_type": "MiniMaxH3ImageToVideo", "inputs": {
        "clip": ["2", 0], "vae": ["3", 0], "prompt": t["prompt"],
        "width": 960, "height": 544, "length": t["frames"]}}
    if t["first"]:
        i6["inputs"]["first_frame"] = ["5", 0]
        wf["5"] = {"class_type": "LoadImage", "inputs": {"image": t["first"]}}
    if t["last"]:
        i6["inputs"]["last_frame"] = ["5b", 0]
        wf["5b"] = {"class_type": "LoadImage", "inputs": {"image": t["last"]}}
    wf["6"] = i6
    return wf

def submit(wf):
    req = urllib.request.Request(f"{HOST}/prompt", data=json.dumps({"prompt": wf}).encode(),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)["prompt_id"]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--submit", action="store_true", help="真正提交（默认只打印）")
    ap.add_argument("--only", help="只跑指定任务名（逗号分隔）")
    args = ap.parse_args()
    names = [x.strip() for x in args.only.split(",")] if args.only else None
    for t in TASKS:
        if names and t["name"] not in names:
            continue
        wf = build_wf(t)
        if not args.submit:
            print(f"[dry] {t['name']}: frames={t['frames']} first={t['first']} last={t['last']} prompt_len={len(t['prompt'])}")
        else:
            pid = submit(wf)
            print(f"[ok]  {t['name']}: enqueued -> {pid}", flush=True)

if __name__ == "__main__":
    main()
