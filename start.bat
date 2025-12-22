@echo off
chcp 65001 >nul
title FinQuery - 金融数据智能查询助手

echo ==============================================
echo    FinQuery - 金融数据智能查询助手
echo ==============================================
echo.

REM 检查 Python 环境
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo 错误: 未找到 Python，请先安装 Python
    pause
    exit /b 1
)

REM 获取脚本所在目录
cd /d "%~dp0"

REM 检查是否需要安装依赖
if not exist ".deps_installed" (
    echo 首次运行，正在安装依赖...
    pip install -r requirements.txt
    if %errorlevel% equ 0 (
        echo. > .deps_installed
        echo 依赖安装完成！
    ) else (
        echo 依赖安装失败，请手动运行: pip install -r requirements.txt
        pause
        exit /b 1
    )
)

REM 检查 .env 文件
if not exist "src\.env" (
    echo 警告: 未找到 src\.env 文件
    echo 请创建 src\.env 并添加: DEEPSEEK_API_KEY=your_api_key
    pause
    exit /b 1
)

echo.
echo 正在启动服务...
echo Web 界面地址: http://localhost:5000
echo.
echo 按 Ctrl+C 停止服务
echo ==============================================
echo.

REM 启动 Flask 服务
cd src
python ..\backend\app.py

pause
