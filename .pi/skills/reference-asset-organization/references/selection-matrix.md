<!-- Owner: Sean -->

# H3 per-shot selection matrix

## Selection table

| Shot need | Character | Scene | Spell | Prop |
|---|---|---|---|---|
| ordinary single-person medium shot | identity/full-body; face if visible | scene view | omit | omit |
| close-up or speaking | face + identity | usually omit unless environment is important | omit | omit |
| side/back/turn | matching side or back + identity | scene if needed | omit | omit |
| two-person interaction | each character's own identity/board; face if close | scene | omit unless active | omit unless active |
| spell casting | character identity/face | scene | effect reference | omit unless active |
| character holding prop | character identity/face | scene | omit unless active | clean prop reference; use hand-held aid only if needed |

### View-trigger rule

The main/canonical view is the default input for every object type. Add a same-object side reference when an orbit or action exposes the object's side surface, and add a back reference when the shot exposes its rear surface. This applies equally to characters, scenes, spells, and props. These are conditional geometry/identity constraints, not mandatory image counts and not guarantees of exact pose, camera angle, or frame-by-frame physics.
| strong left/right staging | each character identity | scene | active effect if any | active prop if any; optional pair board |

The table describes default selection, not a mandate to fill every column. Omit an asset that is not visible or causally relevant in the shot.

## H3 binding rules

For ordinary Ref2VA, use the official six sections:

```text
subject_definitions
summary
retention_analysis
detailed_description
overall_soundscape
non_diegetic_music
```

Use `<Subject N>` for reusable visible entities and `<Picture N>` only when an image acts as a concrete frame or composition anchor. When an image only defines a character, scene, spell, or prop, cite it inside that subject definition rather than inventing a separate frame role.

Every image must be described by role, for example:

```text
<Subject 1> is Character A. <Picture 1> is the authoritative face and identity reference; <Picture 2> is the same character's wardrobe and body-silhouette reference.
<Subject 2> is the observatory environment defined by <Picture 3>; it does not define either character.
<Subject 3> is the cyan spell effect defined by <Picture 4>; it belongs to <Subject 1> only when the shot description says so.
<Subject 4> is the brass compass defined by <Picture 5>; it is not part of either character's identity.
```

Keep labels and meanings identical across all six sections. In `retention_analysis`, distinguish identity, wardrobe, scene, spell, and prop preservation. Do not use vague wording such as “all pictures jointly define the scene.”

## Tested organization candidates

- Independent semantic references (A): default baseline for one character or few objects.
- Semantic-cluster mix (D): default candidate for complex two-person/multi-object shots; each object remains separately bound.
- Staging/pair board (C): use when relative placement is the main problem, while retaining individual identity sources.
- One total board (E): negative/control style only; do not use as the normal package.

Current evidence is from ordinary Ref2VA at 768×448, 20 steps, low/moderate motion. Do not extrapolate these choices to fast action or high-resolution production without a new check.
