# 安装和部署指南

## 一、系统要求

### 硬件要求
- CPU: 双核及以上
- 内存: 4GB 及以上（使用本地模型建议 8GB+）
- 硬盘: 至少 2GB 可用空间

### 软件要求
- Python 3.9 或更高版本
- 操作系统: Windows 10+, macOS 10.15+, Ubuntu 20.04+

## 二、详细安装步骤

### 步骤 1: 安装 Python

#### Windows
1. 访问 [Python官网](https://www.python.org/downloads/)
2. 下载并安装 Python 3.9+
3. 安装时勾选 "Add Python to PATH"

#### macOS
```bash
# 使用 Homebrew
brew install python@3.9
```

#### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install python3.9 python3-pip
```

### 步骤 2: 创建虚拟环境（推荐）

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 步骤 3: 安装依赖包

```bash
# 安装所有依赖
pip install -r requirements.txt

# 或使用国内镜像加速
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 步骤 4: 安装 Ollama（本地模型）

#### macOS
```bash
# 下载并安装
curl -fsSL https://ollama.ai/install.sh | sh
```

#### Windows
1. 访问 [Ollama官网](https://ollama.ai/download)
2. 下载 Windows 安装包
3. 运行安装程序

#### Linux
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

### 步骤 5: 拉取模型

```bash
# 拉取中文模型（推荐）
ollama pull qwen2.5:7b

# 或使用其他模型
# ollama pull llama3:8b
# ollama pull qwen2:7b
```

### 步骤 6: 配置环境变量

```bash
# 复制配置文件模板
cp .env.example .env

# 编辑 .env 文件
# Windows: notepad .env
# macOS/Linux: nano .env
```

配置内容：
```ini
AI_MODEL_TYPE=local
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5:7b
```

## 三、启动应用

### 方式 1: 直接运行

```bash
python main_window.py
```

### 方式 2: 创建快捷方式

#### Windows
创建批处理文件 `start.bat`:
```batch
@echo off
call venv\Scripts\activate
python main_window.py
pause
```

#### macOS/Linux
创建启动脚本 `start.sh`:
```bash
#!/bin/bash
source venv/bin/activate
python main_window.py
```

添加执行权限:
```bash
chmod +x start.sh
```

## 四、使用云端API（可选）

如果不想使用本地模型，可以使用云端API：

### OpenAI
```ini
AI_MODEL_TYPE=cloud
OPENAI_API_KEY=sk-your-key-here
OPENAI_API_BASE=https://api.openai.com/v1
OPENAI_MODEL=gpt-4
```

### DeepSeek
```ini
AI_MODEL_TYPE=cloud
OPENAI_API_KEY=sk-your-deepseek-key
OPENAI_API_BASE=https://api.deepseek.com/v1
OPENAI_MODEL=deepseek-chat
```

### 其他兼容API
任何兼容 OpenAI API 格式的服务都可以使用。

## 五、常见安装问题

### 问题 1: pip 安装失败

**解决方案**:
```bash
# 升级 pip
python -m pip install --upgrade pip

# 使用国内镜像
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
```

### 问题 2: PySide6 安装失败

**解决方案**:
```bash
# macOS: 安装 Qt 依赖
brew install qt

# Linux: 安装 Qt 依赖
sudo apt install libqt6-dev

# Windows: 通常不需要额外操作
```

### 问题 3: Ollama 无法启动

**解决方案**:
```bash
# 检查 Ollama 是否运行
curl http://localhost:11434/api/tags

# 重启 Ollama
# macOS: 在应用中重启
# Windows: 在服务管理器中重启
# Linux: systemctl restart ollama
```

### 问题 4: 模型下载慢

**解决方案**:
```bash
# 使用镜像（如果有）
export OLLAMA_MIRROR=https://ollama.registry.example.com

# 或手动下载模型文件
```

## 六、开发者设置

### 安装开发依赖

```bash
pip install pytest black flake8 mypy
```

### 代码格式化

```bash
# 格式化代码
black .

# 检查代码风格
flake8 .
```

### 运行测试

```bash
# 测试文档解析
python document_parser.py

# 测试AI引擎
python ai_engine.py

# 测试报告生成
python report_generator.py

# 测试工作流
python review_workflow.py
```

## 七、部署到其他机器

### 方法 1: 打包成可执行文件

```bash
# 安装 PyInstaller
pip install pyinstaller

# 打包
pyinstaller --onefile --windowed main_window.py

# 生成的文件在 dist/ 目录
```

### 方法 2: Docker 容器

创建 `Dockerfile`:
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["python", "main_window.py"]
```

构建和运行:
```bash
docker build -t contract-reviewer .
docker run -it --rm contract-reviewer
```

## 八、性能优化

### 本地模型优化

```bash
# 使用量化模型（显存更小）
ollama pull qwen2.5:7b-q4_0

# 设置 GPU 加速（如果支持）
export OLLAMA_GPU=nvidia
```

### 应用配置优化

在 `.env` 中调整：
```ini
# 减少并发数
MAX_CONCURRENT_REVIEWS=1

# 调整日志级别
LOG_LEVEL=WARNING
```

## 九、卸载

### 完全卸载

```bash
# 1. 停止应用和 Ollama

# 2. 删除虚拟环境
deactivate
rm -rf venv

# 3. 删除应用数据
rm -rf cache/ output/ temp/

# 4. 卸载 Ollama (可选)
# macOS: 删除应用程序
# Windows: 在控制面板卸载
# Linux: systemctl disable ollama && apt remove ollama
```

## 十、更新

### 更新依赖包

```bash
pip install --upgrade -r requirements.txt
```

### 更新 Ollama 模型

```bash
ollama pull qwen2.5:7b
```

### 更新应用代码

```bash
git pull origin main
# 或重新下载最新版本
```

---

如有问题，请查看 [README.md](README.md) 或提交 Issue。
