# [Sean] Qwen Image 2.1 object prompt A/B

`owner: Sean`

Compare three prompt paths for the existing Qwen Image 2.1 V3 static-prompt adaptation, using the same source objects and seed sets:

1. Existing hand-written V3 prompts (baseline outputs are reused from the 2026-10-03 domain validation).
2. Qwen Image 2.1 PE-I2I: image-grounded prompt rewrite from the official Comfy-Org checkpoint, using the reviewed `QwenImage21_EditPromptRewrite` custom node and upstream rewrite system prompt.
3. A Qwen3-VL 8B image-conditioned prompt generator, prompted as the object-sheet Agent with a per-object view plan and explicit handling of unknown hidden surfaces.

The PE node source was reviewed and pinned at commit `fe166a199d3d1f2397a97bab230ae74657fc5c09`; the node is installed in the shared ComfyUI custom-node directory for this test. Its weights are from the official `Comfy-Org/Qwen-Image-2.1` repository. Restart the healthy shared instance only through `scripts/comfy-stack.sh`, with an empty queue and no active GPU lease, then confirm both new node registrations before submitting the batch.

Cases: round shield, brass lantern, and fully sheathed katana. Each automated branch receives the correct view set for that object. Existing baseline runs use seeds shield 2026100391–0393, lantern 2026100340–0342, and katana 2026100370–0372. New branches will use the same per-case seeds and V3 parameters. The Agent test is a single image-conditioned prompt-generation call; it does not yet test multi-turn QC or retries. This is a prompt-path feasibility comparison, not a broad model benchmark.

### QC

Completed results and the shared scoring rubric are in [QC.md](QC.md). Contact sheets are in `outputs/comparison_*.jpg`. The PE node's internal reasoning output is not archived; the parsed positive prompt, final prompts, generated sheets, prompt IDs, seeds, timings, and image hashes are retained here. The prior domain validation remains the baseline source of its run metadata and QC.
