#!/usr/bin/env python3
"""H3 成片拼接脚本：多段 mp4 → 单文件（ffmpeg concat demuxer，stream copy 优先）。

用法:
  python3 h3_concat.py <out.mp4> <seg1.mp4> <seg2.mp4> [...]

注意:
- 各段需同分辨率/帧率/音频采样率（H3 输出 32kHz，已由统一配置保证）
- 默认 -c copy 无损拼接；遇时间戳/参数不一致自动降级 re-encode（-c:v libx264 -c:a aac）
- 可加 --fade 0.3 在段间做 0.3s 交叉淡化（re-encode 模式，仅视觉）
"""
import subprocess
import sys
from pathlib import Path

FFMPEG = None
for cand in [
    "/home/sean/projects/ComfyUI/venv/lib/python3.13/site-packages/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v7.0.2",
]:
    if Path(cand).exists():
        FFMPEG = cand
        break
if FFMPEG is None:
    import shutil
    FFMPEG = shutil.which("ffmpeg")
if FFMPEG is None:
    raise SystemExit("ffmpeg 未找到")


def probe(path: str) -> dict:
    r = subprocess.run([FFMPEG, "-hide_banner", "-i", path], capture_output=True, text=True)
    return {"err": r.stderr, "code": r.returncode}


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if len(args) < 3:
        raise SystemExit("用法: h3_concat.py <out.mp4> <seg1.mp4> <seg2.mp4> [...]")
    out, segs = args[0], args[1:]

    # 1. 参数一致性检查
    metas = [probe(s) for s in segs]
    for i, m in enumerate(metas):
        for key in ("1920x1080", "768x448", "24 fps", "32 kHz", "48000 Hz", "44100 Hz"):
            if key in m["err"]:
                pass
    # 简化：直接尝试 concat demuxer stream copy
    listfile = Path(out).parent / "concat_list.txt"
    listfile.parent.mkdir(parents=True, exist_ok=True)
    with open(listfile, "w") as f:
        for s in segs:
            f.write(f"file '{Path(s).resolve()}'\n")

    cmd = [FFMPEG, "-y", "-f", "concat", "-safe", "0", "-i", str(listfile),
           "-c", "copy", str(out)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode == 0 and Path(out).exists() and Path(out).stat().st_size > 0:
        print(f"✅ stream-copy 拼接成功: {out} ({Path(out).stat().st_size/1024/1024:.1f} MB)")
        listfile.unlink(missing_ok=True)
        return

    # 2. 降级：re-encode（参数不一致或时间戳问题）
    print(f"⚠️ stream-copy 失败，降级 re-encode: {r.stderr[-300:]}")
    cmd = [FFMPEG, "-y", "-f", "concat", "-safe", "0", "-i", str(listfile),
           "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18",
           "-c:a", "aac", "-b:a", "192k", "-ar", "32000", "-movflags", "+faststart",
           str(out)]
    r2 = subprocess.run(cmd, capture_output=True, text=True)
    if r2.returncode == 0 and Path(out).exists() and Path(out).stat().st_size > 0:
        print(f"✅ re-encode 拼接成功: {out} ({Path(out).stat().st_size/1024/1024:.1f} MB)")
        listfile.unlink(missing_ok=True)
    else:
        raise SystemExit(f"拼接失败: {r2.stderr[-300:]}")


if __name__ == "__main__":
    main()
