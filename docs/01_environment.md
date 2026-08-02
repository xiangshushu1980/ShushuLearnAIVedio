# 01 环境、启动与 API

> 合并自原 01（安装/启动/维护）+ 03（API/客户端/自动化）。最后更新：2025-08-02

## 环境
- Ubuntu 24.04 (WSL2, mirror 网络模式) / RTX 4090 24GB / Python 3.13
- ComfyUI 安装于 `/home/sean/projects/ComfyUI`（PyTorch 2.13.0 + CUDA 13.0）
- WSL mirror 模式下 Windows 浏览器直接访问 `localhost:8188`

## 启动与维护

```bash
cd /home/sean/projects/ComfyUI
./start.sh                          # 前台；后台: nohup ./start.sh > /tmp/comfyui_start.log 2>&1 &
# 停止: pkill -f "[m]ain.py"（[m] 避免匹配自身 shell）
# 日志: tail -f /tmp/comfyui_start.log（采样进度也打印在这里）
# 磁盘: df -h /home/sean
```

- 界面 http://localhost:8188；局域网/远程需 `--listen 0.0.0.0`（无鉴权，勿公网暴露）
- 模型首载较慢（Anima 4GB ~6s / Krea 12.9GB ~16s / Wan GGUF ~45s），同模型任务有缓存

## 关键脚本（comfy-ops/）

| 脚本 | 作用 |
|------|------|
| `run_workflow.py` | UI 格式工作流 JSON → API 格式并提交运行 |
| `comfy_client.py` | API 客户端（`ComfyClient` + `build_wan_i2v_workflow`） |
| `scripts/mem0_mcp.py` | Mem0 共享记忆 MCP server（见 .pi/skills/mem0/） |

## 核心 API 端点

| 端点 | 方法 | 用途 |
|------|------|------|
| `/prompt` | POST | 提交工作流（API 格式） |
| `/queue` | GET | 运行/等待队列 |
| `/history/{prompt_id}` | GET | 任务结果 |
| `/view?filename=..&type=output` | GET | 下载生成文件 |
| `/upload/image` | POST | 上传图片到 input/ |
| `/system_stats` | GET | 系统/GPU 状态 |
| `/object_info` | GET | 节点定义 |
| `/ws` | WebSocket | 实时执行进度 |
| `/api/assets`（0.29） | GET/POST | 文件索引（sqlite）/ 手动重扫（prune_first=True）|

## 客户端用法

```python
from comfy_client import ComfyClient, build_wan_i2v_workflow
client = ComfyClient("http://127.0.0.1:8188")
image_name = client.upload_image("my_image.jpg")
wf = build_wan_i2v_workflow(prompt="...", negative="...", image_name=image_name,
                            width=512, height=512, length=33, steps=20)
pid = client.queue_workflow(wf)
result = client.wait_for_result(pid)
urls = client.get_output_urls(result)
```

## API 格式要点
- API 格式 = `{"节点ID": {"class_type": 类型, "inputs": {参数: 值或 ["节点ID", 槽位]}}}`（`"model": ["54", 0]` 表示节点 54 第 0 输出）
- UI 专用控件（control_after_generate、image_upload）不提交
- `run_workflow.py` 内部用 WIDGET_NAMES 表做 UI→API 转换（已覆盖本项目节点）
- 生成文件命名：SaveVideo 的 filename_prefix 决定（`video/api` → `output/video/api_00001_.mp4`）

## 目录结构

```
/home/sean/projects/ComfyUI/
├── models/         模型（unet, diffusion_models, text_encoders, vae, loras, clip_vision, RMBG, upscale_models...）
├── custom_nodes/   自定义节点（Manager、comfyui-browser、GGUF、ComfyUI-RMBG 等）
├── input/          输入（start/ 公用起始图，test/ 测试素材）
├── output/         生成结果（anima/ krea/ compare/ video/ img_*/ res_test/）
└── user/           用户数据（workflows/ + comfyui.db assets 索引）
```
