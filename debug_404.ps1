Write-Host "=== Chi tiet 404 response headers ===" -ForegroundColor Cyan
try {
    $r = Invoke-WebRequest -Uri "http://localhost/game/" -UseBasicParsing -TimeoutSec 5
    Write-Host "  OK: $($r.StatusCode)"
} catch {
    $ex = $_.Exception
    if ($ex.Response) {
        Write-Host "  Status: $([int]$ex.Response.StatusCode)"
        Write-Host "  Server: $($ex.Response.Headers['Server'])"
        Write-Host "  X-Powered-By: $($ex.Response.Headers['X-Powered-By'])"
        Write-Host "  All headers:"
        foreach ($h in $ex.Response.Headers.AllKeys) {
            Write-Host "    $h : $($ex.Response.Headers[$h])"
        }
        # Lay noi dung response 404
        $stream = $ex.Response.GetResponseStream()
        $reader = New-Object System.IO.StreamReader($stream)
        $body = $reader.ReadToEnd()
        Write-Host ""
        Write-Host "  Body (500 chars):"
        Write-Host $body.Substring(0, [Math]::Min(500, $body.Length))
    } else {
        Write-Host "  Khong co response: $($ex.Message)" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "=== Test /game/index.html truc tiep ===" -ForegroundColor Cyan
try {
    $r = Invoke-WebRequest -Uri "http://localhost/game/index.html" -UseBasicParsing -TimeoutSec 5
    Write-Host "  OK: $($r.StatusCode) ($($r.Content.Length) bytes)" -ForegroundColor Green
    Write-Host "  Preview: $($r.Content.Substring(0, 100))"
} catch {
    Write-Host "  LOI: $($_.Exception.Message)" -ForegroundColor Red
}
