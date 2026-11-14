@echo off
REM Abre o jogo no navegador. Nao precisa de internet.
cd /d "%~dp0"
py -m interface.jogo_web
start "" "jogo.html"
