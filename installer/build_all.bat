@echo off
chcp 65001 >nul
echo ========================================
echo    合同审查小助手 - 完整打包流程
echo ========================================
echo.
echo 此脚本将执行完整的打包和安装程序制作流程
echo.

REM 检查Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到Python
    pause
    exit /b 1
)

echo [阶段 1/2] 打包可执行文件...
echo ----------------------------------------
call build_windows.bat

if errorlevel 1 (
    echo [错误] 打包失败
    pause
    exit /b 1
)

echo.
echo [阶段 2/2] 制作安装程序...
echo ----------------------------------------

if not exist "installer" (
    echo [错误] installer 文件夹不存在
    pause
    exit /b 1
)

cd installer
call build_installer.bat
cd ..

echo.
echo ========================================
echo    全部完成！
echo ========================================
echo.
echo 输出文件:
if exist "合同审查小助手_安装程序.exe" (
    echo ✓ 合同审查小助手_安装程序.exe
)
if exist "release\便携版" (
    echo ✓ release\便携版\
)
echo.
echo 可以分发这些文件给用户使用
echo.
pause
