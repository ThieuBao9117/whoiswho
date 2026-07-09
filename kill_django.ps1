$proc = netstat -ano | Select-String ":8000" | Select-String "LISTENING"
Write-Host "Found: $proc"
if ($proc) {
    # Get the last token (PID)
    $lines = $proc -split "`n"
    foreach ($line in $lines) {
        if ($line.Trim() -ne "") {
            $parts = $line.Trim() -split "\s+"
            $pidToKill = $parts[-1]
            Write-Host "Killing PID: $pidToKill"
            Stop-Process -Id $pidToKill -Force -ErrorAction SilentlyContinue
        }
    }
}
Write-Host "Done."
