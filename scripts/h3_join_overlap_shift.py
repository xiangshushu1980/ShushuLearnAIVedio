#!/usr/bin/env python3
"""Join one trimmed A clip and one untrimmed MC B clip with a movable seam.

The B clip must contain the MC pinned head.  For keep_head=k, A loses k
frames at its tail, while B starts k frames earlier and contributes the same
number of total frames as the k=0 join.  This moves the seam without changing
the output duration.
"""
import argparse
import subprocess


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--a", required=True)
    p.add_argument("--b-untrim", required=True)
    p.add_argument("--audio", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--a-frames", type=int, default=107)
    p.add_argument("--b-visible-frames", type=int, default=90)
    p.add_argument("--context-frames", type=int, default=22)
    p.add_argument("--keep-head", type=int, default=0)
    args = p.parse_args()

    if not 0 <= args.keep_head <= args.context_frames:
        p.error("keep-head must be between 0 and context-frames")
    a_take = args.a_frames - args.keep_head
    b_start = args.context_frames - args.keep_head
    b_take = args.b_visible_frames + args.keep_head
    if a_take < 1 or b_start + b_take < 1:
        p.error("invalid frame geometry")

    fc = (
        f"[0:v]trim=end_frame={a_take},setpts=PTS-STARTPTS,crop=768:432:0:8[v0];"
        f"[1:v]trim=start_frame={b_start}:end_frame={b_start + b_take},"
        "setpts=PTS-STARTPTS,crop=768:432:0:8[v1];"
        "[v0][v1]concat=n=2:v=1:a=0[v]"
    )
    duration = (a_take + b_take) / 24.0
    cmd = [
        "ffmpeg", "-hide_banner", "-loglevel", "error",
        "-i", args.a, "-i", args.b_untrim, "-i", args.audio,
        "-filter_complex", fc, "-map", "[v]", "-map", "2:a:0",
        "-t", f"{duration:.6f}", "-r", "24", "-c:v", "libx264",
        "-crf", "18", "-preset", "medium", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k", "-ar", "32000", "-ac", "2",
        "-shortest", args.out,
    ]
    print(f"keep_head={args.keep_head} A={a_take}F B={b_start}:{b_start+b_take}F duration={duration:.6f}s")
    subprocess.run(cmd, check=True)


if __name__ == "__main__":
    main()
