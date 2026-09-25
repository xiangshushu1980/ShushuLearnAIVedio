#!/usr/bin/env python3
"""Run a provider-neutral daily video pipeline without external services.

The POC deliberately uses deterministic director templates and ffmpeg. Real
source adapters, LLM director, TTS, H3 and VLM adapters can replace stages
without changing the artifact contracts.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


PROFILES = {
    "news_brief": ["hook", "facts", "impact", "close"],
    "host_explainer": ["hook", "context", "explain", "close"],
    "blog_commentary": ["hook", "facts", "opinion", "close"],
    "dialogue": ["question", "position_a", "position_b", "close"],
    "interview": ["question", "answer", "follow_up", "close"],
    "entertainment": ["hook", "reaction", "fact", "close"],
}


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as f:
        value = json.load(f)
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def event(events: list[dict], stage: str, status: str, **extra: object) -> None:
    events.append({"at": now(), "stage": stage, "status": status, **extra})


def make_script(pack: dict, profile: str) -> dict:
    topic = pack.get("topic", "未命名话题")
    evidence = pack.get("evidence", [])
    if not evidence:
        raise ValueError("input must contain at least one evidence item")
    first = evidence[0]
    claim = first.get("claim", "资料包尚未提供摘要")
    source_name = first.get("source", {}).get("name", "来源")
    stages = PROFILES[profile]
    templates = {
        "hook": f"今天用一分钟看懂：{topic}。",
        "question": f"关于{topic}，我们先问一个关键问题。",
        "facts": f"目前能确认的核心事实是：{claim}。",
        "context": f"先把背景放回{topic}本身来看。",
        "explain": f"这意味着，接下来最值得关注的是：{claim}。",
        "impact": "它的直接影响，需要结合后续公开信息继续观察。",
        "opinion": "这里是基于已知资料的解释，不把推断当成事实。",
        "position_a": "第一种看法强调事实本身和眼前影响。",
        "position_b": "另一种看法会关注长期变化和潜在风险。",
        "answer": f"根据目前资料，比较稳妥的回答是：{claim}。",
        "follow_up": "还有未解决的问题，我们把它列为下一轮核查。",
        "reaction": "这件事之所以值得注意，是因为它正在改变大家的预期。",
        "fact": f"再复述一次已经有来源支持的部分：{claim}。",
        "close": f"以上内容依据{source_name}等资料整理，后续更新会继续核对来源。",
    }
    segments = []
    for index, kind in enumerate(stages, 1):
        segments.append({
            "id": f"seg_{index:02d}",
            "kind": "host",
            "speaker": "host_01",
            "text": templates[kind],
            "evidence_ids": [first.get("id", "ev_001")] if kind not in {"hook", "close"} else [],
            "visual_intent": {"role": "host", "asset_query": topic},
            "delivery": {"tone": "calm", "pace": "normal"},
            "review": {"fact_status": "supported" if kind not in {"hook", "close", "opinion"} else "inferred"},
        })
    return {"schema_version": "daily-video/script.v1", "profile": profile, "title": topic, "segments": segments}


def make_timeline(script: dict) -> dict:
    cursor = 0.0
    items = []
    for segment in script["segments"]:
        duration = max(2.0, min(8.0, 0.42 * len(segment["text"]) + 0.8))
        items.append({"id": segment["id"], "start_s": round(cursor, 3), "duration_s": round(duration, 3), "script_id": segment["id"], "tracks": ["host", "subtitles"]})
        cursor += duration
    return {"schema_version": "daily-video/timeline.v1", "duration_s": round(cursor, 3), "items": items}


def make_claims(pack: dict) -> list[dict]:
    claims = []
    for item in pack.get("evidence", []):
        claims.append({
            "id": item.get("id", "ev_unknown").replace("ev_", "claim_"),
            "text": item.get("claim", ""),
            "claim_type": "fact",
            "evidence_ids": [item.get("id", "ev_unknown")],
            "status": "supported" if item.get("quality", {}).get("confidence", 0) >= 0.7 else "needs_review",
        })
    return claims


def make_storyboard(script: dict, timeline: dict) -> dict:
    return {
        "schema_version": "daily-video/storyboard.v1",
        "shots": [
            {
                "id": item["id"],
                "start_s": item["start_s"],
                "duration_s": item["duration_s"],
                "script_id": item["script_id"],
                "visual": script_item["visual_intent"],
                "asset_status": "pending",
            }
            for item, script_item in zip(timeline["items"], script["segments"])
        ],
    }


def make_qc(out: Path, script: dict, timeline: dict) -> dict:
    evidence_covered = all(segment["evidence_ids"] or segment["review"]["fact_status"] != "supported" for segment in script["segments"])
    files = ["evidence.json", "claims.json", "script.json", "storyboard.json", "timeline.json", "subtitles.srt", "preview.mp4"]
    return {
        "schema_version": "daily-video/qc.v1",
        "status": "pass" if evidence_covered and all((out / name).exists() for name in files) else "warn",
        "checks": {
            "artifact_set_complete": all((out / name).exists() for name in files),
            "supported_script_segments_have_evidence": evidence_covered,
            "timeline_has_positive_duration": timeline["duration_s"] > 0,
        },
    }


def write_srt(script: dict, timeline: dict, path: Path) -> None:
    def stamp(seconds: float) -> str:
        ms = int(round(seconds * 1000))
        h, ms = divmod(ms, 3600000)
        m, ms = divmod(ms, 60000)
        s, ms = divmod(ms, 1000)
        return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

    by_id = {s["id"]: s for s in script["segments"]}
    lines = []
    for index, item in enumerate(timeline["items"], 1):
        lines += [str(index), f"{stamp(item['start_s'])} --> {stamp(item['start_s'] + item['duration_s'])}", by_id[item["script_id"]]["text"], ""]
    path.write_text("\n".join(lines), encoding="utf-8")


def render_preview(out: Path, timeline: dict, script: dict, audio: Path | None) -> None:
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise RuntimeError("ffmpeg is required for preview rendering")
    duration = timeline["duration_s"]
    title = script["title"].replace(":", "\\:").replace("'", "\\'")
    video = out / "preview.mp4"
    inputs = ["-f", "lavfi", "-i", f"color=c=0x18212f:s=1280x720:r=25:d={duration}"]
    if audio:
        inputs += ["-i", str(audio)]
    else:
        inputs += ["-f", "lavfi", "-i", f"sine=frequency=220:sample_rate=24000:duration={duration}"]
    vf = f"drawtext=text='{title}':fontcolor=white:fontsize=52:x=(w-text_w)/2:y=(h-text_h)/2"
    cmd = [ffmpeg, "-y", *inputs, "-vf", vf, "-map", "0:v:0", "-map", "1:a:0", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", "-shortest", str(video)]
    subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def run(input_path: Path, out: Path, profile: str, audio: Path | None) -> None:
    # Provider boundaries are imported here to keep this standalone renderer
    # usable as a library while making the vertical slice exercise Source and
    # Director independently.
    from director_provider import direct
    from audio_provider import synthesize
    from source_provider import collect
    from render_provider import render
    from qc_provider import check

    pack = collect(str(input_path))
    out.mkdir(parents=True, exist_ok=True)
    events: list[dict] = []
    event(events, "source", "completed", input=str(input_path))
    script = direct(pack, profile)
    claims = make_claims(pack)
    (out / "evidence.json").write_text(json.dumps(pack, ensure_ascii=False, indent=2), encoding="utf-8")
    (out / "claims.json").write_text(json.dumps(claims, ensure_ascii=False, indent=2), encoding="utf-8")
    (out / "script.json").write_text(json.dumps(script, ensure_ascii=False, indent=2), encoding="utf-8")
    event(events, "director", "completed", profile=profile, segments=len(script["segments"]))
    timeline = make_timeline(script)
    (out / "timeline.json").write_text(json.dumps(timeline, ensure_ascii=False, indent=2), encoding="utf-8")
    (out / "storyboard.json").write_text(json.dumps(make_storyboard(script, timeline), ensure_ascii=False, indent=2), encoding="utf-8")
    write_srt(script, timeline, out / "subtitles.srt")
    event(events, "timeline", "completed", duration_s=timeline["duration_s"])
    if audio is None:
        audio_meta = synthesize(script, timeline, out / "audio.wav")
        audio = out / "audio.wav"
        (out / "audio.json").write_text(json.dumps(audio_meta, ensure_ascii=False, indent=2), encoding="utf-8")
        event(events, "tts", "completed", output="audio.wav", duration_s=audio_meta["duration_s"])
    render_meta = render(script, timeline, audio, out / "preview.mp4")
    (out / "render.json").write_text(json.dumps(render_meta, ensure_ascii=False, indent=2), encoding="utf-8")
    event(events, "render", "completed", output="preview.mp4")
    qc = check(out, script, timeline)
    (out / "qc.json").write_text(json.dumps(qc, ensure_ascii=False, indent=2), encoding="utf-8")
    manifest = {"schema_version": "daily-video/run.v1", "run_id": out.name, "started_at": events[0]["at"], "finished_at": now(), "profile": profile, "input": str(input_path), "artifacts": [e.name for e in sorted(out.iterdir()) if e.is_file() and e.name not in {"run.json", "manifest.json"}], "events": events, "qc": qc}
    (out / "run.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    (out / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="topic/evidence JSON")
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--profile", choices=sorted(PROFILES), default="news_brief")
    parser.add_argument("--audio", type=Path, help="optional WAV/MP3; otherwise generate a tone")
    args = parser.parse_args()
    try:
        run(args.input, args.out, args.profile, args.audio)
    except (OSError, ValueError, RuntimeError, subprocess.CalledProcessError) as exc:
        print(f"daily-video-poc: {exc}", file=sys.stderr)
        return 1
    print(f"completed: {args.out / 'preview.mp4'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
