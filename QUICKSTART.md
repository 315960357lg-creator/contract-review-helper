# 🚀 快速使用指南

## 第一次使用（5分钟上手）

### 步骤 1: 安装依赖

```bash
# 进入项目目录
cd "/Volumes/吴落落🉐拓展盘/审查合同助手"

# 安装Python依赖
pip install -r requirements.txt
```

### 步骤 2: 选择AI模型

#### 选项A: 使用本地模型（推荐，保护隐私）

```bash
# 1. 安装 Ollama
# macOS: 访问 https://ollama.ai 下载安装
# Windows: 访问 https://ollama.ai 下载安装
# Linux: 运行 curl -fsSL https://ollama.ai/install.sh | sh

# 2. 拉取中文模型
ollama pull qwen2.5:7b

# 3. 启动 Ollama（通常自动启动）
# 验证: curl http://localhost:11434/api/tags
```

#### 选项B: 使用云端API（需要API密钥）

```bash
# 复制配置文件
cp .env.example .env

# 编辑 .env 文件
AI_MODEL_TYPE=cloud
OPENAI_API_KEY=your_api_key_here
OPENAI_API_BASE=https://api.openai.com/v1
OPENAI_MODEL=gpt-4
```

### 步骤 3: 启动应用

```bash
python start.py
```

或直接运行：
```bash
python main_window.py
```

### 步骤 4: 开始使用

1. **拖放合同文件**到窗口中
2. **选择身份**（甲方或乙方）
3. **输入合同类型**（如：软件开发合同）
4. **输入关注点**（如：关注付款周期和知识产权）
5. **点击"开始审查"**
6. **等待AI完成分析**（可能需要1-3分钟）
7. **查看报告**并导出

## 常用操作

### 查看输出报告

报告保存在 `output/` 目录，文件名格式：
```
合同审查报告_[合同名称]_[时间戳].docx
```

### 更换AI模型

编辑 `.env` 文件：

```ini
# 使用 Ollama 本地模型
AI_MODEL_TYPE=local
OLLAMA_MODEL=qwen2.5:7b

# 或使用 DeepSeek
AI_MODEL_TYPE=cloud
OPENAI_API_KEY=your_deepseek_key
OPENAI_API_BASE=https://api.deepseek.com/v1
```

### 调整审查参数

在 `.env` 中设置：

```ini
# 减少并发数（低配置电脑）
MAX_CONCURRENT_REVIEWS=1

# 调整日志级别
LOG_LEVEL=WARNING  # INFO, WARNING, ERROR

# 默认输出格式
DEFAULT_EXPORT_FORMAT=markdown  # word 或 markdown
```

## 故障排除

### 问题1: "无法连接到Ollama"

```bash
# 检查Ollama是否运行
curl http://localhost:11434/api/tags

# 重启 Ollama
# macOS: 在应用程序中重启
# Windows: 在任务管理器中重启
```

### 问题2: "缺少依赖包"

```bash
# 重新安装依赖
pip install -r requirements.txt --upgrade

# 使用国内镜像
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 问题3: "文档解析失败"

- 确保文件格式正确（.docx 或 .pdf）
- 检查文件是否加密
- 尝试另存为新的文件

### 问题4: 审查速度慢

- 使用本地模型（更快）
- 选择较小的模型（qwen2.5:7b）
- 检查网络连接（云端API）

## 使用技巧

### 1. 精确描述关注点

❌ 不好：
```
帮我看看这个合同
```

✅ 好：
```
我是乙方，关注付款周期（希望不超过30天）、
知识产权归属（希望归我方）、违约责任（希望对等）
```

### 2. 明确合同类型

告诉AI具体是什么类型的合同，可以提高审查准确性：
- 软件开发合同
- 劳动合同
- 采购合同
- 租赁合同
- 借款合同

### 3. 批量审查

如果有多份合同，可以逐个上传审查。报告会保存在 `output/` 目录。

## 下一步

- 📖 阅读完整文档：[README.md](README.md)
- 🔧 查看安装指南：[INSTALL.md](INSTALL.md)
- 📋 了解项目架构：[设计框架.md](设计框架.md)
- 📊 查看项目总结：[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)

## 获取帮助

如有问题：
1. 查看 `cache/app.log` 日志文件
2. 检查 `.env` 配置
3. 确认AI模型正常运行

---

**祝使用愉快！** 🎉
