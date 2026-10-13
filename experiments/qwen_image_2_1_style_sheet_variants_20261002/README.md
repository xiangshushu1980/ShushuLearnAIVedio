# [Sean] Qwen style variants for H3 video main-image candidates

## Goal

Restyle one Qwen full-body character image into five candidate rendering styles while preserving face, clothes, armor, weapon family, and a clean single-person full-body composition.

## Intended video use

These Qwen outputs are **experimental main-image candidates**, not canonical H3 reference assets. The project reference workflow is: select a main image, generate H3 full-view/video material, then extract role-specific references (face, whole body, wardrobe body, side/back as needed) and QC them. Do not treat a multi-view contact sheet as the default video identity input. This experiment stops before H3 generation.

## Style variants

Anime cel shading, painterly concept art, stylized 3D game render, graphic novel, and watercolor/gouache. All use the same source image, seed, and Qwen parameters. No Krea2, LoRA, or extra reference image.


Outputs (all 1536×1024): `outputs/style_anime_cel.png`, `style_painterly_concept.png`, `style_3d_game_render.png`, `style_graphic_novel.png`, and `style_watercolor_gouache.png`.
