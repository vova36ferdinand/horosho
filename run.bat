@echo off
setlocal
cd /d "%~dp0" || (echo ERROR: Cannot enter project folder.& pause & exit /b 1)
title Project launcher

 echo ==========================================
 echo        PROJECT TESTS AND COVERAGE
 echo ==========================================

where py >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python Launcher 'py' was not found.
    echo Install Python and enable the Python Launcher option.
    pause
    exit /b 1
)

py -c "import pytest, hypothesis, coverage" >nul 2>&1
if errorlevel 1 (
    echo Installing required packages...
    py -m pip install pytest hypothesis coverage
    if errorlevel 1 (
        echo ERROR: Package installation failed. Check your internet connection.
        pause
        exit /b 1
    )
)

echo.
echo Running tests...
py -m coverage erase
py -m coverage run --branch -m pytest -vv -s
if errorlevel 1 (
    echo.
    echo TESTS FAILED. The menu will not be started.
    pause
    exit /b 1
)

echo.
echo Coverage report:
py -m coverage report -m
if errorlevel 1 (
    echo ERROR: Could not generate coverage report.
    pause
    exit /b 1
)

echo.
echo Starting application menu...
py src\repl.py
set "APP_EXIT=%ERRORLEVEL%"
echo.
echo Application closed. Exit code: %APP_EXIT%
pause
exit /b %APP_EXIT%
