Write-Host "=== Restart IIS ===" -ForegroundColor Cyan
iisreset /restart
Start-Sleep -Seconds 3

Write-Host ""
Write-Host "=== Test URLs sau restart ===" -ForegroundColor Cyan
$urls = @(
    "http://localhost/game/",
    "http://localhost/game/sso",
    "http://localhost/game/assets/index-BgJUTbye.css"
)
foreach ($url in $urls) {
    try {
        $r = Invoke-WebRequest -Uri $url -UseBasicParsing -TimeoutSec 5
        $code = $r.StatusCode
        $len = $r.Content.Length
        Write-Host ("  {0} -> {1} ({2} bytes)" -f $url, $code, $len) -ForegroundColor Green
    } catch {
        $ex = $_.Exception
        if ($ex.Response) {
            $code = [int]$ex.Response.StatusCode
        } else {
            $code = "ERR"
        }
        Write-Host ("  {0} -> {1}: {2}" -f $url, $code, $ex.Message) -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "=== Kiem tra file game trong HRM dir ===" -ForegroundColor Cyan
$hrmGame = "C:\HRM_WEB\HRM_WEB\HRM_WEB\game"
if (Test-Path "$hrmGame\index.html") {
    Write-Host "  OK - $hrmGame\index.html ton tai" -ForegroundColor Green
} else {
    Write-Host "  THIEU - $hrmGame\index.html khong co!" -ForegroundColor Red
}
if (Test-Path "$hrmGame\assets") {
    Write-Host "  OK - $hrmGame\assets ton tai" -ForegroundColor Green
} else {
    Write-Host "  THIEU - $hrmGame\assets khong co!" -ForegroundColor Red
}
