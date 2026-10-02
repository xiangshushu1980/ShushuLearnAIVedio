#!/usr/bin/env python3
"""Owner: Sean. CPU-only descriptive motion measurements and comparison frames."""
import json
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
CASES = ["baseline", "motion_07", "motion_08"]
TIMES = [0.4, 1.2, 2.0, 2.8, 3.6, 4.4]


def analyze(name):
    cap = cv2.VideoCapture(str(ROOT / f"{name}.mp4"))
    if not cap.isOpened():
        raise RuntimeError(f"Missing or unreadable {name}.mp4")
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    frames = []
    centers = []
    magnitudes = []
    previous = None
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        frames.append(frame)
        small = cv2.resize(frame, (384, 224))
        hsv = cv2.cvtColor(small, cv2.COLOR_BGR2HSV)
        mask = (((hsv[:, :, 0] < 17) | (hsv[:, :, 0] > 170)) &
                (hsv[:, :, 1] > 70) & (hsv[:, :, 2] > 30)).astype(np.uint8)
        y, x = np.nonzero(mask)
        centers.append([float(x.mean() * width / 384), float(y.mean() * height / 224)] if len(x) > 100 else [None, None])
        gray = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)
        if previous is not None:
            flow = cv2.calcOpticalFlowFarneback(previous, gray, None, 0.5, 3, 15, 3, 5, 1.2, 0)
            background = np.concatenate([flow[:, :40].reshape(-1, 2), flow[:, -40:].reshape(-1, 2)])
            shift = np.median(background, axis=0)
            magnitude = np.linalg.norm(flow - shift, axis=2)
            region = cv2.dilate(mask, np.ones((25, 25), np.uint8)).astype(bool)
            magnitudes.append(float(np.percentile(magnitude[region], 90) * width / 384) if region.any() else None)
        previous = gray
    cap.release()
    values = np.array([c for c in centers if c[0] is not None])
    valid_flow = [v for v in magnitudes if v is not None]
    result = {
        "case": name,
        "frames": len(frames), "fps": fps, "width": width, "height": height,
        "red_region_centroid_x_p95_minus_p05_px": float(np.percentile(values[:, 0], 95) - np.percentile(values[:, 0], 5)),
        "red_region_centroid_y_p95_minus_p05_px": float(np.percentile(values[:, 1], 95) - np.percentile(values[:, 1], 5)),
        "median_subject_flow_p90_px_per_frame": float(np.median(valid_flow)),
        "centroid_xy_by_frame": centers,
        "subject_flow_p90_by_frame": magnitudes,
    }
    return result, [Image.fromarray(cv2.cvtColor(frames[min(round(t * fps), len(frames) - 1)], cv2.COLOR_BGR2RGB)) for t in TIMES]


def main():
    report = {
        "owner": "Sean",
        "method": "Red-region centroid spread (robust p95-p05), plus Farneback p90 flow inside dilated red-region mask, corrected by median left/right border background flow. Flow computed on 384x224 images, scaled to source pixels. CPU only.",
        "limitations": "Descriptive motion proxies only: clothing shape changes and pose changes affect the red-region centroid; flow includes cloth and body motion and synthesis artifacts. These measurements do not measure action correctness, cycle count, identity fidelity, anatomy, or overall quality.",
        "cases": [],
    }
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
    canvas = Image.new("RGB", (1728, 3 * 202), "#202020")
    draw = ImageDraw.Draw(canvas)
    for row, name in enumerate(CASES):
        record, pictures = analyze(name)
        report["cases"].append(record)
        for column, picture in enumerate(pictures):
            x, y = column * 288, row * 202
            draw.text((x + 5, y + 5), f"{name} | {TIMES[column]:.1f}s", font=font, fill="white")
            canvas.paste(picture.resize((288, 168)), (x, y + 34))
    canvas.save(ROOT / "comparison_contact.png")
    (ROOT / "motion_metrics.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps([{k: v for k, v in r.items() if not k.endswith("by_frame")} for r in report["cases"]], indent=2))


if __name__ == "__main__":
    main()
