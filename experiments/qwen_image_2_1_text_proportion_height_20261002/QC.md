# Visual QC

> Reviewer: Codex · 2026-10-02 · 3 conditions × 2 matched seeds

See [comparison sheet](outputs/proportion_height_comparison.png). All images use the same two identity references, shared uniform reference, and short prompt format; no body-proportion guide was supplied.

| Condition | Seed | Relative height | Requested head/body ratio | Two identities / uniform / hands | Notes |
|---|---:|---|---|---|---|
| 8 vs 9, same 170 cm | 6200411 | Pass: nearly same total height | Weak / not clearly separated | Pass / Pass / Pass | The requested head-count difference is not visually clear. |
| 8 vs 9, same 170 cm | 6200412 | Pass: nearly same total height | Weak / not clearly separated | Pass / Pass / Pass | Similar result; no reliable 8-vs-9 proportion contrast. |
| 9 vs 9, 160 vs 180 cm | 6200411 | Pass: right figure clearly taller | Pass visually: both similarly proportioned | Pass / Pass / Pass | Height difference reads clearly against a shared ground line. |
| 9 vs 9, 160 vs 180 cm | 6200412 | Pass: right figure clearly taller | Pass visually: both similarly proportioned | Pass / Pass / Pass | Similar height ordering and figure proportions. |
| 8 vs 9, 160 vs 180 cm | 6200411 | Pass: right figure clearly taller | Weak / not measurable from visual output | Pass / Pass / Pass | Height ordering is clear; exact head-count distinction is not. |
| 8 vs 9, 160 vs 180 cm | 6200412 | Pass: right figure clearly taller | Weak / not measurable from visual output | Pass / Pass / Pass | Similar result; numerical proportions remain uncertain. |

## Conclusion

The model followed the requested relative height ordering in all four outputs where the prompt specified different heights. It did not reliably express an eight-head versus nine-head difference when the two figures were requested at the same height. In the mixed condition, the taller right figure is clear, while exact head-count proportions cannot be confirmed by visual review.

For this model and prompt style, height contrast is more controllable through text than exact head/body ratio. This suggests numeric prompts alone should not replace the body guide for head proportion. The review is visual and covers two seeds per condition; heights were not measured from image segmentation.
