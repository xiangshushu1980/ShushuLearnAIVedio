#!/usr/bin/env bash
# Owner: Sean — approved, serialized ComfyUI H3 flow smoke for the Reference import.
set -euo pipefail

project_root="/home/sean/projects/comfy-ops"
comfy_root="/home/sean/projects/ComfyUI"
experiment_root="$project_root/experiments/ai_film_editor_flow_20261003"
import_root="$experiment_root/imports/e0797899-ccb5-46d1-b461-13035a820dbc/assets"
input_root="$comfy_root/input"
comfy_output="$comfy_root/output/video/sean_ai_film_flow_20261003"
local_output="$experiment_root/outputs"
task_id="remote-750a1fff-c5dc-426c-81d1-4e33811caab4"
comfy_pid="16853"
lease_id=""
peak_vram_mb=0

finish() {
  if [[ -n "$lease_id" ]]; then
    hive-resource lease release "$lease_id" || true
  fi
}
trap finish EXIT

curl -fsS --max-time 5 http://127.0.0.1:8188/queue | node -e '
  let body = "";
  process.stdin.on("data", chunk => body += chunk);
  process.stdin.on("end", () => {
    const queue = JSON.parse(body);
    const running = queue.queue_running || [];
    const pending = queue.queue_pending || [];
    if (running.length || pending.length) {
      console.error(`ComfyUI queue is not empty (running=${running.length}, pending=${pending.length}); stopping before upload.`);
      process.exitCode = 2;
    } else console.log("ComfyUI queue is empty.");
  });
'

stage_asset() {
  local source_path="$1"
  local target_path="$2"
  if [[ -e "$target_path" ]]; then
    if ! cmp -s "$source_path" "$target_path"; then
      echo "Refusing to overwrite different ComfyUI input: $target_path" >&2
      return 3
    fi
    echo "Reusing byte-identical staged input: $target_path"
  else
    cp "$source_path" "$target_path"
  fi
}

process_args=$(ps -p "$comfy_pid" -o args=)
if [[ "$process_args" != *"main.py"* ]]; then
  echo "ComfyUI PID $comfy_pid no longer matches the expected main.py process; stopping." >&2
  exit 3
fi

lease_output=$(hive-resource lease acquire --owner "$task_id" --resources gpu:0 --pid "$comfy_pid" --ttl 600000)
printf '%s\n' "$lease_output"
lease_id=$(printf '%s\n' "$lease_output" | sed -n 's/^租约 \([^ ]*\) 已授予.*/\1/p')
if [[ -z "$lease_id" ]]; then
  echo "Could not parse GPU lease ID; stopping before staging inputs." >&2
  exit 4
fi

stage_asset "$import_root/af9823e0-1b27-48b7-a469-47ddcf4b7534.png" "$input_root/sean_ai_film_main_appearance.png"
stage_asset "$import_root/432cfa98-83f2-416e-b600-01090075fb73.png" "$input_root/sean_ai_film_three_view.png"
stage_asset "$import_root/1e2f367f-132f-4c92-93d7-660422eaf8be.wav" "$input_root/sean_ai_film_voice.wav"

mkdir -p "$local_output"
mkdir -p "$comfy_root/output/video"
echo "Starting three serial H3 Ref2VA cases; the H3 model will load through the existing shared ComfyUI instance."
set +e
"$comfy_root/venv/bin/python" -u "$project_root/scripts/h3_batch_runner.py" \
  "$experiment_root/h3_cases.json" --interval 10 2>&1 | tee "$experiment_root/runner.log" &
runner_pid=$!
set -e

while kill -0 "$runner_pid" 2>/dev/null; do
  current_vram=$(/usr/lib/wsl/lib/nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits | head -1 | tr -d ' ')
  if [[ "$current_vram" =~ ^[0-9]+$ ]] && (( current_vram > peak_vram_mb )); then
    peak_vram_mb=$current_vram
  fi
  sleep 35
  hive-resource lease heartbeat "$lease_id" --ttl 600000
done

set +e
wait "$runner_pid"
runner_status=$?
set -e
if (( runner_status != 0 )); then
  echo "H3 runner exited with status $runner_status; preserving any ComfyUI output for diagnosis." >&2
  exit "$runner_status"
fi

shopt -s nullglob
generated=("$comfy_output"/*.mp4)
if (( ${#generated[@]} == 0 )); then
  echo "Runner completed without MP4s at $comfy_output" >&2
  exit 5
fi
for output_file in "${generated[@]}"; do
  mv "$output_file" "$local_output/"
done
sha256sum "$local_output"/*.mp4 > "$experiment_root/outputs.sha256"

if (( peak_vram_mb > 0 )); then
  hive-resource observe --resource gpu:0 --job "$task_id" --metrics "{\"peakVramMb\":$peak_vram_mb}"
fi
echo "Archived ${#generated[@]} MP4 candidate(s) under $local_output; sampled peak VRAM ${peak_vram_mb} MB."
