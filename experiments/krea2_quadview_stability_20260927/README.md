# [Sean] Krea2 QuadView layout stability — 2026-09-27

Owner: Sean

## Current focus

Stabilize the fixed three-view and four-view layouts first. DynamicCharacterSheet is deferred. The user-facing home for this run is this directory: prompts, `manifest.json`, QC, and the selected image under `outputs/`. ComfyUI's original output path is retained in the manifest as provenance.

The red mage result for `D_threeview_front_threequarter_back` has been confirmed by Sean as having the desired three-quarter angle. The A2 prompt-only attempt still clipped the left shoulder. The current single-image review is `outputs/sean_t48_A3_upperbody_crop_left_red_mage.png`: the upper half of the full-body front panel is cropped and placed at the far left at the original scale. Both shoulders are visible. See `QC.md` for details and the review gate.

## Parameters

- LoRA: `QuadView_krea2_v1.safetensors`, strength 1.0
- Canvas: 1536×1024; 10 steps; CFG 1; Euler/simple; ref boost 1
- Current single case: red mage, seed 4801002
- Earlier 24-image batch conditions and provenance: `manifest.json` and `run.log`

See `manifest.json`, `prompts/`, and `QC.md` for exact inputs, results, and status.
