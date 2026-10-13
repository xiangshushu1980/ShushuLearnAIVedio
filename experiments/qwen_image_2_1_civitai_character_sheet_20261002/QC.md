# [Sean] First smoke QC

## Result

- Source image is a new Qwen Image 2.1 text-to-image output with no image references, Krea2 assets, or LoRAs.
- Character sheet is a Qwen Image 2.1 edit using only that source image.
- The output includes four face expressions, front/side/back full-body views, and one katana detail tile in a clean 3:2 sheet.

## Visual review

- Identity and tied-back hairstyle are recognizable across the expressions and three body views.
- Navy uniform, silver shoulder armor, forearm guards, belt, trousers, and boots remain coherent across views.
- The side and back views expose useful hidden clothing structure while keeping the same silhouette and apparent height.
- Exactly one character appears. The sheet contains no labels or stray text.
- The weapon remains recognizable as one sheathed katana in the body views and the detail strip. Fine weapon construction and some back-view details still need user review.

## Limits

- This was one source seed and one sheet seed.
- Output was 1536×1024 (1.57 MP), below the source workflow author's recommended 3.4 MP balanced setting.
- The original workflow's `ThinkingLLM` PE and `VAEDeGrid` nodes were unavailable. The PE was replaced with a manual prompt; standard VAE decode replaced `VAEDeGrid`.
- The output looks photorealistic because this smoke did not set a style LoRA or a painterly style target.

Conclusion: the Qwen-only reference-to-sheet path is promising and warrants a 3.4 MP pass after the user accepts the panel content.


# [Sean] Face portrait + turnaround layout test

## Result

- Prompted Qwen for one large head-and-shoulders portrait at left and three evenly spaced full-body views at right: front, strict side, and back.
- The requested composition appeared cleanly in one 1536×1024 image. The portrait is clear, and all three body views are approximately equal height.
- Face, ponytail, navy uniform, silver armor, trousers, and boots remain recognizable across views. The side profile reads clearly.

## Issues

- Katana placement is clear in the front view but ambiguous in the back view, where dark diagonal shapes may read as an extra or misplaced weapon. Weapon carry details are not reliably preserved by this one-pass layout.
- This confirms that panel composition can be changed with the prompt; it does not guarantee exact prop geometry.
- Generation took 18.02 seconds. Peak VRAM was not sampled during this run.


# [Sean] Face close-up + front/back layout test

## Result

- The large face close-up fills the left third; the right side contains exactly two full-body views, front and back.
- Both body views are similarly scaled and show the complete figure. Face, hairstyle, uniform, armor, trousers, and boots remain coherent. The requested composition is clear at a glance.
- Generation took 16.38 seconds at 1536x1024. Peak VRAM was not sampled during the run.

## Issue

- The front view shows the katana hilt and scabbard clearly. The back view shows a long dark diagonal shape, but its attachment is less clear. The layout is successful; weapon placement still needs a dedicated reference or another pass if exact carry geometry matters.


# [Sean] V3.0 Simple static-prompt smoke

- Used the static prompt embedded in V3.0 `Character_Sheet_Simple.json`, with the initial Qwen-generated full-body image as sole reference.
- The adapted output shows four head-and-shoulders expressions at left and front/side/back full-body views at right. Identity, tied-back hair, uniform, and silver guards read consistently. No stray labels or other characters.
- The back view does not clearly show the katana, and this static layout has no separate equipment macro. Treat this as a useful composition result, not proof that weapon details are locked.
- Runtime: 18.02 seconds, 1536×1024, seed 6200605. Used local Qwen Image 2.1 int8; replaced missing `VAEDeGrid` with standard VAE decode. This was an adapted static-prompt pass, not execution of the unmodified V3 node graph. No H3 video was generated.
- H3 reference status: experimental input candidate only. Follow the project H3 turnaround/extraction and QC path before treating derived face/body/wardrobe/side/back images as video-ready assets.
