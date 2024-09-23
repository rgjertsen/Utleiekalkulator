@echo off
REM Slett gamle build- og dist-mapper samt .spec-filen
IF EXIST build (
    rmdir /s /q build
)
IF EXIST dist (
    rmdir /s /q dist
)
IF EXIST Utleiekalkulator.spec (
    del /q Utleiekalkulator.spec
)

REM Kjør PyInstaller med spesifikt navn og ikon
python -m PyInstaller --onefile --windowed --name "Utleiekalkulator" --icon="C:\Users\Reidar\Desktop\Utleiekalkulator\icon.ico" utleiekalkulator.py

REM Flytt den kjørbare filen til ønsket sted (valgfritt)
IF EXIST "dist\Utleiekalkulator.exe" (
    move /y "dist\Utleiekalkulator.exe" .
)

REM Slett build- og dist-mapper samt .spec-filen etter bygging for å rydde opp
IF EXIST build (
    rmdir /s /q build
)
IF EXIST dist (
    rmdir /s /q dist
)
IF EXIST Utleiekalkulator.spec (
    del /q Utleiekalkulator.spec
)

echo Bygging fullført!

