@echo off
python -m pip uninstall aws-tools --break-system-packages
call %~dp0clean.bat
