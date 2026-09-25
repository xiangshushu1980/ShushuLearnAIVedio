"""Thin Windows queue wrapper around video2dlssnr's nr_video.py.

The wrapper is intentionally stdlib-only. It owns queueing, stable-file
detection, output naming and logs; DLSS5/D3D12/FFmpeg remain in the upstream
engine.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable


VIDEO_EXTENSIONS = {".mp4", ".mov", ".mkv", ".webm", ".avi", ".m4v"}
STATE_NAME = ".dlss5-queue.json"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


@dataclass
class Job:
    input: str
    output: str
    status: str
    started_at: str | None = None
    finished_at: str | None = None
    returncode: int | None = None
    log: str | None = None
    error: str | None = None
    source_size: int | None = None
    source_mtime_ns: int | None = None


class QueueState:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.jobs: dict[str, Job] = {}
        if path.exists():
            try:
                raw = json.loads(path.read_text(encoding="utf-8"))
                self.jobs = {
                    key: Job(**value) for key, value in raw.get("jobs", {}).items()
                }
            except (OSError, ValueError, TypeError) as exc:
                print(f"[dlss5] warning: cannot read state file: {exc}")

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = {"updated_at": utc_now(), "jobs": {k: asdict(v) for k, v in self.jobs.items()}}
        temp = self.path.with_suffix(self.path.suffix + ".tmp")
        temp.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        os.replace(temp, self.path)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Queue Windows video jobs for video2dlssnr")
    parser.add_argument("--engine-root", type=Path, required=True, help="video2dlssnr root containing nr_video.py")
    parser.add_argument("--input", type=Path, required=True, help="input file or directory")
    parser.add_argument("--output", type=Path, required=True, help="output directory")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--once", action="store_true", help="process current files and exit")
    mode.add_argument("--watch", action="store_true", help="watch input directory continuously")
    parser.add_argument("--python", default="", help="Python executable; defaults to current interpreter")
    parser.add_argument("--scale", type=float, default=1.0, help="DLSS scale factor, e.g. 1, 1.5 or 2")
    parser.add_argument("--width", type=int, default=0, help="exact output width; mutually exclusive with --scale != 1")
    parser.add_argument("--height", type=int, default=0, help="exact output height; mutually exclusive with --scale != 1")
    parser.add_argument("--style", type=int, choices=(0, 1, 2), default=1, help="0 default, 1 natural, 2 cinematic")
    parser.add_argument("--preset", type=int, choices=(0, 1, 2, 3), default=0, help="DLSS5 NR render preset")
    parser.add_argument("--sr-preset", default="default", help="DLSS SR preset, e.g. default, K or M")
    parser.add_argument("--intensity", type=float, default=0.7)
    parser.add_argument("--detail", type=float, default=0.7)
    parser.add_argument("--color", type=float, default=0.0, help="0 keeps original hue; 1 adopts NR colour")
    parser.add_argument("--no-motion", action="store_true", help="disable optical-flow motion guides")
    parser.add_argument("--codec", default="hevc_nvenc")
    parser.add_argument("--cq", type=int, default=19)
    parser.add_argument("--bit-depth", type=int, choices=(8, 10), default=10)
    parser.add_argument("--poll-seconds", type=float, default=3.0)
    parser.add_argument("--stable-polls", type=int, default=2, help="unchanged size polls before processing")
    parser.add_argument("--force", action="store_true", help="reprocess existing successful jobs")
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def video_files(root: Path) -> Iterable[Path]:
    if root.is_file():
        if root.suffix.lower() in VIDEO_EXTENSIONS:
            yield root
        return
    if root.exists():
        for path in sorted(root.iterdir()):
            if path.is_file() and path.suffix.lower() in VIDEO_EXTENSIONS and not path.name.startswith("."):
                yield path


def output_path(source: Path, output_dir: Path) -> Path:
    return output_dir / f"{source.stem}.dlss5{source.suffix.lower()}"


def build_command(args: argparse.Namespace, source: Path, destination: Path) -> list[str]:
    script = args.engine_root / "nr_video.py"
    python = args.python or sys.executable
    command = [python, str(script), "--in", str(source), "--out", str(destination)]
    if args.width or args.height:
        if args.scale != 1.0:
            raise ValueError("--width/--height cannot be combined with --scale other than 1")
        if args.width:
            command += ["--nr-width", str(args.width)]
        if args.height:
            command += ["--nr-height", str(args.height)]
    else:
        command += ["--nr-scale", str(args.scale)]
    command += [
        "--nr-style", str(args.style),
        "--nr-preset", str(args.preset),
        "--nr-sr-preset", args.sr_preset,
        "--nr-intensity", str(args.intensity),
        "--nr-detail", str(args.detail),
        "--nr-color", str(args.color),
        "--codec", args.codec,
        "--cq", str(args.cq),
        "--bit-depth", str(args.bit_depth),
    ]
    if args.no_motion:
        command += ["--nr-motion", "0"]
    return command


def stable(path: Path, previous: dict[str, tuple[int, int]], required_polls: int) -> bool:
    try:
        stat = path.stat()
    except OSError:
        return False
    current = (stat.st_size, stat.st_mtime_ns)
    size, count = previous.get(str(path), ((-1, -1), 0))
    count = count + 1 if current == size else 1
    previous[str(path)] = (current, count)
    return count >= required_polls and stat.st_size > 0


def run_job(args: argparse.Namespace, state: QueueState, source: Path) -> None:
    destination = output_path(source, args.output)
    key = str(source.resolve()).lower()
    old = state.jobs.get(key)
    stat = source.stat()
    unchanged = old and old.source_size == stat.st_size and old.source_mtime_ns == stat.st_mtime_ns
    if old and old.status == "success" and destination.exists() and unchanged and not args.force:
        return
    log_path = args.output / f"{source.stem}.dlss5.log"
    job = Job(
        str(source), str(destination), "running", utc_now(), log=str(log_path),
        source_size=stat.st_size, source_mtime_ns=stat.st_mtime_ns,
    )
    state.jobs[key] = job
    state.save()
    command = build_command(args, source, destination)
    print("[dlss5]", " ".join(f'"{part}"' if " " in part else part for part in command), flush=True)
    if args.dry_run:
        job.status = "dry-run"
        job.finished_at = utc_now()
        state.save()
        return
    args.output.mkdir(parents=True, exist_ok=True)
    try:
        with log_path.open("w", encoding="utf-8", errors="replace") as log:
            log.write(f"started={job.started_at}\ncommand={json.dumps(command, ensure_ascii=False)}\n\n")
            result = subprocess.run(command, cwd=args.engine_root, stdout=log, stderr=subprocess.STDOUT, check=False)
        job.returncode = result.returncode
        job.status = "success" if result.returncode == 0 and destination.exists() else "failed"
        if job.status == "failed":
            job.error = f"engine exited {result.returncode} or output is missing"
    except OSError as exc:
        job.status = "failed"
        job.error = str(exc)
    job.finished_at = utc_now()
    state.jobs[key] = job
    state.save()
    print(f"[dlss5] {job.status}: {source.name}", flush=True)


def main() -> int:
    args = parse_args()
    if not args.once and not args.watch:
        args.once = True
    if not (args.engine_root / "nr_video.py").exists():
        print(f"[dlss5] missing engine entrypoint: {args.engine_root / 'nr_video.py'}", file=sys.stderr)
        return 2
    args.output.mkdir(parents=True, exist_ok=True)
    state = QueueState(args.output / STATE_NAME)
    seen_sizes: dict[str, tuple[int, int]] = {}
    while True:
        for source in video_files(args.input):
            if stable(source, seen_sizes, max(1, args.stable_polls)):
                try:
                    run_job(args, state, source)
                except ValueError as exc:
                    print(f"[dlss5] invalid settings: {exc}", file=sys.stderr)
                    return 2
        if args.once:
            return 0
        time.sleep(max(0.2, args.poll_seconds))


if __name__ == "__main__":
    raise SystemExit(main())
