# Spatial and camera constraints for H3

Use this guide when a generated video must preserve scene layout, provide stable multi-view references, or follow a specific camera path. It is a **reusable prompt-writing method**, not a universal prompt to paste verbatim. Derive scene facts from that video's approved stills, scene plan, Blender previz, or measurements. Keep unknown scene measurements explicitly unknown; do not present guessed meter values or angles as facts. Camera motion can still have a numeric **design target** chosen from the shot request or a clearly labeled experiment contract (for example, “one full 360-degree orbit”). Record whether each value is source-measured, source-estimated, or a requested target. Copy the completed constraint card into that run's `run-log.md` so a later reviewer can see which facts shaped the prompt.

## Build a scene-specific constraint card

Before writing the H3 prompt, record only the facts that matter to acceptance:

| Field | Per-video value |
|---|---|
| Scene anchor / camera target | A stable central subject or world point |
| Layout anchors | Object identities and their relative positions, e.g. left/right, near/far, in front of/behind |
| Object state | Which objects remain fixed; which may move and how |
| Start camera | View direction, height/elevation, distance/framing, and projection only when known |
| Camera path | Pan/arc/track, direction, approximate angular or screen-space travel, duration and speed |
| End view | Required view or composition, if any |
| Invariants | No cuts, no zoom, fixed camera height/radius, no object swaps/duplication, as required |
| Evidence source / confidence | Image, measured scene, previz, or approximate visual estimate |

For camera values, label each one as **measured**, **estimated from source**, or **requested target**. A requested target does not claim H3 can obey it and does not claim the input scene was captured at that calibrated value.

Do not treat these fields as a fixed H3 syntax. Choose the few concrete constraints needed for this scene and express them as natural English inside the official prompt structure for the selected mode.

## Prompting rules

- State the scene/layout lock before describing the camera move: name the anchor object, preserve the relative arrangement, and say which objects remain stationary. Use visible relationships rather than an ungrounded list of coordinates.
- Describe the camera as **path + direction + amount + speed + target**. If supported by the scene plan, add elevation/height and distance/radius. Example shape: “The camera makes one continuous clockwise arc around [anchor], moving from [start view] toward [end view] by approximately [angle] over [duration], at a steady height and distance.”
- Add only relevant invariants: “one continuous shot,” “no cuts,” “no zoom,” “keep the fountain near frame center,” or “do not cross to the opposite side of the bench.” Avoid piling on redundant negatives.
- If the source video or Blender previz is assigned as the camera authority (notably video-led Ref2VA), bind that authority explicitly and do not write a competing camera path in prose. Use the detailed camera constraints when the prompt itself is authorized to control camera behavior.
- Projection words such as “orthographic” may be misunderstood by video models. Use them only when the mode needs them, describe the visible consequence (“parallel verticals, no perspective convergence, the full object remains inside frame”), and verify the generated frames. Do not treat wording as a camera calibration guarantee.
- Numeric values are requests to the model, not proof of compliance. Review actual start/middle/end frames and camera direction. For geometry work, retain measured depth/layout analysis as a separate stage; prompting alone does not produce calibrated 3D.

## Fillable wording pattern

Adapt and translate this pattern into the selected official prompt fields; replace every bracketed item with scene-specific facts or remove it when unknown:

> Keep [scene identity] and preserve the established arrangement: [object A relation], [object B relation], and [object C relation]. [Stationary objects] remain fixed in place and keep their shape and identity. In one continuous shot, the camera [path and direction] around [anchor], moving from [start view] to [end view] by about [amount] over [duration] at [speed]. Keep [height/elevation] and [distance/framing] steady; [target/framing rule]. [Relevant constraints such as no cuts or zoom].

## Current 3D courtyard example (scene-specific, not a default)

For the tested courtyard, the approximate plan is: fountain near the center, tree toward the far-left, bench along the far side, and two planters on the nearer left/right sides. A camera-control test could request a single continuous clockwise arc around the fountain, keeping a steady radius and height, with all props stationary and their positions preserved. Add a numeric angular travel or a specific endpoint only if it is defined by the approved source views. This wording is a test prompt hypothesis; it has not itself been shown to make H3 obey calibrated angles.
