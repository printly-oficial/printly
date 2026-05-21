@echo off
title Printly - Servidor local
 
echo Iniciando API de Printly...
start "Printly API" cmd /k "python C:\printly_gcodes\printly_api.py"
 
timeout /t 2 /nobreak > nul
 
echo Iniciando ngrok...
start "Printly ngrok" cmd /k "ngrok http --domain=epilepsy-overuse-underpaid.ngrok-free.dev 5000"
 
echo.
echo Printly arrancado correctamente.
echo URL fija: https://epilepsy-overuse-underpaid.ngrok-free.dev
pause