# [Sean] Krea2 QuadView layout stability — 2026-09-27

Owner: Sean

## Current focus

Stabilize the fixed three-view and four-view layouts first. DynamicCharacterSheet is deferred. The user-facing home for this run is this directory: prompts, `manifest.json`, QC, and the selected image under `outputs/`. ComfyUI's original output path is retained in the manifest as provenance.

The red mage result for `D_threeview_front_threequarter_back` has been confirmed by Sean as having the desired three-quarter angle. The half-body branch is abandoned: prompt-only A2 did not fully show the shoulder, and a crop from the full-body panel does not add generated detail. A3 is excluded from candidate layouts. The prior single `52/24/24` face-focused preview showed a larger face, but stable panel-width control did not pass; see `QC.md`.

## Parameters

- LoRA: `QuadView_krea2_v1.safetensors`, strength 1.0
- Canvas: 1536×1024; 10 steps; CFG 1; Euler/simple; ref boost 1
- Current single case: red mage, seed 4801002
- Earlier 24-image batch conditions and provenance: `manifest.json` and `run.log`

See `manifest.json`, `prompts/`, and `QC.md` for exact inputs, results, and status.
