# Visual QC

> Reviewer: Codex · 2026-10-02 · 3 prompt variants × 2 matched seeds

See [seed-aligned body type comparison](outputs/body_type_comparison_seed_aligned.png). Each row reuses one seed across the three build prompts. All six images use the same face, uniform, katana, and scene references; only the body-build sentence changes.

| Build prompt | Seed | Body silhouette | One character / identity | Uniform | One katana | Scene/style | Pose and framing |
|---|---:|---|---|---|---|---|---|
| Slender | 6200511 | Pass: leaner torso and limbs | Pass | Pass | Pass | Pass | Partial: full body, slight stance/framing drift |
| Slender | 6200512 | Pass: narrow, long silhouette | Pass | Pass | Pass | Pass | Partial: full body, three-quarter angle |
| Athletic | 6200511 | Pass: broader shoulders and firmer limbs than slender | Pass | Pass | Pass | Pass | Partial: more frontal stance than slender |
| Athletic | 6200512 | Pass: fit, moderate build | Pass | Pass | Pass | Pass | Partial: figure scale and angle vary |
| Powerful | 6200511 | Pass: visibly thicker torso and limbs | Pass | Pass | Pass | Pass | Partial: wider stance and larger figure |
| Powerful | 6200512 | Pass: broad shoulders, arms and thighs | Pass | Pass | Pass | Pass | Partial: figure is larger and more frontal |

The three silhouettes are visibly distinct in both seed comparisons, strongest for the powerful build. The uniform and moonlit courtyard remain recognizable across all six. The katana count stays at one, though hip angle and scabbard presentation shift. This run did not precisely lock pose, camera distance, or figure scale despite asking to keep them fixed. The uniform reference is a headless full-body garment image and may also anchor the starting silhouette.

## Conclusion

For this single-character setup, concise body-build language can produce a useful visible difference while identity, uniform family, one katana, scene elements, and painterly style remain intact. It does not provide precise control of pose or scale, and the exact garment details and scene geometry still vary. If the target build needs closer matching than these broad categories, the next useful comparison is a target body-silhouette reference against the same prompt-only condition, with the four existing asset references held fixed.

Two seeds per build are a small visual check, not a general reliability claim. No pixel-based body measurement was performed.
