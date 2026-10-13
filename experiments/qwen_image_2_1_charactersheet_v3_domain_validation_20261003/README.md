# [Sean] Qwen Image 2.1 Character Sheet V3 domain validation

## Goal

Check whether the CivitAI Character Sheet V3 workflow's static-prompt Qwen Image 2.1 adaptation can create useful multi-view sheets for a character, a prop, a standalone object, and a scene. The existing character V3 smoke is prior evidence; this matrix uses a single-face-plus-front/side/back character layout and three non-character domains.

## Fixed local route

- V3 Simple source graph, with the static prompt replaced for each domain.
- Qwen Image 2.1 int8 UNet, Qwen3VL 8B int8, Qwen Image 2.1 BF16 VAE.
- 1536x1024 output, 25 steps, CFG 1, Euler/simple, reference conditioning 1024, standard VAE decode.
- The source V3 graph requires VAEDeGrid, which is unavailable locally; this is an adapted V3 run, not an unmodified upstream graph.
- The saved V2/V3 graphs contain no LoRA loader. This validation concerns the Character Sheet workflow.
- One fixed Qwen-generated or previously generated source reference per domain; three sheet seeds per domain.

## Validation cases

1. Character: one large face portrait plus exactly front, strict side, and back full-body views.
2. Prop: one ceremonial katana, front/side/back orthographic views, no person.
3. Standalone object: one brass camping lantern, front/side/back orthographic views, no person.
4. Scene: one mountain shrine courtyard shown from three defined camera positions: entrance, side elevation, and reverse view from inside. Retain fixed spatial landmarks.

## QC gates

For each output, record whether there are exactly three requested views (and one face portrait for the character case), whether all panels show the same subject, whether signature geometry/landmarks persist, whether the requested angles are distinct, whether labels/text or extra subjects appear, and whether the output is usable as a design reference. Three seeds per domain allow a repeatability signal, not a production guarantee.

## Status

Generation and first-pass visual QC are complete. See [QC.md](QC.md) and `manifest.json`. Results are exploratory workflow validation and are not promoted to a production baseline.
