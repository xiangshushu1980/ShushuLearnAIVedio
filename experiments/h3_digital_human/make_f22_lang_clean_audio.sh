#!/usr/bin/env bash
set -euo pipefail
OUT=/home/sean/projects/ComfyUI/input/h3_avatar/f22_lang
for lang in yue zh en; do
  # 纯 break：保留 100ms 停顿，下一段做淡入，避免人为点击声。
  ffmpeg -y -hide_banner -loglevel error -i "$OUT/${lang}_ctx.wav" -f lavfi -t 0.10 -i "anullsrc=r=48000:cl=stereo" -i "$OUT/${lang}_next.mp3" \
    -filter_complex "[0:a]atrim=0:0.916667,asetpts=PTS-STARTPTS[a];[1:a]atrim=0:0.10,asetpts=PTS-STARTPTS[b];[2:a]atrim=0:1.416667,afade=t=in:st=0:d=0.025,asetpts=PTS-STARTPTS[c];[a][b][c]concat=n=3:v=0:a=1,atrim=0:2.333333,asetpts=PTS-STARTPTS" \
    -ar 48000 -ac 2 "$OUT/${lang}_pure_break_clean.wav"
  # 说话中间：只做 25ms 极短 crossfade，消除两个 TTS 文件边界的点击声。
  ffmpeg -y -hide_banner -loglevel error -i "$OUT/${lang}_ctx.wav" -i "$OUT/${lang}_next.mp3" \
    -filter_complex "[0:a]atrim=0:0.916667,asetpts=PTS-STARTPTS[a];[1:a]atrim=0:1.441667,asetpts=PTS-STARTPTS[b];[a][b]acrossfade=d=0.025:c1=tri:c2=tri,atrim=0:2.333333,asetpts=PTS-STARTPTS" \
    -ar 48000 -ac 2 "$OUT/${lang}_mid_speech_clean.wav"
  # 弱起音：保留弱音设定，但在弱音开头做淡入，避免音量突变。
  ffmpeg -y -hide_banner -loglevel error -i "$OUT/${lang}_ctx.wav" -i "$OUT/${lang}_next.mp3" \
    -filter_complex "[0:a]atrim=0:0.916667,asetpts=PTS-STARTPTS[a];[1:a]atrim=0:0.35,volume=0.22,afade=t=in:st=0:d=0.025,asetpts=PTS-STARTPTS[b];[1:a]atrim=start=0.35:duration=1.066667,asetpts=PTS-STARTPTS[c];[a][b][c]concat=n=3:v=0:a=1,atrim=0:2.333333,asetpts=PTS-STARTPTS" \
    -ar 48000 -ac 2 "$OUT/${lang}_weak_onset_clean.wav"
done
