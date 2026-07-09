$appcmd = "C:\Windows\System32\inetsrv\appcmd.exe"

"=== appcmd list site ===" | Out-File C:\WHO\csbwhoiswho\iis_result.txt
& $appcmd list site 2>&1 | Out-File C:\WHO\csbwhoiswho\iis_result.txt -Append

"`n=== appcmd list app ===" | Out-File C:\WHO\csbwhoiswho\iis_result.txt -Append
& $appcmd list app 2>&1 | Out-File C:\WHO\csbwhoiswho\iis_result.txt -Append

"`n=== appcmd list vdir ===" | Out-File C:\WHO\csbwhoiswho\iis_result.txt -Append
& $appcmd list vdir 2>&1 | Out-File C:\WHO\csbwhoiswho\iis_result.txt -Append

"`n=== web.config game ===" | Out-File C:\WHO\csbwhoiswho\iis_result.txt -Append
Get-Content "C:\inetpub\wwwroot\game\web.config" -ErrorAction SilentlyContinue | Out-File C:\WHO\csbwhoiswho\iis_result.txt -Append

"Done" | Out-File C:\WHO\csbwhoiswho\iis_result.txt -Append
