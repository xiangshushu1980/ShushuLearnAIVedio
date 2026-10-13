# [Sean] Qwen staged character assets and reference sheets

## Goal

Test a staged Qwen Image 2.1 workflow: generate face, uniform, armor, and katana references separately; compose several full-body character candidates from those assets; then derive two character-reference layouts from each candidate.

## Matrix

- Four prompt-only assets: face, uniform clothing, silver armor gear, and one sheathed katana.
- Three full-body candidates use the same four reference assets.
- Each candidate produces `face+front+back` and `face+front+side+back` sheets.
- Qwen Image 2.1 only. No Krea2, external reference, or LoRA.

See `manifest.json` for seeds, timings, ComfyUI prompt IDs, and exact outputs. Prompts and submitted API graphs are preserved under `prompts/` and `api_workflows/`.


## Fast review links

- Candidate 1: `outputs/character_candidate_01.png`
- Candidate 2: `outputs/character_candidate_02.png`
- Candidate 3: `outputs/character_candidate_03.png`
- Candidate sheet pairs are named `outputs/candidate_0N_face_front_back.png` and `outputs/candidate_0N_face_front_side_back.png`.
