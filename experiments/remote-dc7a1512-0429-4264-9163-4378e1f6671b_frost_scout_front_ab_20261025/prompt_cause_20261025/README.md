# Frost Scout prompt cause matrix

This directory contains the frozen six-render prompt-cause plan and a bounded six-image generic-flow follow-up. Both phases are complete; each has a contact sheet, per-image QC and request/graph/receipt/history/output hash evidence.

## Comparison

- A reproduces the historical full prompt from the gray/white seed 423490 run.
- B is the minimal target-only wording; it contains no reference/depth/grayscale assignment and names no character colors or shoe type.
- C is byte-for-byte B plus the two historical grayscale-depth instruction sentences. B versus C is the intended single wording contrast.
- Seeds 423490 (historical gray/white) and 423530 (recent full-color) receive all three conditions. Each run keeps the same appearance image, front depth map, BF16 model stack, 768×1024 canvas, 25 steps, CFG 1, Euler/simple, and depth strength 0.5 from 0% to 100%. Prompt SHA-256 values are frozen in `plan.json`.

A is contextual historical reproduction and differs from B/C on multiple prompt details. A/B is not a causal single-variable comparison. Two seeds cannot establish cross-character or cross-view stability.

## Graph contract

`TextEncodeQwenImageEditPlus.image1` receives only the frozen appearance reference. `image2` is disconnected. `QwenImageDiffsynthControlnet.image` receives only the matching frontal depth map. The runner snapshots the actual submitted API graph, node schemas, input upload hashes, seed, prompt, request, receipt, terminal history, and output hashes. It refuses to submit if the shared queue is nonempty or ComfyUI reports less free VRAM than the 2,303,689,644-byte conservative experiment guard recorded immediately before the preceding successful eight-image strength batch. This is an observed guard for this experiment, not a proven minimum VRAM requirement for the models or a universal ComfyUI capacity limit.

## Resource gate

At the 2026-10-25 07:21:14 UTC refresh, the task queue and lease occupancy were empty, but ComfyUI reported only 977,863,596 bytes free; Windows reported 21,710 MiB used on the RTX 4090 and two Blender MCP processes whose WDDM per-process VRAM values were `N/A`. These figures do not establish which process owns the memory or that it can be reclaimed. No process was stopped, no model was unloaded, no lease was acquired, and no prompt was submitted. See `resource_preflight_20261025-072114.json`.

After the user authorized release of unused ComfyUI cache and the competing GPU lease naturally expired, a fresh resource refresh showed 23,982,637,056 bytes free and queue 0/0. The `gpu:0` lease was then acquired under the active conversation before submitting A/B/C. After terminal images, idle cache was released only when this task held the lease and the shared queue was 0/0; each action is recorded in `comfy_cache_release_after_423490_A_20261025.json` and `cache_lifecycle.json`. The six-image runner completed and released its lease; `lease_released.json` and `postrun_queue.json` record the terminal state.

The 2,303,689,644-byte threshold is a conservative experiment guard measured before a successful eight-image run, not a proven model minimum VRAM requirement. The runner unloads idle Comfy cache after a terminal image only when refreshed free memory falls below that guard, then requires a successful response and rechecks free memory before continuing.

## Results

The two-seed B/C contrast reproduced a strong desaturation change when the complete historical two-sentence grayscale-depth instruction block was added to the otherwise identical target-only prompt. This establishes the block-level effect in this fixed Frost Scout front setup; it does not isolate an individual term or show that depth prompts generally gray images. See [`parent_cause_audit.json`](parent_cause_audit.json) for parent-reviewed graph diffs and auxiliary saturation measurements, and [`parent_historical_reproduction_audit.json`](parent_historical_reproduction_audit.json) for the seed 423490 historical output RGB identity check.

The later bounded generic validation completed six more images: two front appearance-only controls paired with existing B depth outputs, plus two left-profile appearance-only/depth pairs. All six receipts and output hashes are verified; the queue ended empty and the new lease was released. See [`generic_validation/QC.md`](generic_validation/QC.md), [`generic_validation_contact_sheet.png`](generic_validation/generic_validation_contact_sheet.png), and `generic_validation/lease_released.json`. The candidate graph has bounded visual support for Frost Scout front and left profile only; back and other characters remain unvalidated. A final authorized idle cache release is recorded in `generic_validation/postrun_idle_cache_release.json`.

## Recovery

The Task Center remains authoritative for task status and controller/generation. Before resuming, inspect the current task info and checkpoint, then verify each local receipt and prompt ID against live ComfyUI history and queue. Do not resubmit a request with a `running` or `unresolved` receipt until the original prompt is confirmed terminal; a POST timeout may still have queued work. Keep the associated resource lease alive while the server task is unresolved. The runner skips a `completed` receipt only after every recorded output still exists with its saved SHA-256; non-completed receipts require manual recovery review and are not retried. Once a prompt is terminal and results are collected, take a fresh queue/GPU/process snapshot, clean only request-owned temporary files by exact path and hash, and release only this run's lease. A/B/C receipts are all `completed`; the six outputs are in `prompt_cause_contact_sheet.png` and per-seed condition folders.

The directory `candidate/` contains the reusable single-view request, graph, and thin execution candidate. The graph is bounded-validated only for Frost Scout front and left profile. The single-request runner completed one front smoke request whose pixels match B423490 exactly; see [`generic_validation/candidate_smoke_front_seed423490/QC.md`](generic_validation/candidate_smoke_front_seed423490/QC.md). Back and other characters remain unvalidated.

## Visual QC when runs complete

Record each image independently against the frozen appearance reference and depth map:

- image contains the full figure, straight-on front view, centered, upright, both arms and feet visible;
- identity and face/hair; outfit design and surface rendering style;
- palette/saturation and material appearance (visual assessment; color statistics are auxiliary);
- silhouette, stance and body proportions;
- front-visible equipment presence and placement, while excluding details absent from the depth/reference evidence;
- any gray/white, line-art, material washout, or other failure mode.

Do not treat API success or one matching sample as proof. Compare B versus C within each seed first, then check whether that difference repeats across both seeds. For the generic candidate, use the separate scope and QC recorded in `generic_validation/QC.md`; do not extend its result to back views, other characters, or universal geometry gains.
