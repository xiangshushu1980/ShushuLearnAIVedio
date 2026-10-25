# QC — seed 423490 / C_minimal_plus_grayscale_depth_block

- API state: completed; prompt ID `6b946281-c0b2-42ff-be3c-df705c915ecf`.
- Output: `output.png`, 768×1024, SHA-256 `d35717ceccf493ad7d97b52cc8d492cc42e5a7047542c841cb9baae2df19f629`.
- Framing/view: centered, full-body, straight-on front; upright; both arms and feet visible.
- Appearance: near-monochrome gray rendering across skin, clothing, leather, and boots, with strong color/material separation lost. This is visibly more severe than A's washed but colored output and B's strongly colored output.
- Structure: full silhouette and gear remain present; not line art.
- Matched comparison: relative to seed-matched B, adding only the old grayscale-depth instruction block changes the result to near-monochrome. This is direct evidence that the block can cause a grayscale appearance under this seed and frozen graph; verify replication with seed 423530 before judging robustness.
