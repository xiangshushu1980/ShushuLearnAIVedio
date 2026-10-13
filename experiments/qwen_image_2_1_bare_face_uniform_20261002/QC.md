# Visual QC

> Reviewer: Codex · 2026-10-02 · 2 identity-reference edits + 4 duo outputs

See `outputs/identity_reference_review.png` to compare the original clothed crops with the edited bare-shoulder identity images, and `outputs/duo_comparison.png` for the four short-prompt results.

| Condition | Seed | Exactly two people | Face identities distinct | Shared uniform | Hands visible | Notes |
|---|---:|---|---|---|---|---|
| Clothed face crops | 6200301 | Pass | Pass | Fail | Pass | Black-haired character keeps dark lamellar armor; red-haired character keeps burgundy/gold source costume. |
| Clothed face crops | 6200302 | Pass | Pass | Fail | Pass | Original outfit cues are stronger: the two characters visibly keep different clothing/shoulder armor. |
| Bare-neck head/shoulder portraits | 6200301 | Pass | Pass | Pass | Pass | Both use matching navy/ivory/red uniform and same shoulder guard. Head scale is visually close. |
| Bare-neck head/shoulder portraits | 6200302 | Pass | Pass | Pass | Pass | Uniform stays matched, with both pairs of hands visible and empty. Head/shoulder scale remains similar. |

The two edited identity portraits retained the respective face and hairstyle well enough for this visual check, removed the source clothing/armor, and present comparable head-and-shoulder framing. One small earring remains in the red-haired identity crop, so “bare” here means no clothing or armor in the crop, not a jewelry-free face.

## Conclusion

For this setup, the clothing carried by the original face crops clearly interfered with uniform transfer: 0/2 clothed-crop outputs matched both outfits. With the edited bare-shoulder identity portraits, the same brief prompt and same uniform reference produced two distinct people in matching uniforms with visible hands in 2/2 seeds. The head-to-shoulder references also gave visibly more consistent head scale in this pair.

This supports the proposed sequence: make identity refs neutral and consistently framed; solve people, head/body scale, uniform and hands first; add weapons and accessories only after this baseline is accepted. It remains a two-seed check for this pair, not a general reliability claim.
