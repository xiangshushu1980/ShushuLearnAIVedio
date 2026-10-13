#!/usr/bin/env bash
set -euo pipefail
SRC=/home/sean/projects/ComfyUI/input/hk_a_30s.wav
OUT=/home/sean/projects/ComfyUI/input/h3_avatar/f22_master
mkdir -p "$OUT"

for spec in pure_break:7.837875 mid_speech:5.500000 weak_onset:6.200000; do
  name=${spec%%:*}; t=${spec##*:}
  astart=$(awk -v t="$t" 'BEGIN{printf "%.6f", t-3.75}')
  bstart=$(awk -v t="$t" 'BEGIN{printf "%.6f", t-0.916667}')
  ffmpeg -y -hide_banner -loglevel error -ss "$astart" -i "$SRC" -t 3.75 -ar 48000 -ac 2 "$OUT/${name}_a.wav"
  ffmpeg -y -hide_banner -loglevel error -ss "$bstart" -i "$SRC" -t 2.333333 -ar 48000 -ac 2 "$OUT/${name}_b.wav"
done
echo "created $OUT"
