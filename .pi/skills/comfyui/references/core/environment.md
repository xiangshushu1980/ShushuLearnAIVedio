# ComfyUI 环境与运行入口

## 本机入口

- ComfyUI：`/home/sean/projects/ComfyUI`
- 项目工作流、脚本、实验：`/home/sean/projects/comfy-ops`
- 服务：`http://127.0.0.1:8188`
- 启动：`cd /home/sean/projects/comfy-ops && ./scripts/comfy-stack.sh start`
- Python：`/home/sean/projects/ComfyUI/venv/bin/python`
- 当前版本以运行时探测为准；skill 记录的环境基线为 Ubuntu/WSL2、RTX 4090 24GB、Python 3.13。

## 常用动作

1. 先确认服务和模型文件。
2. 优先复用 `workflows/` 中的 JSON。
3. 用 ComfyUI API/MCP 提交和轮询任务。
4. 生成文件名时直接写入目标子目录，不事后重命名。
5. 新工作流先验证 graph health，再做最小实跑。

模型清单以 [docs/02_models.md](../../../../../docs/02_models.md) 为准；启动、维护和 API 细节见 [01_environment.md](../../../../../docs/01_environment.md)。其中的旧模型示例应先与当前模型清单和工作流核对。
