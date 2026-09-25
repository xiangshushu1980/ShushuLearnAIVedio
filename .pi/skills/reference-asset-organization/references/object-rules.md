<!-- Owner: Sean -->

# Same-object package rules

## Package levels

Use the smallest package that covers the intended shots. Choose views by the surfaces the shot will expose, not by a fixed number of images: the canonical/main view is the default, and side/back views are conditional aids for orbiting, turning, or reverse-facing coverage.

| Object | Minimum package | Add only when needed |
|---|---|---|
| Character | identity/front or full-body + face when face matters | side for orbit/side exposure, back for reverse-facing details, wardrobe/accessory detail, variant, action/pose, pair staging |
| Scene | clean establishing view | side/back or alternate angle when an orbit exposes spatial structure; landmark detail, lighting/atmosphere variant |
| Spell | clean effect view | charge/release states, scale variant, interaction/staging view |
| Prop | clean single-object view | side/back/detail when the shot rotates or reveals hidden surfaces, hand-held/use view, scale relationship |

## Character rules

The canonical identity image owns face, hair, eyes, age, and overall identity. The full-body image owns silhouette, clothing, shoes, and carried signature items. The face image is an independent close-up for close shots. Side and back images fill view-specific information and are generated from the same canonical identity, with the same wardrobe description.

Permitted same-character merge:

```text
front identity + face + side + back + wardrobe/accessory detail
```

Not permitted:

```text
character A + character B
character + unrelated scene
character + spell as one identity source
character + prop as the prop's canonical source
```

If a prop is permanently attached to the character, it may appear in the character's wardrobe/identity image, but create a separate prop package when the prop has its own close-up, ownership, or continuity requirement.

## Scene rules

Scene sources should be clean of principal characters and major foreground props. They define spatial layout, architecture, palette, lighting direction, and atmosphere. Alternate scene views may share a scene package only if they are the same location and lighting state. For an orbit, add only the side/back scene view that the camera will expose; do not merge unrelated locations into one package. A day/night/rain change is a variant, not an accidental inconsistency.

## Spell rules

Spell sources define the effect's shape, color family, geometry, particle behavior, and scale family. They should not be used to establish which character owns the effect; ownership is written explicitly in the H3 prompt and attached to the character subject. Mark a state change such as charge → release as a variant inside the spell package, not as a new unrelated spell unless its identity changes.

The visual reference only locks broad effect structure. Fine particles and exact frame-by-frame physics remain prompt/motion-controlled and should not be promised as fully preserved.

## Prop rules

Prop sources define silhouette, material, color, markings, and relative scale. Use a clean single-object image as the canonical source. Add side/back/detail references only when the motion or camera exposes those surfaces; this constrains hidden geometry but does not freeze the object's position or deformation during use. A hand-held image is a relationship/staging aid and must not replace the clean prop source. If two props are visually similar but semantically distinct, keep separate packages and IDs.

## Boards and contact sheets

A same-object board may contain several accepted views of one object with clear separation and no unrelated entities. It is useful for human review, package indexing, and as an optional auxiliary H3 reference when tested. Keep every source image separately available.

Do not create a board containing all characters, the whole scene, spells, and props and call it a canonical object reference. That is a staging board/negative control, not a same-object package.
