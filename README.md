# 📄 合同审查小助手

> 基于AI的智能合同审查桌面应用程序

一个专业的合同审查助手，帮助用户快速识别合同中的法律风险，提供专业的修改建议。支持本地模型和云端API，保护隐私安全。

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)

## ✨ 功能特性

### 核心功能
- 🤖 **AI智能审查**: 基于大语言模型的深度合同审查
- 📋 **需求转化**: 将用户的简单需求转化为专业的法律审查清单
- 🔍 **风险识别**: 自动识别合同中的潜在风险和不平等条款
- 📝 **修改建议**: 提供具体可操作的修改建议和参考文本
- 📊 **对比报告**: 生成原文与建议的对比表格

### 文档支持
- 📄 **Word文档**: 支持 .docx 格式
- 📕 **PDF文档**: 支持 .pdf 格式
- 📑 **章节识别**: 自动识别合同章节结构

### 导出格式
- Microsoft Word (.docx)
- Markdown (.md)

### 模型支持
- 🏠 **本地模型**: Ollama (Qwen2.5, Llama3等)
- ☁️ **云端API**: OpenAI GPT-4, DeepSeek等

## 🚀 快速开始

### 环境要求

- Python 3.9 或更高版本
- Windows / macOS / Linux

### 1. 克隆项目

```bash
git clone <repository_url>
cd 审查合同助手
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置环境变量

复制 `.env.example` 为 `.env` 并配置：

```bash
cp .env.example .env
```

编辑 `.env` 文件：

```ini
# 模型类型: local (Ollama) 或 cloud (OpenAI/DeepSeek)
AI_MODEL_TYPE=local

# 本地模型配置
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5:7b

# 或使用云端API
# AI_MODEL_TYPE=cloud
# OPENAI_API_KEY=your_api_key
# OPENAI_API_BASE=https://api.openai.com/v1
# OPENAI_MODEL=gpt-4
```

### 4. 启动应用

#### 方式1：使用启动器（推荐）

```bash
python start.py
```

会弹出版本选择对话框，选择适合的界面版本：
- 📱 **简洁版**：快速审查单个合同
- 💼 **专业版**：批量审查，三段式专业布局

#### 方式2：直接启动

```bash
# 简洁版
python main_window.py

# 专业版（三段式布局）
python main_window_pro.py

# 版本选择器
python launch.py
```

## 📖 使用指南

### 基本使用流程

1. **选择合同文件**
   - 点击"浏览文件"按钮选择合同
   - 或直接拖拽文件到拖放区域

2. **设置审查参数**
   - 选择客户身份（甲方/乙方）
   - 输入合同类型（如：软件开发合同）
   - 输入关注点（如：关注付款周期和知识产权）

3. **开始审查**
   - 点击"开始审查"按钮
   - 等待AI完成分析（可能需要几分钟）

4. **查看报告**
   - 审查完成后，结果会显示在界面上
   - 点击"打开报告"查看完整报告

### 使用本地模型 (推荐)

1. 安装 [Ollama](https://ollama.ai/)
2. 拉取中文模型：

```bash
ollama pull qwen2.5:7b
```

3. 启动Ollama服务（默认运行在 `http://localhost:11434`）

### 使用云端API

在 `.env` 文件中配置：

```ini
AI_MODEL_TYPE=cloud
OPENAI_API_KEY=your_api_key_here
OPENAI_API_BASE=https://api.openai.com/v1
OPENAI_MODEL=gpt-4
```

## 🎨 界面版本

项目提供两种界面版本，满足不同用户需求：

### 📱 简洁版 (Simple)
- **特点**：垂直布局，操作流程清晰
- **适合**：快速审查单个合同
- **功能**：拖放上传 → 填写参数 → 查看结果

### 💼 专业版 (Professional)
- **特点**：三段式水平布局，专业高效
- **适合**：批量审查和专业分析
- **功能**：批量管理、AI对话、实时进度、原文对照

详细对比请查看 [VERSION_COMPARISON.md](VERSION_COMPARISON.md)

## 🏗️ 项目架构

