# Test Django va IIS routing
Write-Host "=== Test Django truc tiep :8000 ===" -ForegroundColor Cyan
try {
    $r = Invoke-WebRequest -Uri "http://localhost:8000/game/" -UseBasicParsing -TimeoutSec 5
    Write-Host "  Django /game/ -> $($r.StatusCode)"
    Write-Host "  Body preview: $($r.Content.Substring(0, 200))"
} catch {
    Write-Host "  Django /game/ -> LOI: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "=== Test localhost:80 /game/ ===" -ForegroundColor Cyan
try {
    $r = Invoke-WebRequest -Uri "http://localhost:80/game/" -UseBasicParsing -TimeoutSec 5
    Write-Host "  :80 /game/ -> $($r.StatusCode)" -ForegroundColor Green
} catch {
    Write-Host "  :80 /game/ -> LOI: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "=== Test file tinh ton tai trong HRM ===" -ForegroundColor Cyan
$testFile = "C:\HRM_WEB\HRM_WEB\HRM_WEB\game\assets\index-BgJUTbye.css"
if (Test-Path $testFile) {
    Write-Host "  File ton tai: $testFile" -ForegroundColor Green
    Write-Host "  Size: $((Get-Item $testFile).Length) bytes"
} else {
    Write-Host "  File KHONG ton tai!" -ForegroundColor Red
}

Write-Host ""
Write-Host "=== Kiem tra IIS site binding ===" -ForegroundColor Cyan
try {
    $appcmd = "C:\Windows\System32\inetsrv\appcmd.exe"
    $result = & $appcmd list app "/site.name:HRMWeb" 2>&1
    Write-Host $result
} catch {
    Write-Host "  appcmd loi: $_" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "=== IIS Error logs ===" -ForegroundColor Cyan
$logDir = "C:\inetpub\logs\LogFiles"
if (Test-Path $logDir) {
    $latestLog = Get-ChildItem $logDir -Recurse -Filter "*.log" | Sort-Object LastWriteTime -Descending | Select-Object -First 1
    if ($latestLog) {
        Write-Host "Latest log: $($latestLog.FullName)"
        Get-Content $latestLog.FullName | Select-Object -Last 10
    }
}
