@echo off
setlocal
cd /d "%~dp0" || exit /b 1
py src\repl.py --rpc %*
set "APP_EXIT=%ERRORLEVEL%"
pause
exit /b %APP_EXIT%
