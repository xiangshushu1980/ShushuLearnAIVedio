#!/usr/bin/env python3
"""Validate and select Sean reference asset packages.

Owner: Sean
This first version is deliberately deterministic: it never promotes or
generates an asset. Generation and masking backends can be attached later.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

ROLE_ORDER = ("F", "W", "WB", "S", "Q", "B")
SHOT_ROLES = {
    "closeup": ("F", "W"),
    "medium": ("F", "WB"),
    "full_body": ("F", "W"),
    "side": ("F", "WB", "S"),
    "three_quarter": ("F", "WB", "Q"),
    "back": ("F", "WB", "B"),
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_manifest(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("schema") != "sean.reference_asset_manifest.v1":
        raise ValueError("unsupported or missing schema: expected sean.reference_asset_manifest.v1")
    if not data.get("character_id"):
        raise ValueError("character_id is required")
    return data


def asset_path(manifest_path: Path, asset: dict) -> Path:
    raw = asset.get("path")
    if not raw:
        raise ValueError(f"asset {asset.get('role')} has no path")
    path = Path(raw)
    return path if path.is_absolute() else (manifest_path.parent / path)


def validate(manifest_path: Path) -> int:
    data = load_manifest(manifest_path)
    errors: list[str] = []
    warnings: list[str] = []
    seen: set[str] = set()
    assets = {asset.get("role"): asset for asset in data.get("assets", [])}
    generator = data.get("generator", {})
    provider = str(generator.get("provider", "")).lower()
    if "h3" not in provider or "multi" not in provider:
        errors.append("generator.provider must identify the H3 multi-view pipeline")

    for asset in data.get("assets", []):
        role = asset.get("role")
        if not role:
            errors.append("asset without role")
            continue
        if role in seen:
            errors.append(f"duplicate role: {role}")
        seen.add(role)
        path = asset_path(manifest_path, asset)
        status = asset.get("status", "missing")
        if status in {"canonical", "conditional", "experimental"} and not path.is_file():
            errors.append(f"{role}: file missing: {path}")
        if path.is_file() and path.suffix.lower() not in {".png", ".jpg", ".jpeg", ".webp"}:
            warnings.append(f"{role}: non-image extension: {path.suffix}")
        if status == "canonical" and not asset.get("qc", {}).get("human_reviewed", False):
            warnings.append(f"{role}: canonical without human_reviewed=true")

    if assets.get("F", {}).get("status") not in {"canonical", "conditional"}:
        warnings.append("F is experimental/missing; no production shot package may use this manifest")
    if assets.get("WB", {}).get("status") not in {"canonical", "conditional"}:
        warnings.append("WB is not ready; medium/side/back packages cannot be production-default")

    print(json.dumps({
        "character_id": data["character_id"],
        "status": "error" if errors else "warning" if warnings else "ok",
        "errors": errors,
        "warnings": warnings,
        "assets": {
            role: {"status": asset.get("status"), "path": str(asset_path(manifest_path, asset)),
                   "sha256": sha256(asset_path(manifest_path, asset)) if asset_path(manifest_path, asset).is_file() else None}
            for role, asset in assets.items()
        },
    }, ensure_ascii=False, indent=2))
    return 1 if errors else 0


def plan(manifest_path: Path, shot: str) -> int:
    data = load_manifest(manifest_path)
    if shot not in SHOT_ROLES:
        raise ValueError(f"unknown shot {shot}; choose from {', '.join(SHOT_ROLES)}")
    assets = {asset.get("role"): asset for asset in data.get("assets", [])}
    selected = []
    missing = []
    for role in SHOT_ROLES[shot]:
        asset = assets.get(role)
        if not asset or asset.get("status") not in {"canonical", "conditional"}:
            missing.append(role)
            continue
        path = asset_path(manifest_path, asset)
        if not path.is_file():
            missing.append(role)
            continue
        selected.append({"role": role, "path": str(path), "status": asset.get("status")})
    result = {"character_id": data["character_id"], "shot": shot, "selected": selected,
              "missing": missing, "ready": not missing}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if not missing else 2


def main() -> int:
    parser = argparse.ArgumentParser(description="[Sean] reference asset manifest validator")
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("validate", "plan"):
        child = sub.add_parser(name)
        child.add_argument("manifest", type=Path)
        if name == "plan":
            child.add_argument("--shot", choices=tuple(SHOT_ROLES), required=True)
    args = parser.parse_args()
    try:
        return validate(args.manifest) if args.command == "validate" else plan(args.manifest, args.shot)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
