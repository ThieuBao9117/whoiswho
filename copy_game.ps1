$src = 'C:\inetpub\wwwroot\game'
$dst = 'C:\HRM_WEB\HRM_WEB\HRM_WEB\game'

if (-not (Test-Path $dst)) {
    New-Item -ItemType Directory -Path $dst -Force | Out-Null
    Write-Host "Created $dst"
}

Write-Host "Copying from $src to $dst ..."
Copy-Item -Path "$src\*" -Destination $dst -Recurse -Force
Write-Host "Copy done. Contents:"
Get-ChildItem $dst -Recurse | ForEach-Object { Write-Host "  $($_.FullName)" }
