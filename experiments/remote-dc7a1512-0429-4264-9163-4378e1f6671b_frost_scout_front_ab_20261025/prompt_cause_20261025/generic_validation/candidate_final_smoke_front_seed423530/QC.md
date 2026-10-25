# Final single-view runner regression QC

The final reviewed runner completed one front request using the exact B prompt and seed 423530. The actual request, workflow, node schemas, upload metadata, submission, terminal history, receipt, output and lease cleanup are preserved in this directory.

## Visual and pixel comparison

The image is centered and upright, straight-on, and full-body with both feet visible. It retains visibly distinct blue cloth, brown leather, dark trousers and skin against the warm off-white background. No gray wash is visible.

The rendered prompt bytes exactly match the frozen `B_minimal_target` prompt for seed 423530. Both decoded RGB images are the same size and pixel-identical. The PNG file hashes differ. `comparison_to_B423530.json` records image hashes and all workflow-source hashes.

## Runtime contract evidence

- Task Center preflight: task remained `running`; controller conversation `01a17196-d81d-7d73-839b-b3f51564bfae`, generation 3.
- This delegated executor's actual host identity was `CODEX_THREAD_ID=01a171ee-f984-7651-bc87-eb0e12bb000e`. The independently acquired lease recorded this identity in both `conversationId` and `threadId`; it included `gpu:0`. This executor did not claim or change Task Center ownership.
- Fresh preflight showed queue 0/0, occupancy empty, RTX 4090 1870/24564 MiB used and 0% utilization, and ComfyUI free VRAM 23,982,637,056 bytes. `request_frozen.json` preserves the occupancy and Comfy stats used by the runner.
- Runner exited 0 after terminal success, exact output hashing, temporary upload cleanup, and release of lease `efae...` (full ID in `lease_released.json`). Final queue was 0/0 and occupancy empty.
- User-authorized idle cache release ran once after the runner had released its lease and after queue/occupancy checks. HTTP 200; ComfyUI free VRAM changed from 2,286,486,444 to 9,721,938,876 bytes. See `postrun_idle_cache_release.json`.
- `request_frozen.json` records SHA-256 for the final runner, shared helper, API graph template, and prompt template. The runner code was not changed after this execution.

## Recovery boundary

No error injection was performed. The runner records unresolved POST/history state and retains its heartbeat for manual read-only reconciliation; it does not retry an uncertain POST. Terminal non-success paths clean up and release only after queue-empty confirmation, then return a nonzero exit status.
