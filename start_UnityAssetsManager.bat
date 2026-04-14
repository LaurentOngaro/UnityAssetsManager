@echo off
setlocal

cd /d "%~dp0"

set "PYTHON_CMD="
set "PYTHON_ARGS="

where python >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    set "PYTHON_CMD=python"
) else (
    where py >nul 2>&1
    if %ERRORLEVEL% EQU 0 (
        set "PYTHON_CMD=py"
        set "PYTHON_ARGS=-3"
    )
)

if not defined PYTHON_CMD (
    echo [ERROR] Python not found.
    echo Install Python 3 or add it to PATH.
    pause
    exit /b 1
)

echo [INFO] Using Python from PATH
if defined PYTHON_ARGS (
    %PYTHON_CMD% %PYTHON_ARGS% --version
    if errorlevel 1 goto :python_error
    %PYTHON_CMD% %PYTHON_ARGS% -m pip install -q -r requirements.txt
) else (
    %PYTHON_CMD% --version
    if errorlevel 1 goto :python_error
    %PYTHON_CMD% -m pip install -q -r requirements.txt
)
if errorlevel 1 goto :pip_error

echo [INFO] Starting UnityAssetsManager
if defined PYTHON_ARGS (
    %PYTHON_CMD% %PYTHON_ARGS% app.py
) else (
    %PYTHON_CMD% app.py
)

set EXIT_CODE=%ERRORLEVEL%
if not "%EXIT_CODE%"=="0" (
    echo.
    echo [WARN] App exited with code %EXIT_CODE%.
    pause
)

exit /b %EXIT_CODE%

:python_error
echo [ERROR] Python is available but could not start.
pause
exit /b 1

:pip_error
echo [ERROR] Failed to install dependencies from requirements.txt.
pause
exit /b 1
