@echo off
rem -- This script builds the application using PyInstaller --

echo Cleaning up previous build...
rem -- Delete the existing build and dist folders
rd /s /q build
rd /s /q dist

echo Building the application...
rem -- The --distpath flag is added to specify the output directory for the executable
pyinstaller --onefile --windowed --clean --log-level=INFO ^
--distpath="release" ^
--name "MPA-Portable" ^
--icon="img/mpas.ico" ^
--add-data "img;img" ^
--add-data "otherapps;otherapps" ^
--add-data "core/model/data/wifi_profiles.db;core/model/data" ^
main.py

echo Build process finished.
pause
