@echo off
REM refresh_indexes.bat — Rebuilds all corpus indexes in dependency order.
REM Sequential execution: each step must succeed before the next runs.
REM Double-click from Python/ in Explorer to run.

setlocal
cd /d "%~dp0"

echo.
echo === [1/3] Mapping directory (compressed)...
python map_directory.py --no-pause
if errorlevel 1 (
    echo.
    echo [FAIL] map_directory.py exited with errors.
    pause
    exit /b 1
)

echo.
echo === [2/3] Mapping directory (with files)...
python map_directory_with_files.py --no-pause
if errorlevel 1 (
    echo.
    echo [FAIL] map_directory_with_files.py exited with errors.
    pause
    exit /b 1
)

echo.
echo === [3/3] Building search index...
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
