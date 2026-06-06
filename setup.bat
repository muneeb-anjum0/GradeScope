@echo off
title GradeScope Setup
echo ==========================================
echo GradeScope Setup
echo ==========================================
echo.

python --version >nul 2>&1
IF ERRORLEVEL 1 (
    echo Python is not installed or not added to PATH.
    echo Install Python from https://www.python.org/downloads/
    echo During installation, enable: Add Python to PATH
    pause
    exit /b 1
)

echo Python found.
python --version
echo.

IF NOT EXIST ".venv" (
    echo Creating virtual environment...
    python -m venv .venv
) ELSE (
    echo Virtual environment already exists.
)

echo.
echo Activating virtual environment...
call .venv\Scripts\activate.bat

echo.
echo Upgrading pip...
python -m pip install --upgrade pip

echo.
echo Installing requirements...
pip install -r requirements.txt
IF ERRORLEVEL 1 (
    echo Failed to install requirements.
    pause
    exit /b 1
)

echo.
echo Installing Playwright browser...
python -m playwright install
IF ERRORLEVEL 1 (
    echo Failed to install Playwright browsers.
    pause
    exit /b 1
)

echo.
echo ==========================================
echo Setup complete.
echo Run start_gradescope.bat to launch GradeScope.
echo ==========================================
pause