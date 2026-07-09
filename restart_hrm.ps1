Write-Host "=== Danh sach Windows Service HRM ===" -ForegroundColor Cyan
Get-Service | Where-Object { $_.Name -like "*HRM*" -or $_.Name -like "*waitress*" -or $_.Name -like "*django*" } |
    Format-Table Name, Status, DisplayName -AutoSize

Write-Host ""
Write-Host "=== Restart HRMWeb service ===" -ForegroundColor Cyan
$svc = Get-Service -Name "HRMWeb" -ErrorAction SilentlyContinue
if ($svc) {
    Restart-Service -Name "HRMWeb" -Force
    Start-Sleep -Seconds 3
    $svc = Get-Service -Name "HRMWeb"
    Write-Host "  Service status: $($svc.Status)" -ForegroundColor Green
} else {
    # Thu tim service khac
    $svc2 = Get-Service | Where-Object { $_.Name -like "*HRM*" -or $_.DisplayName -like "*HRM*" } | Select-Object -First 1
    if ($svc2) {
        Write-Host "  Tim thay service: $($svc2.Name) ($($svc2.DisplayName))"
        Restart-Service -Name $svc2.Name -Force
        Start-Sleep -Seconds 3
        Write-Host "  Restarted OK" -ForegroundColor Green
    } else {
        Write-Host "  Khong tim thay service HRM!" -ForegroundColor Red
        Write-Host "  Ban can restart Django bang tay."
    }
}
