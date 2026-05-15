@echo off
REM Batch wrapper for YAML type field fixer
REM Double-click this file to run the fixer

cd /d "%~dp0\.."
python Python\fix_yaml_types.py
pause
