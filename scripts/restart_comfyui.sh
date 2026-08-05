#!/bin/bash
# ComfyUI 安全重启脚本（2026-08-05 定稿，替代手工 kill+启动）
# 用法:
#   ./restart_comfyui.sh           # 重启（默认 sage 开，同 start.sh）
#   ./restart_comfyui.sh --nosage  # 重启并关闭 SageAttention（音频/对照测试用）
#   ./restart_comfyui.sh --status  # 只查状态不重启
#
# 设计要点（吸取 2026-08-05 补测批踩坑）：
# 1. 精确拿 PID（模式锚定 ^，避免 pgrep -f 匹配到 bash 包装自身而误杀 shell）
# 2. 杀进程等端口真正释放，避免新实例端口冲突静默失败
# 3. 启动后健康检查通过才返回（避免过渡期提交任务被 runner 误判）
# 4. 自动 source venv（忘记 activate 会 sqlalchemy ModuleNotFoundError）

set -u
COMFY_DIR="/home/sean/projects/ComfyUI"
PORT=8188
SAGE=1
LOG=/tmp/comfyui_start.log

for arg in "$@"; do
  case "$arg" in
    --nosage) SAGE=0 ;;
    --status) STATUS_ONLY=1 ;;
  esac
done

pid_of() {
  # 锚定完整命令行，只匹配真正的 ComfyUI 主进程
  ps aux | awk '$11 ~ /^python3$/ && $12 == "main.py" && $13 ~ /^--enable-assets/ {print $2}' | head -1
}

if [ "${STATUS_ONLY:-0}" = "1" ]; then
  PID=$(pid_of)
  if [ -n "$PID" ]; then
    echo "ComfyUI 运行中 PID=$PID 参数: $(ps -o args= -p $PID)"
    curl -s -m 3 "http://127.0.0.1:$PORT/system_stats" >/dev/null && echo "端口 $PORT 健康 ✅" || echo "端口 $PORT 无响应 ⚠️"
  else
    echo "ComfyUI 未运行"
  fi
  exit 0
fi

# --- 1. 杀旧进程 ---
PID=$(pid_of)
if [ -n "$PID" ]; then
  echo "停止旧进程 PID=$PID ..."
  kill "$PID" 2>/dev/null
  for i in $(seq 1 10); do
    sleep 1
    if [ -z "$(pid_of)" ]; then break; fi
  done
  if [ -n "$(pid_of)" ]; then
    echo "15 秒未退出，强制 kill -9"
    kill -9 "$PID" 2>/dev/null
    sleep 3
  fi
else
  echo "无旧进程"
fi

# --- 2. 等端口释放 ---
for i in $(seq 1 15); do
  if ! curl -s -m 2 "http://127.0.0.1:$PORT/system_stats" >/dev/null 2>&1; then
    echo "端口 $PORT 已释放"; break
  fi
  [ "$i" = 15 ] && echo "⚠️ 端口 $PORT 仍被占用，可能被其他进程持有" && exit 1
  sleep 1
done

# --- 3. 启动（带 sage 或不带） ---
cd "$COMFY_DIR" || exit 1
source venv/bin/activate
if [ "$SAGE" = "1" ]; then
  echo "启动（SageAttention 开）..."
  setsid nohup python3 main.py --enable-assets --use-sage-attention > "$LOG" 2>&1 < /dev/null &
else
  echo "启动（SageAttention 关）..."
  setsid nohup python3 main.py --enable-assets > "$LOG" 2>&1 < /dev/null &
fi

# --- 4. 健康检查（最长 120s） ---
for i in $(seq 1 24); do
  sleep 5
  if curl -s -m 3 "http://127.0.0.1:$PORT/system_stats" >/dev/null 2>&1; then
    PID=$(pid_of)
    echo "✅ ComfyUI 就绪 PID=$PID（$((i*5))s）"
    free -g | awk 'NR==2 {print "内存: "$2"GB 总量 / "$4"GB 可用"}'
    echo "日志: $LOG"
    exit 0
  fi
done
echo "❌ 120s 内未就绪，查日志 $LOG"
tail -20 "$LOG"
exit 1
