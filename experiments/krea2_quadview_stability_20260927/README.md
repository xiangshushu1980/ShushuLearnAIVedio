# [Sean] Character reference pipeline — stages 1–2

Owner: Sean  
Task: T-comfy-ops-48

Current scope is character design prompt → main full-body reference image → three-view image. H3 is not part of this stage.

The fixed procedure and its correction history are recorded in [threeview_fixed_flow.md](threeview_fixed_flow.md). The corrected text-only Jibs-style trial is under `../krea2_role_reference_20260927/`; it separates per-role design prompts from the fixed generation settings and fixed three-view prompt.

Earlier QuadView layout experiments remain in this directory as background. Provenance review found that the six images in `threeview_verify_2/` and `threeview_verify_4/` were all generated upstream with a Shushu portrait as their image reference and with Jibs LoRA strength 0. Their view-count results do not validate clean role identity generation or the intended Jibs-style first stage.
