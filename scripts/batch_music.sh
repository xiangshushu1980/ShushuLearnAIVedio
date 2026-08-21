#!/bin/bash
# 批量生成 Music3 测试曲 + 超分 + 母带，累积到 comfy-ops/output/audio/
# 每首串行生成（ComfyUI 一次一个任务），生成完统一处理
set -u
cd /home/sean/projects/comfy-ops
VPY=/home/sean/projects/ComfyUI/venv/bin/python3
OUTMP3=/home/sean/projects/ComfyUI/output/audio
LOG=/tmp/batch_music4.log
echo "=== batch start $(date +%T) ===" >> $LOG

# tag, json, duration, seed
GEN=(
  "arabic_oud_fix arabic_oud_fix_input.json 75 20260851"
  "celtic_irish_fix celtic_irish_fix_input.json 75 20260852"
  "german_harpsichord_fix german_harpsichord_fix_input.json 80 20260853"
  "japanese_koto_fix japanese_koto_fix_input.json 90 20260831"
  "jazz_trio_fix jazz_trio_fix_input.json 75 20260854"
  "pureorch_fix pureorch_fix_input.json 90 20260855"
  "scandinavian_folk_fix scandinavian_folk_fix_input.json 80 20260856"
  "scottish_bagpipe_fix scottish_bagpipe_fix_input.json 75 20260857"
  "string_quartet_fix string_quartet_fix_input.json 75 20260858"
  "turkish_ney_fix turkish_ney_fix_input.json 80 20260859"
  "vietnamese_danbai_fix vietnamese_danbai_fix_input.json 80 20260860"
  "weak_instr_fix weak_instr_fix_input.json 90 20260861"
)

for spec in "${GEN[@]}"; do
  set -- $spec; tag=$1; json=$2; dur=$3; seed=$4
  echo ">> GEN $tag ($json, ${dur}s, seed=$seed) $(date +%T)" >> $LOG
  $VPY scripts/run_music3.py --input scripts/$json --duration $dur --seed $seed --tag $tag >> $LOG 2>&1
  echo ">> GEN_DONE $tag $(date +%T)" >> $LOG
done

# 处理：超分 + 母带
for spec in "${GEN[@]}"; do
  set -- $spec; tag=$1
  src="$OUTMP3/minimax_music3_${tag}_00001.mp3"
  [ -f "$src" ] || { echo ">> SKIP $tag (no source)" >> $LOG; continue; }
  echo ">> PROCESS $tag $(date +%T)" >> $LOG
  $VPY scripts/upscale_music3.py --input "$src" --output "output/audio/${tag}_sr48k.wav" >> $LOG 2>&1
  python3 scripts/master_music.py --input "output/audio/${tag}_sr48k.wav" --out "output/audio/${tag}_mastered.wav" >> $LOG 2>&1
  echo ">> PROCESS_DONE $tag $(date +%T)" >> $LOG
done
echo "=== batch ALL DONE $(date +%T) ===" >> $LOG
