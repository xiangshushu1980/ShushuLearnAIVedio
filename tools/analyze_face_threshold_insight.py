#!/usr/bin/env python3
"""Measure face boxes with the InsightFace backend used by identity tracking."""

from __future__ import annotations

import argparse
import csv
import os

import cv2
from insightface.app import FaceAnalysis


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--video", required=True)
    p.add_argument("--out-csv", required=True)
    p.add_argument("--det-size", type=int, default=640)
    args = p.parse_args()
    app = FaceAnalysis(name="buffalo_l", root="/home/sean/projects/ComfyUI/models/insightface",
                       providers=["CPUExecutionProvider"])
    app.prepare(ctx_id=-1, det_size=(args.det_size, args.det_size))
    cap = cv2.VideoCapture(args.video)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)); height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    rows = []
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        faces = app.get(frame)
        sizes = sorted([(float(x.bbox[3] - x.bbox[1]), float(x.det_score)) for x in faces], reverse=True)
        row = {"frame": len(rows), "width": width, "height": height,
               "face_count": len(sizes), "faces": ";".join(f"{h:.1f}:{s:.3f}" for h, s in sizes),
               "largest_h_px": sizes[0][0] if sizes else 0.0,
               "largest_h_frac": sizes[0][0] / height if sizes else 0.0,
               "largest_h_latent_px": sizes[0][0] / 8.0 if sizes else 0.0,
               "largest_conf": sizes[0][1] if sizes else 0.0}
        rows.append(row)
    cap.release()
    os.makedirs(os.path.dirname(os.path.abspath(args.out_csv)), exist_ok=True)
    fields = ["frame", "width", "height", "face_count", "faces", "largest_h_px",
              "largest_h_frac", "largest_h_latent_px", "largest_conf"]
    with open(args.out_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows(rows)
    nonempty = [r for r in rows if r["face_count"]]
    print(f"frames={len(rows)} detected_frames={len(nonempty)} csv={args.out_csv}")
    if nonempty:
        for start, end in ((0, 40), (41, 80), (81, 120), (121, len(rows)-1)):
            part = [r for r in nonempty if start <= r["frame"] <= end]
            if part:
                hs = [r["largest_h_px"] for r in part]
                fs = [r["largest_h_frac"] for r in part]
                counts = sorted(set(r["face_count"] for r in part))
                print(f"frames {start}-{end}: n={len(part)} face_px={min(hs):.1f}/{sum(hs)/len(hs):.1f}/{max(hs):.1f} "
                      f"frac={min(fs):.4f}/{sum(fs)/len(fs):.4f}/{max(fs):.4f} counts={counts}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
