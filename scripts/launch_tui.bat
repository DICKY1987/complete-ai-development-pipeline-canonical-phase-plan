@echo off
REM AI Pipeline TUI Launcher
REM Launches the Textual-based TUI for pipeline monitoring

REM Set working directory to project root
cd /d "%~dp0.."

REM Set window title
title AI Pipeline TUI - Monitoring Dashboard

REM Activate virtual environment if exists
if exist ".venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call .venv\Scripts\activate.bat
)

REM Display startup message
echo.
echo ========================================
echo   AI Pipeline TUI - Starting...
echo ========================================
echo.
echo Press 'q' to quit
echo Press 'r' to refresh
echo Press 'd' for Dashboard
echo Press 'f' for Files
echo Press 't' for Tools
echo Press 'l' for Logs
echo Press 'p' for Patterns
echo.

REM Launch TUI
python -m gui.tui_app.main

REM Check exit code and keep window open on error
if errorlevel 1 (
    echo.
    echo ========================================
    echo   [ERROR] TUI crashed
    echo ========================================
    echo.
    echo Exit code: %ERRORLEVEL%
    echo Check logs above for details.
    echo.
    pause
)

REM Normal exit - window closes automatically
