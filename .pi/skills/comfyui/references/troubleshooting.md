# 踩坑记录（全量）

## 文件与历史
- ⚠️ 事后 mv 重命名 output 文件会破坏 /view 链接和前端引用 → 在 filename_prefix 里直接命名
- ⚠️ `POST /history {"clear": true}` **全清所有历史**（内存，不可还原）→ 只删指定用 `{"delete": [prompt_ids]}`；文件不受影响
- ⚠️ 前端黑色占位符 = 服务端历史记录引用了已删文件 → 删文件后同步删对应历史条目

## ComfyUI 0.29 Assets 系统（2025-07-31 摸清）
- `--enable-assets` 启动参数必须加（已写进 start.sh），否则 assets API 全 403、数据库 0 行
- 启动时 asset_seeder 自动扫描 models/input/output → 文件索引入 sqlite（user/comfyui.db，**持久化，重启不丢**）→ 前端 **Assets→Imported** 显示（历史资源浏览入口）
- **Media Assets / Assets→Generated = 会话任务(jobs)记录，内存态，重启清空**（同 /history）→ 新任务后才显示
- jobs 数据源 `/api/jobs`；文件索引数据源 `/api/assets`（注意是 /api/assets 不是 /assets）
- **MCP/API 提交的任务也计入 jobs**（MCP 提交后 /api/jobs 出现记录）
- **移动/改名文件后重启 ComfyUI** → main.py 启动扫描 prune_first=True 软删旧路径（is_missing=1），API 层自动过滤，无需手动清库

## 前端/插件
- ⚠️ **Image Feed(Custom-Scripts) 弃用**：pythongosssss 插件在 0.29 Vue 前端兼容性差（点开不显示）；用途仅是"会话内实时预览"，与 Media Assets 重叠 → 已删除
- **Nodes 2.0 保持关闭**（官方文档确认：性能优化中 + 自定义节点兼容性风险，可一键切换）
- comfyui-browser 代码 2024-11 停更，前端无"新建文件夹"入口 → 目录管理用 Windows 资源管理器（\\wsl.localhost\...\output）或 agent

## 构图
- ⚠️ I2V 构图锚定起始图：人物在底部 → 输出从底部出现；换居中图解决（构图分析：PIL 分三带比颜色差异，主体带差异最大）

## pip / comfy-cli
- ⚠️ **ComfyUI venv 的 pip 配了阿里云镜像**（`mirrors.aliyun.com`，全局 index-url），镜像缺 comfy-cli → 报 "Could not find a version... (from versions: none)"。**绕行：`venv/bin/pip install comfy-cli -i https://pypi.org/simple/`** 显式走官方 PyPI（miniconda 的 pip 无镜像配置，不受影响）
- comfy-cli 安装位置：装进 ComfyUI 工作区 venv（`venv` 或 `.venv` 均可被 comfyui-mcp 探测到），**不要依赖 `.mcp.json` env 或 PATH**（pi 的 MCP spawn 环境不可控，见 CivitAI token 坑）；装完用 `comfy_cli_status`(detail=env) 验证

## 内存/OOM（系统崩溃）
- ⚠️ **2025-08-02 实测：连续跑 Bernini 大任务（尤其 40 步无 LoRA 质量模式）后，ComfyUI python 进程内存飙到 ~30GB → 触发系统 OOM killer → dockerd panic → 整个 WSL2 需重启**
  - 日志证据：`journalctl -b -1` 显示 `Out of memory: Killed process python3 total-vm:177917948kB anon-rss:30888192kB` + `dockerd: panic: runtime error`
- **防护**：① 大任务之间 sleep 30-60s 让缓存回收 ② 不要连续多个 40 步任务 ③ 每任务后 `nvidia-smi` + `free -h` 确认内存回落 ④ 重启后 history 清空（内存态），重跑丢失任务
- **重启命令**：`cd /home/sean/projects/ComfyUI && setsid ./start.sh > /tmp/comfyui_start.log 2>&1 < /dev/null &`（nohup 在会话结束时可能被杀，setsid 更稳）；日志文件被清空过（启动时截断）

## 下载（HF/CivitAI）
- ⚠️ HF 下载频繁断线 → `curl -L -C -` 断点续传 + 循环重试脚本（setsid 脱离会话）；直连/mirror 波动时测速切换（hf-mirror.com vs huggingface.co）
- ⚠️ MCP `apply_manifest` 大下载会请求超时（部分节点会装，模型不会）→ 大文件用 bash 手动下载
- ⚠️ **CivitAI token 注入坑**：`.mcp.json` 的 env 加了 `CIVITAI_API_TOKEN` 后，pi 的 MCP spawn 机制不读新增 env（进程 environ 里只有 COMFYUI_URL）→ `download_civitai_model` 仍 401。**绕行：`curl -L -H "Authorization: Bearer $TOKEN" -o <文件> "https://civitai.com/api/download/models/<version_id>?type=Model&format=SafeTensor"` 直接下载**（token 本身有效，API 测 200）
- ⚠️ 并行下载多个大文件可能触发 HF 限流 → 网络变慢时减少并发

## 队列/性能
- ⚠️ **队列首任务慢 = 模型切换**：每批任务第一个含模型加载（Anima 4GB ~6s / Krea 12.9GB ~16s / Wan GGUF ~45s），后续同模型任务才快（猫 9.56s vs 后续 2.7s 同理）

## 进程管理
- ⚠️ **pkill 自杀坑**：`pkill -f "main.py"` 会匹配自身 shell 命令行（含 main.py 字符串）把自己 TERM → 用 `pkill -f "[m]ain.py"` 或 pgrep 精确 PID

## 模型能力
- ⚠️ 当前模型 deepseek-v4-flash **不支持图片** → 无法视觉评估，视频质量靠用户反馈

## 网络工作流拉取
- `comfyui_run_workflow_url` 返回 404 说明 URL 不存在（通路正常）；需指向公开 raw .json / GitHub raw 链接
- 拉取的工作流常有模型名不匹配 → `comfyui_check_workflow_runtime` 检查兼容性，缺模型先下载再跑
