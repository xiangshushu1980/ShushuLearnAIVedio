#!/usr/bin/env bash
# Owner: Sean
# Run one command under a hive-resource lease. Heartbeats stay inside this
# process so callers do not need one tool call per renewal.
set -Eeuo pipefail

usage() {
  sed -n '1,18p' "$0"
  cat >&2 <<'EOF'

Usage:
  hive_resource_run.sh --owner OWNER [--resources R1,R2] [--ttl-ms MS]
                       [--interval-sec SEC] -- COMMAND [ARGS...]

Defaults:
  ttl-ms       600000 (10 minutes)
  interval-sec 30
EOF
}

owner=""
resources=""
ttl_ms=600000
interval_sec=30

while (($#)); do
  case "$1" in
    --owner) owner="${2:?--owner requires a value}"; shift 2 ;;
    --resources) resources="${2:?--resources requires a value}"; shift 2 ;;
    --ttl-ms) ttl_ms="${2:?--ttl-ms requires a value}"; shift 2 ;;
    --interval-sec) interval_sec="${2:?--interval-sec requires a value}"; shift 2 ;;
    --) shift; break ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown option: $1" >&2; usage >&2; exit 2 ;;
  esac
done

if [[ -z "$owner" || "$#" -eq 0 ]]; then
  usage >&2
  exit 2
fi
if ! [[ "$ttl_ms" =~ ^[1-9][0-9]*$ && "$interval_sec" =~ ^[1-9][0-9]*$ ]]; then
  echo "ttl-ms and interval-sec must be positive integers" >&2
  exit 2
fi

acquire_args=(lease acquire --owner "$owner" --ttl "$ttl_ms")
if [[ -n "$resources" ]]; then
  acquire_args+=(--resources "$resources")
fi

acquire_output="$(hive-resource "${acquire_args[@]}" 2>&1)" || {
  printf '%s\n' "$acquire_output" >&2
  exit 1
}
printf '%s\n' "$acquire_output"

lease_id="$(printf '%s\n' "$acquire_output" | sed -n 's/^租约 \([0-9a-f-][0-9a-f-]*\) 已授予.*/\1/p' | head -n 1)"
if [[ -z "$lease_id" ]]; then
  echo "Could not parse lease id from hive-resource output" >&2
  exit 1
fi

child_pid=""
heartbeat_pid=""
cleaned=0

cleanup() {
  [[ "$cleaned" -eq 1 ]] && return
  cleaned=1
  if [[ -n "$heartbeat_pid" ]]; then
    kill "$heartbeat_pid" 2>/dev/null || true
    wait "$heartbeat_pid" 2>/dev/null || true
  fi
  hive-resource lease release "$lease_id" >/dev/null 2>&1 || true
}
trap cleanup EXIT INT TERM

heartbeat_loop() {
  while kill -0 "$child_pid" 2>/dev/null; do
    sleep "$interval_sec"
    kill -0 "$child_pid" 2>/dev/null || return 0
    if ! hive-resource lease heartbeat "$lease_id" --ttl "$ttl_ms" >/dev/null 2>&1; then
      echo "hive-resource heartbeat failed; stopping command (lease $lease_id)" >&2
      kill -TERM "$child_pid" 2>/dev/null || true
      return 1
    fi
  done
}

"$@" &
child_pid=$!
heartbeat_loop &
heartbeat_pid=$!

set +e
wait "$child_pid"
command_status=$?
set -e
exit "$command_status"
