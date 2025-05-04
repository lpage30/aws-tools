@echo off
setlocal
pushd %~dp0
call :DEL_DIRS __pycache__
call :DEL_DIRS dist
call :DEL_DIRS build
call :DEL_DIRS egg-info
popd
GOTO :EOF

:DEL_DIRS
for /r /d %%d in (*) do (
  echo "%%d" | findstr %1 1>nul && (
     echo "rmdir /s /q %%d"
     rmdir /s /q %%d
  )
)
GOTO :EOF
endlocal