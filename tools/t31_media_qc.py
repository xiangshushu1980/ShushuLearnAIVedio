#!/usr/bin/env python3
"""Deterministic QC for T31 H3 audio-driven chains.

This is a screening tool, not a learned lip-sync judge.  It measures:
* audio/video duration and an audio-envelope vs mouth-motion lag proxy;
* face position/size stability and normalized face-crop similarity;
* frame-to-frame jumps at known MC seams and ordinary-motion baseline.

Run with ComfyUI's venv because it supplies cv2/scipy/skimage:
  /home/sean/projects/ComfyUI/venv/bin/python tools/t31_media_qc.py VIDEO [--out REPORT.json]
"""
from __future__ import annotations

import argparse
import json
import math
import subprocess
import tempfile
import wave
from pathlib import Path

import cv2
import numpy as np
from scipy.signal import correlate
from skimage.metrics import structural_similarity


def probe(path: str) -> dict:
    raw = subprocess.check_output([
        "ffprobe", "-v", "error", "-show_entries",
        "format=duration:stream=codec_type,width,height,r_frame_rate,sample_rate,channels",
        "-of", "json", path], text=True)
    return json.loads(raw)


def audio_wave(path: str, rate: int = 16000) -> tuple[np.ndarray, int]:
    with tempfile.NamedTemporaryFile(suffix=".wav") as tmp:
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", path,
                        "-vn", "-ac", "1", "-ar", str(rate), tmp.name], check=True)
        with wave.open(tmp.name, "rb") as w:
            data = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32)
            return data / 32768.0, w.getframerate()


def norm_crop(frame: np.ndarray, box: tuple[int, int, int, int] | None,
              size: tuple[int, int] = (160, 160)) -> np.ndarray:
    h, w = frame.shape[:2]
    if box is None:
        x, y, bw, bh = int(.25*w), 0, int(.5*w), int(.72*h)
    else:
        x, y, bw, bh = box
        # Include some hair/shoulder context while keeping a stable face anchor.
        x = max(0, x - int(.35*bw)); y = max(0, y - int(.25*bh))
        bw = min(w-x, int(1.7*bw)); bh = min(h-y, int(1.65*bh))
    crop = frame[y:y+bh, x:x+bw]
    if crop.size == 0:
        crop = frame
    return cv2.resize(cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY), size)


