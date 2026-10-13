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


## Face-scale prompt and strength ladder

All valid runs use the same red-mage anchor, seed `4801002`, 1792×1024 canvas, and sampler settings. The concise J2 prompt is reused for the strength comparison.

| Run | LoRA strength | Visual result |
|---|---:|---|
| G | 1.0 | Face visibly larger than F; best current face-scale result. Left panel stays near 36%, not 60%. |
| H / I / J2 | 1.0 | Stronger “fill the panel” wording did not clearly increase the face beyond G; shoulder/chest crop wording was not followed. |
| K | 0.8 | No clear additional face enlargement; layout similar. |
| L | 0.6 | No clear additional face enlargement; three views remain. |
| M | 0.4 | No meaningful width gain; visibly blurry and costume texture drifts. Rejected. |

Conclusion: the prompt can enlarge the face versus F, but QuadView does not honor requested panel ratios and stronger wording/lower LoRA strength have not enlarged it further. For more generated face detail, evaluate a dedicated face-close-up generation path instead of cropping the full-body view. Cross-character stability of G is still untested.

## Resolution test (N)

- Variant: `N_face_focus_2048_width`
- Case: `red_mage`, seed `4801002`, LoRA `1.0`
- Change from G: canvas width only, from `1792×1024` to `2048×1024`; prompt and sampler settings held fixed.
- Result: face remains sharp and gains more absolute pixels; the front and back full-body views remain present. The left panel is still only about 40% of canvas width, rather than the requested 60%, so widening the canvas improves available face detail but does not reliably control panel proportions.
- Output: `outputs/sean_t48_N_face_focus_2048_width_red_mage.png`
- Sean accepted this image as a candidate.

## Narrower canvas test (N2)

- Variant: `N2_face_focus_1920_width`
- Case: `red_mage`, seed `4801002`, LoRA `1.0`
- Change from N: canvas width only, from `2048×1024` to `1920×1024`.
- Result: face is still sharp, but the model generated four views, including a duplicated front view, despite the unchanged three-view prompt. This does not pass the requested stable three-view layout. Width reduction is therefore not accepted as an improvement; use N as the current candidate.
- Output: `outputs/sean_t48_N2_face_focus_1920_width_red_mage.png`
- File size: about `2.22 MiB`; N is about `2.25 MiB`. The small width change barely affects file size.

## Final capability summary and official QuadView settings

Sean's final review narrows this task to the static `QuadView_krea2_v1` LoRA only; no Ref2VA video test is part of this stage.

