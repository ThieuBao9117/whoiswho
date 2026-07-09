Write-Host "=== Noi dung web.config trong game ===" -ForegroundColor Cyan
Get-Content "C:\inetpub\wwwroot\game\web.config" -ErrorAction SilentlyContinue

Write-Host ""
Write-Host "=== Chay appcmd list app voi admin ===" -ForegroundColor Cyan
$appcmd = "C:\Windows\System32\inetsrv\appcmd.exe"
& $appcmd list app
Write-Host ""
& $appcmd list vdir

Write-Host ""
Write-Host "=== appcmd list site detail ===" -ForegroundColor Cyan
& $appcmd list site /text:*
