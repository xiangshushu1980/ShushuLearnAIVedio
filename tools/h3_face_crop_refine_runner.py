#!/usr/bin/env python3
"""Single-subject H3 FaceRefine crop -> resample -> stitch test."""

from __future__ import annotations

import argparse
import json
import time
import urllib.error
import urllib.request


API = "http://127.0.0.1:8188"


def api(path: str, payload: dict | None = None):
    request = urllib.request.Request(API + path)
    if payload is not None:
        request = urllib.request.Request(
            API + path, data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.load(response)
    except urllib.error.HTTPError as error:
        raise RuntimeError(error.read().decode("utf-8", errors="replace")) from error


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--video", required=True)
    p.add_argument("--identity", required=True)
    p.add_argument("--h3-reference", default=None,
                   help="Optional separate H3 object/reference image. If omitted, --identity is also used for H3.")
    p.add_argument("--identity-model", choices=["insightface", "clip_vision", "ccip"],
                   default="insightface")
    p.add_argument("--identity-threshold", type=float, default=0.20,
                   help="Identity match threshold; ClipVision generally needs a higher value (about 0.80)")
    p.add_argument("--clip-vision", default="clip_vision_h.safetensors")
    p.add_argument("--detector", default="face_yolov8m.pt",
                   help="Detector model; person_yolov8m-seg.pt enables the separate whole-person experiment")
    p.add_argument("--prompt", required=True)
    p.add_argument("--canvas", type=int, default=512)
    p.add_argument("--canvas-width", type=int, default=None)
    p.add_argument("--canvas-height", type=int, default=None)
    p.add_argument("--length", type=int, default=124,
                   help="Number of source frames to process; 124=5.17s, 241=10s at 24fps")
    p.add_argument("--crop-factor", type=float, default=2.0)
    p.add_argument("--denoise", type=float, default=0.25)
    p.add_argument("--steps", type=int, default=20)
    p.add_argument("--seed", type=int, default=20260920)
    p.add_argument("--out-prefix", default="face_solution/face_crop_refine")
    p.add_argument("--tracking-preview-prefix", default=None,
                   help="Optional output prefix for a marked tracking preview. Green=face "
                        "detected, yellow=body fallback, red=interpolated/dropout.")
    p.add_argument("--fast-detect", action="store_true",
                   help="Use largest-face YOLO tracking without per-frame InsightFace matching")
    p.add_argument("--face-index", type=int, default=0,
                   help="Ranked face to select in fast mode; 0 is largest, 1 is second-largest")
    p.add_argument("--per-frame-denoise", action="store_true",
                   help="Scale denoise by source face size and smooth it over time")
    p.add_argument("--small-face-mult", type=float, default=1.0)
    p.add_argument("--large-face-mult", type=float, default=0.35)
    p.add_argument("--face-px-small", type=float, default=30.0)
    p.add_argument("--face-px-large", type=float, default=120.0)
    p.add_argument("--denoise-gamma", type=float, default=1.0)
    p.add_argument("--smooth-frames", type=int, default=9)
    p.add_argument("--paste-region", choices=["face_only", "face_ellipse", "full_crop"],
                   default="face_only",
                   help="Paste region; with a person detector, face_only means the detected person box")
    p.add_argument("--person-mask", action="store_true",
                   help="Generate a per-frame person segmentation mask on the tracked crop and use it for stitching")
    p.add_argument("--undetected-frames", choices=["fade_out", "skip", "composite_anyway"],
                   default="fade_out",
                   help="How to stitch frames where the face tracker has no detection; skip preserves original pixels")
    p.add_argument("--vosr2-upscale", type=int, choices=[1, 2, 3, 4], default=0,
                   help="Apply VOSR 2.0 to each refined crop before stitching; output is resized back to the crop canvas")
    p.add_argument("--vosr2-seed", type=int, default=42)
    p.add_argument("--report-only", action="store_true",
                   help="Run face selection/tracking only and print per-frame threshold diagnostics; no H3 sampling")
    p.add_argument("--report-max-rows", type=int, default=400)
    p.add_argument("--analysis-report-prefix", default=None,
                   help="When set, save the pre-analysis selection and transform reports as text files")
    p.add_argument("--analysis-manifest-prefix", default=None,
                   help="When set, save a reusable JSON face-analysis manifest")
    p.add_argument("--analysis-manifest", default=None,
                   help="Reuse a saved JSON face-analysis manifest; skips face detection and identity selection")
    p.add_argument("--refine-start-px", type=float, default=70.0,
                   help="Source face height at which the manifest enables refine")
    p.add_argument("--timeout", type=int, default=1200)
    args = p.parse_args()

    canvas_width = args.canvas_width or args.canvas
    canvas_height = args.canvas_height or args.canvas

    h3_reference = args.h3_reference or args.identity
    graph = {
        "sel": {"class_type": "H3FaceSelect", "inputs": {
            "video": args.video,
            "detector": args.detector,
            "confidence": 0.25,
            "select": "largest_face" if args.fast_detect else "identity_reference",
            "select_index": args.face_index,
            "confirmed_pick": "",
            "cut_detection": "none",
            "cut_threshold": 3.0,
            "skip_first_frames": 0,
            "frame_load_cap": args.length,
            "select_every_nth": 1,
            "identity_reference": ["id", 0],
            "identity_model": args.identity_model,
            "identity_threshold": args.identity_threshold,
        }},
        "transform_info": {"class_type": "H3FaceTransformInfo", "inputs": {
            "transform": ["crop", 1], "max_rows": args.report_max_rows,
        }},
        "id": {"class_type": "LoadImage", "inputs": {"image": args.identity}},
        "h3id": {"class_type": "LoadImage", "inputs": {"image": h3_reference}},
        "crop": {"class_type": "H3FaceTrackCrop", "inputs": {
            "images": ["sel", 0],
            "detector": args.detector,
            "confidence": 0.25,
            "crop_factor": args.crop_factor,
            "canvas_width": canvas_width,
            "canvas_height": canvas_height,
            "canvas_mode": "manual",
            "smooth_window": 21,
            "size_smooth_window": 51,
            "smooth_method": "gaussian",
            "size_mode": "per_frame",
            "identity_reference": ["id", 0],
            "identity_track": False if args.analysis_manifest else not args.fast_detect,
            "identity_threshold": args.identity_threshold,
            "select": "largest_face",
            "fallback_detector": "none",
            "fallback_head_frac": 0.5,
            "select_index": args.face_index,
            "identity_model": args.identity_model,
            "cut_detection": "none",
            "cut_threshold": 3.0,
            "absent_shots": "off",
            "X": 0, "Y": 0, "frame_index": 0,
            "face_pick": ["sel", 2],
        }},
        "u": {"class_type": "UNETLoader", "inputs": {
            "unet_name": "minimax_h3_ref2va_pruned_int8_convrot.safetensors",
            "weight_dtype": "default",
        }},
        "c": {"class_type": "CLIPLoader", "inputs": {
            "clip_name": "qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors",
            "type": "minimax", "device": "default",
        }},
        "v": {"class_type": "VAELoader", "inputs": {
            "vae_name": "minimax_h3_video_vae_fp16.safetensors",
        }},
        "av": {"class_type": "VAELoader", "inputs": {
            "vae_name": "minimax_h3_audio_vae_fp32.safetensors",
        }},
        "cond": {"class_type": "MiniMaxH3ReferenceToVideo", "inputs": {
            "clip": ["c", 0], "vae": ["v", 0], "audio_vae": ["av", 0],
            "prompt": open(args.prompt, encoding="utf-8").read(),
            "width": canvas_width, "height": canvas_height, "length": args.length,
            "ref_image_size": "max", "ref_images.ref_image_0": ["h3id", 0],
        }},
        "inject": {"class_type": "H3InjectVideoLatent", "inputs": {
            "av_latent": ["cond", 1], "images": ["crop", 0], "vae": ["v", 0],
        }},
        "sampler": {"class_type": "KSamplerSelect", "inputs": {"sampler_name": "res_multistep"}},
        "sched": {"class_type": "BasicScheduler", "inputs": {
            "model": ["u", 0], "scheduler": "simple",
            "steps": args.steps, "denoise": args.denoise,
        }},
        "guide": {"class_type": "BasicGuider", "inputs": {"model": ["u", 0], "conditioning": ["cond", 0]}},
        "noise": {"class_type": "RandomNoise", "inputs": {"noise_seed": args.seed}},
        "sample": {"class_type": "SamplerCustomAdvanced", "inputs": {
            "noise": ["noise", 0], "guider": ["guide", 0], "sampler": ["sampler", 0],
            "sigmas": ["sched", 0], "latent_image": ["inject", 0],
        }},
        "decode": {"class_type": "VAEDecode", "inputs": {"samples": ["sample", 0], "vae": ["v", 0]}},
        "stitch": {"class_type": "H3FaceStitch", "inputs": {
            "base_images": ["sel", 0], "refined_crops": ["decode", 0],
            "transform": ["crop", 1], "paste_region": args.paste_region,
            "mask_dilation": 16, "feather": 6, "colour_match": 1.0,
            "blend": 1.0, "undetected_frames": args.undetected_frames,
            "feather_scales_with_crop": False,
        }},
        "video": {"class_type": "CreateVideo", "inputs": {
            "images": ["stitch", 0], "fps": 24.0, "audio": ["sel", 1],
            "bit_depth": 8, "codec": "none",
        }},
        "save": {"class_type": "SaveVideo", "inputs": {
            "video": ["video", 0], "filename_prefix": args.out_prefix,
            "format": "mp4", "codec": "auto",
        }},
    }
    if args.analysis_manifest:
        graph["sel"]["inputs"]["analysis_manifest"] = args.analysis_manifest
    if args.report_only:
        # H3FaceTransformInfo is the only output node on this path. ComfyUI will
        # therefore execute selection + tracking but will not load H3 or sample.
        graph = {k: graph[k] for k in ("sel", "id", "crop", "transform_info")}
        if args.analysis_report_prefix:
            # KJNodes persists STRING outputs under ComfyUI/output. Keeping the
            # reports as files makes report-only analysis reusable and auditable;
            # the report node itself is not a video preview or an H3 generation.
            graph["save_selection_report"] = {"class_type": "SaveStringKJ", "inputs": {
                "string": ["sel", 4],
                "output_folder": "face_solution/analysis",
                "filename_prefix": args.analysis_report_prefix + "_selection",
                "file_extension": ".txt",
            }}
            graph["save_transform_report"] = {"class_type": "SaveStringKJ", "inputs": {
                "string": ["transform_info", 0],
                "output_folder": "face_solution/analysis",
                "filename_prefix": args.analysis_report_prefix + "_transform",
                "file_extension": ".txt",
            }}
        if args.analysis_manifest_prefix:
            graph["save_analysis_manifest"] = {"class_type": "H3FaceManifestSave", "inputs": {
                "face_pick": ["sel", 2],
                "transform": ["crop", 1],
                "source_video": args.video,
                "identity_model": args.identity_model,
                "identity_threshold": args.identity_threshold,
                "refine_start_px": args.refine_start_px,
                "filename_prefix": args.analysis_manifest_prefix,
            }}
    if args.vosr2_upscale:
        graph["vosr2_model"] = {"class_type": "VOSR2ModelLoader", "inputs": {
            "model": "VOSR2", "dtype": "default",
        }}
        graph["vosr2"] = {"class_type": "VOSR2Upscale", "inputs": {
            "model": ["vosr2_model", 0], "image": ["decode", 0],
            "upscale": args.vosr2_upscale, "seed": args.vosr2_seed,
            "color_alignment": "wavelet", "tile_size": 512,
            "tile_overlap": 64, "vae_tile_size": 1024,
            "vae_tile_overlap": 128,
        }}
        graph["vosr2_resize"] = {"class_type": "ImageScale", "inputs": {
            "image": ["vosr2", 0], "upscale_method": "lanczos",
            "width": canvas_width, "height": canvas_height,
            "crop": "disabled",
        }}
        graph["stitch"]["inputs"]["refined_crops"] = ["vosr2_resize", 0]
    if args.person_mask:
        graph["person_mask"] = {"class_type": "AILab_YoloV8Adv", "inputs": {
            "images": ["crop", 0],
            "yolo_model": "segm/person_yolov8m-seg.pt",
            "mask_count": "1",
            "classes": "0",
        }}
        graph["stitch"]["inputs"]["masks"] = ["person_mask", 1]
        if args.tracking_preview_prefix:
            graph["mask_preview_video"] = {"class_type": "CreateVideo", "inputs": {
                "images": ["person_mask", 0], "fps": 24.0,
                "bit_depth": 8, "codec": "none",
            }}
            graph["mask_preview_save"] = {"class_type": "SaveVideo", "inputs": {
                "video": ["mask_preview_video", 0],
                "filename_prefix": args.tracking_preview_prefix + "_mask_overlay",
                "format": "mp4", "codec": "auto",
            }}
    if args.tracking_preview_prefix:
        graph["preview_video"] = {"class_type": "CreateVideo", "inputs": {
            "images": ["crop", 2], "fps": 24.0, "audio": ["sel", 1],
            "bit_depth": 8, "codec": "none",
        }}
        graph["preview_save"] = {"class_type": "SaveVideo", "inputs": {
            "video": ["preview_video", 0],
            "filename_prefix": args.tracking_preview_prefix,
            "format": "mp4", "codec": "auto",
        }}
    if args.identity_model == "clip_vision":
        graph["cv"] = {"class_type": "CLIPVisionLoader", "inputs": {
            "clip_name": args.clip_vision,
        }}
        graph["sel"]["inputs"]["identity_clip_vision"] = ["cv", 0]
        graph["crop"]["inputs"]["identity_clip_vision"] = ["cv", 0]
    if args.per_frame_denoise:
        graph["pf"] = {"class_type": "H3PerFrameDenoise", "inputs": {
            "model": ["u", 0], "av_latent": ["inject", 0],
            "transform": ["crop", 1],
            "denoise_multiplier_small_face": args.small_face_mult,
            "denoise_multiplier_large_face": args.large_face_mult,
            "scale_mode": "absolute_px",
            "face_px_small": args.face_px_small,
            "face_px_large": args.face_px_large,
            "gamma": args.denoise_gamma,
            "smooth_frames": args.smooth_frames,
        }}
        graph["sched"]["inputs"]["model"] = ["pf", 2]
        graph["guide"]["inputs"]["model"] = ["pf", 2]
        graph["sample"]["inputs"]["latent_image"] = ["pf", 0]
    queued = api("/prompt", {"prompt": graph, "client_id": "h3-face-crop-refine"})
    prompt_id = queued["prompt_id"]
    print(json.dumps({"prompt_id": prompt_id, "canvas": [canvas_width, canvas_height],
                      "crop_factor": args.crop_factor, "denoise": args.denoise,
                      "per_frame_denoise": args.per_frame_denoise}), flush=True)
    started = time.time()
    while time.time() - started < args.timeout:
        time.sleep(5)
        history = api("/history/" + prompt_id)
        if prompt_id not in history:
            continue
        record = history[prompt_id]
        status = record.get("status", {})
        print(json.dumps({"prompt_id": prompt_id, "status": status.get("status_str"),
                          "elapsed_s": round(time.time() - started, 1),
                          "outputs": record.get("outputs", {})}, ensure_ascii=False), flush=True)
        return 0 if status.get("status_str") != "error" else 1
    print(json.dumps({"prompt_id": prompt_id, "status": "timeout"}), flush=True)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
