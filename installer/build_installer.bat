@echo off
chcp 65001 >nul
echo ========================================
echo    合同审查小助手 - 安装制作脚本
echo ========================================
echo.

REM 检查是否存在NSIS
where makensis >nul 2>&1
if errorlevel 1 (
    echo [提示] 未检测到NSIS，将创建便携版安装包
    echo       如需制作安装程序，请安装NSIS: https://nsis.sourceforge.io/
    echo.
    goto PORTABLE_VERSION
)

echo [检测] NSIS已安装，将制作专业安装程序
echo.

REM 创建NSIS脚本
echo !define APP_NAME "合同审查小助手" > installer.nsi
echo !define APP_VERSION "1.0.0" >> installer.nsi
echo !define APP_PUBLISHER "合同审查工具" >> installer.nsi
echo !define APP_EXE "合同审查小助手.exe" >> installer.nsi
echo. >> installer.nsi
echo ; 包含现代UI >> installer.nsi
echo !include "MUI2.nsh" >> installer.nsi
echo. >> installer.nsi
echo ; 安装程序属性 >> installer.nsi
echo Name "${APP_NAME}" >> installer.nsi
echo OutFile "合同审查小助手_安装程序.exe" >> installer.nsi
echo InstallDir "$PROGRAMFILES\${APP_NAME}" >> installer.nsi
echo InstallDirRegKey HKCU "Software\${APP_NAME}" "" >> installer.nsi
echo RequestExecutionLevel admin >> installer.nsi
echo. >> installer.nsi
echo ; 界面设置 >> installer.nsi
echo !define MUI_ABORTWARNING >> installer.nsi
echo !define MUI_ICON "assets\app_icon.ico" >> installer.nsi
echo !define MUI_UNICON "assets\app_icon.ico" >> installer.nsi
echo. >> installer.nsi
echo ; 安装页面 >> installer.nsi
echo !insertmacro MUI_PAGE_WELCOME >> installer.nsi
echo !insertmacro MUI_PAGE_LICENSE "LICENSE" >> installer.nsi
echo !insertmacro MUI_PAGE_COMPONENTS >> installer.nsi
echo !insertmacro MUI_PAGE_DIRECTORY >> installer.nsi
echo !insertmacro MUI_PAGE_INSTFILES >> installer.nsi
echo !insertmacro MUI_PAGE_FINISH >> installer.nsi
echo. >> installer.nsi
echo ; 卸载页面 >> installer.nsi
echo !insertmacro MUI_UNPAGE_WELCOME >> installer.nsi
echo !insertmacro MUI_UNPAGE_CONFIRM >> installer.nsi
echo !insertmacro MUI_UNPAGE_INSTFILES >> installer.nsi
echo !insertmacro MUI_UNPAGE_FINISH >> installer.nsi
echo. >> installer.nsi
echo ; 语言 >> installer.nsi
echo !insertmacro MUI_LANGUAGE "SimpChinese" >> installer.nsi
echo. >> installer.nsi
echo ; 安装段 >> installer.nsi
echo Section "主程序" SecMain >> installer.nsi
echo   SectionIn RO >> installer.nsi
echo   SetOutPath "$INSTDIR" >> installer.nsi
echo   File /r "dist\*.*" >> installer.nsi
echo   WriteRegStr HKCU "Software\${APP_NAME}" "" $INSTDIR >> installer.nsi
echo   CreateDirectory "$SMPROGRAMS\${APP_NAME}" >> installer.nsi
echo   CreateShortCut "$SMPROGRAMS\${APP_NAME}\${APP_NAME}.lnk" "$INSTDIR\${APP_EXE}" >> installer.nsi
echo   CreateShortCut "$DESKTOP\${APP_NAME}.lnk" "$INSTDIR\${APP_EXE}" >> installer.nsi
echo SectionEnd >> installer.nsi
echo. >> installer.nsi
echo ; 卸载段 >> installer.nsi
echo Section "Uninstall" >> installer.nsi
echo   Delete "$INSTDIR\${APP_EXE}" >> installer.nsi
echo   RMDir /r "$INSTDIR" >> installer.nsi
echo   Delete "$SMPROGRAMS\${APP_NAME}\${APP_NAME}.lnk" >> installer.nsi
echo   RMDir "$SMPROGRAMS\${APP_NAME}" >> installer.nsi
echo   Delete "$DESKTOP\${APP_NAME}.lnk" >> installer.nsi
echo   DeleteRegKey HKCU "Software\${APP_NAME}" >> installer.nsi
echo SectionEnd >> installer.nsi

echo [1/2] 生成NSIS安装脚本...
makensis installer.nsi

if errorlevel 1 (
    echo [错误] NSIS编译失败
    goto PORTABLE_VERSION
)

echo.
echo [2/2] 清理临时文件...
del installer.nsi

echo.
echo ========================================
echo    安装程序制作完成！
echo ========================================
echo.
echo 输出文件: 合同审查小助手_安装程序.exe
echo.
goto END

:PORTABLE_VERSION
echo ========================================
echo    制作便携版安装包
echo ========================================
echo.

if not exist "release" mkdir "release"
if not exist "release\便携版" mkdir "release\便携版"

echo [1/3] 复制程序文件...
xcopy /s /e /y "dist\*" "release\便携版\" >nul

echo [2/3] 创建启动脚本...
echo @echo off > "release\便携版\启动助手.bat"
echo chcp 65001 ^>nul >> "release\便携版\启动助手.bat"
echo echo 启动合同审查小助手... >> "release\便携版\启动助手.bat"
echo start "" "合同审查小助手.exe" >> "release\便携版\启动助手.bat"

echo [3/3] 创建说明文件...
echo 合同审查小助手 - 便携版 > "release\便携版\使用说明.txt"
echo. >> "release\便携版\使用说明.txt"
echo 1. 双击 "合同审查小助手.exe" 启动程序 >> "release\便携版\使用说明.txt"
echo 2. 或双击 "启动助手.bat" 启动 >> "release\便携版\使用说明.txt"
echo 3. 首次运行会自动创建配置文件 >> "release\便携版\使用说明.txt"
echo 4. 需要配置AI模型（本地Ollama或云端DeepSeek） >> "release\便携版\使用说明.txt"
echo. >> "release\便携版\使用说明.txt"
echo 详细文档请查看目录中的Markdown文件 >> "release\便携版\使用说明.txt"

echo.
echo ========================================
echo    便携版制作完成！
echo ========================================
echo.
echo 位置: release\便携版\
echo.

:END
pause
