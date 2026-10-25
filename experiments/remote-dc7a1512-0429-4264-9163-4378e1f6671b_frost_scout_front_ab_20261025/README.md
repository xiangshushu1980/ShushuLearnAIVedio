# Qwen Image 2.1 appearance and depth role validation

Task: `remote-dc7a1512-0429-4264-9163-4378e1f6671b`  
Status: current minimal generic default configured but not generated; historical standing full-body front/left-profile tests and entry regressions remain evidence for the previous version only.

## Result summary

Four matched seed pairs were generated: two frontal (423520, 423521) and two left-side (423522, 423523). Each pair holds the appearance reference, prompt, base model, canvas, sampler, and seed constant; the depth-guided branch adds the grayscale depth map through `QwenImageDiffsynthControlnet`.

- **Appearance condition:** identity, face/hair, outfit palette and materials remain visually consistent in all depth-guided outputs. No broad appearance displacement was visible in this small sample.
- **Depth condition:** the front view did not show a strong incremental geometry effect because the appearance reference and prompt were already frontal. The side-view pair showed a more distinct rear-side waist/hip projection in both depth-guided images, broadly matching an unlabeled projection in the control map. Its object identity remains unresolved; score it only as geometry.
- **Evidence boundary:** color or material output is not evidence that grayscale depth supplied appearance. Gear visible in both branches or not clearly represented in a depth map cannot be credited to depth. No stability guarantee is claimed.
- **Upstream and local status:** Comfy-Org documentation supports a DiffSynth depth patch path and preprocessed depth input. It does not establish behavior for this exact local Fun Control Union BF16 weight file. Local node/model availability was verified against ComfyUI 0.42.1, and all eight generations completed; these are local findings only.

## Matched experiment matrix

| View | Seed | Appearance-only | Same appearance + depth |
|---|---:|---|---|
| Front | 423520 | [image](seed_423520/appearance-only/output.png) | [image](seed_423520/depth-guided/output.png) |
| Front | 423521 | [image](seed_423521/appearance-only/output.png) | [image](seed_423521/depth-guided/output.png) |
| Left side | 423522 | [image](side_view/seed_423522/appearance-only/output.png) | [image](side_view/seed_423522/depth-guided/output.png) |
| Left side | 423523 | [image](side_view/seed_423523/appearance-only/output.png) | [image](side_view/seed_423523/depth-guided/output.png) |

## Follow-up: depth strength and gray appearance

A later matched dose-response check tested appearance-only versus depth strength 0.50, 0.75, and 1.00 across seeds 423530 and 423531. It did not show obvious palette washout at 0.75 or 1.00, although the 1.00 outputs were somewhat darker. In one seed, all depth branches omitted a bow that remained in appearance-only; the depth map did not encode it. See the [strength QC and limits](strength_ab_20261025/QC.md) and [contact sheet](strength_ab_20261025/strength_contact_sheet.png). This remains a bounded local sample, not a color guarantee.

## Evidence

- Front phase: [QC](QC.md) · [contact sheet](front_ab_contact_sheet.png)
- Side phase: [QC](side_view/QC.md) · [contact sheet](side_view/side_ab_contact_sheet.png)
- Reproducible experiment parameters, prompt, source hashes, and official URLs: [front plan](plan.json), [side plan](side_view/plan.json)
- Each run folder contains `request.json`, `workflow.json`, `submission.json`, `history.json`, `receipt.json`, and output image.
- Each stage's `preflight.json`, empty post-run queue, lease release, and exact temporary-file cleanup are retained in its phase folder.

## Recovery

The front runner is `run_matched_ab.py`; the side runner is `side_view/run_matched_ab.py`. Each reads the local `plan.json` beside it and writes run receipts under its own directory. Before rerunning, verify current Task Center controller/generation, shared ComfyUI queue, GPU occupancy, and acquire a new `gpu:0` lease with the active conversation ID. Use new seed IDs for new samples; do not overwrite this evidence.

## Prompt-cause follow-up and generic flow

The same two-seed prompt test now isolates the historical grayscale-depth wording block: B is a target-only prompt with no descriptions of input sources; C is exactly B plus the old two-sentence grayscale-depth instruction block. With the same images, model graph, seed and sampler, both B outputs retain normal color while both C outputs become near-monochrome. The old full prompt reproduces the historical washed seed423490 output pixel-for-pixel in RGB, but behaves differently at seed423530. This identifies the inserted instruction block as a reproducible appearance-interference cause for these local cases; it does not identify one word or explain every possible appearance shift.

- [Prompt-cause QC](prompt_cause_20261025/QC.md) and [six-image board](prompt_cause_20261025/prompt_cause_contact_sheet.png).
- [Independent parent audit](prompt_cause_20261025/parent_cause_audit.json) verifies all six receipts/hashes and that B/C graphs differ only in prompt and output prefix.
- [Generic validation QC](prompt_cause_20261025/generic_validation/QC.md): front seeds423490/423530 plus left-profile seeds423532/423533, four matched depth/no-depth pairs (eight outputs, including two reused B outputs). All were visually reviewed without gray conversion.
- [Task-local reusable flow](prompt_cause_20261025/candidate/README.md), with the frozen generic prompt, API graph, request schema and single-view entry. Current exact validation/entry status is recorded there.

The flow uses the appearance image only through EditPlus image1 and the matching depth image only through Fun Control. Prompt text describes the requested picture, with no input-source role allocation or character-specific palette. The bounded baseline is Qwen Image2.1 BF16, Fun Control BF16 strength0.5/interval0–1, 768×1024, 25 steps, CFG1, Euler/simple. Other roles and back views remain unverified. Equipment/bow problems remain with the original character-sheet task; no shared skill/preset is modified by this task-local baseline.

## Current configuration correction and next conversation

The user identified that the tested prompt imposed an arm position and standing full-body composition that initial references are not guaranteed to have. The current default in [candidate/generic_prompt.txt](prompt_cause_20261025/candidate/generic_prompt.txt) is now minimal and has no pose/view/framing/background/light assumptions. `view` is optional in the single-image entry. This revision has not been generated; previous standing/full-body tests remain historical evidence. See [handoff](HANDOFF.md) before revising the overall flow in the next conversation.
