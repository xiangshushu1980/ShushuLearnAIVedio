# Qwen Image 2.1 appearance/depth role check — Frost Scout left side

Task: `remote-dc7a1512-0429-4264-9163-4378e1f6671b`  
Date: 2026-10-25  
Phase: second view, matched A/B across two new seeds

## Question and limits

The same frozen front appearance reference and a fixed left-profile prompt were compared with and without the matching Blender side depth map. This view changes the requested direction from the reference's frontal view, so it provides a more useful structure-transfer check than the first phase.

The source map is a normalized Blender Z pass from the Hunyuan3D mesh, 768×1024, 8-bit grayscale (`L`), camera direction `[1,0,0]`. Its silhouette and side profile are clear. A visible upper-back/rear-side projection is present, but the mesh has no semantic sub-parts; its identity is unresolved. Score it only as a geometric projection. Do not call it a correctly transferred pack, bow, or other named equipment.

## Inputs and fixed settings

The plan and exact prompt are in [`plan.json`](plan.json). The source image and depth map are copied into `inputs/` unchanged and their hashes match the source records.

- Appearance reference: 1024×1536 RGBA; SHA-256 `143533307a2b505a0137401d66ce1c3b46b0ac0fdbc1c7fe598780f92ec4d2ea`.
- Left-side depth: 768×1024 grayscale; SHA-256 `e3bccaa52e5f449d1be997c0941ab42df2af87371e2ddef9976a9c8a41db1d82`.
- Source GLB and camera/normalization facts: [`manifest.json`](../../qwen_3d_guided_cross_reference_20261024/frost_scout/blender-depth/manifest.json). Existing read-only review of the ambiguous projection: [`left_side_projection_review_20261025.md`](../../qwen_3d_guided_cross_reference_20261024/frost_scout/blender-depth/left_side_projection_review_20261025.md).
- Qwen Image 2.1 BF16 + Fun Control Union BF16; Qwen3-VL 8B INT8 encoder; BF16 VAE; no Character Sheet LoRA.
- 768×1024, 25 steps, CFG 1, Euler/simple; depth strength 0.5, interval 0.0–1.0.
- Seeds 423522 and 423523. Each pair uses the same appearance image, exact prompt, model, dimensions, sampler, and seed; only the depth-control branch is present or absent.

Graph checks: the appearance image connects only to `TextEncodeQwenImageEditPlus.image1`; `image2` remains disconnected. The side map connects only to `QwenImageDiffsynthControlnet.image` in the depth-guided workflow.

## Results

| Seed | Appearance-only | Appearance + depth | Visual comparison |
|---|---|---|---|
| 423522 | [output](seed_423522/appearance-only/output.png) · SHA `b157989542798d8c6822650866b2e83e64299460bde0f49759688fc0c57cf568` | [output](seed_423522/depth-guided/output.png) · SHA `847ffb814c2dc2a0c9ed23d4916cfad67a08ca05249d16197e96ad72dd29c42f` | Both face image-left in a complete profile. The depth output has a more distinct rear-side waist projection; the appearance-only image has a smaller tab-like shape there. |
| 423523 | [output](seed_423523/appearance-only/output.png) · SHA `59e229f48b0eb93129e7b628bb7c8a86e6923870afd97c94acea51c6867a087a` | [output](seed_423523/depth-guided/output.png) · SHA `3db969c06ee978d3a3bb20f835fa9f861635728e735e8a4690fa44cf42de0593` | Both face image-left in a complete profile. The depth output again has a more distinct narrow projection behind the torso around waist/hip height; its semantic identity remains unknown. |

All four images are 768×1024. The contact sheet is [`side_ab_contact_sheet.png`](side_ab_contact_sheet.png). Requests, actual graphs, prompt IDs, ComfyUI histories, receipts, output hashes, preflight, and cleanup records are retained per run.

### Appearance retention

Across both seeds and both conditions, the face/profile, gray hair and braid, quilted blue tunic, brown leather pieces, dark trousers, fur-lined boots, and overall painterly/rendered treatment remain visually consistent with the source reference. Depth addition does not visibly replace or recolor the character appearance in this sample. Side-view equipment and its semantics are not claimed as stable because the only appearance reference is frontal and the mesh projection is unlabeled.

### Structure transmission

All four outputs achieve the prompted left profile, so the view direction alone is not an incremental depth success: the prompt carries that target in both branches. In both matched seed pairs, the depth-guided result shows a more visible rear-side projection in the same general location as the source depth map. In seed 423522 the no-depth output already has a smaller tab-like feature, so the evidence is a repeated change in prominence/location rather than proof of a wholly new object. This is local evidence of geometry influencing silhouette, not evidence that depth supplies identity, palette, material, or prop semantics.

## Interim conclusion

The paired views show the intended separation in this bounded sample: the appearance reference is consistent with the retained identity and costume, while adding depth changes a broad side silhouette feature. The depth map's semantic ambiguity and small two-seed sample limit the conclusion. Across the front and side phases there are four seeds and two views of one character; this supports an initial observation but not a general stability claim or a cross-character conclusion.

A stronger correctness test for the rear projection requires a trusted side/back appearance reference or an independently accepted source inventory. No prompt color repair, negative color instruction, or shared preset change was made.

## Runtime and sources

- ComfyUI 0.42.1; all requested nodes and model choices were present in the live instance.
- Queue was empty before each submission and after output collection. GPU lease `df1d8609-7413-4079-8191-760dc1cd79ac` was acquired for this task and conversation, heartbeated, and released. Post-run current system sample: 20,382/24,564 MiB used, 47°C, 0% utilization. This is not a peak or task-attributed measurement; Hive observation `0e457756-37a8-41cf-a332-07323107f8e0` records that limit.
- Official Comfy-Org documentation lists the DiffSynth depth patch workflow and says depth input needs a preprocessed depth map: [Qwen Image in ComfyUI](https://github.com/Comfy-Org/docs/blob/main/tutorials/image/qwen/qwen-image.mdx).
- Official template: [Qwen Image ControlNet Patch](https://github.com/Comfy-Org/workflow_templates/blob/main/templates/image_qwen_image_controlnet_patch.json).
- Official docs establish the native workflow family and depth-map requirement. They do not establish behavior for the exact locally installed Fun Control Union BF16 weights used here; compatibility and all visual findings are local to these inputs, graph, seeds, and settings.
