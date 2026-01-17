@echo off
chcp 65001 >nul
echo ========================================
echo    合同审查小助手 - Windows打包脚本
echo ========================================
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到Python，请先安装Python 3.8+
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [1/6] 检查Python环境...
python --version

echo.
echo [2/6] 安装打包依赖...
pip install pyinstaller==6.3.0

echo.
echo [3/6] 安装项目依赖...
pip install -r requirements.txt

echo.
echo [4/6] 清理旧的打包文件...
if exist "dist" rmdir /s /q dist
if exist "build" rmdir /s /q build

echo.
echo [5/6] 开始打包（这可能需要几分钟）...
pyinstaller build.spec --clean

if errorlevel 1 (
    echo.
    echo [错误] 打包失败！
    pause
    exit /b 1
)

echo.
echo [6/6] 复制配置文件...
if not exist "dist\配置文件" mkdir "dist\配置文件"
copy .env.example "dist\配置文件\.env.example" >nul
copy INSTALL.md "dist\安装说明.md" >nul
copy README.md "dist\使用说明.md" >nul

echo.
echo ========================================
echo    打包完成！
echo ========================================
echo.
echo 可执行文件位置: dist\合同审查小助手.exe
echo.
echo 说明:
echo 1. 首次运行会自动创建配置文件
echo 2. 需要配置AI模型（本地Ollama或云端DeepSeek）
echo 3. 详细说明请查看: dist\安装说明.md
echo.
pause
