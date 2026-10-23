---
name: seed-audio
description: Use the project-owned Seed Audio 1.0 ComfyUI node to turn scripts, dialogue, sound effects, ambience, and optional voice or image references into a unified audio clip; also use when writing or reviewing Seed Audio prompts.
---

# Seed Audio 1.0

Use this skill when a request mentions Seed Audio, asks to turn a screenplay or scene into generated audio, or combines dialogue with environment and action sounds. Read [the usage guide](references/usage-guide.md) before writing a prompt or assembling a generation workflow. The guide contains the official limits and the project's node mapping, so routine use does not require fetching the API documentation.

## Generation path

- Use the project-owned `SeedAudioBytePlus` ComfyUI node as the normal generation interface. It calls the selected provider API internally. Do not bypass it with a direct Seed Speech HTTP request for ordinary creation.
- A ComfyUI API workflow still means a graph containing this node executed by the shared ComfyUI service; it is distinct from calling the provider API directly. Follow the shared [ComfyUI skill](/home/sean/.pi/agent/skills/comfyui/SKILL.md) and its HTTP API contract when submitting or monitoring a graph.
- The API-format starting workflow is `workflows/seed_audio_byteplus_api.json`; it is not a canvas layout. The node package also includes a canvas example. Check the live node schema before submission if the installed version or graph shape may differ.
- Connect the `audio` output to ComfyUI `Preview Audio` or `Save Audio`. Inspect the returned duration and listen to the actual result; successful execution alone does not prove the requested dialogue, roles, timing, or mix were achieved.

## Work from scripts

- Preserve supplied dialogue verbatim unless the user asks for rewriting. Do not invent or change plot facts, lines, or speaker intent to fill gaps.
- Organize a scene prompt from its overall duration and setting, to role/voice descriptions and exact dialogue, then the order and overlap of environment and action sounds, and finally the ending/tail. Use natural-language time cues when timing matters.
- For each named speaker, identify the speaker before their line and give only useful voice/performance traits from the script or user: language/accent, perceived register or timbre, pace, emotion, and delivery. Describe ambient beds, foreground effects, distance/movement, and relative loudness so the model can mix them as one scene.
- The organization template and official-versus-inferred distinctions are in the usage guide. Treat it as a prompt aid, not as a required API grammar.
- If the user asks only for a prompt or script plan, deliver that without submitting a generation. A generation is a metered external request: execute only when the user asks to create audio or has authorized generation. Keep `generation_count` at 1 unless they ask for multiple takes; each take is a separate request.

## Reference selection

- No reference media: use `text only`; describe each voice and the scene in `text_prompt`.
- Image reference: select `image reference` and connect one image or use a public HTTPS image URL. The prompt still needs to specify the audio to produce.
- Voice/audio reference: select `audio reference`; use up to three connected audio clips or reference-source fields, and label clip references as `@Audio1`–`@Audio3` in matching order when the prompt uses them. A source field can instead carry a supported speaker ID or HTTP(S) audio URL.
- Preset voice: use `preset voice` and provide the supported speaker ID.
- Do not combine image and audio references in one request. The API treats these as incompatible reference modes. If the user supplies both and the choice affects the result, explain the limitation and ask which reference should control; never silently discard one.
- A prompt can describe multiple characters, but do not promise stable per-character voice identity from descriptive text alone. If fixed voice IDs or reference clips are needed, bind them explicitly where supported and do not claim voice consistency beyond what the current run demonstrates.

## Current skill boundary

This is a project-level use-case skill. General ComfyUI service, API, queue, and shared-resource procedures remain in their shared skills; do not copy those contracts here. Official Seed Audio behavior is maintained in the usage guide. Add local experience there only after it is repeatable and record it separately from official requirements.
