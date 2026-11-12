@echo off
REM Gera e abre a visualização animada no navegador (não precisa de internet).
cd /d "%~dp0"
py -m interface.visualizacao
start "" "visualizacao.html"
