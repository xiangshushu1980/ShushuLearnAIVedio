# [Sean] Qwen style variant QC for H3 main-image candidates

## Visual review

- All five outputs are single-person, full-body images with the boots inside frame and a clean background. Face, ponytail, navy uniform, silver armor, and overall body silhouette remain recognizable.
- Anime cel and graphic novel produce the clearest style changes from the photorealistic source.
- Painterly concept and watercolor/gouache shift surface treatment and texture, but remain relatively close to the source.
- The 3D game render prompt produces a polished image but stays close to the source's realistic studio appearance; Qwen's text-only style direction is weak for this variant.
- The katana remains present, though fine belt/scabbard geometry is not fully stable.

## Video-reference boundary

These images are experimental Qwen main-image candidates only. This run did not generate H3 video, extract F/W/WB/S/B assets, or validate how each style behaves in motion. Select a style candidate first, then use the project H3 turnaround workflow and review the resulting role-specific stills before treating any asset as video-ready.

## Runtime

Five images, 1536×1024, shared seed 6200801, 25 steps, CFG 1.0, Qwen Image 2.1 int8, no Krea2 or LoRA. Summed generation time: 80.45 seconds. Peak VRAM was not sampled.
