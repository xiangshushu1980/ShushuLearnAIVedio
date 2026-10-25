# Reusable single-view reference + depth candidate

**Workflow status: BOUNDED_VALIDATION_PASSED for Frost Scout front and left profile only. Runner status: one front smoke request executed successfully.** The exact front target prompt and graph settings were exercised through the task-local `../generic_validation/` matrix, and `run_single_view.py` completed one front request with seed 423490. Its decoded RGB pixels exactly match the existing same-seed B output. The workflow remains unvalidated for back views, other characters, and production guarantees. This is not a shared skill or preset.

## Request

One request creates one image. Supply absolute `appearance_path`, `depth_path`, integer `seed`, `view` (`front` or `left_profile`), and an absolute `output_dir`; see `request.schema.json`. The depth file must correspond to the requested view. Back is future work and is not accepted by the current runner. Input paths are caller-selected; no character-specific values are embedded in this candidate.

`generic_prompt.txt` is the entire text prompt template. The caller replaces `{view_phrase}` with exactly one of:

- `front`: `strict straight-on frontal`
- `left_profile`: `strict left-facing side profile`
- `back`: `straight-on rear-facing`

The wording describes the desired picture only. It does not name an input source's responsibilities or specify a character palette, outfit or footwear.

## Fixed generation settings

The API graph template pins Qwen Image 2.1 BF16, Qwen3-VL 8B INT8 ConvRot, Qwen Image 2.1 VAE BF16, and Qwen Image 2.1 Fun Control Union BF16, at 768×1024, 25 steps, CFG 1, Euler/simple, denoise 1.0, control strength 0.5 from 0.0 to 1.0. `seed` is the only sampler setting supplied by the request. No model installation, download, or path copy is implied.

## API graph contract

`api_graph.template.json` is an API-format ComfyUI graph with string placeholders for the uploaded filenames and rendered prompt. Set KSampler's numeric `seed` from the request. The appearance image connects only to `TextEncodeQwenImageEditPlus.image1`; `image2` is omitted. The matching view depth map connects only to `QwenImageDiffsynthControlnet.image`. The control model patch feeds the ControlNet node; the patched model feeds Qwen cache and then KSampler. Resolve the current node schema and installed model choices on the live service before any submission; this saved graph is a candidate wiring, not proof of runtime compatibility.

## Runtime and artifact contract

Reuse the shared ComfyUI HTTP API and hive-resource procedures. Do not duplicate a large runner here. Before GPU work, check Task Center control if this request belongs to a remote task, check shared queue, occupancy, refreshed hardware/process attribution, then successfully acquire `gpu:0` with the active conversation ID. Keep the lease alive while work is queued/running; submit serially and do not retry an uncertain `/prompt` POST. Poll the returned prompt ID to terminal state before releasing the lease. If a POST times out, inspect queue/history and preserve the lease while recovering; a timeout does not authorize resubmission.

`run_single_view.py` is a thin task-local runner that imports the adjacent Comfy API/hash/heartbeat helper. It requires a caller-supplied, already acquired `HIVE_LEASE_ID`, a host identity variable (`CODEX_THREAD_ID`, `HIVE_CONVERSATION_ID`, or `PI_SESSION_ID`), and one request JSON. If multiple host identity variables are set, they must agree. It validates known fields and strict seed range; verifies lease metadata includes the active conversation and `gpu:0`; checks live schema/model choices; freezes request, input, prompt, graph-template, helper and runner hashes; uploads both inputs; and submits once. A completed receipt is reusable only when the request, source input hashes, rendered prompt and output hashes all match; otherwise use a new `output_dir`. After a terminal failure or output collection error it performs cleanup and releases its lease, then exits nonzero. It was invoked for the front smoke directories under `../generic_validation/`; the request, graph, receipt, hashes and QC are preserved there.

The task-root [strength preflight](../../strength_ab_20261025/preflight.json) records 2,303,689,644 bytes of free CUDA VRAM before an immediately preceding successful eight-image batch. The prompt-cause runner uses this as a **conservative experiment guard**, not as a proven model minimum or a universal ComfyUI capacity requirement. If refreshed free memory is below that guard, defer submission until process attribution and capacity are understood; do not unload, stop, or interfere with other GPU processes to make room.

For a terminal run, preserve the input hashes, exact prompt, seed, resolved settings, actual API graph, queue snapshot, prompt ID/receipt, terminal `/history` response, output image and SHA-256. Remove only temporary ComfyUI input/output files whose names and hashes match this request. Keep a visual QC record for framing, view direction, silhouette/pose, identity/style, color/material, and visible equipment. API success alone is not visual acceptance.

## Validation evidence and remaining gates

See [`../generic_validation/QC.md`](../generic_validation/QC.md) for per-image review and [`../generic_validation/plan.json`](../generic_validation/plan.json) for frozen prompt/input hashes and comparison scope. Back view and other characters still require separate validation with matching depth inputs. Keep this experimental contract task-local; do not mark it general across characters or views based on this Frost Scout sample.
