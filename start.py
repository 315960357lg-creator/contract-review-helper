#!/usr/bin/env python3
"""
合同审查小助手 - 启动脚本
"""
import sys
import logging
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 检查依赖
def check_dependencies():
    """检查必要的依赖是否安装"""
    missing = []

    try:
        import PySide6
    except ImportError:
        missing.append("PySide6")

    try:
        import docx
    except ImportError:
        missing.append("python-docx")

    try:
        import openai
    except ImportError:
        missing.append("openai")

    if missing:
        print("❌ 缺少必要的依赖包:")
        for pkg in missing:
            print(f"   - {pkg}")
        print("\n请运行以下命令安装:")
        print("pip install -r requirements.txt")
        return False

    return True


def check_config():
    """检查配置文件"""
    from config import Config

    # 检查 .env 文件
    env_file = project_root / ".env"
    if not env_file.exists():
        print("⚠️  未找到 .env 配置文件")
        print("正在从 .env.example 创建默认配置...")

        env_example = project_root / ".env.example"
        if env_example.exists():
            import shutil
            shutil.copy(env_example, env_file)
            print("✅ 已创建 .env 文件")
            print("请根据需要修改配置")
        else:
            print("❌ 未找到 .env.example 文件")
            return False

    # 初始化目录
    try:
        Config.init_directories()
        print(f"✅ 目录初始化成功")
        print(f"   缓存目录: {Config.CACHE_DIR}")
        print(f"   输出目录: {Config.OUTPUT_DIR}")
    except Exception as e:
        print(f"❌ 目录初始化失败: {e}")
        return False

    return True


def check_ai_connection():
    """检查AI模型连接"""
    import requests

    if Config.AI_MODEL_TYPE == "local":
        # 检查 Ollama
        try:
            response = requests.get(f"{Config.OLLAMA_BASE_URL}/api/tags", timeout=5)
            if response.status_code == 200:
                print(f"✅ Ollama 服务运行正常")
                models = response.json().get("models", [])
                if models:
                    print(f"   已安装模型: {', '.join([m['name'] for m in models[:3]])}")
                else:
                    print(f"⚠️  未检测到已安装的模型")
                    print(f"   请运行: ollama pull {Config.OLLAMA_MODEL}")
                return True
        except Exception as e:
            print(f"❌ 无法连接到 Ollama 服务: {e}")
            print(f"   请确保 Ollama 正在运行: {Config.OLLAMA_BASE_URL}")
            return False
    else:
        # 检查云端API
        if not Config.OPENAI_API_KEY:
            print(f"⚠️  未配置 OPENAI_API_KEY")
            print(f"   请在 .env 文件中设置 API 密钥")
            return False
        else:
            print(f"✅ 云端API配置已设置")
            return True

    return True


def main():
    """主函数"""
    print("=" * 60)
    print("📄 合同审查小助手 - 启动中...")
    print("=" * 60)
    print()

    # 1. 检查依赖
    print("[1/4] 检查依赖包...")
    if not check_dependencies():
        input("\n按回车键退出...")
        sys.exit(1)
    print()

    # 2. 检查配置
    print("[2/4] 检查配置文件...")
    if not check_config():
        input("\n按回车键退出...")
        sys.exit(1)
    print()

    # 3. 检查AI连接
    print("[3/4] 检查AI模型连接...")
    ai_ok = check_ai_connection()
    if not ai_ok:
        print("\n⚠️  AI模型连接检查失败，但仍可启动应用")
        print("   请在应用启动后检查配置")
        # input("\n按回车键继续...")
    print()

    # 4. 启动应用
    print("[4/4] 启动应用界面...")
    print()

    try:
        # 使用新的启动器，提供版本选择
        from launch import main
        main()
    except Exception as e:
        print(f"❌ 应用启动失败: {e}")
        logging.exception("应用启动异常")
        input("\n按回车键退出...")
        sys.exit(1)


if __name__ == "__main__":
    # 导入配置
    from config import Config

    # 配置日志
    logging.basicConfig(
        level=getattr(logging, Config.LOG_LEVEL),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(Config.CACHE_DIR / "app.log", encoding='utf-8'),
            logging.StreamHandler()
        ]
    )

    # 运行主程序
    main()