```
审查合同助手/
├── config.py              # 配置管理
├── prompts.py             # 提示词工程
├── document_parser.py     # 文档解析模块
├── ai_engine.py          # AI引擎模块
├── report_generator.py   # 报告生成模块
├── review_workflow.py    # 工作流编排
├── main_window.py        # 主窗口界面
├── requirements.txt      # 依赖包列表
├── .env.example         # 环境变量模板
├── README.md            # 项目说明
├── 设计框架.md          # 详细设计文档
└── cache/               # 缓存目录
    └── app.log          # 应用日志
```

### 模块说明

| 模块 | 功能 | 技术栈 |
|------|------|--------|
| **UI层** | 图形界面 | PySide6 |
| **文档解析** | Word/PDF解析 | python-docx, PyMuPDF |
| **AI引擎** | 模型调用 | LangChain, OpenAI SDK |
| **报告生成** | 格式化输出 | python-docx, Jinja2 |
| **工作流** | 流程编排 | 自定义 |

## 🔧 配置说明

### 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `AI_MODEL_TYPE` | 模型类型 (local/cloud) | local |
| `OLLAMA_BASE_URL` | Ollama服务地址 | http://localhost:11434 |
| `OLLAMA_MODEL` | Ollama模型名称 | qwen2.5:7b |
| `OPENAI_API_KEY` | OpenAI API密钥 | - |
| `OPENAI_API_BASE` | OpenAI API地址 | https://api.openai.com/v1 |
| `OPENAI_MODEL` | OpenAI模型名称 | gpt-4 |
| `DEFAULT_EXPORT_FORMAT` | 默认导出格式 | word |
| `LOG_LEVEL` | 日志级别 | INFO |

### 目录配置

应用会在首次运行时自动创建以下目录：

- `cache/` - 缓存文件和日志
- `output/` - 生成的报告
- `temp/` - 临时文件

## 📝 提示词工程

### 提示词A: 任务细化专家

将用户的简单需求转化为具体的法律审查清单。

**输入示例**：
- 客户身份: 乙方
- 合同类型: 软件开发合同
- 关注点: 关注付款周期

**输出示例**：
```json
{
  "contract_focus": ["主体资格", "付款条款", "知识产权"],
  "specific_checks": [
    {"point": "付款周期审查", "logic": "检查付款周期是否合理"}
  ]
}
```

### 提示词B: 合同审查律师

基于审查清单对合同进行深度分析，生成专业的审查报告。

**输出内容**：
- 核心风险提示
- 修改方案对比表
- 其他建议

## 🐛 常见问题

### 1. Ollama连接失败

**问题**: 提示 "Ollama请求失败"

**解决**:
```bash
# 检查Ollama服务状态
ollama list

# 重启Ollama服务
# macOS: 在应用程序中找到Ollama并重启
# Windows: 在服务管理器中重启
# Linux: systemctl restart ollama
```

### 2. 文档解析失败

**问题**: 提示 "文档解析失败"

**解决**:
- 确保文档格式正确（.docx 或 .pdf）
- 检查文档是否加密
- 尝试另存为新的文档

### 3. AI响应慢

**问题**: 审查过程耗时过长

**解决**:
- 使用本地模型（Ollama）
- 选择较小的模型（如 qwen2.5:7b）
- 检查网络连接（云端API）

### 4. 报告生成失败

**问题**: 提示 "生成报告失败"

**解决**:
- 检查输出目录权限
- 确保有足够的磁盘空间
- 查看日志文件 `cache/app.log`

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## 🤝 贡献

欢迎贡献代码、报告问题或提出建议！

1. Fork 本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## ⚠️ 免责声明

本软件由AI辅助生成，仅供学习和参考使用。

- 本工具生成的审查报告**不构成法律意见**
- 请在签署重要合同前咨询专业律师
- 开发者不对使用本工具造成的任何后果承担责任

## 📮 联系方式

如有问题或建议，请通过以下方式联系：

- 提交 Issue
- 发送邮件

## 🙏 致谢

感谢以下开源项目：

- [PySide6](https://doc.qt.io/qtforpython/) - Qt for Python
- [LangChain](https://python.langchain.com/) - LLM应用框架
- [Ollama](https://ollama.ai/) - 本地LLM运行
- [python-docx](https://python-docx.readthedocs.io/) - Word文档处理

---

**⭐ 如果这个项目对您有帮助，请给个星标支持！**
