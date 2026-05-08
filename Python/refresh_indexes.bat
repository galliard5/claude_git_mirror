@echo off
REM refresh_indexes.bat — Rebuilds all corpus indexes in dependency order.
REM Sequential execution: each step must succeed before the next runs.
REM Double-click from Python/ in Explorer to run.

setlocal
cd /d "%~dp0"

echo.
echo === [1/2] Building directory indexes (both files from one walk)...
python build_directory_indexes.py --no-pause
if errorlevel 1 (
    echo.
    echo [FAIL] build_directory_indexes.py exited with errors.
    pause
    exit /b 1
)

echo.
echo === [2/2] Building search index...
python build_search_index.py --no-pause
if errorlevel 1 (
    echo.
    echo [FAIL] build_search_index.py exited with errors.
    pause
    exit /b 1
)

echo.
echo === All indexes refreshed successfully.
echo.
pause
