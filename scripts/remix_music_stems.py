#!/usr/bin/env python3
"""demucs 分离 stems 后重混：乐器轨针对性增强（补 punch/body/presence）+ 与人声平衡 + 母带。

用法:
  python3 remix_music_stems.py --stems-dir <htdemucs/<track>> [--out out.wav]
  [--vocal-db 0] [--other-db 3] [--drums-db 5] [--bass-db 8]
  [--bass-body 3] [--drums-presence 3] [--other-presence 2] [--lufs -14]

说明:
  分离目录结构: demucs -o <base> <in.wav>  →  <base>/htdemucs/<track>/vocals.wav 等
  默认各轨增益根据实测响度差设定（vocals -14 / other -19 / drums -23 / bass -26）
"""
import argparse, subprocess, sys
from pathlib import Path

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stems-dir", required=True, help="htdemucs/<track> 目录（含 vocals/drums/bass/other.wav）")
    ap.add_argument("--out", default=None)
    ap.add_argument("--vocal-db", type=float, default=0)
    ap.add_argument("--other-db", type=float, default=3)
    ap.add_argument("--drums-db", type=float, default=5)
    ap.add_argument("--bass-db", type=float, default=8)
    ap.add_argument("--bass-body", type=float, default=3, help="bass 80Hz body boost dB")
    ap.add_argument("--bass-mud", type=float, default=-2, help="bass 250Hz 箱音削减 dB")
    ap.add_argument("--drums-presence", type=float, default=3, help="drums 5kHz presence dB")
    ap.add_argument("--other-presence", type=float, default=2, help="other 3kHz presence dB")
    ap.add_argument("--other-hiss", type=float, default=0, help="other 7kHz 杂音削减 dB（负值=衰减，治笛子/竖琴气声）")
    ap.add_argument("--lufs", type=float, default=-14.0)
    args = ap.parse_args()

    d = Path(args.stems_dir)
    stems = {k: d / f"{k}.wav" for k in ("vocals", "drums", "bass", "other")}
    for k, p in stems.items():
        if not p.exists():
            print(f"❌ 缺 {p}"); sys.exit(1)

    out = args.out or (d.parent / (d.name + "_remix.wav"))
    fc = []
    # vocals: 原样（可减一点让位乐器）
    fc.append(f"[0]volume={args.vocal_db}dB[voc]")
    # other: presence + 高频杂音削减(笛子/竖琴气声) + 增益
    fc.append(f"[3]equalizer=f=3000:t=q:w=1.4:g={args.other_presence}"
              f",equalizer=f=7000:t=q:w=1.5:g={args.other_hiss},volume={args.other_db}dB[oth]")
    # drums: presence + 增益（轻度瞬态）
    fc.append(f"[1]equalizer=f=5000:t=q:w=1.4:g={args.drums_presence},volume={args.drums_db}dB[drm]")
    # bass: body boost + 去箱音 + 增益
    bass_eq = f"equalizer=f=80:t=q:w=1.0:g={args.bass_body}"
    if args.bass_mud:
        bass_eq += f",equalizer=f=250:t=q:w=1.2:g={args.bass_mud}"
    fc.append(f"[2]{bass_eq},volume={args.bass_db}dB[bss]")
    # 混音 + 母带
    fc.append(f"[voc][drm][bss][oth]amix=inputs=4:normalize=0:duration=longest,"
              f"loudnorm=I={args.lufs}:TP=-1.0:LRA=11[mix]")

    cmd = ["ffmpeg", "-y",
           "-i", str(stems["vocals"]), "-i", str(stems["drums"]),
           "-i", str(stems["bass"]), "-i", str(stems["other"]),
           "-filter_complex", ";".join(fc),
           "-map", "[mix]", "-ar", "48000", "-ac", "2", "-sample_fmt", "s16",
           str(out)]
    print(f"➡️  重混: {d.name}")
    print(f"   vocal={args.vocal_db}dB other={args.other_db}dB drums={args.drums_db}dB bass={args.bass_db}dB  (bass_body={args.bass_body})")
    print(f"   target LUFS={args.lufs}")
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print("❌ ffmpeg:", r.stderr[-1500:]); sys.exit(1)
    print(f"✅ 完成: {out}")

if __name__ == "__main__":
    main()
