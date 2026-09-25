#!/usr/bin/env python3
"""Make a labeled original-vs-refined side-by-side video.

The left panel uses the same face detector family as the H3 route to make the
effective gate visible: a detected face is marked REFINE; no detected face is
marked ORIGINAL. This is a diagnostic overlay, not an additional refinement.
"""

from __future__ import annotations

import argparse
import os
import subprocess

import cv2
from ultralytics import YOLO


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--original", required=True)
    p.add_argument("--refined", required=True)
    p.add_argument("--detector", default="/home/sean/projects/ComfyUI/models/ultralytics/bbox/face_yolov8m.pt")
    p.add_argument("--output", required=True)
    p.add_argument("--confidence", type=float, default=0.25)
    p.add_argument("--title", default="FaceRefine tracking gate")
    p.add_argument("--start-refine-frame", type=int, default=0,
                   help="Keep original pixels before this zero-based frame")
    p.add_argument("--start-refine-frac", type=float, default=0.0,
                   help="Latch refine on when detected face height / frame height falls below this ratio")
    p.add_argument("--device", default="cpu")
    p.add_argument("--target", choices=["largest", "leftmost", "rightmost"], default="largest",
                   help="Which detected face to use for the diagnostic gate in multi-person clips")
    args = p.parse_args()

    cap = cv2.VideoCapture(args.original)
    ref = cv2.VideoCapture(args.refined)
    if not cap.isOpened() or not ref.isOpened():
        raise RuntimeError("cannot open original/refined video")
    fps = cap.get(cv2.CAP_PROP_FPS) or 24.0
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    rw = int(ref.get(cv2.CAP_PROP_FRAME_WIDTH))
    rh = int(ref.get(cv2.CAP_PROP_FRAME_HEIGHT))
    os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
    tmp = args.output + ".tmp.mp4"
    writer = cv2.VideoWriter(tmp, cv2.VideoWriter_fourcc(*"mp4v"), fps, (w + rw, max(h, rh)))
    model = YOLO(args.detector)
    frame = 0
    size_started = False
    try:
        while True:
            ok, img = cap.read()
            ok2, out = ref.read()
            if not ok or not ok2:
                break
            result = model.predict(img, conf=0.01, imgsz=640, device=args.device, verbose=False)[0]
            boxes = []
            if result.boxes is not None:
                for box, conf in zip(result.boxes.xyxy.cpu().numpy(), result.boxes.conf.cpu().numpy()):
                    if float(conf) >= args.confidence:
                        x0, y0, x1, y1 = [int(round(v)) for v in box]
                        boxes.append((x0, y0, x1, y1, float(conf)))
            if args.start_refine_frac > 0.0 and boxes:
                if args.target == "leftmost":
                    gate_box = min(boxes, key=lambda b: (b[0] + b[2]) / 2.0)
                elif args.target == "rightmost":
                    gate_box = max(boxes, key=lambda b: (b[0] + b[2]) / 2.0)
                else:
                    gate_box = max(boxes, key=lambda b: b[3] - b[1])
                gate_h = gate_box[3] - gate_box[1]
                if gate_h / max(1, h) <= args.start_refine_frac:
                    size_started = True
            started = frame >= args.start_refine_frame or size_started
            if not started:
                # The source is still sharp before degradation. Do not let the
                # already-rendered refine batch overwrite those pixels.
                out = img.copy()
                if args.start_refine_frac > 0.0:
                    status = f"ORIGINAL -> NO REFINE | waiting face/frame <= {args.start_refine_frac:.3f}"
                else:
                    status = f"ORIGINAL -> NO REFINE | before start frame {args.start_refine_frame}"
                colour = (255, 190, 40)
            elif boxes:
                if args.target == "leftmost":
                    x0, y0, x1, y1, conf = min(boxes, key=lambda b: (b[0] + b[2]) / 2.0)
                elif args.target == "rightmost":
                    x0, y0, x1, y1, conf = max(boxes, key=lambda b: (b[0] + b[2]) / 2.0)
                else:
                    x0, y0, x1, y1, conf = max(boxes, key=lambda b: b[3] - b[1])
                face_h = y1 - y0
                if face_h >= 35:
                    phase = "LARGE / NO REFINE"
                elif face_h >= 25:
                    phase = "TRANSITION / REFINE"
                else:
                    phase = "SMALL / REFINE"
                status = f"TRACKED -> REFINE | face={face_h}px conf={conf:.2f} | {phase}"
                colour = (40, 220, 40)
                cv2.rectangle(img, (x0, y0), (x1, y1), colour, max(2, w // 500))
            else:
                status = "NOT TRACKED -> ORIGINAL | refine output skipped"
                colour = (40, 40, 230)
            left = img
            if rh != h or rw != w:
                out = cv2.resize(out, (rw, rh), interpolation=cv2.INTER_AREA)
            panel_h = max(h, rh)
            if left.shape[0] != panel_h:
                left = cv2.copyMakeBorder(left, 0, panel_h - left.shape[0], 0, 0,
                                          cv2.BORDER_CONSTANT, value=(0, 0, 0))
            if out.shape[0] != panel_h:
                out = cv2.copyMakeBorder(out, 0, panel_h - out.shape[0], 0, 0,
                                         cv2.BORDER_CONSTANT, value=(0, 0, 0))
            cv2.putText(left, "ORIGINAL / TRACK STATUS", (24, 42),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2, cv2.LINE_AA)
            cv2.putText(left, status, (24, 84), cv2.FONT_HERSHEY_SIMPLEX,
                        0.72, colour, 2, cv2.LINE_AA)
            cv2.putText(out, "FACEREFINE OUTPUT", (24, 42),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2, cv2.LINE_AA)
            cv2.putText(left, f"frame={frame}  {args.title}", (24, panel_h - 24),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.62, (230, 230, 230), 2, cv2.LINE_AA)
            writer.write(cv2.hconcat([left, out]))
            frame += 1
    finally:
        cap.release(); ref.release(); writer.release()
    subprocess.run(["ffmpeg", "-y", "-i", tmp, "-i", args.original,
                    "-map", "0:v:0", "-map", "1:a?", "-c:v", "libx264", "-crf", "18",
                    "-pix_fmt", "yuv420p", "-c:a", "aac", "-shortest", args.output],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    os.unlink(tmp)
    print(f"wrote {args.output} frames={frame} fps={fps} size={w+rw}x{panel_h}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
