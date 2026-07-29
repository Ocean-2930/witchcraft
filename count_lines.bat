@echo off
setlocal

set "LINE_COUNT_ROOT=%~dp0"

for /f "usebackq delims=" %%L in (`powershell.exe -NoProfile -Command "$root = $env:LINE_COUNT_ROOT; $files = Get-ChildItem -LiteralPath $root -Recurse -File -Filter '*.py' | Where-Object { $_.FullName -notmatch '[\\/](\.git|\.venv|__pycache__)[\\/]' }; $total = ($files | Get-Content -Encoding UTF8 | Measure-Object -Line).Lines; if ($null -eq $total) { 0 } else { $total }"`) do set "TOTAL_LINES=%%L"

if not defined TOTAL_LINES set "TOTAL_LINES=0"

echo total lines: %TOTAL_LINES%
echo.
set /p "=press enter to exit" <nul
set /p "LINE_COUNT_EXIT="

endlocal
