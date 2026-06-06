@echo off
title GradeScope Portal
echo ==========================================
echo Starting GradeScope Portal
echo ==========================================
echo.

IF NOT EXIST ".venv\Scripts\activate.bat" (
    echo Virtual environment not found.
    echo Run setup.bat first.
    pause
    exit /b 1
)

call .venv\Scripts\activate.bat

IF NOT EXIST "app.py" (
    echo app.py not found.
    echo Make sure you are running this file from the GradeScope project folder.
    pause
    exit /b 1
)

echo Opening GradeScope in your browser...
echo.
streamlit run app.py

pause