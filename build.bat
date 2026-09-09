@echo off
REM Build script for SudokuMaster executable
REM Usage: build.bat

echo Building SudokuMaster.exe ...

pyinstaller build.spec --clean

if errorlevel 1 (
    echo Build FAILED!
    pause
    exit /b 1
)

echo.
echo Build SUCCESS!
echo Executable location: dist\SudokuMaster.exe
echo.
pause