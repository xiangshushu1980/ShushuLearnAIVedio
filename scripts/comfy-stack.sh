#!/usr/bin/env bash
# Owner: Sean
# Single entrypoint for the shared ComfyUI instance.
#
# The MCP/Agent process is client-managed through .mcp.json. This script must
# not start a second comfyui-mcp process; it only makes ComfyUI available for
# that client and records the shared service in hive-resource.
set -Eeuo pipefail

COMFY_DIR="${COMFY_DIR:-/home/sean/projects/ComfyUI}"
PORT="${COMFY_PORT:-8188}"
HOST="${COMFY_HOST:-127.0.0.1}"
LOG="${COMFY_LOG:-/tmp/comfyui_start.log}"
PID_FILE="${COMFY_PID_FILE:-/tmp/comfyui-stack.pid}"
LOCK_FILE="${COMFY_LOCK_FILE:-/tmp/comfyui-stack.lock}"
READY_TIMEOUT="${COMFY_READY_TIMEOUT:-120}"
SYSTEMD_UNIT="${COMFY_SYSTEMD_UNIT:-comfyui.service}"

usage() {
  cat <<'EOF'
Usage:
  scripts/comfy-stack.sh start
  scripts/comfy-stack.sh stop
  scripts/comfy-stack.sh restart
  scripts/comfy-stack.sh status

This is the only supported ComfyUI startup entrypoint for comfy-ops.
The ComfyUI process lifecycle is managed by the user systemd unit
comfyui.service; this wrapper delegates start/stop/restart to systemd.
The Agent/MCP server is started by the client from .mcp.json and is not
started by this script.
EOF
}

health_url() {
  printf 'http://%s:%s/system_stats' "$HOST" "$PORT"
}

is_healthy() {
  curl -fsS -m 3 "$(health_url)" >/dev/null 2>&1
}

pid_is_comfy() {
  local pid="$1" args
  args="$(ps -o args= -p "$pid" 2>/dev/null || true)"
  [[ "$args" == *"$COMFY_DIR"* && "$args" == *"main.py"* ]]
}

pid_from_file() {
  local pid
  [[ -s "$PID_FILE" ]] || return 1
  read -r pid < "$PID_FILE"
  [[ "$pid" =~ ^[0-9]+$ ]] || return 1
  kill -0 "$pid" 2>/dev/null && pid_is_comfy "$pid" || return 1
  printf '%s\n' "$pid"
}

pid_from_processes() {
  ps -eo pid=,args= | awk -v dir="$COMFY_DIR" '
    index($0, dir) && $0 ~ /(^|[[:space:]])main\.py([[:space:]]|$)/ { print $1; exit }
  '
}

comfy_pid() {
  pid_from_file || pid_from_processes
}

remove_pid() {
  rm -f "$PID_FILE"
}

systemd_show() {
  systemctl --user show "$SYSTEMD_UNIT" "$@"
}

systemd_state() {
  local state substate main_pid
  state="$(systemd_show -p ActiveState --value 2>/dev/null || true)"
  substate="$(systemd_show -p SubState --value 2>/dev/null || true)"
  main_pid="$(systemd_show -p MainPID --value 2>/dev/null || true)"
  printf 'systemd: unit=%s active=%s sub=%s mainPID=%s\n' \
    "$SYSTEMD_UNIT" "${state:-unknown}" "${substate:-unknown}" "${main_pid:-unknown}"
}

require_systemd_unit() {
  command -v systemctl >/dev/null 2>&1 || {
    echo "systemctl is unavailable; cannot manage $SYSTEMD_UNIT." >&2
    return 1
  }
  systemd_show -p LoadState --value >/dev/null 2>&1 || {
    echo "Cannot query user systemd or unit $SYSTEMD_UNIT." >&2
    return 1
  }
}

gpu_occupancy() {
  if ! command -v nvidia-smi >/dev/null 2>&1; then
    echo "GPU: nvidia-smi unavailable"
    return 0
  fi

  nvidia-smi \
    --query-gpu=index,name,memory.used,memory.total,utilization.gpu \
    --format=csv,noheader,nounits 2>&1 |
    sed 's/^/GPU: index,name,memory.used(MiB),memory.total(MiB),utilization(%): /'
}

hive_preflight() {
  if ! command -v hive-resource >/dev/null 2>&1; then
    echo "Hive: CLI unavailable; continuing with local singleton checks." >&2
    return 0
  fi

  echo "Hive: current lease occupancy"
  timeout 3s hive-resource occupancy 2>&1 || \
    echo "Hive: occupancy unavailable; this is informational only." >&2
}

hive_register_service() {
  if ! command -v hive-resource >/dev/null 2>&1; then
    return 0
  fi

  # Service registration is metadata, not a GPU lease. A long-lived ComfyUI
  # process must not hold a short-TTL exclusive generation lease.
  timeout 5s hive-resource register service \
    --id service:comfyui \
    --name "ComfyUI shared instance" \
    --port "$PORT" >/dev/null 2>&1 || \
    echo "Hive: service registration unavailable; ComfyUI is still healthy." >&2
}

