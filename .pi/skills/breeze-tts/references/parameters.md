# Breeze TTS 2 parameter notes

## Verified local baseline

Project-local runtime paths:

- code: `tools/breeze-tts`
- Python: `.venv-breeze-tts/bin/python`
- model: `models/breeze-tts-2`
- outputs: `outputs/breeze-tts`

- GPU: NVIDIA GeForce RTX 4090, 24,564 MiB reported by `nvidia-smi`.
- Torch: 2.9.1+cu128.
- Model: official `BreezeBlue/Breeze-TTS-2` checkpoint.
- Output: 24 kHz, mono, 16-bit WAV.
- `--cfg-scale 4`: used successfully for Chinese Voice Design with a natural-language speaker/performance description.
- For natural account narration, a conservative baseline was better in a direct A/B test: no inline vocal event, a short instruction describing normal spoken Mandarin, and `--cfg-scale 1.5`. The stronger “bright/感染力” wording plus `[笑]` caused a singing-like delivery in one test; add emotional wording incrementally instead of starting from CFG 4.
- `--seed`: available for repeatable comparisons; hold it fixed during A/B tests.
- `--fast-all`: available, but not yet benchmarked locally. Official memory and latency figures are not local measurements.

## CLI options

```text
--text TEXT
--instruction INSTRUCTION
--ref-audio REF_AUDIO
--ref-text REF_TEXT
--output OUTPUT
--seed SEED
--cfg-scale CFG_SCALE
--fast-all / --no-fast-all
--fast-text-encoder / --no-fast-text-encoder
--fast-backbone-prefill / --no-fast-backbone-prefill
--fast-backbone-decode / --no-fast-backbone-decode
--fast-depth-decoder / --no-fast-depth-decoder
--fast-codec / --no-fast-codec
```

## Practical test matrix

For a personal video account, compare the same 20–40 second script with:

1. Voice Design, `cfg_scale=4`, calm explanatory instruction.
2. Voice Design, `cfg_scale=4`, energetic recommendation instruction.
3. Voice Clone, `cfg_scale=1` baseline, with a clean reference and verified transcript.
4. Voice Direction, `cfg_scale=4`, same reference, with calm/energetic instructions.

Judge pronunciation, naturalness, identity consistency, emotional controllability, sentence endings, and editing convenience. Do not judge a clone using a synthetic reference; use a real authorized recording.
