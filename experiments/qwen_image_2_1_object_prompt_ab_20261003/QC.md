# [Sean] Qwen Image 2.1 object prompt A/B — QC

## Method

Reviewed all 18 new renders beside the reused manual-prompt baseline, aligned by object and seed. A render passes only when all three panels show the same complete object in the requested views, with no part separation or object-state change. Fine hidden-side features are treated as unknown when the reference does not show them.

This is a three-object feasibility check. The Agent path is one Qwen3-VL 8B image-conditioned prompt-generation call with a human-authored object-specific instruction. It does not analyze its own renders or retry them.

## Results

| Object | Manual baseline | Qwen3-VL Agent prompt | PE-I2I prompt | Observation |
|---|---:|---:|---:|---|
| Shield | 3/3 | 3/3 | 3/3 | All preserve the round shield, central boss, and three broad views. The manual baseline's rear with arm straps is the most functionally informative for a usable prop, although strap count/layout varies (four, two, or a joined pair). Agent and PE show a bare rear because their instructions explicitly said not to invent hidden hardware; this is an instruction effect, not evidence that Qwen3-VL cannot infer or render straps. |
| Lantern | 3/3 layout passes | 3/3 layout passes | 3/3 layout passes | These are useful front-plus-side sheets, not dependable front/side/rear turnarounds: the third view looks much like the front, and the hidden rear remains unknown. Small frame/control details vary. |
| Fully sheathed katana | 1/3 | 0/3 | 0/3 | All methods struggle with the long thin object. Agent and PE outputs separate the handle from the scabbard in one or more panels; some side panels omit the handle, detach fittings, or expose an unsheathed blade. Neither prompt rewrite repairs cross-view object identity/state. The manual 1/3 is the prior baseline QC result. |

The Agent and PE branches each produced 9/9 usable shield/lantern layouts and 0/3 strict katana passes. The numeric counts score whether each requested sheet remains intact across seeds; they do not measure whether those views are best for later video conditioning. The shield comparison favors the manual prompt for showing a useful reverse with straps, while the lantern comparison is better understood as front-plus-side coverage.

## Prompt-path observations

- The image-conditioned Agent prompts completed in about 4 seconds each. They explicitly name panel order, object identity, and unknown hidden surfaces.
- PE-I2I prompts took about 113–170 seconds each on this local setup. They were substantially more verbose and accurately described many visible details, but verbosity did not improve the katana results.
- For the shield, the image-aware prompts were told to keep the unseen rear plain. That instruction suppressed arm straps which appear in the more useful manual-baseline reverse. A future prompt should request plausible functional attachment hardware, then flag its configuration as inferred rather than reference-verified.
- For the lantern, the repeated front-like panel makes these sheets more suitable as front-plus-side references than as full reverse coverage.
- For the katana, a full-length object view plus separate blade and hilt detail views may suit video reference conditioning better than three orthographic views. This is a new hypothesis, not tested in this run.
- Prompt generation alone is enough for the shield and lantern examples. A closed-loop Agent might help detect and retry failures, but this run did not test that capability and cannot establish that it would fix the katana geometry.

## Artifacts

- `outputs/comparison_shield.jpg`, `outputs/comparison_lantern.jpg`, `outputs/comparison_katana.jpg`: rows are seeds; columns are manual baseline, Agent, PE.
- Final Agent prompts: `prompts/agent_qwen3vl_*.txt`.
- Final PE prompts: `prompts/pe_i2i_*.txt`.
- `manifest.json`: model/checkpoint, workflow, prompt IDs, seeds, timings, output paths, and hashes.

## Video-conditioning limitation and next experiment

No video was generated from these sheets. A multi-view contact sheet could help video preserve object identity, but it can also make the model treat panels as one composite scene, jump between viewpoints, or confuse a detail panel for a separate prop. The current results do not predict which behavior will dominate.

Test video use separately with matched source prompts and seeds: compare a single hero/product view, the current three-view sheet, and an object-specific reference board. For the katana, make the reference board full-length + blade close-up + hilt close-up. Judge temporal identity, material/detail stability, unwanted cuts/panel copying, and whether the object stays in the requested state. Use the same short motion prompt for every condition.

## Conclusion

Character Sheet V3 is viable for coherent multi-view layouts of the tested shield and lantern, but view utility depends on the asset and downstream task. The Qwen3-VL Agent prompt path is fast; its hidden-side result followed the conservative instruction it was given. Prompt instructions should specify whether to preserve known functional parts, infer plausible hidden hardware, or leave it blank. Do not treat these still-image scores as video-conditioning evidence. Neither Agent nor PE improved the katana's multi-view consistency in this test.
