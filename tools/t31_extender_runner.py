#!/usr/bin/env python3
"""Submit the smallest T31 H3 Extender validation run to ComfyUI.

This intentionally uses only local assets and one five-second clip.  It is an
API-format workflow, so it does not depend on the browser's UI serialization.
"""
from __future__ import annotations

import json
import time
import urllib.request
import urllib.error
from pathlib import Path


API = "http://127.0.0.1:8188"
DRIVER_AUDIO = "T31_audio_driver_20260907.wav"
IMAGE = "T31_audio_ref.png"
PROMPT = """subject_definitions:
<Picture 1> defines the exact identity, face, hairstyle, clothing and appearance of <Subject 1>.
<Audio 1> provides the dialogue, speech timing and expressive rhythm.

summary:
<Subject 1> presents the narration naturally to camera while preserving the identity and studio scene from <Picture 1>, synchronized to <Audio 1>.

retention_analysis:
<Picture 1>: fully_preserved - keep the same face, hair, clothing, proportions and identity throughout.
<Audio 1>: attribute_transfer - follow its speech timing, pauses and expressive rhythm for accurate lip synchronization.

detailed_description:
Photorealistic continuous presenter video. The subject speaks naturally to camera with stable identity, clothing, studio scene and framing from <Picture 1>, synchronized to <Audio 1>. Keep the scene and character consistent across all continuation segments.

overall_soundscape:
Preserve the timing and natural sound character of <Audio 1>.

non_diegetic_music:
N/A"""


def post(path: str, payload: dict) -> dict:
    req = urllib.request.Request(
        API + path,
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            return json.loads(response.read())
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", "replace")
        raise RuntimeError(f"ComfyUI {path} returned HTTP {exc.code}: {detail}") from exc


def workflow(validated_count: int = 0) -> dict:
    clips = {
        "version": 1,
        "clips": [{
            "id": f"t31_a24_clip_{i}",
            "name": f"T31 audio-only Ref2VA MC audio-context-24 clip {i}",
            "prompt": PROMPT + (f"\n\nThis is continuation segment {i} of 4. Continue naturally from the previous segment." if i > 1 else ""),
            "seed": 310907 + i - 1,
            "seed_mode": "fixed",
            "duration": 5.0,
            "validated": i <= validated_count,
            "color_adjustment": {"saturation": 100, "contrast": 100, "brightness": 100},
        } for i in range(1, 5)],
    }
    refs = {"version": 2, "refs": [None] * 9}
    return {
        "1": {"class_type": "UNETLoader", "inputs": {
            "unet_name": "minimax_h3_ref2va_pruned_int8_convrot.safetensors",
            "weight_dtype": "default",
        }},
        "2": {"class_type": "CLIPLoader", "inputs": {
            "clip_name": "qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors",
            "type": "minimax", "device": "default",
        }},
        "3": {"class_type": "VAELoader", "inputs": {"vae_name": "minimax_h3_video_vae_fp16.safetensors"}},
        "4": {"class_type": "VAELoader", "inputs": {"vae_name": "minimax_h3_audio_vae_fp32.safetensors"}},
        "5": {"class_type": "LoraLoaderModelOnly", "inputs": {
            "model": ["1", 0],
            "lora_name": "minimax_h3_ref2v_turbo_4step_v0.1_comfyui_bf16.safetensors",
            "strength_model": 0.95,
        }},
        "6": {"class_type": "LoadImage", "inputs": {"image": IMAGE}},
        "7": {"class_type": "LoadAudio", "inputs": {"audio": DRIVER_AUDIO}},
        "8": {"class_type": "MiniMaxH3ReferencePackBridge", "inputs": {"ref_1": ["6", 0]}},
        "91": {"class_type": "MiniMaxH3Extender", "inputs": {
            "model": ["5", 0], "clip": ["2", 0], "vae": ["3", 0], "audio_vae": ["4", 0],
            "ref_audio_1": ["7", 0], "ref_pack": ["8", 0],
            "run_mode": "clip_by_clip", "width": 768, "height": 512, "ref_image_size": "match",
            "steps": 4, "sampler_name": "euler", "scheduler": "simple", "denoise": 1.0,
            "context_length": "22", "audio_context_length": 24,
            "clips_json": json.dumps(clips, ensure_ascii=False),
            "resolution_mode": "auto_from_ref", "megapixels": 0.4,
            "refs_json": json.dumps(refs), "generation_mode": "ref2va",
        }},
        "10": {"class_type": "MiniMaxH3MotionContextDiskFinalDecode", "inputs": {
            "cache": ["91", 0], "vae": ["3", 0], "audio_vae": ["4", 0],
            "fps": 24.0, "filename_prefix": "extender_audio_only_clip_by_clip_a24_chain4", "output_directory": "/home/sean/projects/ComfyUI/output/video/T31",
            "codec": "H.264", "crf": 17, "preset": "fast", "audio_bitrate": "192k", "autoplay": True,
        }},
    }


def main() -> None:
    for validated_count in range(4):
        info = post("/prompt", {"prompt": workflow(validated_count), "client_id": "T-comfy-ops-31-clip-by-clip"})
        prompt_id = info["prompt_id"]
        print(json.dumps({"prompt_id": prompt_id, "status": "queued", "validated_before": validated_count}, ensure_ascii=False), flush=True)
        deadline = time.time() + 900
        while time.time() < deadline:
            req = urllib.request.Request(API + f"/history/{prompt_id}")
            with urllib.request.urlopen(req, timeout=30) as response:
                history = json.loads(response.read())
            if prompt_id in history:
                item = history[prompt_id]
                status = item.get("status", {})
                if status.get("completed"):
                    print(json.dumps({"prompt_id": prompt_id, "status": "completed", "clip_step": validated_count + 1, "outputs": item.get("outputs", {})}, ensure_ascii=False), flush=True)
                    break
                if status.get("status_str") == "error" or status.get("messages", []) and any(m[0] == "execution_error" for m in status["messages"]):
                    print(json.dumps({"prompt_id": prompt_id, "status": "error", "details": status}, ensure_ascii=False), flush=True)
                    raise SystemExit(2)
            time.sleep(5)
        else:
            raise SystemExit(f"timeout waiting for {prompt_id}")


if __name__ == "__main__":
    main()
