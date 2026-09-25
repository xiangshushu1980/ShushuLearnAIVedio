---
name: h3-prompt-writing
description: Write MiniMax H3 video generation prompts for T2VA, I2VA, FL2VA, L2VA, and Ref2VA. Use when rewriting multimodal requests into H3 prompt structures, composing integrated_multimodal_description, overall_soundscape, and non_diegetic_music, aligning keyframes, or defining reference labels for images, videos, and audio.
metadata:
  compatibility: Portable to any agent that can read local files; no MiniMax Hub runtime is required.
---

# H3 Prompt Writing

## Workflow

1. Identify the input mode: T2VA, I2VA, FL2VA, L2VA, or full-reference Ref2VA.
2. For base text/keyframe modes, read `references/base-en.txt` and follow its final prompt structure.
3. For full-reference mode, read `references/ref-en.txt` and follow its six-section rewrite format.
4. When this skill is used inside the comfy-ops repository, also read `../../../docs/17_h3_prompt_writing_rules.md` as the project strategy overlay. Official references own field names, labels, ordering, and syntax; the project overlay owns local defaults and verified operating constraints.
5. Preserve the exact field names, section order, labels, and timing notation from the selected official guide.

## Base Modes

- T2VA: build the full audiovisual timeline from text.
- I2VA: start from the first frame and develop forward from it.
- FL2VA: describe the continuous path between the first and last frames.
- L2VA: infer a plausible opening and converge to the supplied last frame.

Use `integrated_multimodal_description`, `overall_soundscape`, and `non_diegetic_music` in the order shown in `references/base-en.txt`.

## Full-Reference Mode

Ref2VA rewrites use `subject_definitions`, `summary`, `retention_analysis`, `detailed_description`, `overall_soundscape`, and `non_diegetic_music` in that order. Reference labels stay consistent across all sections.

Read `references/ref-en.txt` for label rules, retention analysis, and complete examples.

## Output Rules

- Write rewrite sections in English; preserve dialogue, lyrics, and visible scene text in their original language.
- Describe each shot by composition, subjects, environment, actions, camera, sound, and the exact point where referenced content appears.
- Avoid plot summaries, unresolved reference labels, and timing that does not match the requested duration.

## Upstream result invariants

- Match the complete prompt timeline to the requested video duration (H3 target range: 4–15 seconds).
- Keep `<Picture N>`, `<Video N>`, and `<Audio N>` labels stable across every section.
- Prefer concrete visual and audio evidence over abstract adjectives such as “cinematic” or “beautiful”.
- For I2VA / FL2VA / L2VA, state explicitly how the supplied first and/or last frame connects to the timeline.

When this repository's rules conflict with these invariants, preserve the official field structure and labels first; apply the project strategy overlay only as a default for controllable generation.
