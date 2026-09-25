#!/usr/bin/env python3
"""T37 Krea2 Identity Edit runner with three evidence-based modes."""

import argparse
import json
import os
import time
import urllib.request

from krea2_prompt_profiles import PROMPT_VERSION, get_prompt


API = "http://127.0.0.1:8188"


def api(path, payload=None):
    data = None if payload is None else json.dumps(payload).encode()
    req = urllib.request.Request(
        API + path,
        data=data,
        headers={"Content-Type": "application/json"} if data else {},
    )
    with urllib.request.urlopen(req, timeout=30) as response:
        return json.loads(response.read())


def graph(args):
    ref = args.reference
    prompt = get_prompt(args.mode, args.remove_item)
    if args.mode == "identity_portrait":
        model = "id_model"
    elif args.mode == "identity_remove":
        model = "id_model"
    elif args.mode == "jibs_style_portrait":
        model = "jibs_model"
    elif args.mode in ("tear_mark_face", "front_reference", "back_reference", "three_quarter_reference"):
        model = "id_model"
    else:
        raise ValueError(f"unknown mode: {args.mode}")

    return {
        "unet": {
            "class_type": "UNETLoader",
            "inputs": {"unet_name": args.unet_name, "weight_dtype": "default"},
        },
        "clip": {
            "class_type": "CLIPLoader",
            "inputs": {"clip_name": "qwen3vl_4b_fp8_scaled.safetensors", "type": "krea2"},
        },
        "vae": {
            "class_type": "VAELoader",
            "inputs": {"vae_name": "qwen_image_vae.safetensors"},
        },
        "id_model": {
            "class_type": "LoraLoaderModelOnly",
            "inputs": {
                "model": ["unet", 0],
                "lora_name": "krea2_identity_edit_v1_2.safetensors",
                "strength_model": 1.0,
            },
        },
        "jibs_model": {
            "class_type": "LoraLoaderModelOnly",
            "inputs": {
                "model": ["id_model", 0],
                "lora_name": "Jibs_Krea_2_Midjourney_Fantasy_Style_V1.safetensors",
                "strength_model": args.jibs_strength,
            },
        },
        "ref": {"class_type": "LoadImage", "inputs": {"image": ref}},
        "ref_latent": {
            "class_type": "VAEEncode",
            "inputs": {"pixels": ["ref", 0], "vae": ["vae", 0]},
        },
        "target": {
            "class_type": "EmptySD3LatentImage",
            "inputs": {"width": args.width, "height": args.height, "batch_size": 1},
        },
        "positive": {
            "class_type": "Krea2EditGroundedEncode",
            "inputs": {
                "clip": ["clip", 0],
                "prompt": prompt,
                "image": ["ref", 0],
                "grounding_px": 768,
                "system_prompt": "",
            },
        },
        "negative": {
            "class_type": "Krea2EditGroundedEncode",
            "inputs": {
                "clip": ["clip", 0],
                # Community workflow uses the same reference image with an empty
                # prompt as the trained unconditional branch.
                "prompt": "",
                "image": ["ref", 0],
                "grounding_px": args.grounding_px,
                "system_prompt": "",
            },
        },
        "patch": {
            "class_type": "Krea2EditModelPatch",
            "inputs": {
                "model": [model, 0],
                "source_latent": ["ref_latent", 0],
                "vae": ["vae", 0],
                "source_image": ["ref", 0],
                "target_latent": ["target", 0],
                "ref_boost": args.ref_boost,
                "ref_boost_a": 1.0,
                "fit_mode": "fit",
            },
        },
        "sample": {
            "class_type": "KSampler",
            "inputs": {
                "model": ["patch", 0],
                "positive": ["positive", 0],
                "negative": ["negative", 0],
                "latent_image": ["target", 0],
                "seed": args.seed,
                "control_after_generate": "fixed",
                "steps": args.steps,
                "cfg": args.cfg,
                "sampler_name": "euler",
                "scheduler": "simple",
                "denoise": 1.0,
            },
        },
        "decode": {
            "class_type": "VAEDecode",
            "inputs": {"samples": ["sample", 0], "vae": ["vae", 0]},
        },
        "save": {
            "class_type": "SaveImage",
            "inputs": {"images": ["decode", 0], "filename_prefix": args.prefix},
        },
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--reference", default="ref2va_refs/fellow/processed/shushu_identity_rebuilt_v2_cap.png")
    parser.add_argument(
        "--mode",
        choices=("identity_portrait", "identity_remove", "jibs_style_portrait", "tear_mark_face", "front_reference", "back_reference", "three_quarter_reference"),
        default="identity_portrait",
        help="Evidence-based Krea2 task mode",
    )
    parser.add_argument("--unet-name", default="krea2_turbo_fp8.safetensors")
    parser.add_argument("--jibs-strength", type=float, default=1.0)
    parser.add_argument("--ref-boost", type=float, default=4.0)
    parser.add_argument("--grounding-px", type=int, default=1024)
    parser.add_argument("--remove-item", default="eyeglasses and all eyewear")
    parser.add_argument("--steps", type=int, default=None)
    parser.add_argument("--cfg", type=float, default=None)
    parser.add_argument("--width", type=int, default=1024)
    parser.add_argument("--height", type=int, default=1024)
    parser.add_argument("--seed", type=int, default=20260920)
    parser.add_argument("--prefix", default="T37_krea2_identity")
    parser.add_argument("--timeout", type=int, default=900)
    args = parser.parse_args()

    if args.mode == "identity_remove":
        if args.unet_name == "krea2_turbo_fp8.safetensors":
            args.unet_name = "krea2_raw_fp8_scaled.safetensors"
        if args.steps is None:
            args.steps = 20
        if args.cfg is None:
            args.cfg = 3.0
    else:
        if args.steps is None:
            args.steps = 10
        if args.cfg is None:
            args.cfg = 1.0
    if args.mode not in ("jibs_style_portrait",):
        args.jibs_strength = 0.0
    if args.mode == "identity_remove" and "turbo" in args.unet_name.lower():
        raise SystemExit("identity_remove requires a Raw Krea2 UNET; pass --unet-name <Raw checkpoint>")
    if args.mode == "identity_remove":
        model_path = os.path.join(
            "/home/sean/projects/ComfyUI/models/diffusion_models", args.unet_name
        )
        if not os.path.isfile(model_path):
            raise SystemExit(
                f"identity_remove requires a local Raw Krea2 UNET, not found: {model_path}"
            )

    queued = api("/prompt", {"prompt": graph(args), "client_id": "t37-krea2-identity"})
    prompt_id = queued["prompt_id"]
    started = time.time()
    print(json.dumps({
        "prompt_id": prompt_id,
        "prompt_version": PROMPT_VERSION,
        "mode": args.mode,
        "unet": args.unet_name,
        "jibs_strength": args.jibs_strength,
        "steps": args.steps,
        "cfg": args.cfg,
        "ref_boost": args.ref_boost,
        "grounding_px": args.grounding_px,
    }), flush=True)
    while time.time() - started < args.timeout:
        history = api("/history/" + prompt_id)
        if prompt_id in history:
            record = history[prompt_id]
            status = record.get("status", {})
            print(json.dumps({
                "prompt_id": prompt_id,
                "status": status.get("status_str"),
                "completed": status.get("completed"),
                "outputs": record.get("outputs", {}),
            }), flush=True)
            return 0 if status.get("status_str") == "success" else 1
        time.sleep(3)
    print(json.dumps({"prompt_id": prompt_id, "status": "timeout"}), flush=True)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
