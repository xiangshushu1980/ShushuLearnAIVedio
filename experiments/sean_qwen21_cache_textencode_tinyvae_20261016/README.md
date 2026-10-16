# [Sean] Qwen Image 2.1 cache, reference encode, Tiny VAE preview smoke

## Scope

Three same-seed 1024×1024, 8-step Qwen Image 2.1 Turbo runs using the same prompt and the same four ordered references (identity, uniform, armor, katana). `TextEncodeQwenImage21` received all four images; `ModelPreviewOverrideKJ` used the Qwen Tiny decoder for live sampling previews; `VAEDecode` used the normal BF16 VAE for the saved final image.

## Runtime

- ComfyUI `v0.40.0`, RTX 4090, shared queue empty at submission; GPU lease `0fd50914-3b78-4c38-88f4-4a78ab8d08b9`.
- Model: `qwen_image_2.1_turbo_int8_convrot.safetensors`; text encoder: `qwen3vl_8b_int8_convrot.safetensors`; final VAE: `qwen_image_2.1_vae_bf16.safetensors`.
- Seed 421016, Euler/simple, CFG 1.0, 8 steps, resolution 1024, same prompt and references.
- Preview decoder: `taeqi2_1_decoder.pth`; standard BF16 VAE remains the output decoder.

## Results

| Cache setting | Wall time | Output | Notes |
|---|---:|---|---|
| `device=auto`, `dtype=default` | 32.05 s | `auto_default.png` | First run included model/text encoder loading. |
| `device=off`, `dtype=default` | 12.02 s | `off_default.png` | RGB output is pixel-identical to auto/default. |
| `device=auto`, `dtype=int8` | 6.01 s | `auto_int8.png` | Mean absolute RGB difference vs default is 0.572/255; 37.46% of pixels differ. |

Timing is not a cache speed benchmark: model load and warm state differ across sequential runs. The default cache and cache-off output equality verifies this same-seed workflow is deterministic under these settings. The int8 image is close overall, though small design details differ; the pixel metrics do not establish perceptual equivalence.

The three API workflows are saved as `workflow_auto_default.json`, `workflow_off_default.json`, and `workflow_auto_int8.json`; raw submission metadata is in `results.json`. All three outputs are 1024×1024. The active ComfyUI batch output files were copied here and then removed from the shared `output/` tree.

## Preview and encoder findings

- All four reference-image slots were accepted and the graph completed. This is a basic functional check, not a systematic reference-count/ordering or text-encoding quality study.
- The KJ preview override accepted `taeqi2_1_decoder.pth` and completed on each sampling run. Its live preview frames are not recorded in the final PNGs, so this run does not quantify Tiny VAE preview fidelity against the full VAE.
- Because final images use the BF16 VAE, the Tiny decoder changes preview fidelity only in this workflow, not final-image decode quality.

## Model files

- H3: `/home/sean/projects/models/comfy/vae_approx/taeh3.safetensors`, ModelScope `Kijai/MiniMax-H3-TAE`, SHA256 `f0f60fa072089997f817402098c2fd90777cb2660dd79cf5df42fc1e3e08e527`.
- Qwen Image 2.1: `/home/sean/projects/models/comfy/vae_approx/taeqi2_1_decoder.pth`, fetched from `huangdffs/taesd` (HF mirror, 15,314,938 bytes), SHA256 `53c2212f4ea6c8ad06a30d4969d891f80339ff87bb3f77fe793848613d3a9042`.
- Both files are in the central model library, and the ComfyUI directory links to it. ComfyUI exposed both names in the KJ node combo without a restart.

## Owner

Sean
