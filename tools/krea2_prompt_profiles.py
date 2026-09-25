"""Canonical Krea2 Identity Edit prompt profiles.

Keep these prompts in one place.  The matching research, rationale, and
parameter contract lives in docs/40_krea2_prompt_and_identity_pipeline.md.
"""

PROMPT_VERSION = "krea2-identity-v1"

IDENTITY_PORTRAIT = (
    "Create a centered, front-facing, square head portrait from this reference image. "
    "Preserve the exact facial identity, facial proportions, eye shape and spacing, "
    "nose, mouth, jawline, hairline, skin tone, and expression. Change only the portrait "
    "rendering while keeping the person recognizable. Use one person, a neutral simple "
    "background, the same head scale and placement for every subject, and only the head "
    "with a very small amount of neck visible."
)

IDENTITY_REMOVE = (
    "Remove {item} from this reference image while preserving the exact person, facial "
    "identity, facial proportions, expression, hairline, head position, lighting, and "
    "composition. Do not redesign the face or add a replacement accessory. Keep the portrait "
    "as a centered square head portrait."
)

JIBS_STYLE_PORTRAIT = (
    "Apply the Jibs World of Warcraft fantasy illustration rendering to this exact person. "
    "Preserve the established facial identity, facial geometry, eye shape and spacing, "
    "nose, mouth, jawline, hairline, expression, and head scale. Change only the visual "
    "rendering style. Create a centered, front-facing, square head portrait with one person, "
    "a simple background, and only the head with a very small amount of neck visible. "
    "Do not redesign the face or introduce new facial features."
)

VIDEO_REFERENCE = (
    "Restage this exact person as a centered character reference portrait. "
    "Preserve the established face and identity. Use the same front-facing head "
    "scale, neutral expression, consistent lighting, plain background, and 1:1 "
    "composition. Do not introduce new facial features or accessories."
)

TEAR_MARK_FACE = (
    "Create a centered, close facial reference portrait of this exact undead elven woman. "
    "Preserve her established facial identity, pale cool skin, pointed ears, sharp elven "
    "facial structure, eye shape, nose, mouth, jawline, hood and dark hairline. Clearly show "
    "two thin dark burgundy-black tear streaks beneath the eyes, painted or embedded directly "
    "on the skin and following the cheeks. These are fixed facial markings attached to skin, "
    "not hair, not fibers, not loose strands, not ribbons, and not floating objects. Keep the "
    "long black hair visibly separate from the markings and attached only to the scalp. Neutral "
    "gray studio background, no wind, no motion, no extra accessories, square close-up, sharp "
    "facial detail, one person."
)

FRONT_REFERENCE = (
    "Create a centered full-body front character reference of this exact undead elven woman. "
    "Preserve her established identity, pale skin, pointed ears, dark hood, long black hair, "
    "dark red and black armor, silhouette and costume details. Show her standing neutrally, "
    "facing directly forward, with the fixed dark tear streaks clearly attached beneath the "
    "eyes as facial skin markings, separate from the hair. Neutral gray studio background, "
    "even lighting, no wind, no motion, no extra characters, full body, one person."
)

BACK_REFERENCE = (
    "Create a centered full-body back character reference of this exact undead elven woman. "
    "Preserve the same identity and costume as the reference: dark hood, long black hair, "
    "dark red and black armor, cape and back silhouette. Show her standing neutrally with her "
    "back directly toward the viewer; the face is not visible. Neutral gray studio background, "
    "even lighting, no wind, no motion, no extra characters, full body, one person."
)

THREE_QUARTER_REFERENCE = (
    "Create a centered full-body three-quarter character reference of this exact undead elven woman, "
    "turned approximately 45 degrees to the viewer's left. Preserve the exact facial identity, pointed "
    "ears, pale skin, platinum hair, dark hood, dark teal armor, belt, bow and cape. Keep the same neutral "
    "standing pose, proportions, costume details, neutral gray studio background and even lighting. Show "
    "one person, no motion, no extra accessories, full body, with the visible three-quarter face and the "
    "near-side costume silhouette clearly readable."
)


def get_prompt(mode, remove_item="eyeglasses and all eyewear"):
    """Return the canonical prompt for a runner mode."""
    if mode == "identity_portrait":
        return IDENTITY_PORTRAIT
    if mode == "identity_remove":
        return IDENTITY_REMOVE.format(item=remove_item)
    if mode == "jibs_style_portrait":
        return JIBS_STYLE_PORTRAIT
    if mode == "tear_mark_face":
        return TEAR_MARK_FACE
    if mode == "front_reference":
        return FRONT_REFERENCE
    if mode == "back_reference":
        return BACK_REFERENCE
    if mode == "three_quarter_reference":
        return THREE_QUARTER_REFERENCE
    raise ValueError(f"unknown Krea2 prompt mode: {mode}")
