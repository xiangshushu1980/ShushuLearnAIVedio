# [Sean] Initial visual QC — T-comfy-ops-48

Owner: Sean

## Test conditions

Four source anchors (eastern swordswoman, red mage, dwarf engineer, ice wolf); same per-character seed across variants; `QuadView_krea2_v1.safetensors`, 1536×1024, 10 steps, CFG 1, Euler/simple, ref boost 1. All 24 ComfyUI jobs completed successfully. Generation success only means the jobs produced files; visual performance has not been established. None of these images is canonical, and no image should proceed to H3 before Sean's individual review.

## Corrected review status

The earlier contact-sheet assessment was unreliable. The thumbnails made it difficult to distinguish views and led to incorrect claims about shoulders, face close-ups, and three-quarter angles. Sean's corrections supersede those claims:

- `A_shoulders_strict_side`: shoulders were not adequately visible. Do not treat this as a passing shoulder-bust result.
- `B_face_three_quarter_side` and `B2_face_threequarter_not_profile`: the outputs did not provide a clear three-quarter face as previously claimed.
- `C_face_strict_side`: the supposed face close-up is not clear; the result reads more like bust/full-body views.
- `D_threeview_front_threequarter_back`: the red mage result below does show a three-quarter view. This is one useful example, not evidence that the prompt is stable across characters.
- `E_threeview_front_strict_side_back`: prior stability claim is withdrawn pending individual review.

No variant is currently approved as a stable standard. Review one named image at a time; after Sean confirms the D/red-mage example, choose the next single image or a focused prompt change. Keep Dynamic deferred.

## Current single image for review

- Variant: `D_threeview_front_threequarter_back`
- Case: `red_mage`
- File: `/home/sean/projects/ComfyUI/output/sean_t48_quadview_stability_20260927_v1/D_threeview_front_threequarter_back/red_mage/result_00001_.png`
- Purpose: confirm whether this is the desired three-quarter angle before proceeding.

## Review sheets

Contact sheets are retained as navigation aids only and must not be used to assert visual pass/fail:

- `review/sean_t48_A_shoulders_strict_side.jpg`
- `review/sean_t48_B_face_three_quarter_side.jpg`
- `review/sean_t48_B2_face_threequarter_not_profile.jpg`
- `review/sean_t48_C_face_strict_side.jpg`
- `review/sean_t48_D_threeview_front_threequarter_back.jpg`
- `review/sean_t48_E_threeview_front_strict_side_back.jpg`

## Next gate

Wait for Sean's review of the single named image. Do not generate another batch or start H3 yet. After individual references are approved, crop each selected view into an independent image (never feed a composite sheet to H3) and follow the H3 validation gate before canonical packaging. DynamicCharacterSheet remains deferred.
