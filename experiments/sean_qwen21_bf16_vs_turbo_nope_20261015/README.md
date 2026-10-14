# Qwen Image 2.1 BF16 vs Turbo INT8, direct prompt

- Owner: Sean
- Task Center task: `remote-97ccaaac-e730-4c57-875c-c86954ca0518` (existing infograph-research task)
- Date: 2026-10-15
- Purpose: compare the practical image quality and speed of the highest-fidelity Qwen Image 2.1 base checkpoint and the fast Turbo checkpoint on infographic layouts.
- Scope: 12 varied infographic structures × 2 shared seeds × 2 checkpoints = 48 planned images.
- Prompt path: direct, hand-authored prompts based on Qwen's official observer-style guidance and infographic skill structure. No PE, prompt rewriter, LoRA, image edit, or post-render text overlay.
- Prompts are byte-for-byte shared between the two checkpoints for each case. Six cases retain Chinese title/data strings; prompt instructions are in English. Both checkpoints use the same 1536×1024 canvas and seeds 42/1337.
- Base sampling: BF16 diffusion weights, BF16 Qwen3-VL 8B encoder, BF16 VAE, 40 steps, CFG 1, Euler/simple.
- Turbo sampling: INT8 ConvRot Turbo diffusion weights, same BF16 encoder and VAE, CFG 1, Euler, official fixed 8-step sigma schedule recorded in each workflow.

This comparison measures the practical base-versus-Turbo experience. The result combines Turbo distillation, its eight-step schedule, and INT8 ConvRot weights; it does not isolate weight precision as a single variable. The casebook contains fixed, prewritten values, with the source and synthetic-data status recorded per case in `source_casebook.json` and `runs/manifest.json`. Synthetic cases use deliberately constructed test values; they are not randomly generated during image creation.

## Files

- `prompts/`: exact direct prompts, no PE output
- `workflows/`: ComfyUI API workflows for every model/case/seed
- `images/`: archived PNGs copied out of ComfyUI's temporary output directory after each successful run
- `runs/`: manifest, per-image run records, ComfyUI prompt IDs, SHA-256 hashes, and GPU sample logs
- `contacts/`: per-model, per-seed contact sheets and paired visual review sheets
- `evaluation.md`: case-by-case human visual review, rubric, and measured speed/resource summary
- `prepare_experiment.py`: deterministic prompt/workflow preparation from the frozen source casebook
- `run_experiment.py`: sequential runner with shared-queue checks, GPU lease heartbeats, telemetry sampling, and archive copy

Sampling reference: [official Qwen Image 2.1 repository](https://github.com/QwenLM/Qwen-Image-2.1). Prompts follow its observer-style guidance and the casebook's infographic skill structure; the PE node is absent from all saved workflows.

Evaluation reviews exact text strings, data-to-mark mapping, infographic/illustration coordination, layout, visual finish, and elapsed generation time. Scores are non-blind human review; no independent reviewer or OCR was used.
