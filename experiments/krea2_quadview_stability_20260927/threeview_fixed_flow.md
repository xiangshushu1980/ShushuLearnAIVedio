# [Sean] Character reference pipeline — stages 1–2

Owner: Sean  
Task: T-comfy-ops-48

## Workflow contract

The variable layer is each role's detailed design prompt. The fixed layer is the generation recipe and the view layout. A new role changes its prompt and seed; it does not change the fixed style or view prompts. Copy `../krea2_role_reference_20260927/manifest_template.json` to start a new role batch; edit each case's `id`, `seed`, and `character_prompt` only.

### Stage 1 — design the canonical front image

- Current baseline is text-to-image from an empty latent: no default image, identity reference, or Shushu image is connected.
- Each case supplies a detailed `character_prompt` for face, hair, body, clothing, weapons and signature accessories.
- Fixed style: Krea2 Turbo, `Jibs_Krea_2_Midjourney_Fantasy_Style_V1.safetensors` at 1.0, trigger `M1djourneyArtStyle`.
- Fixed composition: one centered, full-body, front-facing character on a controlled studio background. Keep the full silhouette and carried items inside the frame.
- Runner: `scripts/krea2_role_t2i_jibs_batch.py`.
- Review the image before Stage 2. Approve only if the face/design is distinct, the full body and signature items are visible, and no unintended identity or props appear.
- This baseline has no image input. If a design needs face, wardrobe, weapon or prop references, those images must be assigned explicit semantic roles in a future input-capable Stage 1 graph; never use an arbitrary reference as the identity anchor.

### Stage 2 — derive the three-view sheet

- Input: the approved Stage 1 image for that same role.
- Fixed prompt candidate (short version): `Three-view Character Sheet: left face close-up, center full-body front, right full-body back. Exactly three views total, no side view, no extra pose, no repeated view. Preserve the same character identity, hair, costume, and equipment in every view.`
- Fixed setup: Krea2 Turbo + `QuadView_krea2_v1.safetensors` at 1.0; 1536×1024; 10 steps; CFG 1; Euler/simple; ref boost 1.0; grounding 768; positive grounding 0.
- Runner: `scripts/krea2_threeview_reference_batch.py`.
- Review the three views for matching face, outfit, silhouette and signature items. If Stage 1 cropped an item, regenerate Stage 1 first; Stage 2 cannot restore missing design information reliably.

Before either stage, check the shared ComfyUI queue and use `hive-resource` for the GPU lease. Stage 1 and Stage 2 are separate runs so the main design can be reviewed before producing its three-view sheet.

The future H3 `object_description` is a separate field from `character_prompt`. Do not copy generation-only language such as art style, camera framing or studio background into the H3 object description. H3 is outside this stage and was not run.

## Root cause found in the earlier six-image batch

The six Stage 2 input files were correctly mapped to six different filenames, but those files had been created earlier with a faulty Stage 1 graph: all six used `ref2va_refs/fellow/processed/shushu_identity_rebuilt_v2_cap.png` as the Krea2 Edit image input, and `Jibs_Krea_2_Midjourney_Fantasy_Style_V1` had strength `0.0`. Their role-specific text differed, but the shared Shushu image could bias the generated faces. Those six samples only support a preliminary view-count result; they do not establish independent role identity fidelity or the intended Jibs-style pipeline.

## Corrected text-to-image and three-view runs

On 2026-09-27, two roles were generated from text with an `EmptyLatentImage`, the Jibs trigger and Jibs LoRA strength 1.0, then passed to Stage 2 with the fixed three-view prompt:

| Role | Stage 1 | Stage 2 | Total | Review |
|---|---:|---:|---:|---|
| Eastern swordswoman | 15.02 s | 27.08 s | 42.10 s | Face and outfit distinct; three views present and coherent. |
| Red mage initial | 9.05 s | 21.08 s | 30.13 s | Distinct face and outfit; staff cropped in Stage 1. This image was superseded after improving Stage 1 framing. |
| Red mage framing retry | 15.02 s | 27.10 s | 42.12 s | Staff fully inside Stage 1 image, but the old fixed prompt produced four panels with a duplicated back view. |

The framing retry was reused for two same-seed prompt probes. The verbose prompt beginning `Create exactly three views...` produced three clean panels in 21.08 s. The compact prompt above also produced three clean panels, preserved the full staff and all three views in 21.07 s. The compact prompt is the current fixed candidate. These two probes share one character and seed, so they show that the prompt can fix this observed layout failure, but do not yet prove cross-role stability. Stage 2 therefore remains a fixed, fast process with mandatory output review, not a guaranteed layout.

The sample outputs and full prompts/seeds are recorded under `../krea2_role_reference_20260927/`, including the framing retry and both prompt probes. Stage 1 is currently text-only; it does not accept image references. Later, an input-capable design stage may support explicitly assigned face/prop/weapon/clothing references, but it must not silently reuse a default identity image. The second stage intentionally uses its selected Stage 1 image as the reference.
