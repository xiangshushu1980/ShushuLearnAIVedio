#!/usr/bin/env bash
# Owner: Sean
# Download selected files from a ModelScope repository into a local model tree.
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage:
  ./download_models.sh <model-id> <local-dir> <repo-file> [repo-file ...]

Examples:
  ./download_models.sh Comfy-Org/MiniMax-H3 ./models \
    diffusion_models/minimax_h3_fl2va_pruned_int8_convrot.safetensors
  ./download_models.sh circlestone-labs/Anima ./models \
    split_files/diffusion_models/anima-base-v1.0.safetensors
  ./download_models.sh Aitrepreneur/FLX ./models \
    4x-ClearRealityV1.pth
  ./download_models.sh 1038lab/BiRefNet ./models/RMBG/BiRefNet \
    BiRefNet_toonout.safetensors

Repository file paths are kept below <local-dir>. At least one file is required
so an accidental full-repository download cannot consume large amounts of disk.
USAGE
}

if (( $# < 3 )); then
  usage >&2
  exit 2
fi

model_id=$1
local_dir=$2
shift 2

if ! command -v modelscope >/dev/null 2>&1; then
  echo "modelscope CLI is not installed in this environment." >&2
  echo "Install it in the active Python environment with: python -m pip install modelscope" >&2
  exit 127
fi

exec modelscope download --model "$model_id" --local_dir "$local_dir" "$@"
