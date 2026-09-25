$pidFile = Join-Path $env:LOCALAPPDATA "comfy-ops\dlss5\web.pid"
if (Test-Path -LiteralPath $pidFile) {
    $targetPid = Get-Content -LiteralPath $pidFile -ErrorAction SilentlyContinue
    if ($targetPid) { taskkill.exe /PID ([int]$targetPid) /T /F | Out-Null }
}
Write-Host "DLSS5 Web 服务已停止（如果正在运行）。"
