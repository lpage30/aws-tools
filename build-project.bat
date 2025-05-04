@echo off
pushd %~dp0
call clean.bat
python -m build
popd