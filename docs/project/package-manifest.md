# 交接包清单

生成日期：2026-09-04

## 包含内容

- `docs/`：项目文档、调研结论和交接说明；
- `scripts/`：运行、批处理、音频/视频处理和校验脚本（不含本地虚拟环境）；
- `workflows/`：ComfyUI API 工作流 JSON；
- `web-shotlist/`：剧本、拍摄本、提示词和实体管理工具源码（不含 `node_modules`、`data`、构建产物）；
- `experiments/`：实验配置、JSON、Markdown、README 和可查询的文字记录；
- `.pi/tasks/`、`.pi/ledger/`：任务进度和结论证据；
- 根目录运行入口和项目配置；
- `docs/archive/project/git-history-handoff.md`：全量 Git 记录导出；
- `docs/project/project-handoff.md`：项目交接总览。

## 排除内容

- `.git/`：Git 历史已单独导出；
- `output/`、`outputs/` 和实验生成的视频、音频、图片；
- `assets/`、`experiments/speech-video/assets/` 等个人媒体素材；
- `web-shotlist/node_modules/`、`web-shotlist/data/`、构建产物；
- `scripts/.venv-vlm/` 等本地 Python 虚拟环境；
- 模型权重、缓存、Docker 镜像和 ComfyUI 本体；
- `.env`、`.mcp.json`、本地设置和其他可能含凭据的运行时文件；
- 外部 LongCat、DUIX 项目源代码。

## 使用说明

解压后先阅读 `docs/project/project-handoff.md` 和 `docs/INDEX.md`。接收方需要自行安装 ComfyUI、模型、Python/Node 依赖，并根据 `docs/01_environment.md` 配置运行环境。
