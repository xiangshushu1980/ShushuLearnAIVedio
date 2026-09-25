#!/usr/bin/env python3
"""Export H3 FaceTrackCrop preview without running H3 sampling."""
from __future__ import annotations

import argparse
import json
import time
import urllib.request

API = "http://127.0.0.1:8188"


def api(path: str, payload: dict | None = None):
    req = urllib.request.Request(API + path)
    if payload is not None:
        req = urllib.request.Request(API + path, data=json.dumps(payload).encode(),
                                     headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--video", required=True)
    p.add_argument("--identity", required=True)
    p.add_argument("--face-index", type=int, default=0)
    p.add_argument("--out-prefix", required=True)
    args = p.parse_args()
    graph = {
        "sel": {"class_type": "H3FaceSelect", "inputs": {
            "video": args.video, "detector": "face_yolov8m.pt",
            "confidence": 0.25, "select": "largest_face",
            "select_index": args.face_index, "confirmed_pick": "",
            "cut_detection": "none", "cut_threshold": 3.0,
            "skip_first_frames": 0, "frame_load_cap": 124,
            "select_every_nth": 1, "identity_reference": ["id", 0],
            "identity_model": "insightface", "identity_threshold": 0.20,
        }},
        "id": {"class_type": "LoadImage", "inputs": {"image": args.identity}},
        "crop": {"class_type": "H3FaceTrackCrop", "inputs": {
            "images": ["sel", 0], "detector": "face_yolov8m.pt",
            "confidence": 0.25, "crop_factor": 3.0,
            "canvas_width": 768, "canvas_height": 768,
            "canvas_mode": "manual", "smooth_window": 21,
            "size_smooth_window": 51, "smooth_method": "gaussian",
            "size_mode": "per_frame", "identity_reference": ["id", 0],
            "identity_track": False, "identity_threshold": 0.20,
            "select": "largest_face", "fallback_detector": "none",
            "fallback_head_frac": 0.5, "select_index": args.face_index,
            "identity_model": "insightface", "cut_detection": "none",
            "cut_threshold": 3.0, "absent_shots": "off", "X": 0, "Y": 0,
            "frame_index": 0, "face_pick": ["sel", 2],
        }},
        "video": {"class_type": "CreateVideo", "inputs": {
            "images": ["crop", 2], "fps": 24.0, "audio": ["sel", 1],
            "bit_depth": 8, "codec": "none",
        }},
        "save": {"class_type": "SaveVideo", "inputs": {
            "video": ["video", 0], "filename_prefix": args.out_prefix,
            "format": "mp4", "codec": "auto",
        }},
    }
    q = api("/prompt", {"prompt": graph, "client_id": "h3-face-preview"})
    pid = q["prompt_id"]
    print(json.dumps({"prompt_id": pid}), flush=True)
    started = time.time()
    while time.time() - started < 600:
        time.sleep(3)
        h = api("/history/" + pid)
        if pid in h:
            st = h[pid].get("status", {}).get("status_str")
            print(json.dumps({"prompt_id": pid, "status": st,
                              "elapsed_s": round(time.time() - started, 1),
                              "outputs": h[pid].get("outputs", {})}), flush=True)
            return 0 if st != "error" else 1
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
