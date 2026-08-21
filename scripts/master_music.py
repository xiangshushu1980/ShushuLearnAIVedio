#!/usr/bin/env python3
"""AI 音乐母带处理（超分之后做）：
响度标准化到流媒体目标 + true-peak 限制 + 可选音色修正（低频浑浊/空气感）。

用法:
  python3 master_music.py --input <in.wav> [--out out.wav] [--lufs -14] [--peak -1.0] [--mud 2.5] [--air 1.0]

参数:
  --lufs  目标响度（Spotify/YouTube -14, Apple -16, TikTok -11~-9），默认 -14
  --peak  true-peak 上限 dBTP，默认 -1.0
  --mud   250-500Hz 减浑浊衰减 dB（0=不动），默认 2.5
  --air   高频空气感 boost dB（0=不动），默认 1.0
输出: 48kHz 立体声 WAV
"""
import argparse, subprocess, sys
from pathlib import Path

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--out", default=None)
    ap.add_argument("--lufs", type=float, default=-14.0)
    ap.add_argument("--peak", type=float, default=-1.0)
    ap.add_argument("--mud", type=float, default=2.5)
    ap.add_argument("--air", type=float, default=1.0)
    args = ap.parse_args()

    out = args.out or (str(Path(args.input).with_suffix("")) + "_mastered.wav")
    af = []
    # 1) 低频浑浊削减（宽 Q，减 mud dB @ ~320Hz）
    if args.mud > 0:
        af.append(f"equalizer=f=320:t=q:w=1.2:g=-{args.mud}")
    # 2) 高频空气感
    if args.air > 0:
        af.append(f"highpass=f=35,equalizer=f=10000:t=q:w=1.4:g={args.air}")
    # 3) 响度标准化到目标 LUFS + true-peak 限制（限幅兜底）
    af.append(f"loudnorm=I={args.lufs}:TP={args.peak}:LRA=11:print_format=summary")
    chain = ",".join(af)

    print(f"➡️  母带: {args.input}")
    print(f"   LUFS={args.lufs} dBTP={args.peak} mud=-{args.mud}dB air=+{args.air}dB")
    cmd = ["ffmpeg", "-y", "-i", args.input,
           "-af", chain,
           "-ar", "48000", "-ac", "2", "-sample_fmt", "s16",
           out]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print("❌ ffmpeg 失败:", r.stderr[-2000:])
        sys.exit(1)
    print(f"✅ 完成: {out}")

if __name__ == "__main__":
    main()
