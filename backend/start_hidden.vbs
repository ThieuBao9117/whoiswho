Set WshShell = CreateObject("WScript.Shell")
WshShell.Run "cmd.exe /c C:\WHO\csbwhoiswho\backend\run_backend_service.bat", 0, False