def metrics(a: np.ndarray, b: np.ndarray) -> dict:
    aa, bb = a.astype(np.float32), b.astype(np.float32)
    return {
        "mae": round(float(np.mean(np.abs(aa-bb))), 3),
        "mse": round(float(np.mean((aa-bb)**2)), 3),
        "ssim": round(float(structural_similarity(a, b, data_range=255)), 4),
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("video")
    ap.add_argument("--out", default=None)
    ap.add_argument("--seams", default="124,226,328",
                    help="output frame indices where a new MC segment starts")
    args = ap.parse_args()
    meta = probe(args.video)
    vs = next(s for s in meta["streams"] if s["codec_type"] == "video")
    fps = eval(vs["r_frame_rate"], {"__builtins__": {}}, {})
    cap = cv2.VideoCapture(args.video)
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps_cap = cap.get(cv2.CAP_PROP_FPS) or fps
    frames: list[np.ndarray] = []
    times: list[float] = []
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        frames.append(frame)
        times.append((len(frames)-1) / fps_cap)
    cap.release()
    total = len(frames)

    # OpenCV 5 packages may omit the legacy Haar API.  Keep a deterministic
    # center-frame fallback rather than making the whole QC depend on it.
    cascade = None
    if hasattr(cv2, "CascadeClassifier"):
        candidate = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
        if not candidate.empty():
            cascade = candidate
    boxes: list[tuple[int, int, int, int] | None] = []
    face_crops: list[np.ndarray] = []
    mouth_motion: list[float] = []
    prev_gray = None
    for frame in frames:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        found = cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5,
                                         minSize=(max(32, frame.shape[1]//12), max(32, frame.shape[0]//12))) if cascade else []
        box = max(found, key=lambda r: r[2]*r[3]) if len(found) else None
        boxes.append(tuple(map(int, box)) if box is not None else None)
        face_crops.append(norm_crop(frame, boxes[-1]))
        if prev_gray is None:
            mouth_motion.append(0.0)
        else:
            if box is not None:
                x, y, w, h = map(int, box)
                # Lower face, where mouth movement dominates over eye/head motion.
                roi = gray[y+int(.48*h):min(gray.shape[0], y+int(.92*h)), x:x+w]
                old = prev_gray[y+int(.48*h):min(prev_gray.shape[0], y+int(.92*h)), x:x+w]
            else:
                # Presenter is centered in this T31 framing; use a mouth-sized
                # ROI so hand/torso motion does not dominate the sync proxy.
                x0, x1 = int(.38*gray.shape[1]), int(.62*gray.shape[1])
                y0, y1 = int(.25*gray.shape[0]), int(.48*gray.shape[0])
                roi, old = gray[y0:y1, x0:x1], prev_gray[y0:y1, x0:x1]
            if roi.size and old.size == roi.size:
                mouth_motion.append(float(np.mean(np.abs(roi.astype(np.float32)-old.astype(np.float32)))))
            else:
                mouth_motion.append(0.0)
        prev_gray = gray

    # Face geometry and crop stability at each MC boundary.
    valid = [b for b in boxes if b is not None]
    geometry = {}
    if valid:
        h, w = frames[0].shape[:2]
        centers = np.array([[(x+fw/2)/w, (y+fh/2)/h, fw/w, fh/h] for x,y,fw,fh in valid])
        geometry = {"detections": len(valid), "detection_ratio": round(len(valid)/max(1,total), 3),
                    "center_std_xy": [round(float(v), 4) for v in centers[:,:2].std(axis=0)],
                    "size_std_wh": [round(float(v), 4) for v in centers[:,2:].std(axis=0)]}

    seam_ids = [int(x) for x in args.seams.split(",") if x.strip()]
    seams = []
    for idx in seam_ids:
        if 1 <= idx < total:
            row = {"frame": idx, "time_s": round(idx/fps_cap, 4),
                   "boundary": metrics(cv2.cvtColor(frames[idx-1], cv2.COLOR_BGR2GRAY),
                                        cv2.cvtColor(frames[idx], cv2.COLOR_BGR2GRAY)),
                   "face_boundary": metrics(face_crops[idx-1], face_crops[idx])}
            seams.append(row)
    anchor_ids = [0] + seam_ids + [total - 1]
    anchors = []
    for idx in anchor_ids:
        if 0 <= idx < total:
            anchors.append({"frame": idx, "time_s": round(idx/fps_cap, 4),
                            "central_anchor_vs_first": metrics(face_crops[0], face_crops[idx])})
    jumps = []
    for i in range(1, total):
        jumps.append(float(np.mean(np.abs(cv2.cvtColor(frames[i], cv2.COLOR_BGR2GRAY).astype(np.float32) -
                                    cv2.cvtColor(frames[i-1], cv2.COLOR_BGR2GRAY).astype(np.float32)))))
    seam_jump = [jumps[s["frame"]-1] for s in seams]
    baseline = np.delete(np.array(jumps), [s["frame"]-1 for s in seams]) if seams else np.array(jumps)

    audio_result = None
    if any(s["codec_type"] == "audio" for s in meta["streams"]):
        audio, ar = audio_wave(args.video)
        # Frame-rate audio envelope, then lag search over +/- 1 sec.
        n = min(total, int(len(audio)/ar*fps_cap))
        env = np.array([math.sqrt(float(np.mean(audio[int(i*ar/fps_cap):int((i+1)*ar/fps_cap)]**2)) + 1e-12)
                        for i in range(n)])
        mm = np.array(mouth_motion[:n])
        def z(x): return (x-x.mean())/(x.std()+1e-8)
        env, mm = z(env), z(mm)
        max_shift = min(int(fps_cap), max(1, n//4))
        corrs = []
        for lag in range(-max_shift, max_shift+1):
            if lag < 0: c = np.corrcoef(env[:lag], mm[-lag:])[0,1]
            elif lag > 0: c = np.corrcoef(env[lag:], mm[:-lag])[0,1]
            else: c = np.corrcoef(env, mm)[0,1]
            corrs.append((float(c) if np.isfinite(c) else 0.0, lag))
        best, lag = max(corrs)
        audio_result = {"audio_duration_s": round(len(audio)/ar, 4),
                        "video_duration_s": round(total/fps_cap, 4),
                        "audio_envelope_mouth_motion_corr": round(best, 4),
                        "best_lag_ms_audio_leads": round(-lag*1000/fps_cap, 1),
                        "interpretation": "proxy only; correlation is not phoneme-level SyncNet"}

    report = {
        "video": args.video, "video_meta": meta, "decoded_frames": total,
        "fps": round(float(fps_cap), 4), "geometry": geometry,
        "anchors": anchors, "seams": seams, "frame_jump_baseline_mean": round(float(baseline.mean()), 3),
        "frame_jump_baseline_p95": round(float(np.percentile(baseline, 95)), 3),
        "seam_jump_ratios_vs_baseline_mean": [round(x/max(1e-6,float(baseline.mean())), 3) for x in seam_jump],
        "audio_video": audio_result,
        "detector": "haar" if cascade else "fixed_center_proxy",
        "verdict_limits": ["face geometry/crop is a drift screening proxy, not identity recognition",
                           "audio result detects gross timing/energy mismatch, not exact phoneme alignment",
                           "seam ratio above 2 is a review flag; compare with the extracted boundary frames"],
    }
    out = Path(args.out) if args.out else Path(args.video).with_suffix(".qc.json")
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2))
    print(json.dumps(report, ensure_ascii=False, indent=2))
    print(f"REPORT={out}")


if __name__ == "__main__":
    main()
