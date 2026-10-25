# Reference + depth single-image flow: current generic prompt

Status: configured per user instruction; the revised generic prompt has NOT been generated or visually validated. The earlier standing full-body recipe was tested, and remains historical evidence rather than validation of this revision.

## Current default prompt

```text
Create a finished image of the same subject. Preserve the subject design and rendering style.
```

The default does not impose a standing pose, arm position, body framing, camera direction, background, lighting or character-specific colors. It contains no reference-image/depth-image descriptions or assignment of responsibilities to input sources.

## Request and execution

Required request fields are absolute `appearance_path`, `depth_path`, integer `seed`, and absolute `output_dir`. `view` is optional. When omitted, the runner adds no view instruction. An explicitly supplied `front` or `left_profile` adds only the corresponding view sentence; choose it only if intended and consistent with the depth input. See `request.schema.json`.

The task-local entry remains `run_single_view.py`. It requires caller resource/task preflight and an active `HIVE_LEASE_ID` belonging to the real host conversation identity. Example invocation after acquiring the lease:

```sh
HIVE_LEASE_ID=<active-lease-id> python run_single_view.py /absolute/request.json
```

The API graph and model/sampler settings retain the preceding experiment configuration: Qwen Image2.1 BF16, Fun Control BF16 strength0.5/interval0–1, 768×1024, 25 steps, CFG1, Euler/simple. These are inherited settings for the next discussion, not a newly validated universal parameter preset. The appearance image enters EditPlus image1 and the depth image enters Fun Control.

## Evidence and handoff

The original prompt is preserved in `historical/standing_full_body_prompt_v1.txt`, with provenance in sibling JSON and commit `da6ae98`. Existing requests, receipts, output hashes, QC and smoke-run code hashes remain unchanged. Those images used the old standing/full-body prompt; they do not validate the current generic default or optional-view rendering.

The completed B/C experiment establishes a reproducible grayscale-depth wording-block interference in the tested local case. It does not establish that initial references always have a specified pose. Overall workflow revision and validation of the new default are deferred to the user's next conversation. No GPU generation is performed for this configuration-only change.
