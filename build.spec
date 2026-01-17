# -*- mode: python ; coding: utf-8 -*-
"""
合同审查小助手 - PyInstaller打包配置
用于将应用打包为独立的可执行文件
"""
import os
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# 项目根目录
project_dir = os.path.getcwd()

# 收集所有需要的数据文件
datas = [
    ('.env.example', '.'),  # 配置模板
    ('assets', 'assets'),    # 资源文件
]

# 收集隐藏导入
hiddenimports = [
    'PySide6.QtCore',
    'PySide6.QtGui',
    'PySide6.QtWidgets',
    'docxtpl',
    'jinja2',
    'python_dotenv',
    'openai',
    'langchain',
    'langchain_openai',
    'langchain_community',
    'requests',
    'pydantic',
    'PIL',
    'fitz',
    'docx',
    'reportlab',
]

# 收集所有数据文件
datas += collect_data_files('docxtpl')
datas += collect_data_files('jinja2')

block_cipher = None

a = Analysis(
    ['launch.py'],  # 入口文件
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='合同审查小助手',  # 可执行文件名
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,  # 使用UPX压缩
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # 不显示控制台窗口
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # 如果有图标文件，在这里指定
)