wait_ready() {
  local elapsed=0
  while (( elapsed < READY_TIMEOUT )); do
    if is_healthy; then
      return 0
    fi
    sleep 2
    elapsed=$((elapsed + 2))
  done
  return 1
}

start_comfy() {
  require_systemd_unit || return 1

  if is_healthy; then
    local existing
    existing="$(comfy_pid || true)"
    if [[ "$(systemd_show -p ActiveState --value 2>/dev/null || true)" != "active" ]]; then
      echo "ComfyUI is healthy but $SYSTEMD_UNIT is not active; refusing to start a second instance." >&2
      systemd_state >&2
      return 1
    fi
    echo "ComfyUI already healthy${existing:+ PID=$existing}; reusing $SYSTEMD_UNIT."
    hive_register_service
    return 0
  fi

  if [[ "$(systemd_show -p ActiveState --value 2>/dev/null || true)" == "active" ]]; then
    echo "$SYSTEMD_UNIT is active but ComfyUI is not healthy; refusing to start a second instance." >&2
    systemd_state >&2
    echo "Inspect: $LOG" >&2
    return 1
  fi

  if [[ -n "$(comfy_pid || true)" ]]; then
    echo "ComfyUI process exists but is not healthy; refusing to start a second instance." >&2
    echo "Inspect: $LOG" >&2
    return 1
  fi

  if timeout 2s bash -c "</dev/tcp/$HOST/$PORT" 2>/dev/null; then
    echo "Port $PORT is occupied but ComfyUI is not healthy; refusing to start." >&2
    return 1
  fi

  hive_preflight
  echo "Starting $SYSTEMD_UNIT ..."
  systemctl --user start "$SYSTEMD_UNIT" || {
    echo "Failed to start $SYSTEMD_UNIT." >&2
    systemd_state >&2
    return 1
  }

  if wait_ready; then
    local actual
    actual="$(comfy_pid || true)"
    echo "ComfyUI ready${actual:+ PID=$actual}; URL=$(health_url)"
    hive_register_service
    return 0
  fi

  echo "ComfyUI did not become ready within ${READY_TIMEOUT}s." >&2
  systemd_state >&2
  systemctl --user status "$SYSTEMD_UNIT" --no-pager --lines=20 >&2 || true
  return 1
}

stop_comfy() {
  require_systemd_unit || return 1
  echo "Stopping $SYSTEMD_UNIT ..."
  systemctl --user stop "$SYSTEMD_UNIT" || {
    echo "Failed to stop $SYSTEMD_UNIT." >&2
    systemd_state >&2
    return 1
  }
  for _ in {1..30}; do
    is_healthy || break
    sleep 1
  done
  if is_healthy; then
    echo "ComfyUI remains healthy after $SYSTEMD_UNIT stopped; refusing direct process termination." >&2
    return 1
  fi
  remove_pid
  echo "ComfyUI stopped; health endpoint is offline."
}

restart_comfy() {
  require_systemd_unit || return 1
  hive_preflight
  echo "Restarting $SYSTEMD_UNIT ..."
  systemctl --user restart "$SYSTEMD_UNIT" || {
    echo "Failed to restart $SYSTEMD_UNIT." >&2
    systemd_state >&2
    return 1
  }
  if wait_ready; then
    local actual
    actual="$(comfy_pid || true)"
    echo "ComfyUI ready after restart${actual:+ PID=$actual}; URL=$(health_url)"
    hive_register_service
    return 0
  fi
  echo "ComfyUI did not become ready after restart within ${READY_TIMEOUT}s." >&2
  systemd_state >&2
  systemctl --user status "$SYSTEMD_UNIT" --no-pager --lines=20 >&2 || true
  return 1
}

status_comfy() {
  local pid
  pid="$(comfy_pid || true)"
  systemd_state
  if is_healthy; then
    echo "ComfyUI: healthy${pid:+ PID=$pid} URL=$(health_url)"
  else
    echo "ComfyUI: not healthy${pid:+ (process PID=$pid)}"
  fi
  echo "Agent/MCP: client-managed via .mcp.json; this wrapper does not start it."
  gpu_occupancy
  if command -v hive-resource >/dev/null 2>&1; then
    timeout 3s hive-resource occupancy 2>&1 || \
      echo "Hive: occupancy unavailable." >&2
  fi
}

main() {
  local command="${1:-}"
  shift || true
  for arg in "$@"; do
    case "$arg" in
      -h|--help) usage; return 0 ;;
      *) echo "Unknown option: $arg" >&2; usage >&2; return 2 ;;
    esac
  done

  case "$command" in
    start|restart|stop)
      exec 9>"$LOCK_FILE"
      flock -n 9 || { echo "Another comfy-stack operation is already running." >&2; return 1; }
      ;;
    status) ;;
    -h|--help) usage; return 0 ;;
    *) usage >&2; return 2 ;;
  esac

  case "$command" in
    start) start_comfy ;;
    stop) stop_comfy ;;
    restart) restart_comfy ;;
    status) status_comfy ;;
  esac
}

main "$@"
