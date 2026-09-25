---
name: reference-asset-organization
description: Plan, generate, organize, and select reference assets for the same character, scene, spell, or prop before H3 Ref2VA generation. Use when establishing an object's canonical reference package or deciding which references a shot needs; do not use it for unrelated image editing or general H3 prompt writing.
metadata:
  short-description: Organize same-object references for H3
---

# Reference Asset Organization

> Owner: Sean

Use this skill for the reference-asset lifecycle:

```text
design → generate → organize same-object package → select per-shot H3 inputs
```

This is a project-level use-case skill. It does not replace the ComfyUI skill, the H3 prompt-writing skill, or the H3 Ref2VA official format.

## First decide the object and stage

Identify one object type: `character`, `scene`, `spell`, or `prop`. Keep the four types semantically separate. A character image may show that character's own clothing or carried prop, but it must not become the canonical reference for the scene, spell, or prop.

Then identify the stage:

1. `design`: derive the minimum and optional images from the shot requirements.
2. `generate`: create or obtain the images, using one canonical source for same-object variants.
3. `organize`: merge only complementary views of the same object into a versioned package and optional board.
4. `select`: choose only the references needed by the current H3 shot.

Do not skip `design` by generating an arbitrary large batch. Do not treat a contact sheet or board as proof that the individual images are consistent.

Read [generation-recipes.md](references/generation-recipes.md) when generating the images. Read [object-rules.md](references/object-rules.md) for per-object requirements and merge boundaries. Read [selection-matrix.md](references/selection-matrix.md) when preparing H3 inputs. Read [package-schema.md](references/package-schema.md) when creating files, manifests, or QC records.

## Default workflow

1. Extract entities, scenes, variants, viewpoints, and shot demands from the character sheet or shot list.
2. Create a `reference_plan` with a minimum package for each object and optional items triggered by actual shots.
3. Generate the canonical identity/source image first. For a character, a Krea2 identity anchor may be used; create side/back/variant images by cascading from the canonical image, not by independently reinventing the character.
4. Generate independent scene, spell, and prop images with clean content boundaries. Do not place unrelated objects in their canonical source image.
5. Human-check each source image before merging. Reject images that introduce a second identity, conflicting wardrobe, unexplained object, text, watermark, or background contamination.
6. Organize the accepted images into one package per object. A board/contact sheet is an index and optional same-object auxiliary reference, not a replacement for the source images.
7. At H3 time, select references by shot. Prefer two to four meaningful inputs; do not submit the entire package by default.
8. For H3 Ref2VA, use the six-section format and stable labels from `h3-prompt-writing`; explicitly bind each image to the object it defines. Read `docs/17_h3_prompt_writing_rules.md` and the Ref2VA reference before writing the prompt.

## Non-negotiable rules

- Same-object merge only: front/face/side/back/wardrobe details of one character may share a package; two characters may not be merged into one character package.
- One image, one semantic job: identity, wardrobe, scene, spell, and prop sources remain distinguishable even when indexed on one board.
- A scene source is empty of principal characters unless the scene itself is the requested object.
- A spell source is an effect source, not a character identity or ownership source.
- A prop source is a prop source, not a hand, character, or scene source.
- Keep the canonical image as the source of truth. Do not “fix” a conflicting variant only with prompt text; regenerate it from the canonical source.
- Do not use one total board as the default H3 reference. It is a staging/layout aid or negative-control style input, not the default identity package.
- When a board is used, explicitly state that it is a same-object design board and must not be copied as a grid, contact sheet, labels, or layout.
- Reference count is shot-dependent. More images are not automatically better; remove references that do not contribute to the shot.
- Record model, prompt, seed or generation ID, source references, version, and QC status for every accepted asset.

## Default decision policy

- One character, ordinary medium shot: independent identity/full-body image plus face image when the face matters; add the scene separately.
- One character, close-up or speaking: face image plus identity image; do not prioritize a board over the face image.
- Side/back/turning shot: add only the matching side or back view; do not add every viewpoint.
- Two or more characters: each character keeps its own identity/board and face assets; add independent scene, spell, and prop assets as needed. The tested D-style semantic grouping is the default candidate for complex multi-object shots.
- Strong staging requirement: a pair/staging board may be added as a composition aid, but it does not replace each character's identity source.
- Spell or prop absent from the shot: omit its reference. This is a shot-level selection rule, not deletion of the asset package.

## Validation and stopping condition

Before declaring a package ready, verify:

- same identity, wardrobe, silhouette, and signature accessories across accepted character views;
- scene layout and lighting are consistent across scene variants;
- spell shape/color/scale family is consistent across spell states;
- prop shape/material/scale family is consistent across prop views;
- no wrong-object ownership, accidental second person, layout-copy risk, or background leakage;
- the package has a minimum set and a clear reason for every optional image;
- the intended H3 shot can be expressed with stable `<Subject N>` and `<Picture N>` bindings.

Stop generating when the minimum package passes QC and all planned shot demands have a suitable image. Generate an additional view only when a new shot requirement, visible failure, or missing object detail justifies it.

## Evidence boundary

The current project evidence supports the rules under ordinary H3 Ref2VA conditions tested at 768×448, low/moderate motion, and 20 steps. It does not prove equal performance for fast action, high resolution, long video, heavy occlusion, or extreme close-ups. Mark such work as an extension test rather than silently changing the baseline.
