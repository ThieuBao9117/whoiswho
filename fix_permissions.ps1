$gamePath = "C:\inetpub\wwwroot\game"
$indexFile = "$gamePath\index.html"

"=== Kiem tra quyền file ===" | Out-File C:\WHO\csbwhoiswho\iis_result.txt
(Get-Acl $indexFile).Access | Format-Table IdentityReference, FileSystemRights, AccessControlType -AutoSize | Out-File C:\WHO\csbwhoiswho\iis_result.txt -Append

"`n=== Them quyen doc cho IIS_IUSRS ===" | Out-File C:\WHO\csbwhoiswho\iis_result.txt -Append
$acl = Get-Acl $gamePath
$rule = New-Object System.Security.AccessControl.FileSystemAccessRule("IIS_IUSRS", "ReadAndExecute", "ContainerInherit,ObjectInherit", "None", "Allow")
$acl.SetAccessRule($rule)
Set-Acl -Path $gamePath -AclObject $acl
"Quyen da duoc cap cho IIS_IUSRS" | Out-File C:\WHO\csbwhoiswho\iis_result.txt -Append

# Recycle app pool
$appcmd = "C:\Windows\System32\inetsrv\appcmd.exe"
& $appcmd recycle apppool /apppool.name:DefaultAppPool 2>&1 | Out-File C:\WHO\csbwhoiswho\iis_result.txt -Append
"Done" | Out-File C:\WHO\csbwhoiswho\iis_result.txt -Append
