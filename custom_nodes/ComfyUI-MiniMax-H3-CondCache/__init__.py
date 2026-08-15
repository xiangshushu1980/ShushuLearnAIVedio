"""ComfyUI-MiniMax-H3-CondCache: save/load MiniMax H3 conditioning to disk.

Two-stage pipeline support for MiniMax H3 (docs/10_h3_batch_optimization.md):
  stage 1: TE (Qwen3VL-32B) encodes N prompts once, each cond saved to disk
  stage 2: DiT samples from disk cond, no TE reload

cond structure (verified 2026-08-16, scripts/h3_cond_roundtrip.py):
  [(embeds (1, seq, 5120), {"minimax_token_tags": (seq,),
                            "minimax_keyframes": [...] | "minimax_refs": [...]}), ...]
  A standard ComfyUI conditioning list, torch.save/load lossless.
"""

from __future__ import annotations

from typing_extensions import override

from comfy_api.latest import ComfyExtension

from .cond_cache import MiniMaxH3CondSaver, MiniMaxH3CondLoader


class MiniMaxH3CondCacheExtension(ComfyExtension):
    @override
    async def get_node_list(self):
        return [MiniMaxH3CondSaver, MiniMaxH3CondLoader]


async def comfy_entrypoint() -> MiniMaxH3CondCacheExtension:
    return MiniMaxH3CondCacheExtension()


__all__ = ["comfy_entrypoint"]
