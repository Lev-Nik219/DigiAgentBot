@echo off
chcp 65001 >nul
setlocal

echo Активирую виртуальное окружение...
call .\venv\Scripts\activate.bat

echo Запускаю DigiAgent бота...
python main.py

echo.
pause