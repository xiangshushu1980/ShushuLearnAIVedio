# Visual QC

> Reviewer: Codex · 2026-10-02 · 10 scored images · two seeds per principal condition, plus two weapon-count prompt refinements.

See `outputs/contact_sheet.png` for a complete overview. This test compares two identities in one image; it does not yet test consistency across separate images or poses.

| Condition | Seed | Exactly two distinct people | Shared uniform | Matching weapon | Notes |
|---|---:|---|---|---|---|
| Prompt only | 6200211 | Pass | Fail | Partial | Each face/hair is distinct, but the black-haired swordswoman keeps the navy/red armor while the red-haired character keeps burgundy/gold mage clothing. Weapon count and hand placement differ. |
| Prompt only | 6200212 | Pass | Fail | Partial | Original outfit distinction remains; the swords are broadly similar but not consistently presented as one item per person. |
| + uniform | 6200211 | Pass | Pass | Partial | The two outfits closely match in coat, ivory front, sash, trousers, boots and shoulder armor. One sword is clear; the other's presentation is partly obscured/at the hip. |
| + uniform | 6200212 | Pass | Pass | Partial | Uniform is nearly duplicated across the two identities. The swords are mostly sheathed and similar, although hand/hip placement varies. |
| + weapon | 6200211 | Pass | Fail | Pass, count varies | Katana designs are visibly similar; the original samurai and mage outfits remain different. Extra hilt/sheath-like forms appear. |
| + weapon | 6200212 | Pass | Fail | Pass, count varies | Same pattern: matching sword style, no outfit convergence, and more than one sword-like component per person. |
| + uniform + weapon | 6200211 | Pass | Pass | Design pass, count fail | Both wear a closely matching uniform and carry matching katana-like swords. Each also has extra hilt/scabbard-like forms, so the one-weapon constraint is not clean. |
| + uniform + weapon | 6200212 | Pass | Pass | Design pass, count fail | Uniform remains tightly matched; extra sword/sheath forms persist on both people. |
| + uniform + weapon, sheathed prompt | 6200211 | Pass | Pass | Design pass, count fail | Uniform and katana design match. Despite explicit “one only, fully sheathed” language, each character appears to have duplicate sword/sheath components. |
| + uniform + weapon, sheathed prompt | 6200212 | Pass | Pass | Design pass, count fail | Same result: strong outfit match, but duplicate hilts/scabbard-like shapes persist. |

## Conclusion

- **Uniform: passed for this same-image, two-person test when a clean uniform-only reference is included (4/4 images across the two uniform-reference conditions).** The prompt-only and weapon-only conditions retained the two source characters' different original outfits (0/4).
- **Weapon design: mostly transferred and matched across the two people when the weapon ref was present (4/4 principal outputs show the same katana family), but item count was not controllable.** Even a second prompt revision explicitly asking for one fully sheathed katana per person still produced duplicate-looking sword/sheath components in both seeds (0/2 clean counts).
- Four references did not create an extra person or collage in Qwen's outputs; the composition stayed two-person and full-body in all ten images.
- Compared with the Krea2 run using the same face crops, Krea2 failed to match the clothing in all conditions and broke composition with all four refs. Qwen's biggest clear advantage here is exact shared clothing transfer. Both models still need a cleanup/edit pass for strict equipment counts.

This is encouraging evidence for Qwen as the main generator for **a shared uniform design in a group image**, not yet proof of cross-image character consistency. For a production sheet, first generate/approve one uniformed character with the weapon loadout, then reuse that canonical image (or separately edit each character) and inspect weapon count/accessory placement. Repeat the test across different poses/seeds before calling it a stable production baseline.

## Follow-up: single sheathed katana prompt

Two prompts were compared using the same faces and uniform reference. Both asked for exactly two weapons in the whole image: one complete sheathed katana on each person's left hip, with one grip and guard connected to one scabbard.

| Condition | Seed | Exactly one sheathed katana each | Uniform match | Notes |
|---|---:|---|---|---|
| Faces + uniform; weapon described in prompt | 6200213 | Pass | Pass | One hilt/scabbard assembly per person, same placement and design. |
| Faces + uniform; weapon described in prompt | 6200214 | Pass | Pass | Same result across the second seed. |
| Faces + uniform + weapon image ref | 6200213 | Fail | Pass | Extra hilt/scabbard components appear on both people. |
| Faces + uniform + weapon image ref | 6200214 | Pass | Partial | One sheathed katana per person, but details and placement diverge more than in the prompt-only pair. |

**Best tested setup:** use the two face refs and the uniform ref, omit the separate weapon image, and define the complete sheathed katana in the prompt. The tighter positive description of the single assembled object worked better than adding more negative clauses. This passed 2/2 seeds; it is a promising control pattern, not yet a broad reliability guarantee.
