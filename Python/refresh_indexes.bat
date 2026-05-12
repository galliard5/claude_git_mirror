@echo off
REM refresh_indexes.bat — Rebuilds all corpus indexes in dependency order.
REM Sequential execution: each step must succeed before the next runs.
REM Double-click from Python/ in Explorer to run.

setlocal
cd /d "%~dp0"

echo.
echo === Building directory and search indexes (all files from one walk)...
python D:\Claude_MCP_folder\Python\build_indexes.py --no-pause
if errorlevel 1 (
    echo.
    echo [FAIL] build_indexes.py exited with errors.
    pause
    exit /b 1
)

echo.
echo === All indexes refreshed successfully.
echo.
pause
