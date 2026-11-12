@echo off
REM Roda todos os testes do projeto. Basta dar dois cliques neste arquivo.
cd /d "%~dp0"
py -m unittest discover -s testes -t . -v
echo.
pause
