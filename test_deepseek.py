#!/usr/bin/env python3
"""
DeepSeek API 连接测试脚本
"""
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from config import Config
from ai_engine import LLMFactory

print("=" * 60)
print("🧪 DeepSeek API 连接测试")
print("=" * 60)
print()

# 显示当前配置
print("📋 当前配置:")
print(f"   模型类型: {Config.AI_MODEL_TYPE}")
print(f"   API地址: {Config.OPENAI_API_BASE}")
print(f"   使用模型: {Config.OPENAI_MODEL}")
print(f"   API密钥: {Config.OPENAI_API_KEY[:20]}...{Config.OPENAI_API_KEY[-4:]}")
print()

# 测试连接
print("🔄 正在测试API连接...")
print()

try:
    # 创建LLM实例
    llm = LLMFactory.create_llm()

    # 发送测试消息
    messages = [
        {
            "role": "user",
            "content": "你好！请用一句话介绍你自己。"
        }
    ]

    print("💬 发送测试消息...")
    response = llm.chat(messages, temperature=0.7, max_tokens=100)

    print("✅ API连接成功！")
    print()
    print("📝 DeepSeek回复:")
    print("-" * 60)
    print(response)
    print("-" * 60)
    print()

    # 测试提示词A
    print("📋 测试提示词A（任务细化）...")
    from prompts import PromptTemplates

    prompt = PromptTemplates.get_planner_prompt(
        client_role="乙方",
        contract_type="软件开发合同",
        user_concerns="关注付款周期和知识产权保护"
    )

    messages = [
        {"role": "system", "content": PromptTemplates.get_system_message()},
        {"role": "user", "content": prompt}
    ]

    print("⏳ 正在生成审查清单（这可能需要几秒钟）...")
    response = llm.chat(messages, temperature=0.3)

    print()
    print("✅ 提示词A测试成功！")
    print()
    print("📊 生成的审查清单:")
    print("-" * 60)
    print(response[:500] + "..." if len(response) > 500 else response)
    print("-" * 60)
    print()

    print("=" * 60)
    print("🎉 所有测试通过！DeepSeek API配置正常。")
    print("=" * 60)
    print()
    print("💡 您现在可以启动应用开始使用：")
    print("   python start.py")
    print()

except Exception as e:
    print()
    print("❌ API连接失败！")
    print()
    print(f"错误信息: {str(e)}")
    print()
    print("🔧 故障排查建议:")
    print("   1. 检查网络连接")
    print("   2. 确认API密钥是否正确")
    print("   3. 检查DeepSeek服务状态")
    print("   4. 查看 .env 文件配置")
    print()
    print("📚 详细信息请查看: DEEPSEEK_CONFIG.md")
    print()

    sys.exit(1)
