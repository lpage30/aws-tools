@echo off
pushd %~dp0
call build-project.bat
python -m pip install -e . --break-system-packages
