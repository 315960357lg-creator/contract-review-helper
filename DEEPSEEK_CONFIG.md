# ✅ DeepSeek API 配置完成

## 配置信息

已成功配置 DeepSeek API！

### 配置详情

- **API密钥**：sk-c0388ccb94a94e459dc152c629849eba
- **API地址**：https://api.deepseek.com/v1
- **使用模型**：deepseek-chat
- **配置文件**：.env

### 模型切换

当前配置为使用 **DeepSeek 云端API**。

如需切换回本地模型（Ollama），编辑 `.env` 文件：

```ini
# 使用本地模型
AI_MODEL_TYPE=local

# 使用DeepSeek云端API
AI_MODEL_TYPE=cloud
```

## 使用说明

### 启动应用

```bash
python start.py
```

### DeepSeek模型优势

✅ **强大的中文理解能力**
- 专门针对中文优化
- 合同审查更准确

✅ **无需本地配置**
- 不需要安装Ollama
- 不需要下载模型文件

✅ **更快的响应速度**
- 云端高性能计算
- 稳定的API服务

✅ **持续更新**
- 模型持续优化
- 自动享受改进

### 费用说明

DeepSeek API按使用量计费：
- 💰 性价比很高
- 📊 查看官网了解详细定价
- 💳 建议设置使用限额

### API状态检查

确认配置正确：

```bash
# 检查配置文件
cat .env

# 应该看到：
# AI_MODEL_TYPE=cloud
# OPENAI_API_KEY=sk-c0388ccb94a94e459dc152c629849eba
# OPENAI_API_BASE=https://api.deepseek.com/v1
# OPENAI_MODEL=deepseek-chat
```

## 快速开始

1. **启动应用**
   ```bash
   python start.py
   ```

2. **选择界面版本**
   - 📱 简洁版：快速审查
   - 💼 专业版：批量处理

3. **上传合同**
   - 拖放或浏览选择文件

4. **设置参数**
   - 身份：甲方/乙方
   - 类型：如"软件开发合同"
   - 关注点：如"付款周期、知识产权"

5. **开始审查**
   - 点击"开始审查"按钮
   - DeepSeek AI将深度分析合同

## 故障排除

### 问题1: API连接失败

**错误**: "无法连接到API"

**解决方案**:
1. 检查网络连接
2. 确认API密钥正确
3. 检查DeepSeek服务状态

### 问题2: API密钥无效

**错误**: "API密钥无效"

**解决方案**:
1. 确认密钥没有过期
2. 检查密钥余额
3. 联系DeepSeek客服

### 问题3: 响应速度慢

**解决方案**:
- 正常情况下DeepSeek响应很快
- 如果慢，可能是网络问题
- 可以切换到本地Ollama模型

## 测试API连接

运行以下命令测试配置：

```bash
python -c "
from ai_engine import LLMFactory, ContractReviewerAI
from config import Config

print('正在测试DeepSeek API连接...')
print(f'API地址: {Config.OPENAI_API_BASE}')
print(f'使用模型: {Config.OPENAI_MODEL}')

try:
    llm = LLMFactory.create_llm()
    messages = [{'role': 'user', 'content': '你好'}]
    response = llm.chat(messages)
    print(f'✅ API连接成功！')
    print(f'AI回复: {response}')
except Exception as e:
    print(f'❌ API连接失败: {e}')
"
```

## 配置文件位置

```
/Volumes/吴落落🉐拓展盘/审查合同助手/.env
```

## 查看日志

应用日志会保存在：
```
cache/app.log
```

如果遇到问题，查看日志了解详情：
```bash
tail -f cache/app.log
```

## 性能对比

| 模型 | 响应速度 | 准确性 | 隐私保护 | 成本 |
|------|---------|--------|---------|------|
| **DeepSeek** | ⚡⚡⚡ 快 | ⭐⭐⭐⭐⭐ 高 | ⚠️ 需上传 | 💰 按量计费 |
| **Ollama本地** | ⚡⚡ 中等 | ⭐⭐⭐⭐ 良好 | ✅ 完全本地 | 💵 免费 |

## 切换建议

### 使用DeepSeek（云端）的情况：
- ✅ 需要最高准确性
- ✅ 对隐私要求不高
- ✅ 有稳定网络连接
- ✅ 希望快速响应

### 使用Ollama（本地）的情况：
- ✅ 合同包含敏感信息
- ✅ 需要完全离线使用
- ✅ 不想产生API费用
- ✅ 网络连接不稳定

## 安全提示

⚠️ **重要**：
1. 不要将 `.env` 文件提交到Git
2. 不要分享API密钥
3. 定期检查API使用量
4. 设置合理的预算限制

## 下一步

配置完成后，您可以：

1. 📖 阅读 [快速开始指南](QUICKSTART.md)
2. 🎨 查看 [UI版本对比](VERSION_COMPARISON.md)
3. 🚀 启动应用开始使用

---

**配置完成时间**: 2025-01-17
**API提供商**: DeepSeek
**状态**: ✅ 已配置并可以使用
