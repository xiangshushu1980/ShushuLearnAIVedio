#!/usr/bin/env python3
"""H3 视频去 BGM 工具（prompt-audio 任务线，2026-08-12 定案）

原理：demucs htdemucs_6s 音乐源分离（MUSDB18 vocals SDR 榜首模型族）。
H3 的 BGM 是标准音乐结构（人声/鼓/贝斯/吉他/钢琴/其他），6s 模型可将
钢琴/吉他等独立 stem 分出——保留 vocals+other（人声+环境音/音效），
去掉 drums/bass/guitar/piano（音乐主体）。

实测结论（2026-08-12，G1-G5 复杂条目 + F2 演唱会）：
- htdemucs_6s 对 H3 音频：钢琴/吉他独立分离、重建相关 ~1.0、纯环境音不幻觉
- AudioSep/FlowSep（语言引导分离）对 H3 音频无效（定位不符，勿用）

用法：
  python3 scripts/h3_demucs.py <视频或音频> [输出前缀]
  例: python3 scripts/h3_demucs.py /tmp/x.mp4 /tmp/x_nobgm
  输出: <前缀>_nobgm.wav（去音乐音频）；若输入是视频，另出 <前缀>_nobgm.mp4（原画面+去音乐音轨）

依赖：ComfyUI venv（GPU torch）：/home/sean/projects/ComfyUI/venv/bin/python
"""
import subprocess
import sys
import os

VENV_PY = "/home/sean/projects/ComfyUI/venv/bin/python"
FFMPEG = "/home/sean/miniconda3/bin/ffmpeg"


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    src = sys.argv[1]
    prefix = sys.argv[2] if len(sys.argv) > 2 else os.path.splitext(src)[0] + "_nobgm"
    is_video = src.lower().endswith((".mp4", ".mov", ".mkv"))

    work = f"/tmp/h3_demucs_{os.getpid()}"
    os.makedirs(work, exist_ok=True)

    # 1. 提取音频（44.1k 单声道或立体声均可，demucs 内部处理）
    audio_in = os.path.join(work, "in.wav")
    subprocess.run([FFMPEG, "-y", "-v", "error", "-i", src, "-ac", "2", "-ar", "44100", audio_in], check=True)

    # 2. demucs 6s 分离
    subprocess.run([VENV_PY, "-m", "demucs", "-n", "htdemucs_6s", "-o", work, audio_in],
                   check=True, capture_output=True)

    # 3. 重混：vocals + other（去 drums/bass/guitar/piano）
    code = f"""
import numpy as np, wave, librosa, soundfile as sf
def load_wav(p):
    w = wave.open(p,'rb')
    ch = w.getnchannels(); n = w.getnframes()
    data = np.frombuffer(w.readframes(n), dtype=np.int16).astype(np.float32)/32768
    if ch > 1: data = data.reshape(-1, ch).mean(axis=1)
    return data
stems = {{}}
for s in ['vocals','drums','bass','guitar','piano','other']:
    stems[s] = load_wav('{work}/htdemucs_6s/in/' + s + '.wav')
n = min(len(x) for x in stems.values())
nobgm = stems['vocals'][:n] + stems['other'][:n]
sf.write('{prefix}_nobgm.wav', nobgm, 44100)
print('nobgm wav done')
"""
    subprocess.run([VENV_PY, "-c", code], check=True)

    # 4. 若是视频，合成原画面+去音乐音轨
    if is_video:
        subprocess.run([FFMPEG, "-y", "-v", "error", "-i", src, "-i", f"{prefix}_nobgm.wav",
                        "-c:v", "copy", "-map", "0:v", "-map", "1:a", "-shortest",
                        f"{prefix}_nobgm.mp4"], check=True)
        print(f"OK -> {prefix}_nobgm.mp4")
    print(f"OK -> {prefix}_nobgm.wav")


if __name__ == "__main__":
    main()
