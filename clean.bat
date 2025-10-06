@echo off
REM Clean Script for Video Enhancement Frames
REM This script directly deletes contents of tmp_frames and out_frames folders

title Cleaning Frames

echo Cleaning tmp_frames folder...
if exist "tmp_frames\" (
    del /q "tmp_frames\*" >nul 2>&1
    for /d %%i in ("tmp_frames\*") do rmdir /q "%%i" >nul 2>&1
    echo Done.
) else (
    echo tmp_frames folder does not exist.
)

echo Cleaning out_frames folder...
if exist "out_frames\" (
    del /q "out_frames\*" >nul 2>&1
    for /d %%i in ("out_frames\*") do rmdir /q "%%i" >nul 2>&1
    echo Done.
) else (
    echo out_frames folder does not exist.
)

echo.
echo Cleanup completed!