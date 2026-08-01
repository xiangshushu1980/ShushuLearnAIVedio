#!/bin/bash
# 监控模型下载进度，每5分钟记录一次，全部完成后退出

MODELS=/home/sean/projects/ComfyUI/models
FILES=(
  "diffusion_models/wan2.1_i2v_480p_14B_fp8_e4m3fn.safetensors:14G"
  "text_encoders/umt5_xxl_fp8_e4m3fn_scaled.safetensors:6G"
  "vae/wan_2.1_vae.safetensors:253M"
  "clip_vision/clip_vision_h.safetensors:2.5G"
)

while true; do
  clear
  echo "$(date '+%H:%M:%S')  模型下载进度"
  echo "═══════════════════════════════════════════"
  ALL_DONE=1
  for entry in "${FILES[@]}"; do
    file="${entry%%:*}"
    total="${entry##*:}"
    if [ -f "$MODELS/$file" ]; then
      size=$(du -h "$MODELS/$file" | cut -f1)
      echo "  $file"
      echo "    $size / $total"
      # 检查是否完成（文件大小与预期接近）
      actual_bytes=$(stat -c%s "$MODELS/$file")
      case "$total" in
        14G)  [ $actual_bytes -lt 14000000000 ] && ALL_DONE=0 ;;
        6G)   [ $actual_bytes -lt 6000000000 ] && ALL_DONE=0 ;;
        253M) [ $actual_bytes -lt 250000000 ] && ALL_DONE=0 ;;
        2.5G) [ $actual_bytes -lt 2400000000 ] && ALL_DONE=0 ;;
      esac
    else
      echo "  $file  未开始"
      ALL_DONE=0
    fi
  done

  # 检查进程
  RUNNING=$(pgrep -c wget 2>/dev/null || echo 0)
  echo "═══════════════════════════════════════════"
  echo "  活跃下载进程: $RUNNING"

  if [ "$ALL_DONE" = "1" ] && [ "$RUNNING" = "0" ]; then
    echo ""
    echo "✅ 全部下载完成！可以启动 ComfyUI 了："
    echo "   cd /home/sean/projects/ComfyUI && ./start.sh"
    exit 0
  fi
  sleep 300
done
