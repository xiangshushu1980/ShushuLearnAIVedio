# [Sean] Initial visual QC — T-comfy-ops-48

Owner: Sean

## Test conditions

Four source anchors (eastern swordswoman, red mage, dwarf engineer, ice wolf); same per-character seed across variants; `QuadView_krea2_v1.safetensors`, 1536×1024, 10 steps, CFG 1, Euler/simple, ref boost 1. All 24 ComfyUI jobs completed successfully. Generation success only means the jobs produced files; visual performance has not been established. None of these images is canonical, and no image should proceed to H3 before Sean's individual review.

## Corrected review status

The earlier contact-sheet assessment was unreliable. The thumbnails made it difficult to distinguish views and led to incorrect claims about shoulders, face close-ups, and three-quarter angles. Sean's corrections supersede those claims:

- `A_shoulders_strict_side`: shoulders were not adequately visible. Do not treat this as a passing shoulder-bust result.
- `B_face_three_quarter_side` and `B2_face_threequarter_not_profile`: the outputs did not provide a clear three-quarter face as previously claimed.
- `C_face_strict_side`: the supposed face close-up is not clear; the result reads more like bust/full-body views.
- `D_threeview_front_threequarter_back`: Sean confirmed the red mage result shows the desired three-quarter view. This is one useful example, not evidence that the prompt is stable across characters.
- `E_threeview_front_strict_side_back`: prior stability claim is withdrawn pending individual review.

No variant is currently approved as a stable standard. Review one named image at a time. Dynamic remains deferred.

## Confirmed example

- Variant: `D_threeview_front_threequarter_back`
- Case: `red_mage`
- Sean confirmed that its three-quarter angle meets expectations.

## Abandoned bust branch

Sean rejected half-body as the target: a crop from the full-body panel does not add generated detail. A2's generated bust also failed because the left shoulder armor was clipped. A3 is only a crop mock-up and is excluded from candidate layouts.

## Face-width status

The earlier `52/24/24` face-focused single preview showed a visibly larger face while retaining the front/back full-body views. This was a visual improvement in one preview, not a stable width result: the later comparison across `43/28.5/28.5`, `52/24/24`, and `60/20/20` returned to near-equal panel widths. Sean also judged the recent B/B2/C results insufficient to read as face close-ups.

## Previous single face-width sample (F)

- Variant: `F_face_focus_wide_left`
- Case: `red_mage`, seed `4801002`
- File: `outputs/sean_t48_F_face_focus_wide_left_red_mage.png`
- Visual assessment: face close-up is clearly readable and enlarged. The requested `52/24/24` panel ratio did not hold; the output looks approximately `36/32/32`. The full-body front and back views are present. The staff appears in the front view and matches the original red-mage anchor; it is naturally hidden from the back view.
- Overall: face scale passes this single visual check; controlled 52/24/24 panel width does not. The prop matches the source. Cross-character stability remains untested.

## Review sheets

Contact sheets are retained as navigation aids only and must not be used to assert visual pass/fail:

- `review/sean_t48_A_shoulders_strict_side.jpg`
- `review/sean_t48_B_face_three_quarter_side.jpg`
- `review/sean_t48_B2_face_threequarter_not_profile.jpg`
- `review/sean_t48_C_face_strict_side.jpg`
- `review/sean_t48_D_threeview_front_threequarter_back.jpg`
- `review/sean_t48_E_threeview_front_strict_side_back.jpg`

## Next gate

Wait for Sean's review of the single named image. Do not generate another batch or start H3 yet. The experiment directory is the user-facing home for this run: prompts, manifest, QC, and selected outputs live together under this directory. After individual references are approved, crop each selected view into an independent image (never feed the composite sheet to H3) and follow the H3 validation gate before canonical packaging. DynamicCharacterSheet remains deferred.


## Current single face-scale retest (G)

- Variant: `G_face_focus_60_left`
- Case: `red_mage`, seed `4801002`
- File: `outputs/sean_t48_G_face_focus_60_left_red_mage.png`
- Compared with F, the face fills more of the left panel. The panel itself remains approximately 36% of the image width even though the prompt requests 60%.
- Front/back full-body views remain visible; the staff matches the source anchor.
- Assessment: face-scale increase passes for this one image. Pixel-level panel-width control still fails. Cross-character stability is untested.
