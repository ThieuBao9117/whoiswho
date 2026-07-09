Get-Service | Where-Object { $_.Name -like "*HRM*" -or $_.Name -like "*waitress*" -or $_.Name -like "*django*" -or $_.Name -like "*CSB*" } | Format-Table Name, Status, DisplayName -AutoSize | Out-File C:\WHO\csbwhoiswho\hrm_restart.txt -Encoding UTF8

$svc = Get-Service -Name "HRMWeb" -ErrorAction SilentlyContinue
if ($svc) {
    "Found HRMWeb service - restarting..." | Out-File C:\WHO\csbwhoiswho\hrm_restart.txt -Append
    Restart-Service -Name "HRMWeb" -Force
    "Restarted" | Out-File C:\WHO\csbwhoiswho\hrm_restart.txt -Append
} else {
    "HRMWeb not found" | Out-File C:\WHO\csbwhoiswho\hrm_restart.txt -Append
    Get-Service | Format-Table Name, Status, DisplayName | Out-File C:\WHO\csbwhoiswho\hrm_restart.txt -Append
}
