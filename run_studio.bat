@echo off
REM ---------------------------------------------------------------------------
REM  run_studio.bat – launch Stride Studio on Windows
REM ---------------------------------------------------------------------------

REM 1.  Activate Conda environment (edit name/path if needed)
echo Activating Conda environment "Stride_Studio"…
call activate Stride_Studio
if %errorlevel% neq 0 (
    echo ERROR: Failed to activate environment "Stride_Studio".
    pause
    exit /b 1
)

REM 2.  Start the GUI (package entry-point)
REM     Change directory to the script's location first
cd /d %~dp0
echo Starting Stride Studio…
python __main__.py %*

REM 3.  Done
echo.
echo Application finished.
REM pause  ←-uncomment to keep the window open after exit
