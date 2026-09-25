#!/usr/bin/env python3
"""Create a static original/refined contact sheet at pixel-size thresholds."""

from __future__ import annotations

import argparse
import os

import cv2
from ultralytics import YOLO


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--original", required=True)
    p.add_argument("--refined", required=True)
    p.add_argument("--thresholds", default="70,60,50,40,30")
    p.add_argument("--detector", default="/home/sean/projects/ComfyUI/models/ultralytics/bbox/face_yolov8m.pt")
    p.add_argument("--output", required=True)
    p.add_argument("--target", choices=["largest", "leftmost", "rightmost"], default="largest")
    args = p.parse_args()
    thresholds = [float(x) for x in args.thresholds.split(",") if x.strip()]
    cap = cv2.VideoCapture(args.original)
    ref = cv2.VideoCapture(args.refined)
    if not cap.isOpened() or not ref.isOpened():
        raise RuntimeError("cannot open source/refined video")
    model = YOLO(args.detector)
    picked = {}
    originals = {}
    refined = {}
    i = 0
    while True:
        ok, frame = cap.read(); ok2, rframe = ref.read()
        if not ok or not ok2:
            break
        result = model.predict(frame, conf=0.01, imgsz=640, device="cpu", verbose=False)[0]
        boxes = []
        if result.boxes is not None:
            for b, c in zip(result.boxes.xyxy.cpu().numpy(), result.boxes.conf.cpu().numpy()):
                if float(c) >= 0.25:
                    x0, y0, x1, y1 = [int(round(v)) for v in b]
                    boxes.append((x0, y0, x1, y1, float(c)))
        if boxes:
            if args.target == "leftmost":
                box = min(boxes, key=lambda x: (x[0] + x[2]) / 2.0)
            elif args.target == "rightmost":
                box = max(boxes, key=lambda x: (x[0] + x[2]) / 2.0)
            else:
                box = max(boxes, key=lambda x: x[3] - x[1])
            face_h = box[3] - box[1]
            for th in thresholds:
                if th not in picked and face_h <= th:
                    picked[th] = i
                    originals[th] = (frame.copy(), box)
                    refined[th] = rframe.copy()
        i += 1
        if len(picked) == len(thresholds):
            break
    cap.release(); ref.release()
    if not picked:
        raise RuntimeError("no threshold crossings detected")
    panels = []
    for th in thresholds:
        if th not in picked:
            continue
        frame, box = originals[th]
        x0, y0, x1, y1, conf = box
        cv2.rectangle(frame, (x0, y0), (x1, y1), (40, 220, 40), 3)
        label = f"face <= {th:.0f}px | frame {picked[th]} | h={y1-y0}px conf={conf:.2f}"
        cv2.putText(frame, "ORIGINAL", (20, 38), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255,255,255), 2, cv2.LINE_AA)
        cv2.putText(frame, label, (20, 76), cv2.FONT_HERSHEY_SIMPLEX, 0.72, (40,220,40), 2, cv2.LINE_AA)
        out = refined[th].copy()
        cv2.putText(out, "REFINED CANDIDATE", (20, 38), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255,255,255), 2, cv2.LINE_AA)
        panels.append(cv2.hconcat([frame, out]))
    sheet = cv2.vconcat(panels)
    os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
    cv2.imwrite(args.output, sheet, [cv2.IMWRITE_JPEG_QUALITY, 94])
    print(f"wrote {args.output} crossings={picked}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
