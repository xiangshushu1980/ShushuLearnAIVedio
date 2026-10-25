# Single-view runner smoke QC

The repaired `candidate/run_single_view.py` executed one front request from `request.json` under a freshly acquired lease. It produced `output.png`; prompt, request, live node schemas, workflow, submission, terminal history, receipt, output hash, task-local input copies, cleanup, and lease release evidence are saved in this directory.

## Visual check

The image is a centered, upright, straight-on full-body Frost Scout against a warm off-white background. Both feet are visible. Blue cloth, brown leather, dark trousers and skin remain visually distinct. No gray wash is present.

## Exact comparison with existing B423490

The rendered prompt bytes and SHA-256 match the frozen B prompt (`d80c9bbf444c0f4e9de83af5f34da3dd20ed01ca17f487cded31a911f917f710`). Both images are 768×1024 and their decoded RGB pixels are exactly identical. PNG file hashes differ, so comparison is pixel-level rather than file-level. Details are in `comparison_to_B423490.json`.

## Execution and cleanup

- Fresh Task Center check confirmed this task remained `running`, controller conversation `01a17196-d81d-7d73-839b-b3f51564bfae`, generation 3.
- Fresh occupancy was empty and ComfyUI queue was 0/0 before acquiring lease `e7ca5d87-25ad-464d-9129-e3feece33c86` for `gpu:0`. The runner verified the lease conversation metadata and resource scope before proceeding.
- The runner exited 0 after terminal history, output hash capture, exact-hash temporary-input cleanup, and releasing its lease. Queue ended 0/0.
- After the runner had released its lease, an authorized idle-cache release ran once with an empty queue and no active lease. HTTP 200; ComfyUI free VRAM changed from 2,286,486,444 to 9,721,938,876 bytes. No released lease ID was reused.
- `request_frozen.json` records the runner code hash and prompt-template hash used by this invocation.
