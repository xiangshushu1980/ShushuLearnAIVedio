# [Sean] Qwen infographic prompt and skill-method A/B

Task: `remote-97ccaaac-e730-4c57-875c-c86954ca0518`  
Run date: 2026-10-14  
Result: 16/16 images generated successfully. Direct image generation only; no image compositing, code-drawn charts, or LoRA.

## Purpose and methods

This small controlled run tests whether adding infographic information planning and Qwen visual-planning rules to the prompt improves the image. Both arms use Qwen-Image-2.1 BF16, the same official T2I Prompt Enhancer (PE), the same ComfyUI graph and parameters, and paired seeds 42/1337. Only prompt organization differs.

- `baseline`: exact data brief, a specified chart/diagram, visual concept, title/subtitle, takeaway, and a no-extra-data instruction; it follows the current Qwen+PE approach without explicit five-second takeaway/topology selection/visual-share rules.
- `skill_guided`: also plans a five-second takeaway and information topology, makes the diagram dominant, caps visible copy, specifies a reading path, and requests distinct editorial composition. These principles are applied from the researched editorial-infographic and Qwen visual-planning skills; the skills themselves were not installed as runtime plugins.

Both arms go through the same official Qwen T2I PE. Thus the comparison is a test of skill-informed prompt planning in this workflow, not a comparison of PE-off versus PE-on or a test of installing a complete skill runtime.

## Cases and artifacts

Four English cases: sourced global electricity access trend (World Bank WDI), synthetic food-waste process, synthetic commute share/time comparison, and synthetic solar project budget. The synthetic cases are illustrative fixtures, not empirical claims.

Each image has its input prompt, actual PE output, API workflow JSON, run JSON, resource samples, and SHA-256. See [`casebook.json`](casebook.json), [`runs/manifest.json`](runs/manifest.json), [`prompts/`](prompts/), [`workflows/`](workflows/), [`runs/`](runs/), and [`images/`](images/). The two overview sheets are [`seed 42`](contact_seed42.jpg) and [`seed 1337`](contact_seed1337.jpg); per-image review is in [`evaluation.md`](evaluation.md).

## Parameters and resources

Qwen-Image-2.1 BF16; Qwen 3VL 8B BF16 encoder; official Qwen 2.1 T2I PE int8_convrot; Qwen 2.1 BF16 VAE; 1536×1024; Euler/simple; 40 steps; CFG 1; denoise 1.0; no LoRA. Each case/arm used matching seeds 42 and 1337.

All runs completed on the shared ComfyUI 0.39.2. Total sampled generation time was 933.2 seconds (about 58.3 seconds/image); peak observed VRAM 23,172 MB, peak GPU temperature 79°C, and peak ComfyUI RSS 40,619 MB. The run held GPU lease `69cdd821-6882-4e78-b20f-3a47f8946da8`; the queue was empty afterward, model memory was freed, GPU use returned to about 588 MiB, the lease was released, and shared ComfyUI remained running.

## Limits

Two seeds per case are a small sample. Evaluation is visual and non-blind, by the same reviewer; no OCR or automated chart-coordinate audit was used. Prompts, generated image artifacts, and the actual PE rewrites are preserved for independent review. Do not generalize this comparison to other Qwen checkpoints, PE versions, data types, or seeds.
