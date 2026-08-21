#!/usr/bin/env python3
"""用 FlashSR 把 MiniMax Music3 等音频超分辨率到 48kHz（补高频，去"录音机/罐头"质感）。
复用 ComfyUI-Egregora-Audio-Super-Resolution 节点的分块 WOLA 逻辑。

用法:
  python3 upscale_music3.py --input <in.mp3/wav> [--output out.wav] [--lowpass] [--output-sr 48000|44100|96000]

输出: 48kHz 立体声 WAV（默认与输出文件同名 .wav）
"""
import sys, os, argparse, subprocess, tempfile
from pathlib import Path
import numpy as np

NODE_DIR = "/home/sean/projects/ComfyUI/custom_nodes/ComfyUI-Egregora-Audio-Super-Resolution"
sys.path.insert(0, NODE_DIR)

def load_audio(path: str):
    """读音频 -> ([C,S] float32, sr)。mp3 用 ffmpeg 转 wav 兜底。"""
    import soundfile as sf
    try:
        data, sr = sf.read(path, dtype="float32", always_2d=False)
    except Exception as e:
        print(f"  [sf 失败 {e}] 走 ffmpeg 转 wav")
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            tmp = f.name
        subprocess.run(["ffmpeg", "-y", "-i", path, "-ac", "2", "-ar", "48000",
                        "-sample_fmt", "f32", tmp], check=True, capture_output=True)
        data, sr = sf.read(tmp, dtype="float32", always_2d=False)
        os.unlink(tmp)
    if data.ndim == 1:
        data = data[None, :]          # [1, S]
    else:
        data = data.T                  # [S, C] -> [C, S]
    return np.ascontiguousarray(data, dtype=np.float32), int(sr)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--output", default=None)
    ap.add_argument("--lowpass", action="store_true", help="超分前低通，减少训练/推理失配")
    ap.add_argument("--output-sr", default="48000", choices=["48000", "44100", "96000"])
    args = ap.parse_args()

    out = args.output or (str(Path(args.input).with_suffix(".wav")))
    print(f"➡️  FlashSR 超分: {args.input} -> {out} @{args.output_sr}Hz (lowpass={args.lowpass})")

    cs, in_sr = load_audio(args.input)
    print(f"   源: {in_sr}Hz, {cs.shape[0]}ch, {cs.shape[1]/in_sr:.1f}s")

    from egregora_audio_super_resolution import EgregoraAudioSuperResolution
    import torch
    wf = torch.from_numpy(cs).unsqueeze(0).contiguous()          # [1,C,S]
    audio = {"waveform": wf, "sample_rate": in_sr}
    node = EgregoraAudioSuperResolution()
    (out_audio,) = node.run(audio=audio, lowpass_input=args.lowpass, output_sr=args.output_sr)

    wf_out = out_audio["waveform"].squeeze(0).cpu().numpy()      # [C,S]
    sr_out = int(out_audio["sample_rate"])
    import soundfile as sf
    sf.write(out, wf_out.T, sr_out)
    print(f"✅ 完成: {out} ({sr_out}Hz, {wf_out.shape[0]}ch)")

if __name__ == "__main__":
    main()
