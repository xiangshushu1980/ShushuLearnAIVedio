# [Sean] Staged character and reference-sheet QC

## Results

- Generated four independent Qwen references: face, navy uniform, silver armor, and one sheathed katana.
- Combined those same four references into three full-body character candidates. The face, navy clothing, black boots, and silver arm armor are recognizable across all three. Candidate 1 largely omits the shoulder armor; candidates 2 and 3 show both shoulder and forearm guards more fully.
- Generated both requested sheets from each candidate: `face+front+back` and `face+front+side+back`. All six show the requested portrait and view counts with clear separation, and retain the same broad face/hair/outfit design.
- The second and third candidates give the most complete armor results. Candidate 2 has a particularly clear face/front/back sheet; candidate 3 has a strong four-view layout.

## Limits

- The weapon is the least stable element. The generated isolated katana is clear, but composition and turnaround stages change how the hilt/scabbard sit on the belt; some back views show ambiguous diagonal black shapes. This chain does not yet lock weapon geometry reliably.
- Repeated sampling changes shoulder armor coverage and small uniform details even though every candidate uses the same source assets.
- All 13 generations took 234.32 seconds summed across jobs. Peak VRAM was not sampled during the run.
- All images are 1536×1024, prompt-only assets or Qwen edits, no Krea2/LoRA.

Conclusion: staged source assets work well for establishing face, clothing family, armor family, and sheet composition. For a production-quality locked prop, use a more explicit weapon-bearing full-body reference or a separate targeted edit after choosing a character candidate.
