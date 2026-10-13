# Visual QC

> Reviewer: Codex · 2026-10-02 · paired 2-seed comparison

See [comparison sheet](outputs/duo_proportion_comparison.png). Seeds 6200311 and 6200312 were reused across conditions. The top row is numeric text only; the bottom row adds the neutral two-person body guide as image 1.

| Condition | Seed | Head/body proportion | Two distinct identities | Shared uniform | Hands visible | Notes |
|---|---:|---|---|---|---|---|
| Text: 8-head prompt | 6200311 | Partial | Pass | Pass | Pass | Complete figures; heads read slightly large and bodies compact. |
| Text: 8-head prompt | 6200312 | Partial | Pass | Pass | Pass | Similar compact proportion; uniform remains consistent. |
| Body guide + text | 6200311 | Pass, visually closer | Pass | Pass | Pass | Smaller relative heads and longer legs; full figures fit. |
| Body guide + text | 6200312 | Pass, visually closer | Pass | Pass | Pass | Proportion tracks guide; full figures, matching uniform and hands. |

The guide itself is a neutral full-body sheet with two equal-height figures, plain gray bodysuits, no weapons or accessories, and visible hands. It carries pose and body scale while identity and uniform come from separate references.

## Conclusion

For this pair and these two seeds, numeric wording alone did not reliably solve the user's large-head concern. Adding the neutral body-proportion guide produced a visibly more elongated figure in both matched comparisons while preserving the face references, shared uniform, and hands. Use the guide in the next production step, then add objects after this baseline is accepted. Visual judgment only; the ratios were not measured from segmentation, and two seeds do not establish general reliability.
