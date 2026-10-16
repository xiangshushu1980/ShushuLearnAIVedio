# Qwen Image 2.1 nodes and Tiny VAE preview (Owner: Sean)

## Current local setup

- `QwenImage21Cache` and `TextEncodeQwenImage21` are registered by the current ComfyUI instance.
- `TextEncodeQwenImage21` supports ordered reference-image inputs. A four-reference graph completed on the local Qwen Image 2.1 Turbo setup.
- For sampling previews, KJNodes `Model Preview Override` accepts `taeqi2_1_decoder.pth`. The final image should continue through `qwen_image_2.1_vae_bf16.safetensors` when final decode quality matters.
- H3 has the same preview route with `taeh3.safetensors`; both files are installed under the central `/home/sean/projects/models/comfy/vae_approx` directory and recognized by the node. No H3 video generation was run in this check.

## Cache smoke result

On 2026-10-16, three Qwen Image 2.1 Turbo outputs used the same four ordered references, prompt, seed 421016, 1024×1024 canvas, 8 Euler/simple steps, and full BF16 final VAE:

- `QwenImage21Cache (auto, default)` and `(off, default)` produced pixel-identical final images.
- `(auto, int8)` differed by mean absolute RGB 0.572/255, with 37.46% of pixels changing. The image remained close overall, but some small design details changed.
- Recorded sequential times were 32.05 s, 12.02 s, and 6.01 s. The first run included model loading, so these figures are not a valid cache speed comparison.

The Tiny decoder was connected only to live preview; saved outputs used the BF16 VAE. Thus this test did not measure any change to final-image quality from Tiny VAE, nor did it preserve the live previews for a direct fidelity comparison.

## Public notes and community signal

- ComfyUI documents the cache as a storage/speed tradeoff: `default` is lossless, `int8` halves cache storage with roughly BF16-level accuracy, and `int4` quarters storage with higher per-step error. Independent community benchmarks specifically comparing `QwenImage21Cache` modes appear sparse; the local matched-seed check above is stronger evidence for this machine and graph than unpaired timings. [ComfyUI cache node docs](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/QwenImage21Cache/en.md)
- `TextEncodeQwenImage21` is the native encoder for Qwen 2.1 prompt and reference inputs. Community reports mainly discuss reference behavior and prompt/workflow quality, not defects in the encoder itself. Reports are mixed: users show multi-reference workflows, while some note that adding many references can increase drift/hallucination; treat these as anecdotal and prompt-dependent. [ComfyUI node docs](https://github.com/Comfy-Org/docs/blob/main/built-in-nodes/TextEncodeQwenImage21.mdx) · [community multi-reference discussion](https://www.reddit.com/r/comfyui/comments/1wu7cd7/comfyui_qwen_image_21_tutorial_generate_edit/)
- TAEQI2.1 is published for real-time preview and lower-resource encode/decode. A preview decoder is expected to trade some reconstruction fidelity for speed, but we do not have a measured preview-versus-full-VAE error for this ComfyUI workflow. The public model card does not establish a universal numerical quality loss. [TAEQI2.1 model card](https://huggingface.co/madebyollin/taeqi2_1) · [KJNodes preview override](https://github.com/kijai/ComfyUI-KJNodes/blob/main/nodes/preview_override_node.py)

See the full workflows, outputs, and manifest in [the experiment folder](../experiments/sean_qwen21_cache_textencode_tinyvae_20261016/README.md).

## Model locations and sources

- H3 preview decoder: `/home/sean/projects/models/comfy/vae_approx/taeh3.safetensors` (ModelScope `Kijai/MiniMax-H3-TAE`).
- Qwen Image 2.1 preview decoder: `/home/sean/projects/models/comfy/vae_approx/taeqi2_1_decoder.pth` (HF mirror `huangdffs/taesd`).
- Both reside in the central model directory; the ComfyUI `models/vae_approx` path resolves there.

## Owner

Sean
