Write-Host "=== Test voi hostname dung: hrm.csbrg.com ===" -ForegroundColor Cyan
# Them tam vao hosts file de test
$hostsEntry = "127.0.0.1 hrm.csbrg.com"
$hostsFile = "C:\Windows\System32\drivers\etc\hosts"
$currentHosts = Get-Content $hostsFile
if ($currentHosts -notcontains $hostsEntry) {
    Write-Host "  Hosts file chua co hrm.csbrg.com -> them vao..."
    # Khong the ghi hosts file khong co quyen admin
    Write-Host "  Can quyen admin de them vao hosts file" -ForegroundColor Yellow
} else {
    Write-Host "  Hosts file da co hrm.csbrg.com" -ForegroundColor Green
}

Write-Host ""
Write-Host "=== Kiem tra port 80 ai dang listen ===" -ForegroundColor Cyan
netstat -ano | Select-String ":80 " | Select-Object -First 10

Write-Host ""
Write-Host "=== Test curl voi header Host ===" -ForegroundColor Cyan
# Su dung WebRequest voi host header
try {
    $r = Invoke-WebRequest -Uri "http://127.0.0.1/game/" -UseBasicParsing -TimeoutSec 5 -Headers @{"Host"="hrm.csbrg.com"}
    Write-Host "  hrm.csbrg.com/game/ -> $($r.StatusCode)" -ForegroundColor Green
    Write-Host "  Preview: $($r.Content.Substring(0, 200))"
} catch {
    $ex = $_.Exception
    if ($ex.Response) {
        Write-Host "  Status: $([int]$ex.Response.StatusCode)"
        $stream = $ex.Response.GetResponseStream()
        $reader = New-Object System.IO.StreamReader($stream)
        $body = $reader.ReadToEnd()
        Write-Host "  Server: $($ex.Response.Headers['Server'])"
        Write-Host "  Body: $($body.Substring(0, [Math]::Min(300, $body.Length)))"
    } else {
        Write-Host "  LOI: $($ex.Message)" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "=== Test game/index.html voi Host header ===" -ForegroundColor Cyan
try {
    $r = Invoke-WebRequest -Uri "http://127.0.0.1/game/index.html" -UseBasicParsing -TimeoutSec 5 -Headers @{"Host"="hrm.csbrg.com"}
    Write-Host "  game/index.html -> $($r.StatusCode)" -ForegroundColor Green
    Write-Host "  Preview: $($r.Content.Substring(0, 100))"
} catch {
    Write-Host "  LOI: $($_.Exception.Message)" -ForegroundColor Red
}
