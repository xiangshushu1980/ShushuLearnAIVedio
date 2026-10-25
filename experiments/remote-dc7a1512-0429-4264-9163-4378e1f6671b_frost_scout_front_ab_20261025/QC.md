# Qwen Image 2.1 appearance/depth role check — Frost Scout front

Task: `remote-dc7a1512-0429-4264-9163-4378e1f6671b`  
Date: 2026-10-25  
Phase: initial front-view matched A/B across two new seeds

## Question and limits

With one frozen Frost Scout appearance reference and one fixed prompt, compare appearance-only against the same inputs plus a Blender frontal depth map applied through `QwenImageDiffsynthControlnet`. The reference and prompt already request a frontal full-body view; this is useful for checking whether appearance remains stable when depth is added, but it is a weak setup for measuring a new view direction because the baseline is already frontal.

The grayscale depth input visibly carries a full-body silhouette, upright stance, arm spacing, and boots. It does not visibly encode the bow or satchel as distinct objects. Equipment visible in output is therefore credited to the appearance reference and prompt, not to depth transfer.

## Inputs and fixed settings

See [`plan.json`](plan.json) for the verbatim prompt, roles, source URLs, and complete input hashes. Inputs were copied into this directory without modification; SHA-256 values match the recorded sources.

- Appearance reference: 1024×1536 RGBA; SHA-256 `143533307a2b505a0137401d66ce1c3b46b0ac0fdbc1c7fe598780f92ec4d2ea`.
- Frontal depth: 768×1024, 8-bit grayscale (`L`); SHA-256 `7a7b47af376c7cd5d2adf5e7c538f3d3975fc3f992879794e86eb5406678f011`.
- Qwen Image 2.1 BF16 + Fun Control Union BF16; Qwen3-VL 8B INT8 encoder; BF16 VAE; no Character Sheet LoRA.
- 768×1024, 25 steps, CFG 1, Euler/simple; depth strength 0.5, interval 0.0–1.0.
- Seeds 423520 and 423521. Within each pair only the depth-control branch is added or absent. Appearance reference, prompt, model family, canvas, sampler, and seed stay fixed.

Graph checks: the appearance image connects only to `TextEncodeQwenImageEditPlus.image1`; `image2` is disconnected. In the depth-guided graph, the grayscale map connects only to `QwenImageDiffsynthControlnet.image`. In appearance-only, the ControlNet branch is absent.

## Results

| Seed | Appearance-only | Appearance + depth | Visual comparison |
|---|---|---|---|
| 423520 | [output](seed_423520/appearance-only/output.png) · SHA `e2443e094998e4e6fdabbaf522df944c33e80563845f2270a4d5d0d393bb02d8` | [output](seed_423520/depth-guided/output.png) · SHA `680fdcb5e9ba5ba9267f721b25ef958ad37b19d4e085f59fab4095c1e01e30ae` | Same identity and costume; depth output has small silhouette/framing differences. Both already read as frontal full-body views. |
| 423521 | [output](seed_423521/appearance-only/output.png) · SHA `6b2b057a5c771232ce7ef33becee96b0bff9fe1fe78b5edc0c2f1296f55adc93` | [output](seed_423521/depth-guided/output.png) · SHA `9fbbb95a8343c9ac8b915e2cdeca2fdc89efe288665d5dea35c7cc91c42283da` | Same identity and costume; depth output changes the pose/silhouette subtly, without a clear new structural feature absent from baseline. |

Each output is 768×1024. Per-run requests, actual graphs, prompt IDs, ComfyUI histories, receipts, output hashes, preflight, lease release, and post-run empty queue are retained alongside the images. Visual board: [`front_ab_contact_sheet.png`](front_ab_contact_sheet.png).

### Appearance retention

Across both seeds, the depth-guided outputs retain the same face, gray braid, blue quilted tunic, brown leather shoulder pieces, dark trousers, and fur-lined boots seen in the appearance reference. Palette and material separation remain visually consistent in this four-image sample. The bow and satchel also remain visible in both branches; because they are already prominent in the appearance reference and are not discernible as separate objects in the frontal depth input, this does not establish depth-driven equipment transfer.

### Structure transmission

The depth-guided images remain full-body and frontal, matching the silhouette/stance represented in the control map. However, the appearance-only outputs already have the same frontal camera direction and nearly the same stance from the reference and prompt. The incremental structural effect is small and not strong enough here to claim reliable silhouette or pose transfer. The depth map's role remains structural by graph design; visual output differences do not imply that it supplied identity, style, palette, or materials.

## Interim conclusion

This initial phase supports that adding the tested depth branch did not visibly disrupt Frost Scout identity or costume appearance across two seeds. It does not yet provide strong evidence of useful incremental structure transfer because the appearance reference and prompt already specify the same frontal view. No color statistics were used, no prompt color repair was added, and no claims are made about guarantees or cross-character stability.

Next: use the same frozen appearance reference with an existing left-side depth render and a fixed side-view prompt. The side-view pair gives the depth map a more distinct structural target than the frontal pair.

## Runtime and sources

- ComfyUI 0.42.1; required node schemas present, including `QwenImageDiffsynthControlnet` strength/start/end fields.
- Shared queue was empty before each submission and after collection. GPU lease `2a97d2f8-1b0e-422b-bb09-320e34bffcaf` was acquired with this task and current conversation metadata, heartbeated, and released after all outputs were collected. Post-run current system sample: 21,231/24,564 MiB used, 41°C, 0% utilization. This is a system-wide point sample, not a task-attributed or peak measurement; Hive observation `5a2983a7-80bc-4453-9c12-5d7aac137c1b` records that limit.
- Official Comfy-Org guide lists DiffSynth depth patches and says the depth input should be preprocessed into a depth map: [Qwen Image in ComfyUI](https://github.com/Comfy-Org/docs/blob/main/tutorials/image/qwen/qwen-image.mdx).
- Official template demonstrates the model-patch workflow: [Qwen Image ControlNet Patch](https://github.com/Comfy-Org/workflow_templates/blob/main/templates/image_qwen_image_controlnet_patch.json).
- Official documentation establishes the native workflow family and depth-map requirement. It does not establish behavior for the exact locally installed Fun Control Union BF16 weights used here; compatibility and visual results for those weights are local observations for this graph and these seeds only.
