#!/usr/bin/env python3
"""
Pexels 素材 → Bernini 兼容预处理
将任意视频缩放到 832×480 (16:9, 16倍数) 并截取到 81帧(4n+1)
输出到 input/video_material_bernini/ 供 Bernini v2v 编辑
用法:
  python3 prep_bernini.py --src <input_dir> --out <output_dir> [--frames 81] [--w 832 --h 480]
"""
import os, sys, subprocess, argparse, glob


def to_bernini(src, dest, w, h, frames, fps):
    """ffmpeg 缩放+裁帧到目标规格"""
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    # 强制 16:9 缩放(拉伸到目标尺寸), 截取前 frames 帧
    cmd = [
        "ffmpeg", "-y", "-i", src,
        "-vf", f"scale={w}:{h}:force_original_aspect_ratio=decrease,"
               f"pad={w}:{h}:(ow-iw)/2:(oh-ih)/2,"
               f"fps={fps},"
               f"select='not(mod(n\\,1))'",  # 保持所有帧
        "-frames:v", str(frames),
        "-r", str(fps),
        "-c:v", "libx264", "-preset", "fast", "-crf", "18",
        "-pix_fmt", "yuv420p",
        dest,
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        return False, r.stderr[-500:]
    return True, ""


def verify(f, w, h, frames):
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0",
         "-show_entries", "stream=width,height,nb_frames,r_frame_rate",
         "-of", "csv=p=0", f],
        capture_output=True, text=True)
    return r.stdout.strip() if r.returncode == 0 else "?"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default="../../ComfyUI/input/video_material")
    ap.add_argument("--out", default="../../ComfyUI/input/video_material_bernini")
    ap.add_argument("--w", type=int, default=832)
    ap.add_argument("--h", type=int, default=480)
    ap.add_argument("--frames", type=int, default=81)
    ap.add_argument("--fps", type=int, default=16)
    ap.add_argument("--max-files", type=int, default=0, help="0=全部, >0 限制处理数量")
    args = ap.parse_args()

    files = sorted(glob.glob(os.path.join(args.src, "*.mp4")))
    if args.max_files > 0:
        files = files[:args.max_files]

    print(f"预处理 {len(files)} 个素材 → {args.w}x{args.h}/{args.frames}帧@{args.fps}fps")
    ok = 0
    for src in files:
        name = os.path.splitext(os.path.basename(src))[0]
        dest = os.path.join(args.out, f"{name}_b81.mp4")
        if os.path.exists(dest):
            print(f"  已存在: {os.path.basename(dest)} ({verify(dest,args.w,args.h,args.frames)})")
            ok += 1
            continue
        print(f"  处理: {os.path.basename(src)} → {os.path.basename(dest)}", end=" ", flush=True)
        success, err = to_bernini(src, dest, args.w, args.h, args.frames, args.fps)
        if success:
            print(f"✓ {verify(dest,args.w,args.h,args.frames)}")
            ok += 1
        else:
            print(f"✗ {err}")
    print(f"\n完成: {ok}/{len(files)} 个素材预处理到 {args.out}")


if __name__ == "__main__":
    main()
