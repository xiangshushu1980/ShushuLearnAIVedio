# Visual QC

> Reviewer: Codex · 2026-10-02 · Main outputs: 8 · Two seeds per condition

Open `outputs/contact_sheet.png` for all eight at a glance and `outputs/reference_sheet.png` for the two helper references.

| Condition | Seed | Exactly two distinct people | Same uniform on both | Same weapon / count | Notes |
|---|---:|---|---|---|---|
| Prompt only | 6200211 | Pass | Fail | Fail | Faces remain distinguishable. Left keeps the red-black samurai armor; right keeps the burgundy mage coat and gold shoulder armor. Both show sword-like blades, with extra/sheath-like lines. |
| Prompt only | 6200212 | Pass | Fail | Fail | Same split: original character costumes persist despite the shared-uniform prompt. Weapons are not clearly one matching, single sword each. |
| + uniform | 6200211 | Pass | Fail | Fail | Shared ivory/navy/red palette appears in places, but left retains heavy red-black lamellar armor while right retains burgundy/gold mage armor. |
| + uniform | 6200212 | Pass | Fail | Fail | Some coat colors converge; shoulder armor, coat cut and overall silhouette still differ substantially. |
| + weapon | 6200211 | Pass | Fail | Partial | The two held blades have a more similar katana silhouette, but the left figure also has a second sword/scabbard-like blade at the hip. Costumes remain distinct. |
| + weapon | 6200212 | Pass | Fail | Partial | Similar katana-like held blades, but extra sword/scabbard shapes remain; outfits remain distinct. |
| + uniform + weapon | 6200211 | Fail | Fail | Fail | Two intended people plus an extra headless floating outfit/body between them; sword duplication and costume-role bleed. Reference-board-like failure. |
| + uniform + weapon | 6200212 | Fail | Fail | Fail | Extra headless outfit/body appears between the two people, with additional weapon shapes. Not a clean two-person image. |

## Result

- Distinct face identities stayed reasonably separated in the first six outputs (6/6), but the face crops still carried enough character context that each role's original outfit persisted.
- Prompt-only and uniform-reference conditions produced no exact matching pair of uniforms (0/4). The outfit image helped with broad palette cues but did not make the armor and garment cut match.
- Weapon reference made the held weapon shapes more alike (2/2 partial), but did not reliably enforce one weapon per person (0/2 clean count).
- Combining both shared-object references with the two face references failed the two-person composition in both samples (0/2), consistent with reference overload/collage behavior.

For this setup, Krea2 can make a coherent two-person illustration with recognizable separate identities, and a shared weapon reference can nudge weapon shape. It does not reliably produce a squad wearing exactly the same outfit or carrying exactly one identical weapon each. For a production character lineup, use one clean full-body uniform anchor and edit/compose individuals in controlled passes, or create a single master design first and reuse it as a stronger reference; the tested four-reference route is not reliable.
