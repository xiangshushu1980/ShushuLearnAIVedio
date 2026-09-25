#!/usr/bin/env python3
"""Measure source-face size and simple quality proxies across a pull-back."""

from __future__ import annotations

import argparse
import csv
import os

import cv2
from ultralytics import YOLO


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--video", required=True)
    p.add_argument("--detector", default="/home/sean/projects/ComfyUI/models/ultralytics/bbox/face_yolov8m.pt")
    p.add_argument("--confidence", type=float, default=0.25)
    p.add_argument("--out-csv", required=True)
    p.add_argument("--device", default="cpu")
    args = p.parse_args()
    model = YOLO(args.detector)
    cap = cv2.VideoCapture(args.video)
    os.makedirs(os.path.dirname(os.path.abspath(args.out_csv)), exist_ok=True)
    rows = []
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        i = len(rows)
        result = model.predict(frame, conf=0.01, imgsz=640, device=args.device, verbose=False)[0]
        candidates = []
        if result.boxes is not None:
            for box, conf in zip(result.boxes.xyxy.cpu().numpy(), result.boxes.conf.cpu().numpy()):
                if float(conf) >= args.confidence:
                    x0, y0, x1, y1 = [int(round(v)) for v in box]
                    if x1 > x0 and y1 > y0:
                        candidates.append((x0, y0, x1, y1, float(conf)))
        if candidates:
            x0, y0, x1, y1, conf = max(candidates, key=lambda b: (b[3] - b[1], b[4]))
            gray = cv2.cvtColor(frame[y0:y1, x0:x1], cv2.COLOR_BGR2GRAY)
            sharp = float(cv2.Laplacian(gray, cv2.CV_64F).var()) if gray.size else 0.0
            face_h = y1 - y0
            rows.append({"frame": i, "face_h_px": face_h, "face_h_latent_px": face_h / 8.0,
                         "confidence": conf, "laplacian": sharp, "tracked": 1})
        else:
            rows.append({"frame": i, "face_h_px": 0, "face_h_latent_px": 0,
                         "confidence": 0, "laplacian": 0, "tracked": 0})
    cap.release()
    fields = ["frame", "face_h_px", "face_h_latent_px", "confidence", "laplacian", "tracked"]
    with open(args.out_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader(); writer.writerows(rows)
    print(f"frames={len(rows)} csv={args.out_csv}")
    for start, end in ((0, 93), (94, 119), (120, 155), (156, 180), (181, len(rows)-1)):
        part = [r for r in rows if start <= r["frame"] <= end and r["tracked"]]
        if not part:
            print(f"frames {start}-{end}: no tracked face")
            continue
        hs = [r["face_h_px"] for r in part]
        cs = [r["confidence"] for r in part]
        ls = [r["laplacian"] for r in part]
        print(f"frames {start}-{end}: n={len(part)} face_px={min(hs):.1f}/{sum(hs)/len(hs):.1f}/{max(hs):.1f} "
              f"latent_px={min(hs)/8:.2f}/{sum(hs)/len(hs)/8:.2f}/{max(hs)/8:.2f} "
              f"conf={min(cs):.3f}/{sum(cs)/len(cs):.3f} lap={min(ls):.1f}/{sum(ls)/len(ls):.1f}")
    for target in (94, 120, 145, 150, 155, 160, 180):
        r = rows[target] if target < len(rows) else None
        print("frame", target, r)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
