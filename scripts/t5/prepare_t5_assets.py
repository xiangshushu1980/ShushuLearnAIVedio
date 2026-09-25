#!/usr/bin/env python3
"""Prepare T5 same-character reference-role assets from accepted T0/T1 sources.

Owner: Sean
This script only derives crops and a manifest; it does not generate new identity content.
"""
from __future__ import annotations

import json
import shutil
from pathlib import Path

from PIL import Image


SRC = Path("/home/sean/projects/ComfyUI/output/sean_h3_character_reference_test")
OUT = SRC / "t5_reference_roles"


def copy(name: str, role: str) -> dict:
    src = SRC / name
    dst = OUT / f"{role}.png"
    shutil.copy2(src, dst)
    with Image.open(dst) as im:
        size = im.size
    return {"role": role, "source": name, "path": dst.name, "size": size}


def crop(name: str, role: str, box: tuple[int, int, int, int]) -> dict:
    src = SRC / name
    dst = OUT / f"{role}.png"
    with Image.open(src) as im:
        im.crop(box).save(dst)
        size = im.crop(box).size
    return {"role": role, "source": name, "crop_box": box, "path": dst.name, "size": size}


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    assets = []
    assets.append(copy("sean_face_closeup.png", "F_face_identity"))
    assets.append(copy("sean_identity_front.png", "W_wardrobe_full"))
    # Front body crop: remove the competing frontal face while retaining hood,
    # hair/neck transition where available, shoulders, clothing and body shape.
    assets.append(crop("sean_identity_front.png", "WB_wardrobe_body", (380, 145, 850, 672)))
    assets.append(copy("sean_view_left.png", "S_view_side"))
    assets.append(copy("sean_view_back.png", "B_view_back"))
    assets.append(copy("sean_character_reference_board_v1.png", "BOARD_existing"))
    manifest = {
        "owner": "Sean",
        "test_id": "remote-c1c2bb3a-432b-4586-af9d-f6ffdde54196",
        "test": "T5_reference_role_conflict",
        "source_of_truth": "accepted T0/T1 assets; no new identity generation",
        "assets": assets,
        "notes": [
            "WB is a front wardrobe/body crop and intentionally does not preserve a frontal face.",
            "The back-of-head/back-wardrobe evidence remains available as B_view_back.",
            "WB must pass human QC for neck/shoulder continuity before H3 runs.",
        ],
    }
    (OUT / "t5_asset_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
