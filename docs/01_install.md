# 01 安装与环境

## 环境
- Ubuntu 24.04 (WSL2, mirror 网络模式) / RTX 4090 24GB / Python 3.13
- ComfyUI 安装于 `/home/sean/projects/ComfyUI`
- PyTorch 2.13.0 + CUDA 13.0

## 启动

```bash
cd /home/sean/projects/ComfyUI
./start.sh
# 后台运行:
nohup ./start.sh > /tmp/comfyui_start.log 2>&1 &
```

- 界面: http://localhost:8188
- 局域网/远程访问需 `--listen 0.0.0.0`
- 启动日志: `/tmp/comfyui_start.log`（采样进度也打印在这里）

## 关键脚本

| 脚本 | 作用 |
|------|------|
| `start.sh` | 启动（已配置清华 pip 源） |
| `run_workflow.py` | 把 UI 格式工作流 JSON 转成 API 格式并提交运行 |
| `comfy_client.py` | API 客户端（软件集成用） |

## 目录

```
models/         模型（unet, diffusion_models, text_encoders, vae, loras, clip_vision...）
custom_nodes/   自定义节点（Manager、comfyui-browser、GGUF 等）
input/          输入图片（start/ 公用起始图，test/ 测试素材）
output/         生成结果（anima/ krea/ compare/ video/ img_*/ res_test/ 子目录）
user/           用户数据（workflows/ + comfyui.db assets 索引）
```

## 常用维护

```bash
# 查看 ComfyUI 进程
ps aux | grep main.py

# 停止（注意：pkill -f "main.py" 会匹配自身 shell → 用 [m]ain.py）
pkill -f "[m]ain.py"

# 查看采样进度
tail -f /tmp/comfyui_start.log

# 磁盘
df -h /home/sean
```

## 注意事项
- WSL mirror 网络模式下，Windows 浏览器直接访问 localhost:8188 即可
- 模型加载首次较慢（Anima 4GB ~6s / Krea 12.9GB ~16s / Wan GGUF ~45s），之后同模型任务有缓存
