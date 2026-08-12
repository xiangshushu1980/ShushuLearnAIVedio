#!/usr/bin/env python3
"""Qwen3-TTS 独立推理脚本（web-shotlist 音色种子生成用）

用法：
  qwen_tts_gen.py --kind custom --speaker ryan --text "你好" --out /tmp/x.wav
  qwen_tts_gen.py --kind design --instruct "清冷少女声，语速偏慢" --text "你好" --out /tmp/x.wav
  qwen_tts_gen.py --kind clone --ref /tmp/ref.wav --ref-text "参考文本" --text "目标文本" --out /tmp/x.wav

模型目录：~/projects/ComfyUI/models/qwen-tts/<repo>/
device 自适应：CUDA 显存充足用 GPU，否则回落 CPU。
"""
import argparse
import os
import sys
import time

MODELS_ROOT = os.path.expanduser('~/projects/ComfyUI/models/qwen-tts')
NODE_DIR = os.path.expanduser('~/projects/ComfyUI/custom_nodes/ComfyUI-Qwen-TTS')
sys.path.insert(0, NODE_DIR)

import numpy as np
import torch

from qwen_tts.inference.qwen3_tts_model import Qwen3TTSModel

REPO = {
    'custom': 'Qwen3-TTS-12Hz-1.7B-CustomVoice',
    'design': 'Qwen3-TTS-12Hz-1.7B-VoiceDesign',
    'base': 'Qwen3-TTS-12Hz-1.7B-Base',
}


def pick_device() -> str:
    # 推理稳定性优先：CPU（Qwen3-TTS 1.7B 短文本 CPU 可接受，且不占显存不打扰跑批）
    # CUDA 的 device 不一致问题在 wrapper 层未处理干净，暂不用 GPU
    return 'cpu'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--kind', choices=['custom', 'design', 'clone'], default='custom')
    ap.add_argument('--speaker', default='ryan')
    ap.add_argument('--instruct', default='', help='VoiceDesign/CustomVoice 风格指令（如：清冷少女声）')
    ap.add_argument('--ref', default='', help='克隆参考音频路径（kind=clone）')
    ap.add_argument('--ref-text', default='', help='克隆参考音频对应文本')
    ap.add_argument('--text', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--seed', type=int, default=42)
    ap.add_argument('--max-new-tokens', type=int, default=2048)
    args = ap.parse_args()

    device = pick_device()
    torch.manual_seed(args.seed)
    np.random.seed(args.seed % (2**32))
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(args.seed)

    if args.kind == 'clone':
        model_key = 'base'
    else:
        model_key = args.kind
    repo = os.path.join(MODELS_ROOT, REPO[model_key])
    if not os.path.isdir(repo):
        raise RuntimeError(f'模型目录不存在: {repo}（先运行 download_models.py 或 curl 拉取）')

    t0 = time.time()
    dtype = torch.bfloat16 if device == 'cuda' else torch.float32
    model = Qwen3TTSModel.from_pretrained(repo, torch_dtype=dtype)
    # 内部从 config 读 device_map；这里显式放到目标设备
    if device == 'cuda':
        model.model = model.model.to('cuda')
    print(f'[load] {model_key} {time.time()-t0:.1f}s device={device}', flush=True)

    if args.kind == 'custom':
        wavs, sr = model.generate_custom_voice(
            text=args.text, speaker=args.speaker, language='auto',
            instruct=args.instruct or None, max_new_tokens=args.max_new_tokens,
        )
    elif args.kind == 'design':
        wavs, sr = model.generate_voice_design(
            text=args.text, language='auto', instruct=args.instruct,
            max_new_tokens=args.max_new_tokens,
        )
    else:  # clone
        clone_prompt = model.create_voice_clone_prompt(args.ref, args.ref_text or None)
        wavs, sr = model.generate_voice_clone(
            text=args.text, voice_clone_prompt=clone_prompt, language='auto',
            max_new_tokens=args.max_new_tokens,
        )

    wav = np.asarray(wavs[0] if isinstance(wavs, list) else wavs)
    if wav.ndim == 1:
        wav = wav[:, None]
    import soundfile as sf
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    sf.write(args.out, wav, sr)
    print(f'[ok] {args.out} sr={sr} shape={wav.shape} dur={len(wav)/sr:.1f}s', flush=True)


if __name__ == '__main__':
    main()
