#!/usr/bin/env python3
"""[Sean] Build four-case visual review sheets from the T48 manifest."""

import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
EXPERIMENT = ROOT / "experiments/krea2_quadview_stability_20260927"
MANIFEST = EXPERIMENT / "manifest.json"
REVIEW = EXPERIMENT / "review"


def main():
    manifest = json.loads(MANIFEST.read_text())
    REVIEW.mkdir(parents=True, exist_ok=True)
    font = ImageFont.load_default()
    width, height = 768, 512
    label_h, gap = 26, 8

    for variant in manifest["prompt_variants"]:
        results = [r for r in manifest["results"] if r["variant"] == variant]
        if not results:
            continue
        canvas = Image.new("RGB", (width * 2 + gap, (height + label_h + gap) * 2), "white")
        draw = ImageDraw.Draw(canvas)
        for index, result in enumerate(results[:4]):
            image = Image.open(result["output"]).convert("RGB")
            image.thumbnail((width, height), Image.Resampling.LANCZOS)
            x = (index % 2) * (width + gap)
            y = (index // 2) * (height + label_h + gap)
            canvas.paste(image, (x, y + label_h))
            draw.text((x + 4, y + 5), f"{result['case_id']} · seed {result['seed']}", fill="black", font=font)
        output = REVIEW / f"sean_t48_{variant}.jpg"
        canvas.save(output, quality=92, optimize=True)
        print(output)


if __name__ == "__main__":
    main()
