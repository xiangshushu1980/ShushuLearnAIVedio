# 03 API 与自动化

## 概述
ComfyUI 提供完整 HTTP API，可被软件/脚本远程调用。本机服务地址 `http://127.0.0.1:8188`。

## 核心端点

| 端点 | 方法 | 用途 |
|------|------|------|
| `/prompt` | POST | 提交工作流（API 格式） |
| `/queue` | GET | 查看运行/等待队列 |
| `/history/{prompt_id}` | GET | 查询任务结果 |
| `/view?filename=..&type=output` | GET | 下载生成文件 |
| `/upload/image` | POST | 上传图片到 input/ |
| `/system_stats` | GET | 系统/GPU 状态 |
| `/object_info` | GET | 所有节点定义 |
| `/ws` | WebSocket | 实时执行进度 |

## 客户端使用（comfy_client.py）

```python
from comfy_client import ComfyClient, build_wan_i2v_workflow

client = ComfyClient("http://127.0.0.1:8188")

# 1. 上传起始图片
image_name = client.upload_image("my_image.jpg")

# 2. 构建工作流（可动态传参）
wf = build_wan_i2v_workflow(
    prompt="your prompt",
    negative="负面词",
    image_name=image_name,
    width=512, height=512, length=33, steps=20,
)

# 3. 提交 + 等待
pid = client.queue_workflow(wf)
result = client.wait_for_result(pid)

# 4. 拿输出链接
urls = client.get_output_urls(result)
```

## API 格式说明

API 格式与 UI 格式不同：
```json
{
  "节点ID": {
    "class_type": "节点类型",
    "inputs": {
      "参数名": 值或 ["来源节点ID", 输出槽位]
    }
  }
}
```

- 节点间连接：`"model": ["54", 0]` 表示来自节点 54 的第 0 号输出
- widget 值直接给：`"steps": 20, "text": "prompt"`
- UI 专用控件（control_after_generate、image_upload）不提交

## 转换工具（run_workflow.py）

把 UI 格式（LiteGraph: nodes + links）转成 API 格式：

```bash
python3 run_workflow.py workflows/wan2.1_i2v_480p.json
```

内部用 WIDGET_NAMES 表映射节点 widget 顺序（已覆盖本项目用到的节点）。

## 交互式编辑工作流（助手协作模式）

助手（pi）可通过以下方式与用户协作编辑：
1. **读**：读取 `workflows/*.json` 了解当前结构
2. **改**：修改节点参数（提示词、尺寸、步数等）后写回 JSON 或直接构建 API
3. **跑**：`python3 run_workflow.py <文件>` 提交运行
4. **看**：检查 `output/video/` 结果 + `/tmp/comfyui_start.log` 日志

## 远程服务注意
- 远程访问需 `./start.sh --listen 0.0.0.0`
- ComfyUI 无鉴权，公网暴露有风险；建议局域网使用或加反向代理
- 生成文件命名：SaveVideo 的 filename_prefix 决定，如 `video/api` → `output/video/api_00001_.mp4`

## 资源系统 API（0.29 Assets）
- `/api/assets` 文件索引（sqlite 持久化）；`/api/jobs` 会话任务（内存态）
- `/api/assets/seed` POST 手动重扫（启动扫描已带 prune_first=True）
- 详见 `.pi/skills/comfyui/references/troubleshooting.md`
