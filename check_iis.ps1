# Test game URLs and web.config
Write-Host "=== Kiem tra http://localhost/game/ ===" -ForegroundColor Cyan
try {
    $r = Invoke-WebRequest -Uri "http://localhost/game/" -UseBasicParsing -TimeoutSec 5
    Write-Host "   Status: $($r.StatusCode)" -ForegroundColor Green
    $preview = $r.Content.Substring(0, [Math]::Min(200, $r.Content.Length))
    Write-Host "   Preview: $preview"
} catch {
    $msg = $_.Exception.Message
    Write-Host "   LOI: $msg" -ForegroundColor Red
}

Write-Host ""
Write-Host "=== Kiem tra http://localhost/game/sso ===" -ForegroundColor Cyan
try {
    $r = Invoke-WebRequest -Uri "http://localhost/game/sso" -UseBasicParsing -TimeoutSec 5
    Write-Host "   Status: $($r.StatusCode)" -ForegroundColor Green
} catch {
    $msg = $_.Exception.Message
    Write-Host "   LOI: $msg" -ForegroundColor Red
}

Write-Host ""
Write-Host "=== Kiem tra http://localhost:7000/ (CSB Backend) ===" -ForegroundColor Cyan
try {
    $r = Invoke-WebRequest -Uri "http://localhost:7000/" -UseBasicParsing -TimeoutSec 5
    Write-Host "   Status: $($r.StatusCode)" -ForegroundColor Green
    Write-Host "   Body: $($r.Content.Substring(0, [Math]::Min(100, $r.Content.Length)))"
} catch {
    $msg = $_.Exception.Message
    Write-Host "   LOI: $msg" -ForegroundColor Red
}

Write-Host ""
Write-Host "=== web.config da co rules CSB? ===" -ForegroundColor Cyan
$wc = Get-Content "C:\HRM_WEB\HRM_WEB\HRM_WEB\web.config" -Raw
if ($wc -match "CSB") {
    Write-Host "   OK - web.config da co rules CSB" -ForegroundColor Green
} else {
    Write-Host "   THIEU rules CSB!" -ForegroundColor Red
}

Write-Host ""
Write-Host "=== Noi dung C:\inetpub\wwwroot\game ===" -ForegroundColor Cyan
Get-ChildItem "C:\inetpub\wwwroot\game" -Recurse | Select-Object FullName, Length | Format-Table -AutoSize
