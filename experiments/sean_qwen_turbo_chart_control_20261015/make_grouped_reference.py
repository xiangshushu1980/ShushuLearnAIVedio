#!/usr/bin/env python3
"""Draw a grouped-bar reference chart. Owner: Sean."""

import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


OUT = Path(__file__).resolve().parent
W, H = 1536, 1024
WHITE, BLACK = (255, 255, 255), (20, 25, 35)
BLUE, ORANGE = (47, 107, 255), (242, 140, 40)
FONT_PATH = "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc"
PLOT = {"left": 205, "top": 190, "right": 1430, "bottom": 850}
CATEGORIES = ["甲", "乙", "丙", "丁"]
SERIES = [
    {"name": "系列一", "color": BLUE, "values": [20, 70, 40, 90]},
    {"name": "系列二", "color": ORANGE, "values": [50, 30, 80, 60]},
]
GROUP_CENTERS = [370, 660, 950, 1240]
BAR_WIDTH, BAR_GAP = 100, 18


def text_record(draw, text, font, center_x, top_y):
    box = draw.textbbox((0, 0), text, font=font)
    x = round(center_x - (box[2] - box[0]) / 2)
    y = top_y - box[1]
    draw.text((x, y), text, fill=BLACK, font=font)
    return {"text": text, "origin": [x, y], "bbox": [x + box[0], y + box[1], x + box[2], y + box[3]]}


def main():
    im = Image.new("RGB", (W, H), WHITE)
    d = ImageDraw.Draw(im)
    title_font = ImageFont.truetype(FONT_PATH, 52)
    legend_font = ImageFont.truetype(FONT_PATH, 32)
    category_font = ImageFont.truetype(FONT_PATH, 36)
    tick_font = ImageFont.truetype(FONT_PATH, 28)
    value_font = ImageFont.truetype(FONT_PATH, 30)

    title_box = d.textbbox((0, 0), "双系列测试", font=title_font)
    title_x = (W - (title_box[2] - title_box[0])) // 2
    title_origin = [title_x, 28 - title_box[1]]
    d.text(title_origin, "双系列测试", fill=BLACK, font=title_font)
    title_record_data = {"text": "双系列测试", "origin": title_origin, "bbox": [title_x + title_box[0], 28, title_x + title_box[2], 28 + title_box[3] - title_box[1]]}

    # Center the legend as a single group; swatches are 26x26 px.
    legend_y, swatch = 112, 26
    legend_layout = []
    entries = []
    cursor = 0
    for s in SERIES:
        label_box = d.textbbox((0, 0), s["name"], font=legend_font)
        label_w = label_box[2] - label_box[0]
        entry_w = swatch + 12 + label_w
        entries.append((s, entry_w, label_box))
        cursor += entry_w
    gap = 56
    total_w = cursor + gap
    x = (W - total_w) // 2
    for i, (s, entry_w, label_box) in enumerate(entries):
        sx, sy = x, legend_y + 4
        d.rectangle((sx, sy, sx + swatch, sy + swatch), fill=s["color"])
        lx = sx + swatch + 12
        ly = legend_y - label_box[1]
        d.text((lx, ly), s["name"], fill=BLACK, font=legend_font)
        legend_layout.append({"series": s["name"], "swatch": [sx, sy, sx + swatch, sy + swatch], "label": {"text": s["name"], "origin": [lx, ly], "bbox": [lx + label_box[0], ly + label_box[1], lx + label_box[2], ly + label_box[3]]}})
        x += entry_w + (gap if i == 0 else 0)

    # Axes, with no grid lines so the paired bars remain easy to read.
    d.line((PLOT["left"], PLOT["top"], PLOT["left"], PLOT["bottom"]), fill=BLACK, width=4)
    d.line((PLOT["left"], PLOT["bottom"], PLOT["right"], PLOT["bottom"]), fill=BLACK, width=4)
    ticks = []
    for val in range(0, 101, 20):
        y = round(PLOT["bottom"] - val / 100 * (PLOT["bottom"] - PLOT["top"]))
        d.line((PLOT["left"] - 12, y, PLOT["left"], y), fill=BLACK, width=3)
        t = str(val)
        b = d.textbbox((0, 0), t, font=tick_font)
        tx = PLOT["left"] - 24 - (b[2] - b[0])
        ty = y - (b[3] - b[1]) / 2 - b[1]
        d.text((tx, ty), t, fill=BLACK, font=tick_font)
        ticks.append({"value": val, "y": y, "mark": [PLOT["left"] - 12, y, PLOT["left"], y], "label": {"text": t, "origin": [tx, round(ty)], "bbox": [tx + b[0], round(ty) + b[1], tx + b[2], round(ty) + b[3]]}})

    groups = []
    total_pair_w = BAR_WIDTH * 2 + BAR_GAP
    for cat, center in zip(CATEGORIES, GROUP_CENTERS):
        left0 = center - total_pair_w // 2
        pair_bars = []
        for si, s in enumerate(SERIES):
            x0 = left0 + si * (BAR_WIDTH + BAR_GAP)
            x1 = x0 + BAR_WIDTH
            value = s["values"][len(groups)]
            y1 = round(PLOT["bottom"] - value / 100 * (PLOT["bottom"] - PLOT["top"]))
            d.rectangle((x0, y1, x1, PLOT["bottom"]), fill=s["color"])
            value_text = str(value)
            value_record = text_record(d, value_text, value_font, (x0 + x1) / 2, y1 - 42)
            pair_bars.append({"series": s["name"], "value": value, "rectangle": [x0, y1, x1, PLOT["bottom"]], "value_label": value_record})
        category_record = text_record(d, cat, category_font, center, PLOT["bottom"] + 28)
        groups.append({"category": cat, "center_x": center, "bars": pair_bars, "category_label": category_record})

    im.save(OUT / "grouped_reference.png")
    geometry = {
        "owner": "Sean",
        "image_size": [W, H],
        "coordinate_convention": "pixel coordinates; rectangles and bounding boxes are [left, top, right, bottom]",
        "plot_box": PLOT,
        "title": title_record_data,
        "legend": legend_layout,
        "axes": {"y_axis": [PLOT["left"], PLOT["top"], PLOT["left"], PLOT["bottom"]], "x_axis": [PLOT["left"], PLOT["bottom"], PLOT["right"], PLOT["bottom"]]},
        "ticks": ticks,
        "baseline_y": PLOT["bottom"],
        "series": [{"name": s["name"], "color_rgb": list(s["color"]), "values": s["values"]} for s in SERIES],
        "groups": groups,
    }
    (OUT / "grouped_reference_geometry.json").write_text(json.dumps(geometry, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
