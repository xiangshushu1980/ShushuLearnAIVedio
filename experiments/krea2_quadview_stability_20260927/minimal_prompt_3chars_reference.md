# [Sean] Recovered matched three-view references — 2026-09-27

Owner: Sean  
Task: T-comfy-ops-48

ComfyUI prompt metadata recovered from three matched samples. All use the same source and seed per character, with three-view and four-view prompts as the only changed factor. The PNGs did not retain prompt IDs or durations.

## Conditions

- Krea2 Turbo; `QuadView_krea2_v1.safetensors`, strength 1.0
- 1536×1024; 10 steps; CFG 1; Euler/simple
- Ref boost 1.0; positive grounding 0; grounding 768
- Eastern swordswoman seed 4801001; red mage seed 4801002; dwarf engineer seed 4801003
- Three-view prompt: `Convert the character in the image to a Character Sheet showing a face close-up, front full body and back full body views.`

All three recovered three-view samples show a face close-up, front full body and back full body. See `outputs/minimal_prompt_3chars/`.
