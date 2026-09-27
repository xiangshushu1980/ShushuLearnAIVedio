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


## Face-panel lower-edge comparison (same restored workflow)

The prior ComfyUI execution graph was recovered from history (`FINAL_FWBS_1536`, prompt ID `2f68fc90-8cea-42b1-bb34-f11611702535`) and reused at 1536×1024 with the same Krea 2 Turbo, QuadView LoRA 1.0, 10 steps, CFG 1, Euler/simple, ref boost 1.0, and grounding settings. The cleaned transient source named in history is no longer present; its stored content hash matches the retained T48 red-mage anchor used for these tests. No compositing or border node is in the executed graph; it decodes and saves one image.

Eight prompt/seed comparisons are saved under `outputs/border_compare/`; the contact sheet is `outputs/border_compare/sean_t48_white_border_comparison_contact_sheet.png`. The two original final outputs also serve as controls.

| Comparison | Result |
|---|---|
| Official four-view prompt, repeated at seeds 4801003 and 4801012 | Four views remain; the face inset's lower white edge appears in both. |
| Remove the `face close-up` item | The face inset disappears and a front view duplicates; not a valid fix. |
| Replace `Character Sheet` with `reference layout` | Face inset and lower edge remain; this phrase alone is not the cause. |
| Add “no frames or borders” to the official prompt | Face inset and lower edge remain; negative wording does not suppress it. |
| Reuse the earlier explicit three-view prompt at the same source/resolution | Face/front/back layout is retained and the face panel reaches the canvas bottom without the lower edge. |
| Two four-view prompts explicitly aligning the face panel to top/bottom edges | The four views remain, but the face-panel lower edge persists in both. |

Conclusion: the line is generated as part of the image, not added by workflow post-processing. The evidence does not implicate `face close-up` alone or the phrase `Character Sheet` alone. The generic learned four-view composition repeatedly renders the face as an inset panel with a lower boundary. The older detailed three-view wording avoids that boundary; the same attempt to force edge-to-edge treatment has not yet removed it in four-view outputs. This is a prompt/layout interaction observed on the red-mage sample, not proof of a universal rule.
