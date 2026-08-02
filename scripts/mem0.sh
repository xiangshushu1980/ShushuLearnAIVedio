#!/bin/bash
# Mem0 HTTP 常驻 server 管理（单实例，服务所有 pi 会话）
# 用法: ./scripts/mem0.sh {start|stop|restart|status}
# 设计要点:
#   - PID 文件管理（.mem0/mem0.pid），不用 pkill -f（会误杀自身命令行）
#   - setsid 脱离进程组，避免 shell 超时回收
#   - curl 带 --max-time，不等 bge-m3 加载（~40s）挂死

set -u
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PY="/home/sean/miniconda3/envs/mem0/bin/python"
PIDFILE="$ROOT/.mem0/mem0.pid"
LOG="/tmp/mem0_server.log"
URL="http://127.0.0.1:8899/mcp"

# 读 PID 文件并校验进程是否真的活着（防止 stale pid）
get_pid() {
  if [ -f "$PIDFILE" ]; then
    local pid
    pid="$(cat "$PIDFILE" 2>/dev/null | tr -d ' ')"
    if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then
      # 确认是 mem0 进程（防 PID 复用误判）
      if grep -q "mem0_mcp.py" "/proc/$pid/cmdline" 2>/dev/null; then
        echo "$pid"
        return 0
      fi
    fi
    rm -f "$PIDFILE"  # stale PID
  fi
  return 1
}

start() {
  local pid
  if pid="$(get_pid)"; then
    echo "✅ mem0 已在运行 (PID $pid) — 端口 http://127.0.0.1:8899/mcp"
    return 0
  fi
  cd "$ROOT"
  setsid nohup "$PY" scripts/mem0_mcp.py > "$LOG" 2>&1 < /dev/null &
  echo "$!" > "$PIDFILE"
  echo "🚀 启动中 (PID $!)，bge-m3 加载约 30-40s，日志: $LOG"
  # 轮询等 HTTP 就绪（最多 90s），不阻塞调用者太久
  for i in $(seq 1 18); do
    sleep 5
    if curl -s --max-time 2 -o /dev/null -X POST "$URL" \
      -H "Content-Type: application/json" \
      -H "Accept: application/json, text/event-stream" \
      -d '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}' 2>/dev/null; then
      echo "✅ mem0 HTTP server 就绪: $URL (PID $(cat "$PIDFILE"))"
      return 0
    fi
    # 提前退出说明启动失败
    if ! kill -0 "$(cat "$PIDFILE" 2>/dev/null)" 2>/dev/null; then
      echo "❌ 启动失败，看日志: tail $LOG"
      rm -f "$PIDFILE"
      return 1
    fi
  done
  echo "⚠️ 90s 未就绪，看日志: tail $LOG"
  return 1
}

stop() {
  local pid
  if pid="$(get_pid)"; then
    kill "$pid"
    # 最多等 15s 优雅退出
    for _ in $(seq 1 15); do
      kill -0 "$pid" 2>/dev/null || break
      sleep 1
    done
    if kill -0 "$pid" 2>/dev/null; then
      echo "⚠️ 未优雅退出，强制 kill"
      kill -9 "$pid"
    fi
    rm -f "$PIDFILE"
    echo "🛑 mem0 已停止 (PID $pid)"
  else
    echo "ℹ️ mem0 未在运行"
  fi
}

status() {
  local pid
  if pid="$(get_pid)"; then
    local mem
    mem="$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits 2>/dev/null || echo '?')"
    echo "✅ mem0 运行中: PID $pid"
    echo "   端口: http://127.0.0.1:8899/mcp"
    echo "   GPU 总显存: ${mem}MiB（mem0 为 CPU 模式，不占显存）"
    echo "   日志: $LOG (最后3行:)"
    tail -3 "$LOG" 2>/dev/null | sed 's/^/     /'
  else
    echo "❌ mem0 未在运行"
    return 1
  fi
}

case "${1:-}" in
  start)   start ;;
  stop)    stop ;;
  restart) stop; start ;;
  status)  status ;;
  *) echo "用法: $0 {start|stop|restart|status}"; exit 1 ;;
esac
