#!/usr/bin/env python3
"""用本地 MusicGen-small 生成背景音乐 (CPU)
用法: python gen_bgm.py "prompt" <duration_sec> <out.wav>
MusicGen 50 tokens/sec; 15s=760 tokens (hyperframe 实测)
"""
import sys, torch, warnings
warnings.filterwarnings("ignore")
from transformers import AutoProcessor, MusicgenForConditionalGeneration

prompt = sys.argv[1]
dur = float(sys.argv[2])
out = sys.argv[3]
max_tokens = int(dur * 50)

print(f"加载本地 MusicGen-small...")
processor = AutoProcessor.from_pretrained("facebook/musicgen-small", local_files_only=True)
model = MusicgenForConditionalGeneration.from_pretrained("facebook/musicgen-small", local_files_only=True)
print(f"模型就绪, 生成 {dur}s (max_new_tokens={max_tokens})")

inputs = processor(text=[prompt], padding=True, return_tensors="pt")
audio = model.generate(**inputs, max_new_tokens=max_tokens)
audio = audio[0, 0].cpu().numpy()

# 写 32kHz mono wav (用标准库 wave, 不依赖 scipy)
import numpy as np, wave, struct
data = np.clip(audio * 32767, -32768, 32767).astype(np.int16)
w = wave.open(out, 'wb')
w.setnchannels(1); w.setsampwidth(2); w.setframerate(32000)
w.writeframes(data.tobytes()); w.close()
print(f"已写 {out}, 时长 {len(audio)/32000:.2f}s")
