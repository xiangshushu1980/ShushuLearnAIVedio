param(
    [string]$ToolRoot = ""
)

$ErrorActionPreference = "Stop"
if ([string]::IsNullOrWhiteSpace($ToolRoot)) {
    $ToolRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
}
$script = Join-Path $ToolRoot "dlss5_web.py"
if (-not (Test-Path $script)) {
    throw "找不到 $script"
}

$desktop = [Environment]::GetFolderPath("Desktop")
$shortcutPath = Join-Path $desktop "ComfyUI DLSS5 视频增强.lnk"
$python = (Get-Command py -ErrorAction SilentlyContinue).Source
if ([string]::IsNullOrWhiteSpace($python)) {
    $python = (Get-Command python -ErrorAction SilentlyContinue).Source
}
if ([string]::IsNullOrWhiteSpace($python)) {
    throw "未找到 py 或 python，请先安装 Windows Python。"
}

$shell = New-Object -ComObject WScript.Shell
$shortcut = $shell.CreateShortcut($shortcutPath)
$shortcut.TargetPath = $python
$shortcut.Arguments = "`"$script`""
$shortcut.WorkingDirectory = $ToolRoot
$shortcut.Description = "浏览 ComfyUI 视频并调用 DLSS5 进行增强"
$shortcut.IconLocation = "$env:SystemRoot\System32\SHELL32.dll,21"
$shortcut.Save()
Write-Host "已创建桌面快捷方式：$shortcutPath"

$stopScript = Join-Path $ToolRoot "stop_dlss5_web.ps1"
$stopPath = Join-Path $desktop "停止 ComfyUI DLSS5 服务.lnk"
$stopShortcut = $shell.CreateShortcut($stopPath)
$stopShortcut.TargetPath = "powershell.exe"
$stopShortcut.Arguments = "-NoProfile -ExecutionPolicy Bypass -File `"$stopScript`""
$stopShortcut.WorkingDirectory = $ToolRoot
$stopShortcut.Description = "停止 ComfyUI DLSS5 本地 Web 服务"
$stopShortcut.IconLocation = "$env:SystemRoot\System32\SHELL32.dll,31"
$stopShortcut.Save()
Write-Host "已创建停止快捷方式：$stopPath"
