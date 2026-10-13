# [Sean] Qwen Image 2.1 Character Sheet V3 domain validation QC

## Summary

The adapted V3 workflow reliably creates a character face-plus-three-view sheet, a brass lantern turnaround, and a three-angle environment sheet when the views are explicitly defined. A round shield also works well as a prop. Fine geometry is less reliable for a long, thin katana, especially when the source contains both an exposed sword and a separate scabbard.

This is a visual review of fixed-reference seed sweeps. It tests the V3 workflow, not a standalone LoRA: the saved V2/V3 workflow graphs have no LoRA loader. The local run uses a manually supplied static prompt, Qwen Image 2.1 int8, 1536×1024 output, and standard VAE decode in place of upstream VAEDeGrid. It is not an unmodified upstream run.

## Results

| Domain | Visual result | QC |
|---|---|---|
| Character face + three views | 3/3 sheets contain one large face portrait and full-body front, side, and back views. Face, tied-back hair, uniform, armor, and silhouette stay recognizable. | Pass for this character and layout. [Seed 2026100300](outputs/character/seed_2026100300.png) · [2026100301](outputs/character/seed_2026100301.png) · [2026100302](outputs/character/seed_2026100302.png) |
| Prop: katana | Initial input had a loose scabbard and exposed blade; only 1/3 sheets kept the weapon state coherent. A new fully sheathed reference and stricter prompt still yielded only 1/3 fully complete views. Other seeds omitted the handle in one panel or changed the center view orientation. | Partial; suitable for rough layout exploration, not dependable prop geometry. [Retry seed 370](outputs/retry/prop_katana_sheathed/seed_2026100370.png) · [371](outputs/retry/prop_katana_sheathed/seed_2026100371.png) · [372](outputs/retry/prop_katana_sheathed/seed_2026100372.png) |
| Prop: round shield | 3/3 sheets show front, edge-on side, and rear views with a stable round silhouette, wood face, rim, and boss. One seed turned the intended two rear straps into four short segments; the other two retain two straps. | Pass for broad silhouette and views; inspect fittings and back hardware before using as a production reference. [Seed 2026100391](outputs/prop_shield/seed_2026100391.png) · [2026100392](outputs/prop_shield/seed_2026100392.png) · [2026100393](outputs/prop_shield/seed_2026100393.png) |
| Standalone object: brass lantern | 3/3 sheets show a front, narrow side, and rear-like view. Handle, frame, glass chamber, cap, and base remain coherent, with minor small-part variation. | Pass as a design reference; not precision manufacturing geometry. [Seed 2026100340](outputs/object_lantern/seed_2026100340.png) · [2026100341](outputs/object_lantern/seed_2026100341.png) · [2026100342](outputs/object_lantern/seed_2026100342.png) |
| Scene: shrine courtyard | The first prompt repeated a frontal view in two panels. After explicitly defining entrance, true side elevation, and overhead site-plan views, all 3 seeds produced three distinct views with the shrine, gate, path/stairs, pine, and lantern generally preserved. Spatial placement is plausible rather than metrically locked. | Pass for concept/reference sheets with explicit view descriptions; not a reliable floor plan or exact scene reconstruction. [Seed 2026100380](outputs/retry/scene_shrine_v2/seed_2026100380.png) · [2026100381](outputs/retry/scene_shrine_v2/seed_2026100381.png) · [2026100382](outputs/retry/scene_shrine_v2/seed_2026100382.png) |

No stray labels or unrelated people were visible in the reviewed outputs. The generated scene references and product sources are in `inputs/`; prompts and seeds are recorded in `prompts/` and `manifest.json`.

## Conclusion

- **Character:** V3 supports the tested single-face-portrait plus front/side/back layout. This matches the requested face-plus-three-view use.
- **Objects:** V3 can make useful multi-view product sheets for a lantern and a broad shield across three seeds each.
- **Props:** the workflow can lay out a prop sheet, but this katana test exposes weak cross-view part/state consistency for narrow elongated objects. The shield result shows that the limitation is not universal across prop shapes.
- **Scenes:** V3 can produce distinct environment views when the prompt names each camera position. For this scene, an entrance/side/overhead set worked better than three conventional perspective views.

These results support using V3 for concept and reference-sheet exploration with per-image review. They do not establish dependable exact geometry across arbitrary props, objects, scenes, seeds, or source art styles. Three seeds per case are a feasibility signal, not a broad benchmark. No output is promoted to canonical or production status here.
