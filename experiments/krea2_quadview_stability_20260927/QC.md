# [Sean] Initial visual QC — T-comfy-ops-48

Owner: Sean

## Test conditions

Four source anchors (eastern swordswoman, red mage, dwarf engineer, ice wolf); same per-character seed across variants; `QuadView_krea2_v1.safetensors`, 1536×1024, 10 steps, CFG 1, Euler/simple, ref boost 1. All 24 ComfyUI jobs completed successfully. This is an initial visual review; Sean's manual review is still required before any H3 use. None of these images is canonical.

## Findings

| Variant | Initial visual result | Assessment |
|---|---|---|
| A — shoulders + strict side | Four panels appear in all four outputs. The first panel reads as an upper-body portrait and keeps the shoulder/armor area visible; some shoulder edges sit close to the crop. | Good candidate for the shoulder-bust use case; manual check should confirm both shoulder edges are sufficiently shown. |
| B — face + three-quarter side | Four panels appear. Sword, mage, and wolf show an oblique side; dwarf falls back to a near-profile. | Angle wording is not stable enough across all four. Retained as the weaker prompt comparison. |
| B2 — face + three-quarter side, not profile | Four panels and a clear face panel appear in all four outputs. All four side panels visibly turn partway toward camera. | Best current fixed four-view candidate for the three-quarter side use case. |
| C — face + strict side | Four panels appear in all four outputs. Face close-up and strict side are clear; front and back remain distinct. | Best current fixed four-view candidate for the face-focused standard. |
| D — three-view front + three-quarter + back | Three panels appear. Mage, dwarf, and wolf distinguish the oblique side; swordswoman repeats a near-front view. | Not stable enough as the default three-view prompt. |
| E — three-view front + strict side + back | Three distinct full-body views appear in all four outputs. The side profile is visibly separate from the front and back. | Best current three-view candidate. |

Panel width and exact layout proportions remain approximate; the prompt reliably changes panel content/count more than pixel-level width. The four-case test does not establish H3 identity retention.

## Review sheets

- `review/sean_t48_A_shoulders_strict_side.jpg`
- `review/sean_t48_B_face_three_quarter_side.jpg`
- `review/sean_t48_B2_face_threequarter_not_profile.jpg`
- `review/sean_t48_C_face_strict_side.jpg`
- `review/sean_t48_D_threeview_front_threequarter_back.jpg`
- `review/sean_t48_E_threeview_front_strict_side_back.jpg`

## Next gate

After Sean confirms the shoulder-bust, face-focused, and three-view candidates, crop each view into an independent image (do not feed the composite sheet to H3) and run a matched 4–15 second Ref2VA comparison against the original source anchor. Only H3-reviewed assets may be considered for canonical packaging. DynamicCharacterSheet remains deferred.
