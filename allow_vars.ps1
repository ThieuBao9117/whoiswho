$appcmd = "C:\Windows\System32\inetsrv\appcmd.exe"
& $appcmd set config -section:system.webServer/rewrite/allowedServerVariables /+"[name='HTTP_X_FORWARDED_HOST']" /commit:apphost
& $appcmd set config -section:system.webServer/rewrite/allowedServerVariables /+"[name='HTTP_X_FORWARDED_PROTO']" /commit:apphost
Write-Host "Server Variables Allowed."
