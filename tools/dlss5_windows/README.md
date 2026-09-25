# DLSS5 Windows Video Queue

这是给 `comfy-ops` 配套的 Windows 端薄封装：WSL 继续负责生成视频，本工具负责把视频交给现成的 `video2dlssnr` 处理。

它不包含 NVIDIA 的 DLSS5 runtime，也不重新实现 DLSS5。需要用户在 Windows 上合法准备：

- `video2dlssnr` 项目目录（包含 `nr_video.py`）；
- 对应的 `nvngx_dlssnr.dll` / `nvngx_dlss.dll` runtime；
- Windows NVIDIA 驱动和 FFmpeg（`video2dlssnr` 也可使用其自带 FFmpeg）。

## Windows 安装

### Web UI（推荐）

`dlss5_web.py` 会启动一个只监听本机的 Web 服务。浏览器界面适合浏览视频缩略图、递归读取子文件夹、原片预览和处理状态查看；服务本身不常驻占用 GPU，只有调用引擎处理视频时才使用 GPU。

桌面启动脚本会创建两个快捷方式：`ComfyUI DLSS5 视频增强`（启动服务并打开浏览器）和 `停止 ComfyUI DLSS5 服务`（停止服务及其处理子进程）。

在 Windows PowerShell 中运行：

```powershell
py -3 tools\dlss5_windows\dlss5_web.py
```

启动后访问 `http://127.0.0.1:8765`。服务会自动扫描：

```text
\\wsl$\<当前发行版>\home\sean\projects\ComfyUI\output\video
```

创建桌面快捷方式：

```powershell
powershell -ExecutionPolicy Bypass -File tools\dlss5_windows\install_desktop_shortcut.ps1
```

默认扫描（启动时通过 `wsl.exe -l -q` 自动读取发行版名称）：

```text
\\wsl$\<当前发行版>\home\sean\projects\ComfyUI\output\video
```

如果你的 ComfyUI 不在默认位置，启动前设置：

```powershell
$env:COMFYUI_VIDEO_DIR = "\\wsl$\你的发行版\home\sean\projects\ComfyUI\output\video"
```

视频扫描是递归的，会读取 `output/video` 下所有层级的 `.mp4`、`.mov`、`.mkv`、`.webm`、`.avi` 和 `.m4v` 文件。音频、图片和 safetensors 会自动忽略。

UI 会自动探测 `VIDEO2DLSSNR_ROOT`、`D:\dlss5\video2dlssnr`、`C:\dlss5\video2dlssnr`、用户目录下的 `dlss5/video2dlssnr`、Downloads 和 Desktop；找不到时仍然可以浏览视频，只会在处理时提示配置引擎。引擎目录需要指向包含 `nr_video.py` 的 `video2dlssnr` 目录，旁边可配置其专用 Python 环境。首次处理建议用 `1x + Natural + intensity 0.7`，先观察身份和口型，再尝试 1.5x/2x。

建议目录结构：

```text
D:\dlss5\video2dlssnr\nr_video.py
D:\dlss5\video2dlssnr\out\...
D:\dlss5\queue\input\
D:\dlss5\queue\enhanced\
```

如果浏览器能看到视频但缩略图为空，通常是 Windows 找不到 FFmpeg；原片仍可直接播放。可把 `ffmpeg.exe` 放在引擎的 `out` 目录，或加入 Windows PATH。

在 Windows PowerShell 中：

```powershell
py -3 tools\dlss5_windows\dlss5_queue.py `
  --engine-root D:\dlss5\video2dlssnr `
  --input D:\dlss5\queue\input `
  --output D:\dlss5\queue\enhanced `
  --once
```

持续监听 WSL 输出目录：

```powershell
py -3 tools\dlss5_windows\dlss5_queue.py `
  --engine-root D:\dlss5\video2dlssnr `
  --input D:\dlss5\queue\input `
  --output D:\dlss5\queue\enhanced `
  --watch
```

默认使用原尺寸 Neural Rendering（`--scale 1`），确认效果后再试 `--scale 2` 或指定 `--width 1920`。

## WSL 调用

把 Windows 输入目录映射到 WSL 后，生成流程只需把最终视频复制到输入目录：

```bash
cp output/final.mp4 /mnt/d/dlss5/queue/input/
```

推荐先由 Windows PowerShell 启动 watcher。后续可以从 WSL 调用 `powershell.exe` 或通过计划任务启动，但不建议每个视频重复启动 Python/worker。

## 设计边界

- 一个输入视频对应一个输出视频；不会覆盖原片。
- 输出保留原始基本名，追加 `.dlss5`。
- 每个任务写入独立 `.log`，队列状态写入 `.dlss5-queue.json`。
- 程序只调用 `nr_video.py`，不下载或复制任何 NVIDIA DLL。
- `--watch` 会等待文件大小稳定后再处理，避免 WSL 正在写入时抢读。
