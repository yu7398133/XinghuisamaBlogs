@echo off
chcp 65001 >nul 2>&1
cd /d "%~dp0"

echo 🌟 星辉云端·控制台 (Web 模式)
echo.

:: 优先尝试 py -3.10
py -3.10 --version >nul 2>&1
if %errorlevel% equ 0 (
    echo [状态] 正在调用 Python 3.10...
    py -3.10 start_web.py
    goto end
)

:: 尝试 python
python --version >nul 2>&1
if %errorlevel% equ 0 (
    for /f "tokens=2 delims=." %%i in ('python --version 2^>^&1') do set "py_major=%%i"
    for /f "tokens=3 delims=. " %%j in ('python --version 2^>^&1') do set "py_minor=%%j"
    if %py_major% equ 3 if %py_minor% geq 10 (
        echo [状态] 正在调用 Python 3.10+...
        python start_web.py
        goto end
    )
)

echo ❌ 未找到 Python 3.10+，请先安装！
pause

:end
echo ✅ 程序已退出
exit /b 0
