# [Sean] Qwen Image 2.1 character design sheet workflow smoke

## Goal

Test the linked Civitai V2.0 character-sheet workflow with a fully Qwen-generated source image. No Krea2 output, Krea2 model, or style LoRA is used.

## Workflow adaptation

- Original Civitai workflow files are preserved under `source_workflow/`.
- The original graph's `ThinkingLLM` prompt enhancer and `VAEDeGrid` node are not installed in the shared ComfyUI. To avoid changing/restarting the shared instance, this smoke uses the same Qwen Image 2.1 edit path and sheet layout intent, with a manually written concise prompt and the local int8 Qwen model stack.
- Output is 1536×1024 (1.57 MP) for the first smoke. Reference conditioning is set to 1024. The source page recommends 3.4 MP for balanced detail; a higher-resolution pass is deferred until this smoke is visually acceptable.

## Outputs

- `inputs/qwen_generated_fullbody.png`: prompt-only Qwen Image 2.1 source; no image references.
- `outputs/character_design_sheet.png`: initial layout with expressions, turnaround, and katana detail.
- `outputs/face_turnaround.png`: layout test with a large face portrait plus front/side/back views, using the same Qwen source.
- `outputs/face_front_back.png`: layout test with a close-up face portrait plus only front and back views.
- `api_workflows/`: exact local ComfyUI API graphs submitted for both stages.
- `manifest.json`: model settings, source workflow URL, deviations, seeds, timings, and output paths.

This is a first feasibility smoke, not a multi-seed consistency result.

## First smoke QC

The generated sheet contains the intended four-expression column, front/side/back full-body row, and one katana detail strip. Face, tied-back hair, navy uniform, silver shoulder/forearm armor, boots, and weapon family remain recognizable across views. The side and back views show useful hidden clothing structure. No extra character or text appeared. The result is clean enough to continue; the exact weapon construction and fine back details still need human review.

The Qwen-only source is photorealistic because no style adapter or explicit painterly style was used. This confirms the sheet workflow can follow a Qwen-produced source without Krea2; it does not yet establish the final art direction. Peak GPU memory observed by Hive was 17,798 MB; generation completed and the GPU lease was released.


## Upstream V3.0 update (2026-10-02)

CivitAI version 3377047 adds a `Simple` workflow with a static-prompt mode and bundles it with a `Production` workflow. It drops GGUF PE support in favor of Safetensors and rewrites the prompt-maker instructions. The image-edit subgraph still includes `VAEDeGrid`; the local shared ComfyUI does not have that node or the recommended Qwen 3.5 PE weight, so V3 is not a drop-in workflow here. Static-prompt mode can bypass PE, using the local int8 Qwen Image 2.1 path and the same standard-decode adaptation as this smoke. Original V3 graphs and version comparison are preserved under `source_workflow_v3/`.


V3.0 static-prompt smoke output: [`outputs/v3_simple_static.png`](outputs/v3_simple_static.png). This used the V3 built-in static prompt with a local Qwen int8 API graph and standard VAE decode in place of missing `VAEDeGrid`; it was not an unmodified workflow run.