The official [CharacterSheet model card](https://huggingface.co/Alissonerdx/CharacterSheet) and [QuadView Krea2 workflow](https://huggingface.co/Alissonerdx/CharacterSheet/blob/main/workflows/QuadView_krea2_v1.json) specify the intended four-view sheet: face close-up, full-body front, full-body side, and full-body back. The recommended baseline is Krea 2 Turbo, `1536×1024`, 10 steps, CFG 1, Euler/simple, and LoRA strength 1.0. The model card's trigger prompt is: “Convert the character in the image to a Character Sheet showing a face close-up, front full body, side full body and back full body views.” The workflow notes 8 steps can favor composition adherence and 12 can add facial detail; 10 is the balanced default. It also says to keep the sheet near 1 MP and go higher mainly for single-person edits.

This experiment's `2048×1024` face-focused run is above the official recommended sheet resolution; its good single-image result does not make that the stable baseline. The height was always 1024; 2048 was the width. The failed `1920×1024` run and 2048 test should be interpreted as layout probes, not official-configuration stability tests.

| Requested composition | Current evidence |
|---|---|
| F + W | Not stable: one 2048×1024 exploratory generation added a duplicate front panel. It was not repeated at the official baseline. |
| F + W + B | Supported as a three-panel prompt variant; Sean accepted the red-mage N image. Panel widths remain approximate. |
| F + W + B + S | The official four-view target is F + W + S + B. Use the official baseline prompt/settings; per-view identity and exact panel width still require QC. |
| F + W + B + S + Q | No official five-view layout and no stability evidence; do not treat it as supported. |

Across the reviewed runs, QuadView behaves primarily as a learned three/four-panel layout. It can produce front, side/three-quarter, and back views, and a three-panel face/front/back variant was accepted. It does not reliably make a shoulder-inclusive bust or obey exact panel-width ratios; approximate width changes are possible but not a dependable control. The official model card also cautions that view consistency is not perfect and side/back views may need reruns or cleanup.

The earlier exploratory F+W+B rerun was interrupted and its temporary input removed. One separate 2048×1024 exploratory F+W output was removed to keep the user-facing output directory clear. Sean then requested a final matched FWB/FWBS pair at the official recommended resolution; results follow.

## Final recommended-resolution pair (red mage)

Both tests use the same source anchor, seed `4801002`, `1536×1024`, Krea 2 Turbo, QuadView LoRA `1.0`, 10 steps, CFG 1, Euler/simple, ref boost 1.0, grounding 768 (positive 0).

| Set | Prompt layout | Visual QC | Output |
|---|---|---|---|
| FWB | Face close-up + front full body + back full body | Exactly three panels; face is clearly enlarged, front/back are full body. No duplicate panel. | `outputs/sean_t48_FINAL_FWB_1536_red_mage.png` |
| FWBS | Official face close-up + front + side + back full-body layout | Exactly four panels; side is a clear strict profile, front/back remain distinct. No duplicate panel. | `outputs/sean_t48_FINAL_FWBS_1536_red_mage.png` |

This is the apples-to-apples final pair at the model card's recommended output resolution. Both requested layouts generated successfully for this red-mage seed. It confirms these two layouts for this sample only; view-to-view identity and cross-character stability still require human QC and additional cases. No Ref2VA generation was performed.

## [Sean] Visual re-review and cleanup record — 2026-09-28

The prior panel-count review did not check whether the face panel matches the full-body views. Re-reviewing the actual images changes the acceptance result:

- `FINAL_FWB_1536` and `FINAL_FWBS_1536` have the requested three/four distinct panels, but **both fail identity QC**. The retained red-mage source anchor is a male character; the generated face close-up is visibly a different, female-looking character while the full-body views remain male. Neither output is an acceptable reference package.
- `output/sean_step2_threeview_red_mage_retry/red_mage/threeview_00001_.png` has a repeated back view (four panels total). The compact and exact-three prompt probes for the separate female red-mage design produced three panels on the same source and seed; this is a useful fix example, not cross-role stability evidence.
- `output/sean_t48_quadview_stability_20260927_v1/N2_face_focus_1920_width/red_mage/result_00001_.png` has four panels despite the three-view prompt: it repeats the front view. The changed canvas width is not a reliable layout control.
- The official four-view layout (face/front/side/back) is structurally achievable in the final 1536×1024 sample, but the identity failure above rejects that sample. Strict-side versus three-quarter selection, shoulder framing, and cross-character repeatability remain unstable or unproven.
- Six older `threeview_verify_2/4` cases passed panel-count review, but their source images share an upstream Shushu image reference. They cannot establish independent identity fidelity for those roles.

Input cleanup on the same date found nine SHA-256 duplicate groups (72 copies); one manifest-compatible representative per group remained in `ComfyUI/input`, and 63 redundant copies were moved to `ComfyUI/temp/ref_input_duplicates_20260928/`. The duplicate inventory is in that directory's `cleanup_manifest.json`. Current T48 manifest source paths were verified after cleanup.

Generated images are exploratory evidence only; no image in this batch is promoted to canonical. The final file-retention action is recorded in `manifest.json` after cleanup.

### Final retention action

At Sean's request, regeneration artifacts were removed after recording their QC: 74 Krea2/QuadView images from the shared ComfyUI output tree and 33 image copies/previews from the experiment folders. The 63 quarantined exact-duplicate input copies and three unused legacy input aliases were also permanently deleted. Total removed: 173 files (about 319 MiB). The six T48 source anchors used by the current manifests remain in `ComfyUI/input`; scripts, prompts, seeds, workflow settings, manifests, run logs, and this review remain. No H3 video was deleted.
