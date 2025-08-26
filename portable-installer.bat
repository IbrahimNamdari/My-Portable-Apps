@echo off
rem -- This script builds the application using PyInstaller --

echo Cleaning up previous build...
rd /s /q build
rd /s /q dist

echo Building the application...
pyinstaller --onefile --windowed --clean --log-level=INFO ^
--name "MPA-Portable" ^
--icon="icon64px.ico" ^
--add-data "img;img" ^
--add-data "otherapps;otherapps" ^
--add-data "core/model/data/wifi_profiles.db;core/model/data" ^
main.py

echo Build process finished.
pause