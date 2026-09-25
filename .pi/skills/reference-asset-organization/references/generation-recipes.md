<!-- Owner: Sean -->

# Reference generation recipes

These are task templates, not claims that one model or prompt guarantees identity. Keep the object ID, canonical source, model, and generation parameters in the manifest.

## Character sequence

Generate in this order:

```text
canonical identity/full-body → face close-up → side/back views → accessory or variant views → optional same-object board
```

For a new stylized character, a Krea2 identity anchor is an acceptable canonical source when Krea2 is the selected image model. Use a plain edit instruction or the model's supported identity workflow; do not treat a style reference as an identity reference. The canonical image should have one character, the intended wardrobe, a neutral or controlled background, and no unrelated props.

Canonical prompt skeleton:

```text
Create one full-body character reference for [character ID]. Preserve the canonical identity: [face/hair/eyes/age/signature features]. Preserve the canonical wardrobe: [silhouette/colors/materials/accessories]. Neutral controlled background, clear full-body view, no other person, no text, no watermark, no scene-specific prop unless it is permanently part of the character design.
```

Derived-view skeleton:

```text
Use the canonical reference for [character ID]. Keep the exact same person, face, hair, eyes, age, wardrobe, colors, and accessories. Show a [left three-quarter / right profile / back] view. Change only the camera/viewpoint. One person, no new costume, no added prop, no text, no watermark.
```

Face skeleton:

```text
Use the canonical reference for [character ID]. Create a clean face close-up of the same person. Preserve face shape, eyes, hairline, hair color, age, and expression family. Keep the wardrobe only as a small contextual edge; no second person, no scene, no text, no watermark.
```

Do not generate side/back views independently from text if the canonical identity is available. If a derived view conflicts with the canonical image, mark it `needs_regeneration` rather than averaging the conflict into a board.

## Scene recipe

```text
Create a clean establishing reference for [scene ID]. Show [architecture/layout/landmarks], [palette], [lighting direction/time/weather], and [camera height or viewpoint]. No principal characters, no foreground prop that is not part of the scene, no text or watermark.
```

Generate lighting or landmark variants only when a shot requires them. Keep the same location ID and label the state explicitly, for example `observatory_night_v1`.

## Spell recipe

```text
Create a clean visual reference for [spell ID] only: [shape/geometry], [color family], [glow], [particle structure], and [scale]. Isolated effect presentation, no character, no hands, no scene, no text or watermark. This defines the effect's visual family, not its owner.
```

For charge/release states, derive both from the same spell canonical source and record them as variants. Use `partially_preserved` for state changes in H3 retention when appropriate.

## Prop recipe

```text
Create a clean single-object reference for [prop ID]: [silhouette], [material], [colors], [markings], and [relative scale cues]. Neutral controlled background, no person holding it, no unrelated objects, no text or watermark.
```

Generate a hand-held/use view only after the clean prop source passes QC. The use view describes relationship and scale; it does not replace the canonical prop image.

## Board recipe

Create a board only after its member images pass QC. Include accepted views of one object, clear spacing, no labels that could be copied into the generated video, and no unrelated objects. Record member asset IDs in the manifest. Keep the original source images beside the board.

The board is for review and optional auxiliary use. For H3, select the individual source images when identity, close-up detail, or semantic binding matters.
