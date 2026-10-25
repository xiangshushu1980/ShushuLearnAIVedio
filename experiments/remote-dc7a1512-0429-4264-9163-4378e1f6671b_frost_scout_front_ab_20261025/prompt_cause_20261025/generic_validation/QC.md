# Generic prompt + reference/depth validation QC

Status: six of six planned images completed. The contact sheet is `generic_validation_contact_sheet.png`; individual requests, prompts, graphs, receipts, histories, outputs and SHA-256 values remain beside each image.

## Per-image visual QC

- `front_seed_423490/appearance_only/output.png` — full figure is centered and frontal; both feet visible; warm neutral background and floor shadow retained. Blue clothing, brown leather and dark trousers remain visually distinct. Compared with the existing same-seed B depth-conditioned result, this no-depth image also retains colored materials. Bow is visible but not scored.
- `front_seed_423530/appearance_only/output.png` — same observations for seed 423530: centered frontal full figure, feet visible, material colors distinct. It pairs with the completed B depth-conditioned image at that seed.
- `left_profile_seed_423532/appearance_only/output.png` — clear left-facing profile and complete figure; material colors remain distinct. The bag/strap silhouette differs from the paired depth output, as expected for a stochastic image comparison.
- `left_profile_seed_423532/reference_plus_depth/output.png` — clear left-facing profile and complete figure. Clothing/leather/skin remain colored and materially separated. The generated silhouette and equipment placement differ from appearance-only; one pair cannot establish a general geometry gain.
- `left_profile_seed_423533/appearance_only/output.png` — clear left-facing profile and complete figure; color/material separation is visible.
- `left_profile_seed_423533/reference_plus_depth/output.png` — clear left-facing profile and complete figure; colors/materials remain distinct. The side silhouette is broadly consistent with appearance-only, with small pose/equipment changes.

## Interpretation and limits

The front no-depth rows preserve visibly colored materials with the exact frozen B target-only prompt for both tested seeds. The two left-profile depth-conditioned rows also retain visible color and material separation with the same generic target description adapted to a strict left-facing profile. This supports using the candidate graph for bounded Frost Scout front and left-profile runs at these settings. It does not prove identity, material or geometry fidelity, does not show depth improves the output in every criterion, and does not validate back views or another character. The side depth/no-depth pair changes a stochastic generation condition, so qualitative differences remain descriptive rather than a universal causal claim.

Bow or equipment correctness is outside this phase's scoring scope.

## Execution evidence

- All six receipts report `completed`; every receipt contains one output whose SHA-256 was rechecked after completion.
- Runner exited 0. Final ComfyUI queue was 0 running / 0 pending.
- New GPU lease `8b6cb017-30a4-497b-a7df-b401e1b61c2f` was released by the runner after terminal outputs and exact-hash temporary-input cleanup.
- `lease_released.json`, `temporary_inputs_removed.json`, `postrun_queue.json`, and `preflight.json` preserve lifecycle evidence.
- GPU floor is a conservative experiment guard inherited from prior successful samples, not a claimed model minimum.
