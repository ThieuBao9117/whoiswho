$appcmd = "C:\Windows\System32\inetsrv\appcmd.exe"

# Tao noi dung web.config moi - dung URL relative 'index.html' thay vi '/game/index.html'
$content = @'
<?xml version="1.0" encoding="UTF-8"?>
<configuration>
  <system.webServer>
    <defaultDocument>
      <files>
        <clear />
        <add value="index.html" />
      </files>
    </defaultDocument>
    <staticContent>
      <remove fileExtension=".js" />
      <mimeMap fileExtension=".js" mimeType="application/javascript" />
      <remove fileExtension=".css" />
      <mimeMap fileExtension=".css" mimeType="text/css" />
      <remove fileExtension=".json" />
      <mimeMap fileExtension=".json" mimeType="application/json" />
      <remove fileExtension=".woff2" />
      <mimeMap fileExtension=".woff2" mimeType="font/woff2" />
      <remove fileExtension=".webp" />
      <mimeMap fileExtension=".webp" mimeType="image/webp" />
    </staticContent>
    <rewrite>
      <rules>
        <rule name="SPA Fallback" stopProcessing="true">
          <match url=".*" />
          <conditions logicalGrouping="MatchAll">
            <add input="{REQUEST_FILENAME}" matchType="IsFile" negate="true" />
            <add input="{REQUEST_FILENAME}" matchType="IsDirectory" negate="true" />
          </conditions>
          <action type="Rewrite" url="index.html" />
        </rule>
      </rules>
    </rewrite>
    <directoryBrowse enabled="false" />
    <httpErrors existingResponse="PassThrough" />
  </system.webServer>
</configuration>
'@

[System.IO.File]::WriteAllText("C:\inetpub\wwwroot\game\web.config", $content, [System.Text.Encoding]::UTF8)
"web.config updated - SPA rewrite url changed to 'index.html' (relative)" | Out-File C:\WHO\csbwhoiswho\iis_result.txt

# Restart app pool de ap dung
& $appcmd recycle apppool /apppool.name:DefaultAppPool 2>&1 | Out-File C:\WHO\csbwhoiswho\iis_result.txt -Append
"AppPool recycled" | Out-File C:\WHO\csbwhoiswho\iis_result.txt -Append
