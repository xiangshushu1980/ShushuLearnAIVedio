#!/usr/bin/env python3
"""Owner: Sean. Measure generated white side bands and show aspect diagnostics."""
import json
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent


def main():
    manifest = json.loads((ROOT / "manifest.json").read_text())
    records = []
    for case in manifest["cases"]:
        if case["status"] != "success":
            continue
        capture = cv2.VideoCapture(str(ROOT / case["output"]))
        widths = []
        height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
        while True:
            ok, frame = capture.read()
            if not ok:
                break
            white = (frame.min(axis=2) > 245).mean(axis=0) > 0.98
            left = right = 0
            while left < len(white) and white[left]:
                left += 1
            while right < len(white) and white[len(white) - 1 - right]:
                right += 1
            widths.append([left, right, len(white) - left - right])
        capture.release()
        if not widths:
            raise RuntimeError(f"No frames in {case['output']}")
        values = np.array(widths)
        records.append({
            "case": case["id"], "height_px": height,
            "median_left_white_px": float(np.median(values[:, 0])),
            "median_right_white_px": float(np.median(values[:, 1])),
            "median_nonwhite_width_px": float(np.median(values[:, 2])),
            "nonwhite_width_range_px": [int(values[:, 2].min()), int(values[:, 2].max())],
            "median_visible_aspect_ratio": float(np.median(values[:, 2]) / height),
        })
    report = {"owner": "Sean", "reference_size": [1344, 1536],
              "ref_image_match_resized_size": [544, 640], "video_size": [768, 448],
              "method": "Side column classified as white when >98% of pixels have all decoded RGB channels >245. Band widths measured across all frames. Not a semantic crop or a quality metric.",
              "results": records}
    (ROOT / "aspect_diagnosis.json").write_text(json.dumps(report, indent=2) + "\n")
    names = ["motion_07", "motion_07_no_ref_latent", "motion_07_fullwidth_prompt", "motion_07_landscape_ref"]
    labels = ["Original 0.7", "Reference VAE off", "Explicit landscape prompt", "Landscape reference"]
    times = [0.4, 1.6, 2.8, 4.0]
    canvas = Image.new("RGB", (1536, len(names) * 258), "#202020")
    draw = ImageDraw.Draw(canvas)
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
    for row, (name, label) in enumerate(zip(names, labels)):
        capture = cv2.VideoCapture(str(ROOT / f"{name}.mp4"))
        for column, t in enumerate(times):
            capture.set(cv2.CAP_PROP_POS_MSEC, t * 1000)
            ok, frame = capture.read()
            if not ok:
                raise RuntimeError(f"Cannot read {name} at {t}s")
            x, y = column * 384, row * 258
            draw.text((x + 5, y + 6), f"{label} | {t:.1f}s", font=font, fill="white")
            image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)).resize((384, 224))
            canvas.paste(image, (x, y + 34))
        capture.release()
    canvas.save(ROOT / "aspect_diagnosis_contact.png")
    print(json.dumps(records, indent=2))


if __name__ == "__main__":
    main()
