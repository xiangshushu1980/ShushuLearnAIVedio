#!/usr/bin/env python3
"""Owner: Sean. Build matched baseline and skill-guided prompts for Qwen-Image-2.1."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
cases = json.loads((ROOT / "casebook.json").read_text())["cases"]
for arm in ("baseline", "skill_guided"):
    out = ROOT / "prompts" / arm
    out.mkdir(parents=True, exist_ok=True)
    for c in cases:
        rows = "\n".join(" | ".join(row) for row in c["rows"])
        exact = f'Exact supplied text and data (preserve spelling, punctuation, units, order, and values):\n{rows}'
        if arm == "baseline":
            prompt = (
                f'Create a finished landscape 3:2 infographic titled "{c["title"]}" with subtitle "{c["subtitle"]}". '
                f'Use a clean editorial vector style with a restrained palette and clear typography. '
                f'Chart or diagram: {c["topology"]}. {c["visual_concept"]} '
                f'{exact}\nKey takeaway: "{c["takeaway"]}". {c["must_preserve"]} '
                'Use a clear grid, readable labels, and a strong title hierarchy. Render only the supplied text. '
                'Do not add labels, values, legends, or claims. Make the chart or diagram a major part of the image.'
            )
        else:
            prompt = (
                f'Finished landscape 3:2 editorial infographic. Its five-second takeaway is: "{c["takeaway"]}". '
                f'Information structure: {c["topology"]}. Give the main visual about 70% of the canvas; '
                f'let {c["visual_concept"]} Keep one obvious reading path from the title to the visual and then to the conclusion. '
                f'Title: "{c["title"]}". Subtitle: "{c["subtitle"]}". '
                f'{exact}\n{c["must_preserve"]} Use only this short copy: the title, subtitle, category labels, and supplied values; '
                'no explanatory paragraphs, decorative lettering, extra numbers, legends, or unsupported claims. '
                'Keep the key marks and labels legible at thumbnail size. Use a quiet background, ample negative space, '
                'one functional accent color, and distinct editorial composition rather than a repeated card grid.'
            )
        (out / f'{c["id"]}.txt').write_text(prompt + "\n", encoding="utf-8")
print(f"Built {len(cases) * 2} matched prompts under {ROOT / 'prompts'}")
