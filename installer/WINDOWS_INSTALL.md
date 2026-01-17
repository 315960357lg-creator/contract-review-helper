# 合同审查小助手 - Windows打包说明

## 打包前准备

### 1. 安装必要工具

#### Python环境
- 下载并安装 Python 3.8 或更高版本
- https://www.python.org/downloads/
- 安装时勾选 "Add Python to PATH"

#### Git（可选）
- 用于版本控制
- https://git-scm.com/download/win

### 2. 克隆或下载项目
```bash
git clone <项目地址>
cd 审查合同助手
```

或直接下载ZIP压缩包并解压。

## 打包步骤

### 方法一：快速打包（推荐）

1. **双击运行 `build_windows.bat`**
   - 会自动安装依赖
   - 自动执行打包
   - 生成独立可执行文件

2. **等待打包完成**
   - 打包过程可能需要 5-10 分钟
   - 完成后可执行文件在 `dist` 文件夹

3. **测试可执行文件**
   ```bash
   cd dist
   合同审查小助手.exe
   ```

### 方法二：手动打包

如果自动脚本失败，可以手动执行：

```bash
# 1. 安装打包工具
pip install pyinstaller==6.3.0

# 2. 安装项目依赖
pip install -r requirements.txt

# 3. 执行打包
pyinstaller build.spec --clean

# 4. 查看结果
cd dist
dir
```

## 创建安装程序

### 便携版（无需安装）

直接将 `dist` 文件夹复制即可使用：
- 文件大小：约 150-200MB
- 适合U盘携带
- 无需安装，双击运行

### 安装版（推荐分发）

#### 使用NSIS制作安装程序

1. **安装NSIS**
   - 下载：https://nsis.sourceforge.io/Download
   - 安装后添加到PATH

2. **运行安装制作脚本**
   ```bash
   cd installer
   build_installer.bat
   ```

3. **生成的文件**
   - `合同审查小助手_安装程序.exe` - 标准安装程序
   - 或 `release\便携版` - 便携版压缩包

#### 使用Inno Setup（备选）

1. 安装 Inno Setup：https://jrsoftware.org/isdl.php

2. 创建 `setup.iss` 配置文件

3. 编译生成安装程序

## 打包输出

### 文件结构
```
dist/
├── 合同审查小助手.exe    # 主程序（单文件）
├── 配置文件/
│   └── .env.example      # 配置模板
├── 安装说明.md
└── 使用说明.md
```

### 系统要求

**最低要求：**
- Windows 7 或更高版本
- 2GB RAM
- 500MB 硬盘空间
- (可选) 本地AI模型需要 8GB+ RAM

**推荐配置：**
- Windows 10/11
- 8GB RAM
- 2GB 硬盘空间
- SSD硬盘

## 分发方式

### 1. 单文件分发
- 直接分发 `合同审查小助手.exe`
- 用户下载后双击运行
- 首次运行自动创建配置

### 2. 压缩包分发
```bash
# 创建压缩包
powershell Compress-Archive -Path dist -DestinationPath 合同审查小助手_v1.0.zip
```

### 3. 安装程序分发
- 分发 `合同审查小助手_安装程序.exe`
- 用户运行安装程序
- 自动创建桌面快捷方式和开始菜单项

## 首次运行配置

用户首次运行时：

1. **自动创建配置文件**
   - 从 `.env.example` 复制到 `.env`
   - 提示用户配置AI模型

2. **配置AI模型**
   - 选项1：本地Ollama（需要先安装Ollama）
   - 选项2：云端DeepSeek API（需要API密钥）

3. **开始使用**
   - 选择简洁版或专业版
   - 上传合同文件
   - 开始审查

## 常见问题

### Q1: 打包失败提示缺少模块
**A:** 手动安装缺失的模块：
```bash
pip install <模块名>
```

### Q2: 打包后文件太大
**A:** 使用UPX压缩（已默认启用），或：
- 修改 `build.spec` 中的 `upx=True`
- 删除不需要的依赖

### Q3: 运行时提示缺少DLL
**A:** 确保在Windows环境下打包，或：
- 使用 `--collect-all` 选项
- 手动复制DLL文件

### Q4: 杀毒软件报毒
**A:** PyInstaller打包的程序可能被误报：
- 添加到白名单
- 或使用代码签名证书

## 版本发布

### 发布检查清单

- [ ] 在Windows 10/11 32位和64位系统测试
- [ ] 验证所有功能正常工作
- [ ] 检查是否包含所有必要文件
- [ ] 准备完整的安装说明
- [ ] （可选）申请代码签名证书

### 版本号管理

在以下文件中更新版本号：
1. `build.spec` - `APP_VERSION`
2. `installer.nsi` - `APP_VERSION`
3. `config.py` - `VERSION`

## 技术支持

如遇到打包问题，请检查：
1. Python版本是否符合要求（3.8+）
2. 所有依赖是否正确安装
3. 是否有足够的磁盘空间（至少5GB）
4. 是否有管理员权限

## 许可证

请确保在分发时包含适当的许可证文件。
