#!/bin/bash
set -e

# =============================================
# ComfyUI 模型下载脚本 — Wan2.1 I2V-480P
# =============================================

cd "$(dirname "$0")"
source venv/bin/activate

MODELS_DIR="models"

echo ""
echo "╔══════════════════════════════════════════════╗"
echo "║      ComfyUI 模型下载 - Wan2.1 I2V-480P     ║"
echo "╚══════════════════════════════════════════════╝"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo " 使用前请先完成以下操作（只需一次）："
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo " ① 浏览器打开（需 VPN）："
echo "    https://huggingface.co/Wan-AI/Wan2.1-I2V-14B-480P"
echo ""
echo " ② 点击「Agree and access repository」接受许可"
echo ""
echo " ③ 然后复制你的 Access Token："
echo "    右上角头像 → Settings → Access Tokens"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 检查是否已登录
if huggingface-cli whoami &> /dev/null; then
    echo "✅ HuggingFace 已登录"
else
    echo "❌ 未登录。请输入你的 Access Token："
    huggingface-cli login
fi

# 配置国内镜像加速
echo ""
echo "配置国内镜像加速下载..."
export HF_ENDPOINT=https://hf-mirror.com

# 开始下载
echo ""
echo "下载 Wan2.1 I2V-14B-480P（~13GB）..."
echo "  - 如果中断，重新运行脚本会自动续传"
echo "  - 脚本会放慢下载速度，不影响正常上网"
echo ""

huggingface-cli download Wan-AI/Wan2.1-I2V-14B-480P \
    --local-dir "$MODELS_DIR/diffusion_models/Wan2.1-I2V-14B-480P" \
    --local-dir-use-symlinks False \
    --resume-download

echo ""
echo "✅ 下载完成！"
echo ""
echo "启动 ComfyUI：./start.sh"
echo "然后在 Workflow 中加载模型即可。"
echo ""
