<!-- Owner: Sean -->

# Reference package and QC schema

Use a stable object ID and version. The exact storage root may be chosen by the active project, but the package should have this logical shape:

```text
<reference_root>/
  <object_id>/
    manifest.json
    source/
      identity_front.png
      face_closeup.png
      side_left.png
      back.png
    board/
      same_object_board.png
    prompts/
      identity_front.txt
      side_left.txt
    qc/
      review.json
```

Not every file is required. Do not create placeholder files for views that are not needed.

Each manifest entry should record at least:

```json
{
  "owner": "Sean",
  "object_id": "character_sylvanas",
  "object_type": "character",
  "package_version": "v1",
  "asset_id": "character_sylvanas_identity_front_v1",
  "role": "identity_front",
  "source_model": "Krea2",
  "source_asset": null,
  "prompt_file": "prompts/identity_front.txt",
  "path": "source/identity_front.png",
  "same_object_as": [],
  "contains": ["face", "hair", "wardrobe"],
  "excluded": ["other_characters", "scene_anchor", "spell_anchor"],
  "qc": {
    "identity_consistent": true,
    "wardrobe_consistent": true,
    "wrong_object_leak": false,
    "background_clean": true,
    "human_reviewed": true,
    "status": "accepted"
  }
}
```

For every accepted asset, preserve the generation model, prompt, seed or request ID, input references, resolution, and creation date when available. For a derived view, record the canonical source asset. For a board, record its member asset IDs and state that it is an index/auxiliary board.

## QC verdicts

- `accepted`: passes identity/content-boundary checks and can enter the package.
- `needs_regeneration`: same object is intended but identity, wardrobe, view, or object detail conflicts.
- `rejected_wrong_object`: contains another character/object or wrong semantic role.
- `invalid_prompt`: prompt mentions an object not enabled by the reference plan; do not use it to judge reference quantity.
- `auxiliary_only`: useful for human review or staging, but not a canonical source.

Before H3 use, make a shot-level record of selected asset IDs and their roles. This makes later drift attributable to the selected references rather than to the entire package.
