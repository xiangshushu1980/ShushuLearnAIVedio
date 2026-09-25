#!/usr/bin/env python3
"""H3 音频分离工具封装（prompt-audio 任务线，2026-08-11）
基于 AudioSep（LA-Sep，"Separate Anything You Describe"，Audio-AGI）：
语言引导音频分离——"remove background music" 按文本指令提取目标声源。

安装（已完成）：
- repo: /home/sean/projects/audio-sep
- 权重: checkpoint/audiosep_base_4M_steps.ckpt (1.26GB) + music_speech_audioset_epoch_15_esc_89.98.pt (2.35GB)
- 依赖: torch/torchvision/torchaudio (CPU 版) + librosa + lightning + laion-clap
- patch: 所有 torch.load 加 weights_only=False；CLAP load_state_dict strict=False

用法:
  python3 scripts/h3_audio_sep.py <视频或音频> <查询词> [输出路径]
  例: python3 scripts/h3_audio_sep.py /tmp/E5.wav "background music" /tmp/e5_music.wav

注意:
- CPU 推理 ~7s/8s 音频（GPU 更快，但依赖 GPU torch，当前用系统 CPU torch）
- 输入重采样到 32kHz 单声道
- 2026-08-11 实测结论：H3 触发音乐态的音轨≈纯音乐（相关度 1.0，无环境音成分），
  分离后残差≈静音——本工具对"音乐+人声/音效混合轨"（如 ref2va 带语音）才有用武之地
"""
import subprocess
import sys
import tempfile

REPO = "/home/sean/projects/audio-sep"
PYTHON = "/home/sean/miniconda3/bin/python3"  # 含 torch 的系统环境（PATH 可能不含 miniconda）


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    src, query = sys.argv[1], sys.argv[2]
    out = sys.argv[3] if len(sys.argv) > 3 else f"/tmp/sep_{query.replace(' ', '_')}.wav"

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        wav = f.name
    subprocess.run(["/home/sean/miniconda3/bin/ffmpeg", "-y", "-v", "error", "-i", src, "-ac", "1", "-ar", "32000", wav], check=True)

    code = f"""
import sys
sys.path.insert(0, {REPO!r})
from pipeline import build_audiosep, separate_audio
model = build_audiosep(
    config_yaml={REPO + '/config/audiosep_base.yaml'!r},
    checkpoint_path={REPO + '/checkpoint/audiosep_base_4M_steps.ckpt'!r},
    device='cpu')
separate_audio(model, {wav!r}, {query!r}, {out!r}, device='cpu')
print('OK ->', {out!r})
"""
    subprocess.run([PYTHON, "-c", code], check=True, cwd=REPO)
    print(f"分离完成: {out}")


if __name__ == "__main__":
    main()
