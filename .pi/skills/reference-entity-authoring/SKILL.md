---
name: reference-entity-authoring
description: Draft or revise Reference entity descriptions and Krea2 concept/main-appearance prompts from explicit entity facts, relationships, story context, and selected images. Use for authoring Reference content; not for H3 video prompts or image generation.
metadata:
  short-description: Author Reference entity text and image prompts
---

# Reference Entity Authoring

> Owner: Sean

Help create and maintain the text that defines a Reference entity and guides its first two image stages. Keep entity facts, relationships, story context, image prompts, and confirmed images distinct.

## Scope

This skill produces:

- an entity introduction/description;
- a **concept image** prompt for a target look, style, atmosphere, or context;
- a separate **main appearance** prompt for the canonical visual reference.

Concept and main-appearance prompts are Krea2 image instructions. They are not H3 Ref2VA video prompts. Do not generate images, submit ComfyUI runs, or claim that text was saved unless a documented write interface is available and was actually used.

## Get entity context

1. Identify the selected entity and the requested operation: create its description, create one or both image prompts, or revise existing text.
2. Read the entity's available properties, relationships, story notes, current description and prompts, and relevant reference-image records. Use only a connected, documented data interface or context actually supplied by the user/current task.
3. If no entity store/API is available, ask for or use a supplied entity-context bundle. Do not scan unrelated project files or imply that the skill has database access.
4. Preserve provenance in the draft: distinguish confirmed facts, user-provided interpretation, and unresolved details. Resolve conflicting sources with the user instead of silently choosing one.

Relationships and story context provide evidence and intent; they are not automatically visual instructions. Include them in an image prompt only when they affect the requested appearance or scene. Do not invent an entity trait from a relationship or a story event.

## Draft the content

### Entity introduction

- Summarize stable identity, role, and appearance from the available entity properties.
- Use relationship and story information only to clarify identity or relevant context; keep plot events separate from permanent traits.
- Keep uncertain or missing details explicit. Do not fill gaps with genre convention.

### Concept image prompt

- State the desired target image and any requested setting, mood, composition, or visual direction.
- Select one required primary reference image and, if useful, one optional second reference from the entity's collected materials. More linked images do not enter the run implicitly.
- Treat the two image slots as input positions. Do not assign fixed meanings such as “identity image” or “style image” unless the user or validated workflow defines them.
- Derive appearance details from the entity introduction, then add only the requested concept-stage context.

### Main-appearance prompt

- Require the entity's **confirmed concept image as its only image reference**. If no confirmed concept exists, explain the prerequisite rather than substituting an early setting image.
- Describe the stable canonical appearance the main image should establish. Keep momentary action/story staging out unless requested.
- Use the concept stage's saved style profile by default. A different saved profile may be selected for a new attempt; do not write LoRA weights or other hidden workflow parameters into the prompt.

For Krea2-specific prompt constraints, consult [`docs/40_krea2_prompt_and_identity_pipeline.md`](../../../docs/40_krea2_prompt_and_identity_pipeline.md). Keep identity preservation, removal of a salient element, and style transfer as distinct goals when the selected workflow requires separate modes. Do not assume a prompt can compensate for an unsupported workflow input.

## Revision and manual editing

- Keep the description, concept prompt, and main-appearance prompt as separate editable revisions. Label which entity facts, relationship/story context, reference-image versions, and style profile informed each draft when that information is available.
- Preserve the user's manually edited text verbatim unless the user asks to revise it. Never silently replace it with a new Agent draft.
- When source facts change, mark dependent prompts as needing review. Do not regenerate automatically. Only create a refreshed prompt draft when the user or caller explicitly invokes this skill for that update; summarize material changes and let the user decide whether to adopt it.
- A draft is not a confirmed image. Image generation and candidate confirmation belong to the Reference workbench workflow.

## Output

Return only the requested fields, using clear headings:

1. `实体介绍`
2. `概念图提示词`
3. `主形象提示词`
4. `依据与待确认` — include source facts, selected image/version, assumptions, and unresolved conflicts when relevant.

Mark fields that were not requested as “未生成”. Keep prose concise and ready to paste into the corresponding editable field. If the user asks for structured data, preserve these field boundaries in the requested format.

## Related skills

- Use [`reference-asset-organization`](../reference-asset-organization/SKILL.md) for planning and organizing same-object image packages and selecting H3 shot references.
- Use [`h3-prompt-writing`](../h3-prompt-writing/SKILL.md) for H3 Ref2VA video prompts, not for these Krea2 image prompts.
