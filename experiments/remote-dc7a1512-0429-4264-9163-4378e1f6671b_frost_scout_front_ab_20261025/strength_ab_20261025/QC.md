# Strength dose response QC

Task: `remote-dc7a1512-0429-4264-9163-4378e1f6671b` · Frost Scout frontal view · two matched seeds.

## Question and fixed variables

Does raising the frontal depth ControlNet strength from 0.50 to 0.75 or 1.00 visibly wash out the appearance-reference palette?

For each seed, the same appearance reference, prompt, model files, 768×1024 canvas, 25 steps, CFG 1, Euler/simple sampler, and depth interval 0–1 were held fixed. The four conditions were appearance-only and the same branch with the depth map at strength 0.50, 0.75, and 1.00. Two seeds (423530, 423531) yielded eight completed images. The appearance image is `inputs/appearance_reference.png` (SHA256 `143533307a2b505a0137401d66ce1c3b46b0ac0fdbc1c7fe598780f92ec4d2ea`); the frontal depth map is `inputs/front_depth.png` (SHA256 `7a7b47af376c7cd5d2adf5e7c538f3d3975fc3f992879794e86eb5406678f011`).

## Visual finding

Across both seeds, higher depth strength did **not** produce an obvious gray or desaturated look. The dark blue jacket and brown leather remain visibly distinct at 0.75 and 1.00. Strength 1.00 appears somewhat darker in places and gives a more pronounced floor/shadow region, but the palette remains present. On this sample, the claim “increasing depth strength to 0.75/1.00 is enough to make the image gray” is not supported.

There is a separate appearance-retention issue in seed 423530: the appearance-only output retains the tall bow visible in the reference, while all three depth-conditioned outputs omit it. The depth map does not encode that bow. Seed 423531 retains the bow across all four branches. This is a one-seed interaction worth tracking, not evidence that depth supplies appearance or that higher strength uniquely caused the omission.

The contact sheet provides the primary visual comparison: [strength_contact_sheet.png](strength_contact_sheet.png).

## Auxiliary whole-image color summary

These simple whole-image means include the off-white background and shadows, so they are descriptive only and cannot replace visual review or isolate garment colors.

| Seed | Condition | Mean luminance | Mean HSV saturation |
|---:|---|---:|---:|
| 423530 | appearance-only | 0.8052 | 0.1301 |
| 423530 | depth 0.50 | 0.8067 | 0.1252 |
| 423530 | depth 0.75 | 0.8034 | 0.1318 |
| 423530 | depth 1.00 | 0.7865 | 0.1389 |
| 423531 | appearance-only | 0.7975 | 0.1502 |
| 423531 | depth 0.50 | 0.7715 | 0.1596 |
| 423531 | depth 0.75 | 0.7739 | 0.1589 |
| 423531 | depth 1.00 | 0.7557 | 0.1742 |

There is no monotonic saturation decrease with strength in either seed; whole-image luminance does fall at 1.00 in these two samples. This supports the visual observation of some darkening without palette washout, not a general color guarantee.

## Run matrix and evidence

| Seed | Appearance only | Depth 0.50 | Depth 0.75 | Depth 1.00 |
|---:|---|---|---|---|
| 423530 | [image](seed_423530/appearance-only/output.png) | [image](seed_423530/depth-050/output.png) | [image](seed_423530/depth-075/output.png) | [image](seed_423530/depth-100/output.png) |
| 423531 | [image](seed_423531/appearance-only/output.png) | [image](seed_423531/depth-050/output.png) | [image](seed_423531/depth-075/output.png) | [image](seed_423531/depth-100/output.png) |

Every run folder includes its prompt, workflow, submission, history, receipt, and output SHA256. `preflight.json`, `postrun_queue.json`, exact temporary upload cleanup and lease release record the shared-service lifecycle.

## Scope and next diagnostic

This tests one character in one frontal setup with one depth map, one appearance reference and two seeds. It does not reproduce or rule out every setting in the earlier promotional-image workflow. If the original image is still gray, compare its exact workflow and inputs against this baseline, then isolate depth preprocessing/map quality, strength interval and any other changed conditioning one variable at a time. Do not treat this result as a color guarantee or infer that depth carries palette/material information.
