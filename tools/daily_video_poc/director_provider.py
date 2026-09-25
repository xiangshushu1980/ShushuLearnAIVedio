"""Provider boundary for turning an Evidence Pack into a reviewed Script."""

from __future__ import annotations

from typing import Any

from poc import PROFILES, make_script


MANIFEST = {
    "capability": "director",
    "version": "director-template@0.1",
    "input_schema": "daily-video/evidence.v1 + daily-video/format-profile.v1",
    "output_schema": "daily-video/script.v1",
    "resources": {"cpu": 1, "gpu": False},
    "retryable": True,
    "failure_classes": ["invalid_evidence", "unsupported_profile", "generation_failed"],
}


def direct(evidence_pack: dict[str, Any], profile: str = "news_brief") -> dict[str, Any]:
    if profile not in PROFILES:
        raise ValueError(f"unsupported format profile: {profile}")
    script = make_script(evidence_pack, profile)
    script["producer"] = {"provider": MANIFEST["version"], "profile": profile}
    return script
