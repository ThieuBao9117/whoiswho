# apply_iis_config.ps1
# Chay tren SERVER voi quyen Administrator
# Muc dich: Them URL Rewrite rules cho /game/ vao IIS web.config cua HRM site

param(
    # Duong dan toi web.config cua HRM site tren server
    # Vi du: D:\WHO\web.config hoac C:\inetpub\wwwroot\hrm\web.config
    [string]$WebConfigPath = ""
)

Write-Host "=== CSB Game - Apply IIS URL Rewrite Rules ===" -ForegroundColor Cyan

# --- Tim web.config neu khong truyen tham so ---
if (-not $WebConfigPath) {
    # Thu cac duong dan pho bien
    $candidates = @(
        "C:\code\HRM\HRM_WEB\web.config",
        "D:\WHO\web.config",
        "C:\inetpub\wwwroot\web.config",
        "C:\inetpub\wwwroot\hrm\web.config",
        "D:\inetpub\wwwroot\web.config"
    )
    foreach ($c in $candidates) {
        if (Test-Path $c) {
            $WebConfigPath = $c
            Write-Host "Tim thay web.config: $c" -ForegroundColor Green
            break
        }
    }
}

if (-not $WebConfigPath -or -not (Test-Path $WebConfigPath)) {
    Write-Host "CANH BAO: Khong tim thay web.config tu dong." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Nhap duong dan day du toi web.config cua HRM site:"
    $WebConfigPath = Read-Host "  > "
    if (-not (Test-Path $WebConfigPath)) {
        Write-Host "LOI: File khong ton tai: $WebConfigPath" -ForegroundColor Red
        exit 1
    }
}

Write-Host "Dang xu ly: $WebConfigPath" -ForegroundColor White

# --- Doc file hien tai ---
[xml]$config = Get-Content $WebConfigPath -Encoding UTF8
$backup = $WebConfigPath -replace "\.config$", "_backup_$(Get-Date -Format 'yyyyMMdd_HHmmss').config"
Copy-Item $WebConfigPath $backup
Write-Host "Da backup: $backup" -ForegroundColor Gray

# --- Kiem tra xem rules da co chua ---
$existingRules = $config.SelectNodes("//rule[@name='CSB API Reverse Proxy']")
if ($existingRules.Count -gt 0) {
    Write-Host "Rules CSB da ton tai. Dang cap nhat..." -ForegroundColor Yellow
    foreach ($r in $existingRules) { $r.ParentNode.RemoveChild($r) | Out-Null }
}

# --- Lay hoac tao node rewrite/rules ---
$systemWeb = $config.SelectSingleNode("//system.webServer")
if (-not $systemWeb) {
    $systemWeb = $config.CreateElement("system.webServer")
    $config.configuration.AppendChild($systemWeb) | Out-Null
}

$rewrite = $config.SelectSingleNode("//rewrite")
if (-not $rewrite) {
    $rewrite = $config.CreateElement("rewrite")
    $systemWeb.AppendChild($rewrite) | Out-Null
}

$rules = $config.SelectSingleNode("//rewrite/rules")
if (-not $rules) {
    $rules = $config.CreateElement("rules")
    $rewrite.AppendChild($rules) | Out-Null
}

# --- Them 3 rules CSB (dat o dau, truoc rule Django) ---
$newRulesXml = @"
<root>
  <rule name="CSB API Reverse Proxy" stopProcessing="true">
    <match url="^game/api/(.*)" />
    <action type="Rewrite" url="http://localhost:7000/api/{R:1}" appendQueryString="true" />
    <!--
    <serverVariables>
      <set name="HTTP_X_FORWARDED_HOST" value="50.50.50.4" />
    </serverVariables>
    -->
  </rule>
  <rule name="CSB Static Assets" stopProcessing="true">
    <match url="^game/assets/(.*)" />
    <conditions>
      <add input="{REQUEST_FILENAME}" matchType="IsFile" />
    </conditions>
    <action type="None" />
  </rule>
  <rule name="CSB Game SPA Fallback" stopProcessing="true">
    <match url="^game(/.*)?$" />
    <conditions logicalGrouping="MatchAll">
      <add input="{REQUEST_FILENAME}" matchType="IsFile" negate="true" />
      <add input="{REQUEST_FILENAME}" matchType="IsDirectory" negate="true" />
    </conditions>
    <action type="Rewrite" url="/game/index.html" />
  </rule>
</root>
"@

[xml]$newRules = $newRulesXml

# Chen vao dau danh sach (truoc cac rule hien co)
$firstChild = $rules.FirstChild
foreach ($rule in $newRules.root.ChildNodes) {
    $imported = $config.ImportNode($rule, $true)
    if ($firstChild) {
        $rules.InsertBefore($imported, $firstChild) | Out-Null
    } else {
        $rules.AppendChild($imported) | Out-Null
    }
    $firstChild = $rules.FirstChild  # update reference
}

# --- Kiem tra proxy ---
$proxy = $config.SelectSingleNode("//system.webServer/proxy")
if (-not $proxy) {
    $proxy = $config.CreateElement("proxy")
    $proxy.SetAttribute("enabled", "true")
    $proxy.SetAttribute("preserveHostHeader", "true")
    $systemWeb.AppendChild($proxy) | Out-Null
}

# --- Luu file ---
$config.Save($WebConfigPath)
Write-Host ""
Write-Host "=== THANH CONG ===" -ForegroundColor Green
Write-Host "Da them 3 rules CSB vao: $WebConfigPath"
Write-Host ""
Write-Host "Dang reset IIS de ap dung thay doi..."
iisreset /noforce 2>&1 | Write-Host
Write-Host ""
Write-Host "Test:"
Write-Host "  http://50.50.50.4/game/        -> Giao dien CSB Game"
Write-Host "  http://50.50.50.4/game/api/    -> CSB API"
