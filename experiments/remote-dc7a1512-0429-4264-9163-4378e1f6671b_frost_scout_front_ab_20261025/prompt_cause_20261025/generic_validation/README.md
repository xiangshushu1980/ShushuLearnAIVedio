# Bounded validation plan for the generic reference + depth candidate

**Status: PREPARED_NOT_SUBMITTED.** The executor has a gate requiring the six-row prompt-cause matrix in the parent `plan.json` to be terminal-successful with matching output hashes. It is a task-local executable candidate, not a shared preset. Do not submit its matrix before the gate and fresh resource checks pass.

## Six planned images

1. **Front appearance-only pair (2 images).** Seed 423490 and 423530, using the exact frozen `B_minimal_target` prompt. Omit the complete ControlNet branch. Compare each result with the already completed same-seed prompt-cause B output, which uses reference + frontal depth at 0.5 from 0–1.
2. **Left-profile matched pairs (4 images).** Seeds 423532 and 423533; each seed gets appearance-only and reference + matching left-side depth (0.5 from 0–1). Both conditions use exactly the generic candidate prompt rendered as “strict left-facing side profile.”

The reference image is the same fixed Frost Scout appearance reference. Depth-only rows use the task's already validated side-depth input. The graph sends appearance only to `TextEncodeQwenImageEditPlus.image1`; it omits `image2`. For control rows, depth connects only to `QwenImageDiffsynthControlnet.image`; appearance-only rows omit the model patch, depth loader and ControlNet node entirely. All rows use the same BF16 model stack, 768×1024, 25 steps, CFG 1, Euler/simple, denoise 1.0.

`plan.json` preserves the exact input hashes and source paths, prompt text and hashes, matrix, and comparison scope. `run_generic_validation.py` imports API, upload, lease heartbeat, hashing and conditional idle-cache helpers from the already reviewed parent `run_prompt_cause.py`; it does not reimplement the HTTP client. It writes request, prompt, graph, receipt, submission, history, output and hashes per image. Completed receipts skip only after all output hashes verify; unresolved receipts are never resubmitted. The matrix gate prevents early submission while the cause experiment is still running.

Before running, check current Task Center controller/generation, shared Comfy queue, occupancy, refreshed GPU/process state, and acquire/retain `gpu:0` under the active conversation. The executor submits sequentially, does not retry an uncertain prompt POST, and polls each prompt ID to terminal state. Any authorized `/free` operation is conditional on terminal work, empty queue, and this task being the only GPU lease; it is recorded in `cache_lifecycle.json`. Temporary files are removed only by exact task-owned path and input/output hash.

This six-image extension is bounded to one character and one left-side view. It does not validate back views, other characters, semantic equipment identity, or a production guarantee. Keep this candidate `UNVALIDATED` until the rendered outputs pass per-image visual review; leave back view explicitly unvalidated.
