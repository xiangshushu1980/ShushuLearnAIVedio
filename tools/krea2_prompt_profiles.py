"""Canonical Krea2 Identity Edit prompt profiles.

Keep these prompts in one place.  The matching research, rationale, and
parameter contract lives in docs/40_krea2_prompt_and_identity_pipeline.md.
"""

PROMPT_VERSION = "krea2-identity-v2-turnaround"

UNIFIED_CHARACTER_STYLE = (
    "High-detail realistic fantasy game character reference photography, physically plausible materials, "
    "clean silhouette, restrained cinematic realism, neutral warm-gray studio background, soft even three-point "
    "lighting, no dramatic perspective, no text, no watermark, no collage, one character only. "
)


def unified_front_reference(character_spec):
    return (
        UNIFIED_CHARACTER_STYLE
        + "Create one centered full-body front subject reference from this exact subject specification: "
        + character_spec
        + " Show the character standing neutrally, facing directly toward the camera, head to feet fully visible. "
        "Keep the same proportions, costume layers, colors, materials, signature accessories and carried equipment "
        "throughout this subject pair. Make the head, face or defining focal features readable, but do not beautify or redesign the subject."
    )


def unified_back_reference(character_spec):
    return (
        UNIFIED_CHARACTER_STYLE
        + "Using the supplied front subject image as the single identity and costume anchor, create one centered "
        "full-body back subject reference of the same exact subject: "
        + character_spec
        + " Show the character standing neutrally with the back directly toward the camera, head to feet fully visible. "
        "Preserve the exact height, body proportions, hair length and color, costume palette, fabric and armor materials, "
        "cape or coat shape, belts, carried equipment and signature accessories from the front image. Reveal only a "
        "plausible rear construction; do not invent a new outfit or a second character."
    )


def unified_turnaround_sheet(character_spec):
    return (
        UNIFIED_CHARACTER_STYLE
        + "Create exactly ONE turnaround sheet containing EXACTLY TWO and only two full-body depictions of the exact same subject from the supplied anchor image. "
        + character_spec
        + " Layout is a strict two-column character sheet: LEFT = one straight FRONT view, RIGHT = one straight BACK view. "
        "There must be no middle figure, no third figure, no duplicate front, no extra head, no inset, no profile, no labels and no text. "
        "Both depictions must use the SAME neutral anatomical standing pose: feet at the same width and matching positions, arms hanging in the same relaxed angle, hands at the same height, head centered, shoulders level, identical scale and full-body framing. "
        "This is a pose-matched front/back record, not a lineup or a character sheet with multiple poses. "
        "The two depictions must be the same physical costume and hairstyle viewed from opposite directions. "
        "Every bilateral structure must correspond to the same body landmark: shoulder armor sits on the same shoulder and same shoulder-blade height; collars, belts, straps, cuffs, gloves, boots and coat hems align in height and width. "
        "Hair must be the same hairstyle, color, length, volume and tied sections; the back view shows the rear of that exact hairstyle, never a redesigned hairstyle. "
        "The front may show front-only fasteners, chest details and face; the back must show plausible rear hair, back collar, shoulder construction, cloak rear, rear belts and back equipment instead of copying front-only details. "
        "Do not mirror front-only details onto the back, do not invent a new costume, do not change the pose between panels, and do not add any other subject or view."
    )

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
    "Create exactly one centered full-body three-quarter character reference of this exact person, "
    "turned approximately 45 degrees to the viewer's left. Preserve the exact facial identity, hair, "
    "skin tone, ears if present, clothing, armor, belt, equipment and cape from the reference. Keep a "
    "neutral standing pose, the same proportions and costume details, a plain neutral gray studio "
    "background and even lighting. No duplicate person, no collage, no motion, no extra accessories; "
    "show one person from head to feet with the visible three-quarter face and near-side costume clearly readable."
)

WARDROBE_FULL_REFERENCE = (
    "Create a centered full-body front character reference of this exact person. "
    "Preserve the established face, hair, body proportions, clothing, armor, equipment "
    "and silhouette from the reference. Show one person standing neutrally, facing the "
    "viewer, with a plain neutral gray studio background, even lighting, no motion, no "
    "extra characters and no newly invented accessories. Make the complete outfit and "
    "body readable from head to feet."
)

WARDROBE_BODY_REFERENCE = (
    "Create a centered full-body wardrobe and body reference from this exact character. "
    "Preserve the clothing, armor, body proportions, shoulder width, collar, hands, "
    "equipment and silhouette exactly. Replace the face and hair with a neutral, faceless "
    "matte mannequin head aligned to the original neck and shoulders; do not show facial "
    "features or identity cues. Keep one standing body, front-facing, head to feet visible, "
    "plain neutral gray studio background, even lighting, no extra objects or characters."
)

SIDE_REFERENCE = (
    "Create exactly one strict full-body left-side profile character reference of this exact person. "
    "Preserve the established facial identity, hair, pointed ear if present, clothing, "
    "armor, equipment and silhouette. The body must be exactly side-on at 90 degrees, "
    "standing neutrally from head to feet, with a plain neutral gray studio background, "
    "even lighting, no motion, no duplicate person, no collage, no extra characters and no invented accessories."
)


def get_prompt(mode, remove_item="eyeglasses and all eyewear", character_spec=None):
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
        if character_spec:
            return unified_front_reference(character_spec)
        return FRONT_REFERENCE
    if mode == "back_reference":
        if character_spec:
            return unified_back_reference(character_spec)
        return BACK_REFERENCE
    if mode == "turnaround_sheet":
        if not character_spec:
            raise ValueError("turnaround_sheet requires character_spec")
        return unified_turnaround_sheet(character_spec)
    if mode == "three_quarter_reference":
        return THREE_QUARTER_REFERENCE
    if mode == "wardrobe_full_reference":
        return WARDROBE_FULL_REFERENCE
    if mode == "wardrobe_body_reference":
        return WARDROBE_BODY_REFERENCE
    if mode == "side_reference":
        return SIDE_REFERENCE
    raise ValueError(f"unknown Krea2 prompt mode: {mode}")
