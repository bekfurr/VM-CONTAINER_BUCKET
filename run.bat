@echo off
echo VM-Container Bucket ishga tushmoqda...
echo.

REM Python mavjudligini tekshirish
python --version >nul 2>&1
if errorlevel 1 (
    echo Xatolik: Python o'rnatilmagan!
    echo Iltimos, Python 3.7+ ni o'rnating: https://python.org
    pause
    exit /b 1
)

REM Kerakli paketlarni o'rnatish
echo Kerakli paketlar o'rnatilmoqda...
pip install -r requirements.txt

REM Dasturni ishga tushirish
echo.
echo Dastur ishga tushmoqda...
python main.py

pause
