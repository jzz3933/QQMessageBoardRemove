@echo off

:start

python ./DeleteMessage2.py

choice /t 5 /d y /n >nul

goto start