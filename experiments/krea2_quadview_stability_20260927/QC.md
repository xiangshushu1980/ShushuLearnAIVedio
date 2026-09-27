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

## Current single image for review

- Variant: `A2_waistup_shoulders`
- Case: `red_mage`
- File: `outputs/sean_t48_A2_waistup_shoulders_red_mage.png`
- Prompt: removed face-close-up emphasis; requested a waist-up first panel with shoulders and upper arms.
- Visual note: the panel extends to the waist and shows the shoulder armor, but the left shoulder armor is clipped at the image edge. Await Sean review before calling this sufficient.

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
