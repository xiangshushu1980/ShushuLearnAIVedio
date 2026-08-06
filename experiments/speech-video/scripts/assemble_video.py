#!/usr/bin/env python3
"""合成分镜视频：读 scenes JSON，每景静态图按时长生成片段，拼接+混音频+烧字幕。
用法: python assemble_video.py --scenes scenes_test.json --imgdir <ComfyUI>/output/img_debate2 \
      --audio <m4a> --srt subtitles_hms.srt --out ../test_15s.mp4 [--fps 30] [--motion]
--motion: 用平滑 zoompan 微动（默认静态，避免震动）
"""
import json, subprocess, argparse, os

FF = "/home/sean/miniconda3/bin/ffmpeg"

def ts(t):
    return f"{int(t//60):02d}:{int(t%60):02d}:{t%60%1*1000:03d}".replace("000", ",000")

def seg_static(img, dur, fps):
    return ["-loop", "1", "-t", f"{dur}", "-i", img]

def build_segment(ff, img, dur, fps, motion, idx):
    frames = int(round(dur * fps))
    cmd = [ff, "-y"]
    if motion:
        cmd += ["-i", img]
        vf = (f"scale=1024:576,zoompan=z='min(zoom+0.0012,1.12)':d={frames}:"
              f"x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1024x576:fps={fps}")
        cmd += ["-vf", vf, "-frames:v", frames]
    else:
        cmd += ["-loop", "1", "-t", f"{dur}", "-i", img, "-vf", f"scale=1024:576,fps={fps}"]
    cmd += ["-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
            "-r", str(fps), f"seg_{idx}.mp4"]
    subprocess.run(cmd, capture_output=True)
    return f"seg_{idx}.mp4"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scenes", required=True)
    ap.add_argument("--imgdir", required=True, help="图片目录(含 <id>_00001_.png)")
    ap.add_argument("--audio", required=True)
    ap.add_argument("--srt", default="")
    ap.add_argument("--out", required=True)
    ap.add_argument("--fps", type=int, default=30)
    ap.add_argument("--motion", action="store_true")
    ap.add_argument("--workdir", default="/tmp/debate_asm")
    args = ap.parse_args()

    os.makedirs(args.workdir, exist_ok=True)
    scenes = json.load(open(args.scenes))
    total = scenes[-1]["e"] - scenes[0]["s"]
    print(f"场景 {len(scenes)} 个, 总时长 {total:.2f}s")

    # 1) 生成各景片段
    segs = []
    for i, s in enumerate(scenes):
        img = os.path.join(args.imgdir, f"{s['id']}_00001_.png")
        dur = s["e"] - s["s"]
        p = build_segment(FF, img, dur, args.fps, args.motion, i)
        segs.append(p)
        print(f"  {s['id']} {s['s']:.2f}-{s['e']:.2f} ({dur:.2f}s)")

    # 2) concat
    lst = os.path.join(args.workdir, "list.txt")
    with open(lst, "w") as f:
        for p in segs:
            f.write(f"file '{os.path.abspath(p)}'\n")
    silent = os.path.join(args.workdir, "silent.mp4")
    subprocess.run([FF, "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", silent],
                   capture_output=True)

    # 3) 混音频 (+可选烧字幕)
    vf = f"fps={args.fps}"
    if args.srt and os.path.exists(args.srt):
        vf += (f",subtitles='{os.path.abspath(args.srt)}':force_style="
               f"'FontName=DejaVu Sans Bold,FontSize=20,PrimaryColour=&H00FFFFFF,"
               f"OutlineColour=&H00000000,BorderStyle=3,Outline=2,Alignment=2,MarginV=34'")
    cmd = [FF, "-y", "-i", silent, "-i", args.audio]
    if vf:
        cmd += ["-vf", vf]
    cmd += ["-map", "0:v", "-map", "1:a",
            "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "192k", "-t", f"{total}", "-r", str(args.fps),
            "-movflags", "+faststart", args.out]
    subprocess.run(cmd, capture_output=True)
    print("成品:", args.out)

if __name__ == "__main__":
    main()
