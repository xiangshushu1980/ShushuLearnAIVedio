#!/bin/bash
# Mem0 HTTP 常驻 server 启动（单实例，服务所有 pi 会话）
# key 从 ~/.config/mem0_deepseek_key 读取（见 mem0_mcp.py _get_api_key）
cd "$(dirname "$0")/.."
if pgrep -f "mem0_mcp.py" > /dev/null; then
  echo "mem0 server 已在运行: $(pgrep -f mem0_mcp.py | tr '\n' ' ')"
  exit 0
fi
nohup /home/sean/miniconda3/envs/mem0/bin/python scripts/mem0_mcp.py > /tmp/mem0_server.log 2>&1 &
sleep 3
if curl -s -o /dev/null http://127.0.0.1:8899/mcp; then
  echo "✅ mem0 HTTP server 启动: http://127.0.0.1:8899/mcp (PID $!)"
else
  echo "⚠️ 启动可能失败，看日志: tail /tmp/mem0_server.log"
fi
