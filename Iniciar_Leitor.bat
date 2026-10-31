@echo off
chcp 65001 >nul
title Tensei Shitara Slime Datta Ken - Biblioteca Completa PT-BR
echo ======================================================================
echo   TENSEI SHITARA SLIME DATTA KEN - BIBLIOTECA COMPLETA PT-BR
echo   Light Novel (Volumes 1 a 20 + 8.5) e Web Novel (303 Capitulos)
echo ======================================================================
echo.
echo Iniciando servidor local em http://localhost:8080 ...
echo Mantenha esta janela aberta enquanto estiver lendo.
echo Pressione Ctrl+C para encerrar o servidor.
echo.
start "" "http://localhost:8080"
python -m http.server 8080
pause
