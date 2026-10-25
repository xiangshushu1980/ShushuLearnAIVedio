# Frost Scout prompt-cause matrix QC

## Matrix and outputs

Two seeds (423490 historical gray/white case; 423530 recent full-color case), each with:

- A: historical complete prompt;
- B: frozen minimal target-only prompt;
- C: byte-identical B plus the historical two-sentence grayscale-depth instruction block.

Every image used the same appearance reference and matching front depth map, Qwen Image 2.1 BF16 / Fun Control BF16, 768×1024, 25 steps, CFG 1, Euler/simple, depth strength 0.5 from 0 to 1. Every receipt reached `completed`, output SHA-256 was recorded, and each image has a separate `qc.md`.

| Seed | A historical full | B target-only | C target-only + grayscale-depth block |
|---|---|---|---|
| 423490 | Full color but visibly washed/desaturated; pixel-identical to historical washed output | Rich color/material contrast | Near-monochrome gray |
| 423530 | Full color; different softer style/equipment arrangement from B/C | Rich color/material contrast | Near-monochrome gray |

The A/423490 output's decoded RGB pixels are exactly identical to the old shape-only sample, despite a different PNG file hash due to container metadata. B/C prompts differ only by the two-sentence grayscale-depth instruction block. Across both fixed seeds, B retains strong color/material separation and C becomes near-monochrome while keeping the silhouette and surface detail. A varies between washed color (423490) and clear color (423530), showing seed sensitivity for the historical full prompt.

## Conclusion and boundary

Under this fixed Frost Scout front reference+depth setup and these two seeds, adding the exact two-sentence grayscale-depth instruction block to the target-only prompt reproducibly causes a near-monochrome appearance. This supports the block-level causal claim for this case. It does not isolate which sentence or word is responsible; the phrases “grayscale depth map” and “do not copy its grayscale appearance” were not tested separately. It does not show that every prompt mentioning depth, or every use of ControlNet, causes gray output. The historical complete prompt is not a one-variable contrast against B because it contains several additional clauses.

All six outputs have complete silhouettes and readable detail; C is not line art. Equipment counts/semantics, bow issues, cross-character generalization, and back views are outside this prompt-cause score. Next bounded validation is recorded separately in `generic_validation/`; do not mark front+side reusable flow validated until that matrix is actually run and visually reviewed. Back remains unvalidated.
