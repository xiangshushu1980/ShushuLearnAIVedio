#!/usr/bin/env bash
set -euo pipefail

OUT=/home/sean/projects/ComfyUI/input/h3_avatar/f22_lang
mkdir -p "$OUT"

edge-tts --voice zh-HK-HiuMaanNeural --text '我哋而家继续测试这一段连接效果，等我讲完上一句之后，马上接住下一句内容。' --write-media "$OUT/yue_base.mp3"
edge-tts --voice zh-CN-XiaoxiaoNeural --text '现在我们继续测试这一段连接效果，等我讲完上一句话之后，马上接着说下一句话。' --write-media "$OUT/zh_base.mp3"
edge-tts --voice en-US-JennyNeural --text 'Now we continue testing this connection, and after I finish the previous phrase, I immediately continue with the next phrase.' --write-media "$OUT/en_base.mp3"

edge-tts --voice zh-HK-HiuMaanNeural --text '下一句内容会继续说出来。' --write-media "$OUT/yue_next.mp3"
edge-tts --voice zh-CN-XiaoxiaoNeural --text '下一句话会继续说出来。' --write-media "$OUT/zh_next.mp3"
edge-tts --voice en-US-JennyNeural --text 'The next phrase continues right away.' --write-media "$OUT/en_next.mp3"

for lang in yue zh en; do
  ffmpeg -y -hide_banner -loglevel error -i "$OUT/${lang}_base.mp3" \
    -af "apad=pad_dur=4,atrim=0:3.75" -ar 48000 -ac 2 "$OUT/${lang}_a.wav"
  ffmpeg -y -hide_banner -loglevel error -i "$OUT/${lang}_a.wav" \
    -af "atrim=start=2.833333:duration=0.916667,asetpts=PTS-STARTPTS" \
    -ar 48000 -ac 2 "$OUT/${lang}_ctx.wav"

  ffmpeg -y -hide_banner -loglevel error \
    -i "$OUT/${lang}_ctx.wav" -f lavfi -t 0.10 -i "anullsrc=r=48000:cl=stereo" -i "$OUT/${lang}_next.mp3" \
    -filter_complex "[0:a]atrim=0:0.916667,asetpts=PTS-STARTPTS[a];[1:a]atrim=0:0.10,asetpts=PTS-STARTPTS[b];[2:a]atrim=0:1.416667,asetpts=PTS-STARTPTS[c];[a][b][c]concat=n=3:v=0:a=1,atrim=0:2.333333,asetpts=PTS-STARTPTS" \
    -ar 48000 -ac 2 "$OUT/${lang}_pure_break.wav"

  ffmpeg -y -hide_banner -loglevel error \
    -i "$OUT/${lang}_ctx.wav" -i "$OUT/${lang}_next.mp3" \
    -filter_complex "[0:a]atrim=0:0.916667,asetpts=PTS-STARTPTS[a];[1:a]atrim=0:1.416667,asetpts=PTS-STARTPTS[b];[a][b]concat=n=2:v=0:a=1,atrim=0:2.333333,asetpts=PTS-STARTPTS" \
    -ar 48000 -ac 2 "$OUT/${lang}_mid_speech.wav"

  ffmpeg -y -hide_banner -loglevel error \
    -i "$OUT/${lang}_ctx.wav" -i "$OUT/${lang}_next.mp3" \
    -filter_complex "[0:a]atrim=0:0.916667,asetpts=PTS-STARTPTS[a];[1:a]atrim=0:0.35,volume=0.22,asetpts=PTS-STARTPTS[b];[1:a]atrim=start=0.35:duration=1.066667,asetpts=PTS-STARTPTS[c];[a][b][c]concat=n=3:v=0:a=1,atrim=0:2.333333,asetpts=PTS-STARTPTS" \
    -ar 48000 -ac 2 "$OUT/${lang}_weak_onset.wav"
done

echo "created $OUT"
