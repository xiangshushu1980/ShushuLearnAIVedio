# [Sean] Matched three-view / four-view QC — T-comfy-ops-48

Owner: Sean
Status: preliminary visual review; not canonical; no H3 run.

## Design

Four clean, role-specific text-to-image anchors were freshly generated with the Jibs style LoRA at 1.0: an eastern swordswoman, red mage, dwarf engineer, and horned lizard warrior. The first lizard anchor had a three-quarter head/body angle, so a stricter front-facing replacement was generated and tested separately. The two downstream layouts use identical per-anchor inputs across matched seeds and the same Krea2 Turbo / QuadView settings: `1536×1024`, 10 steps, CFG 1, Euler/simple, QuadView LoRA 1.0, ref boost 1.0, grounding 768, positive grounding 0. The base four roles each have two seeds; the corrected lizard anchor has two additional matched seeds. This gives ten outputs per layout, twenty total.

The retained `ref_*.png` inputs from the older batch were excluded: their embedded workflow metadata shows they all used the same Shushu image reference and Jibs strength 0. This batch uses the fresh role anchors under `role_anchors/outputs/`.

## Per-image review

| Layout | Role / seeds | Panel and angle check | Identity / outfit / signature item | Result |
|---|---|---|---|---|
| 3-view | Eastern swordswoman / 4803101, 4803111 | Both have face close-up, front full body, back full body | Face, hair, armor, coat and sword remain coherent in both | Pass 2/2 |
| 3-view | Red mage / 4803102, 4803112 | Both have the requested three panels | Face, braids, burgundy outfit, blue pendant and front-view staff match in both | Pass 2/2 |
| 3-view | Dwarf engineer / 4803121, 4803131 | Both have the requested three panels | Face, beard, cap, apron and hand tools match; tool pack is represented on the back | Pass 2/2 |
| 3-view | Horned lizard warrior, angled source / 4803122, 4803132 | Both have three panels; center angle remains three-quarter, matching the source anchor's own angle | Scales, horns, armor, tail, spear and shield match | Panel pass; source-angle carry-through |
| 3-view | Horned lizard warrior, corrected front source / 4803141, 4803142 | Both have the requested face, straight-on front, and back panels | Scales, horns, armor, tail, spear and shield match | Pass 2/2 |
| 4-view | Eastern swordswoman / 4803101, 4803111 | Both have face, front, strict side profile and back | Identity, armor and sword remain coherent in both | Pass 2/2 |
| 4-view | Red mage / 4803102, 4803112 | Both have four panels and a clear side profile | Face and clothing match, but the signature staff is absent from the whole sheet in both | Fail: equipment fidelity 2/2 |
| 4-view | Dwarf engineer / 4803121, 4803131 | Both have face, front, side profile and back | Face, beard, cap, apron and tools remain coherent; tool kit appears from front/side/back | Pass 2/2 |
| 4-view | Horned lizard warrior, angled source / 4803122, 4803132 | Both have face, front, side and back views | Species identity, horns, scales, armor and tail match; spear and shield are absent from both sheets | Fail: equipment fidelity 2/2 |
| 4-view | Horned lizard warrior, corrected front source / 4803141, 4803142 | Both have face, front, side and back views | Species identity, horns, scales, armor and tail match; spear and shield are again absent | Fail: equipment fidelity 2/2 |

## Interim finding

- Structural layout repeated in every run: 3-view produced 10/10 exact three-panel sheets; 4-view produced 10/10 exact four-panel sheets with a side view.
- Face close-ups track the full-body identity in all reviewed samples; the old male red-mage face/body mismatch did not recur on these clean anchors.
- The three-view layout preserved signature items in all ten outputs. On the angled lizard source it repeated the source's three-quarter facing; when the source was regenerated front-facing, both three-view results showed the expected straight-on front.
- The four-view layout preserved the sword for the swordswoman and tools for the dwarf (4/10 outputs with full signature-item fidelity). It dropped the staff for the red mage in 2/2 seeds and dropped both spear and shield for the lizard in 4/4 seeds, including both runs on the corrected front-facing source. The layout is structurally stable in this sample but not reliable for equipment-complete sheets across roles.
- Four roles across two seeds, plus a corrected lizard-anchor pair, provide broader evidence but still do not establish universal stability, precise crop geometry, or downstream H3 identity retention. No output is canonical and H3 was not run.

## Artifacts

- Role anchors and prompt provenance: `role_anchors/manifest.json`
- Three-view prompt, settings and run IDs: `three_view/prompt.md`, `three_view/manifest.json`
- Four-view prompt, settings and run IDs: `four_view/prompt.md`, `four_view/manifest.json`
- Images are retained in each layout's `outputs/` directory. Temporary ComfyUI inputs and this batch's ComfyUI output files were removed after copying.
