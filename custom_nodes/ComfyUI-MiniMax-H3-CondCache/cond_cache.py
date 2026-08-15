"""MiniMax H3 conditioning save/load nodes.

Reference: nicehero/comfyui-conditioning-saver (generic CONDITIONING persist),
adapted to MiniMax H3 cond which is a plain ComfyUI conditioning list:
    [(embeds (1, seq, 5120), {"minimax_token_tags": ...,
                              "minimax_keyframes": [...],
                              "minimax_refs": [...]}), ...]

Both sides only move/reshape the object graph; every tensor is copied to CPU on
save and back to the intermediate device on load, which is bit-lossless
(verified: scripts/h3_cond_roundtrip.py / h3_load_time_sampling.py).
"""

from __future__ import annotations

import logging
import os

import torch

import folder_paths
import comfy.model_management
import comfy.nested_tensor
from comfy_api.latest import io


log = logging.getLogger("MiniMaxH3-CondCache")

DEFAULT_SUBDIR = "conditioning"


def _move(obj, device):
    """Recursively move every tensor (incl. NestedTensor) to `device`, leave
    int/str/None/bool/float and other non-tensor leaves untouched."""
    if isinstance(obj, comfy.nested_tensor.NestedTensor):
        return obj.to(device)
    if isinstance(obj, torch.Tensor):
        return obj.to(device)
    if isinstance(obj, dict):
        return {k: _move(v, device) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_move(v, device) for v in obj]
    if isinstance(obj, tuple):
        return tuple(_move(v, device) for v in obj)
    return obj


def _validate_cond(cond, tag):
    if not isinstance(cond, list) or len(cond) == 0:
        raise ValueError(f"{tag}: expected non-empty conditioning list [(tensor, {{attrs}}), ...], got {type(cond).__name__}")
    for i, entry in enumerate(cond):
        if not isinstance(entry, (list, tuple)) or len(entry) != 2:
            raise ValueError(f"{tag}: entry {i} must be [tensor, attrs_dict], got {type(entry).__name__}")
        if not isinstance(entry[0], torch.Tensor):
            raise ValueError(f"{tag}: entry {i} embeds must be a tensor, got {type(entry[0]).__name__}")
        if not isinstance(entry[1], dict):
            raise ValueError(f"{tag}: entry {i} attrs must be a dict, got {type(entry[1]).__name__}")


def _resolve_path(filename):
    """Absolute path as given, else fall back to output/conditioning/<filename>."""
    if os.path.isabs(filename):
        return filename
    out = os.path.join(folder_paths.get_output_directory(), DEFAULT_SUBDIR, filename)
    if os.path.isfile(out):
        return out
    return filename


class MiniMaxH3CondSaver(io.ComfyNode):
    """Save MiniMax H3 conditioning to disk (stage 1: TE encodes, cond cached)."""

    @classmethod
    def define_schema(cls):
        return io.Schema(
            node_id="MiniMaxH3CondSaver",
            display_name="Save MiniMax H3 Cond",
            category="model/conditioning/minimax",
            is_output_node=True,
            description="Persist MiniMax H3 conditioning (Qwen3VL hidden states + token tags + keyframe/ref latents) to a .pt file so the TE stage can be skipped on later sampling runs.",
            inputs=[
                io.Conditioning.Input("positive"),
                io.String.Input("filename_prefix", default="h3_cond",
                                tooltip="Saved as output/<subdirectory>/<filename_prefix>_NNNNN.pt (auto-incremented)."),
                io.String.Input("subdirectory", default=DEFAULT_SUBDIR, optional=True,
                                tooltip="Subdirectory under the ComfyUI output dir."),
            ],
            outputs=[io.String.Output(display_name="path")],
        )

    @classmethod
    def execute(cls, positive, filename_prefix, subdirectory=DEFAULT_SUBDIR) -> io.NodeOutput:
        _validate_cond(positive, "SaveMiniMaxH3Cond")
        if not filename_prefix or not filename_prefix.strip():
            raise ValueError("filename_prefix must not be empty")
        subdirectory = subdirectory.strip() or DEFAULT_SUBDIR

        out_dir = os.path.join(folder_paths.get_output_directory(), subdirectory)
        os.makedirs(out_dir, exist_ok=True)

        # auto-increment index, matching ComfyUI's Save* convention
        index = 0
        for name in os.listdir(out_dir):
            if name.startswith(filename_prefix + "_") and name.endswith(".pt"):
                stem = name[len(filename_prefix) + 1 : -3]
                if stem.isdigit():
                    index = max(index, int(stem) + 1)

        path = os.path.join(out_dir, f"{filename_prefix}_{index:05d}.pt")
        # CPU copy -> portable, device-agnostic .pt (bit-lossless)
        torch.save(_move(positive, "cpu"), path)
        log.info("saved MiniMax H3 cond -> %s (%d entries)", path, len(positive))
        return io.NodeOutput(path)


class MiniMaxH3CondLoader(io.ComfyNode):
    """Load MiniMax H3 conditioning from disk (stage 2: sample without TE)."""

    @classmethod
    def define_schema(cls):
        return io.Schema(
            node_id="MiniMaxH3CondLoader",
            display_name="Load MiniMax H3 Cond",
            category="model/conditioning/minimax",
            description="Read a .pt saved by SaveMiniMaxH3Cond and return the conditioning, so sampling needs no text encoder (Qwen3VL) at all.",
            inputs=[
                io.String.Input("filename", default="", placeholder="/absolute/path/to/h3_cond.pt",
                                tooltip="Absolute path, or a name under output/conditioning/."),
            ],
            outputs=[io.Conditioning.Output(display_name="positive")],
        )

    @classmethod
    def execute(cls, filename) -> io.NodeOutput:
        filename = (filename or "").strip()
        if not filename:
            raise ValueError("filename must not be empty")
        path = _resolve_path(filename)
        if not os.path.isfile(path):
            raise ValueError(f"cond file not found: {path}")

        cond = torch.load(path, map_location="cpu", weights_only=False)
        _validate_cond(cond, f"LoadMiniMaxH3Cond({os.path.basename(path)})")

        # mirror the TE output device placement (sd1_clip moves embeds to intermediate_device)
        cond = _move(cond, comfy.model_management.intermediate_device())
        log.info("loaded MiniMax H3 cond <- %s (%d entries)", path, len(cond))
        return io.NodeOutput(cond)
