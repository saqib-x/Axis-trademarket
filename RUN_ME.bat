@echo off
REM APS One-Click Runner
setlocal
set ENGINE_DIR=%~dp0engine
set CSV=%~dp0input\test.csv

if not exist "%CSV%" (
  echo [ERROR] Missing input\test.csv
  echo Put a small CSV named test.csv into the input folder, then run again.
  pause
  exit /b 1
)

where py >nul 2>nul
if %errorlevel%==0 (
  py "%ENGINE_DIR%\aps_pipeline.py" "%CSV%"
) else (
  python "%ENGINE_DIR%\aps_pipeline.py" "%CSV%"
)
echo.
echo ===== Open APS_Market_Intelligence_Live\test_DEMO.pdf to view the report =====
pause
