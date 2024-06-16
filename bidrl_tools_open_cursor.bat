@echo off
cd %~dp0
powershell.exe -Command "Set-Location -LiteralPath '%~dp0'; cursor .; exit"
exit