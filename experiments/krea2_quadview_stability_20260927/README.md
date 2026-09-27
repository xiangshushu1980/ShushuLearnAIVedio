# [Sean] Krea2 QuadView layout stability — 2026-09-27

Owner: Sean

## Scope

First stabilize compact prompt variants for `QuadView_krea2_v1`: (A) upper-body portrait with both shoulders visible, (B2) face-focused portrait with a three-quarter side view, and (C) face-focused portrait with a strict side view. The sheet retains four panels: first portrait, then front, side, and back full-body views. Compare three-view front/three-quarter/back with a front/strict-side/back variant.

The same four source anchors, dimensions, sampler settings, and per-character seed are used across all three variants. This isolates prompt wording. DynamicCharacterSheet is deferred.

## Parameters

- LoRA: `QuadView_krea2_v1.safetensors`, strength 1.0
- Canvas: 1536×1024; 10 steps; CFG 1; Euler/simple; ref boost 1
- Cases: eastern swordswoman, red mage, dwarf engineer, ice wolf
- Seeds: fixed per character and shared across prompt variants

## Review

Review identity and costume consistency, first-panel crop (both shoulders for A; clear face for B/C), side angle for B/C, view order, duplicate/missing panels, and crop usability. These are previews only and cannot become canonical without H3 Ref2VA review.

See `manifest.json` and `prompts/` for exact inputs and prompt text.
