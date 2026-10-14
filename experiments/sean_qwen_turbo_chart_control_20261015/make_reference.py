#!/usr/bin/env python3
"""Draw the reference bar chart for the Qwen Turbo chart control experiment.

Owner: Sean
"""

import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


OUT_DIR = Path(__file__).resolve().parent
WIDTH, HEIGHT = 1536, 1024
WHITE = (255, 255, 255)
BLUE = (47, 107, 255)
BLACK = (0, 0, 0)
FONT_PATH = "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc"

# Plot box uses pixel-edge coordinates: left, top, right, bottom.
PLOT = {"left": 200, "top": 120, "right": 1430, "bottom": 850}
VALUES = [20, 70, 40, 90]
CATEGORIES = ["甲", "乙", "丙", "丁"]
BAR_WIDTH = 170
CENTERS_X = [350, 650, 950, 1250]


def main():
    image = Image.new("RGB", (WIDTH, HEIGHT), WHITE)
    draw = ImageDraw.Draw(image)
    font_title = ImageFont.truetype(FONT_PATH, 54)
    font_label = ImageFont.truetype(FONT_PATH, 38)
    font_tick = ImageFont.truetype(FONT_PATH, 30)
    font_value = ImageFont.truetype(FONT_PATH, 34)

    # Title, centered on the image.
    title = "测试数据"
    title_box = draw.textbbox((0, 0), title, font=font_title)
    title_x = (WIDTH - (title_box[2] - title_box[0])) // 2
    title_y = 28
    draw.text((title_x, title_y), title, fill=BLACK, font=font_title)

    # Axes and ticks.
    draw.line((PLOT["left"], PLOT["top"], PLOT["left"], PLOT["bottom"]), fill=BLACK, width=4)
    draw.line((PLOT["left"], PLOT["bottom"], PLOT["right"], PLOT["bottom"]), fill=BLACK, width=4)
    tick_records = []
    for value in range(0, 101, 20):
        y = round(PLOT["bottom"] - (value / 100) * (PLOT["bottom"] - PLOT["top"]))
        draw.line((PLOT["left"] - 12, y, PLOT["left"], y), fill=BLACK, width=3)
        label = str(value)
        box = draw.textbbox((0, 0), label, font=font_tick)
        x = PLOT["left"] - 25 - (box[2] - box[0])
        draw.text((x, y - (box[3] - box[1]) // 2 - box[1]), label, fill=BLACK, font=font_tick)
        tick_records.append({"value": value, "y": y, "mark": [PLOT["left"] - 12, y, PLOT["left"], y], "label": label, "label_origin": [x, y - (box[3] - box[1]) // 2 - box[1]]})

    bars = []
    for category, value, cx in zip(CATEGORIES, VALUES, CENTERS_X):
        x0 = cx - BAR_WIDTH // 2
        x1 = cx + BAR_WIDTH // 2
        y1 = round(PLOT["bottom"] - (value / 100) * (PLOT["bottom"] - PLOT["top"]))
        draw.rectangle((x0, y1, x1, PLOT["bottom"]), fill=BLUE)
        value_text = str(value)
        vb = draw.textbbox((0, 0), value_text, font=font_value)
        value_x = cx - (vb[2] - vb[0]) // 2
        value_y = y1 - 48
        draw.text((value_x, value_y), value_text, fill=BLACK, font=font_value)
        cat_box = draw.textbbox((0, 0), category, font=font_label)
        cat_x = cx - (cat_box[2] - cat_box[0]) // 2
        cat_y = PLOT["bottom"] + 34
        draw.text((cat_x, cat_y), category, fill=BLACK, font=font_label)
        bars.append({
            "category": category,
            "value": value,
            "center_x": cx,
            "rectangle": [x0, y1, x1, PLOT["bottom"]],
            "value_label": {"text": value_text, "origin": [value_x, value_y], "bbox": [value_x + vb[0], value_y + vb[1], value_x + vb[2], value_y + vb[3]]},
            "category_label": {"text": category, "origin": [cat_x, cat_y], "bbox": [cat_x + cat_box[0], cat_y + cat_box[1], cat_x + cat_box[2], cat_y + cat_box[3]]},
        })

    image.save(OUT_DIR / "reference.png")
    geometry = {
        "owner": "Sean",
        "image_size": [WIDTH, HEIGHT],
        "coordinate_convention": "pixel coordinates; rectangles are [left, top, right, bottom]",
        "plot_box": PLOT,
        "title": {"text": title, "origin": [title_x, title_y], "bbox": [title_x + title_box[0], title_y + title_box[1], title_x + title_box[2], title_y + title_box[3]]},
        "axes": {"y_axis": [PLOT["left"], PLOT["top"], PLOT["left"], PLOT["bottom"]], "x_axis": [PLOT["left"], PLOT["bottom"], PLOT["right"], PLOT["bottom"]]},
        "ticks": tick_records,
        "baseline_y": PLOT["bottom"],
        "bars": bars,
    }
    (OUT_DIR / "reference_geometry.json").write_text(json.dumps(geometry, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
