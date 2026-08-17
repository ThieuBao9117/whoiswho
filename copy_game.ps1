# =====================================================
# copy_game.ps1
# Copy frontend dist/ → Django project game/ folder
# (được serve bởi Django, không phải IIS trực tiếp)
# Chạy sau mỗi lần npm run build
# =====================================================

$src = 'C:\WHO\csbwhoiswho\frontend\dist'
$dst = 'C:\HRM_WEB\HRM_WEB\HRM_WEB\game'

if (-not (Test-Path $dst)) {
    New-Item -ItemType Directory -Path $dst -Force | Out-Null
    Write-Host "Created $dst"
}

Write-Host "Copying from $src to $dst ..."
Copy-Item -Path "$src\*" -Destination $dst -Recurse -Force
Write-Host "Copy done. Contents:"
Get-ChildItem $dst -Recurse | ForEach-Object { Write-Host "  $($_.FullName)" }
