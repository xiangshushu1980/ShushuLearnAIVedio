---
name: breeze-tts
description: Use Breeze TTS 2 for local Chinese/English narration, voice design, voice cloning, voice direction, and expressive video-account audio. Apply when generating or evaluating spoken audio with Breeze TTS 2; do not use it for music or speech recognition.
---

# Breeze TTS 2

Use the project-local environment and model:

- code: `tools/breeze-tts`
- Python: `.venv-breeze-tts/bin/python`
- model: `models/breeze-tts-2`
- outputs: `outputs/breeze-tts`

The current local setup is RTX 4090 + Torch 2.9.1/CUDA 12.8. It has been verified to load the official checkpoint and generate Chinese WAV audio. Do not modify the main ComfyUI environment merely to run this skill.

## Choose a mode

- Voice Design: no reference audio; describe the desired speaker in `--instruction`.
- Voice Clone: use clean reference audio plus its exact transcript in `--ref-audio` and `--ref-text`.
- Voice Direction: combine reference audio/transcript with an instruction controlling mood, pace, and delivery.

For a personal video account, prefer a stable designed voice or the user's own authorized recording. Keep the same voice instruction, seed, sample rate, and post-processing across an episode series unless testing a deliberate variation.

## CLI pattern

```bash
.venv-breeze-tts/bin/python tools/breeze-tts/infer.py \
  models/breeze-tts-2 \
  --text '[笑] 欢迎来到今天的视频。' \
  --instruction '温和、可信、表达清晰的中文视频创作者，语速自然，像面对面聊天。' \
  --cfg-scale 4 \
  --output outputs/breeze-tts/sample.wav
```

Voice clone:

```bash
.venv-breeze-tts/bin/python tools/breeze-tts/infer.py \
  models/breeze-tts-2 \
  --ref-audio /path/to/reference.wav \
  --ref-text '参考音频的准确逐字稿。' \
  --text '目标旁白文本。' \
  --output outputs/breeze-tts/clone.wav
```

Voice direction adds `--instruction` and normally uses `--cfg-scale 4`:

```bash
--instruction '保持同一音色，语气更沉稳，语速稍慢，像知识类视频旁白。' --cfg-scale 4
```

Read [references/parameters.md](references/parameters.md) before changing speed, emotion, CFG, fast mode, or cloning inputs.

## Video-account workflow

1. Finalize the script before synthesis.
2. Split long narration at semantic or breath boundaries; generate separate clips so one bad sentence does not invalidate the whole take.
3. Use Chinese inline events only when they serve the performance: `[笑]`, `[叹气]`, `[咳嗽]`, `[清嗓子]`.
4. Listen for pronunciation, unwanted breaths, clipped endings, repeated phrases, and identity drift before sending audio to H3 or video assembly.
5. Keep the generated external WAV as the final audio master when synchronizing a digital human; use H3 audio conditioning for lip/motion guidance only when the workflow calls for it.

## Constraints

- Voice cloning requires an exact reference transcript. Do not trust an automatic transcript without checking it against the audio; a mismatch can cause echo or unstable cloning.
- The official open-weight model is currently bilingual English/Chinese; do not infer Cantonese or other dialect support without a dedicated test.
- Official claims about latency are H100-specific. Measure on the local GPU before promising real-time behavior.
- Model weights, derivatives, and self-hosted outputs are research/non-commercial under the current BreezeBlue license. Check authorization before using generated audio in monetized or client work.
- The model outputs 24 kHz mono WAV/PCM in the tested path.

## Web UI boundary

Do not build a web UI before the CLI parameters and evaluation criteria are settled. A later UI should wrap the proven CLI/API and expose only useful controls: text, instruction, reference audio/transcript, seed, CFG, mode, and output path. Keep model management and arbitrary low-level fast-stage flags out of the first UI.
