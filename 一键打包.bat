@echo off
chcp 65001 >nul
title 合同审查小助手 - 一键打包工具

echo.
echo ========================================
echo    合同审查小助手 - 一键打包工具
echo ========================================
echo.
echo 此工具将自动完成所有打包步骤
echo.

REM 检查Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到Python
    echo.
    echo 请先安装Python 3.8或更高版本
    echo 下载地址: https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

echo [检查] Python环境
python --version

REM 检查必要文件
if not exist "launch.py" (
    echo [错误] 未找到 launch.py
    echo 请确保在项目根目录运行此脚本
    pause
    exit /b 1
)

if not exist "build.spec" (
    echo [错误] 未找到 build.spec
    pause
    exit /b 1
)

echo [检查] 项目文件... OK
echo.

REM 询问打包方式
echo 请选择打包方式:
echo.
echo 1. 快速打包 - 仅生成exe文件 (推荐测试用)
echo 2. 完整打包 - 生成便携版和安装程序 (推荐发布用)
echo.
set /p choice="请输入选择 (1 或 2): "

if "%choice%"=="1" goto QUICK_BUILD
if "%choice%"=="2" goto FULL_BUILD

echo [错误] 无效的选择
pause
exit /b 1

:QUICK_BUILD
echo.
echo ========================================
echo    快速打包模式
echo ========================================
echo.

REM 安装依赖
echo [1/3] 安装打包工具...
pip install pyinstaller==6.3.0 -i https://pypi.tuna.tsinghua.edu.cn/simple

echo [2/3] 安装项目依赖...
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

echo [3/3] 开始打包...
pyinstaller build.spec --clean --noconfirm

if errorlevel 1 (
    echo.
    echo [错误] 打包失败
    pause
    exit /b 1
)

echo.
echo ========================================
echo    打包完成！
echo ========================================
echo.
echo 可执行文件: dist\合同审查小助手.exe
echo.
echo 提示:
echo - 双击运行测试
echo - 可以直接分发此文件
echo - 用户首次运行会自动创建配置
echo.
pause
exit /b 0

:FULL_BUILD
echo.
echo ========================================
echo    完整打包模式
echo ========================================
echo.

REM 调用完整打包脚本
if not exist "installer\build_all.bat" (
    echo [错误] 未找到 installer\build_all.bat
    echo 请确保项目文件完整
    pause
    exit /b 1
)

call installer\build_all.bat

echo.
echo ========================================
echo    全部完成！
echo ========================================
echo.
echo 发布文件已准备好，可以分发给用户
echo.
pause
exit /b 0
