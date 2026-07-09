Write-Host "=== Tim process Django (waitress) :8000 ===" -ForegroundColor Cyan
$proc = netstat -ano | Select-String ":8000 " | Select-Object -First 3
Write-Host $proc

Write-Host ""
Write-Host "=== Tim PID cua waitress/python ===" -ForegroundColor Cyan
Get-Process | Where-Object { $_.Name -like "*python*" -or $_.Name -like "*waitress*" } | 
    Format-Table Id, Name, CPU, @{N='Mem(MB)';E={[math]::Round($_.WorkingSet64/1MB,1)}} -AutoSize
