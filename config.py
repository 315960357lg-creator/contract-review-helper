"""
配置管理模块
加载和管理应用程序配置
"""
import os
from pathlib import Path
from dotenv import load_dotenv
from typing import Literal

# 加载环境变量
load_dotenv()


class Config:
    """应用程序配置类"""

    # 项目根目录
    BASE_DIR = Path(__file__).parent

    # AI模型配置
    AI_MODEL_TYPE: Literal["local", "cloud"] = os.getenv("AI_MODEL_TYPE", "local")

    # 本地模型配置
    OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:7b")

    # 云端API配置
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    OPENAI_API_BASE = os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4")

    # DeepSeek配置
    DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
    DEEPSEEK_API_BASE = os.getenv("DEEPSEEK_API_BASE", "https://api.deepseek.com/v1")

    # 应用配置
    APP_NAME = os.getenv("APP_NAME", "合同审查小助手")
    DEFAULT_EXPORT_FORMAT = os.getenv("DEFAULT_EXPORT_FORMAT", "word")
    MAX_CONCURRENT_REVIEWS = int(os.getenv("MAX_CONCURRENT_REVIEWS", "3"))
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

    # 目录配置
    CACHE_DIR = BASE_DIR / os.getenv("CACHE_DIR", "./cache")
    OUTPUT_DIR = BASE_DIR / os.getenv("OUTPUT_DIR", "./output")
    TEMP_DIR = BASE_DIR / os.getenv("TEMP_DIR", "./temp")

    @classmethod
    def init_directories(cls):
        """初始化必要的目录"""
        for directory in [cls.CACHE_DIR, cls.OUTPUT_DIR, cls.TEMP_DIR]:
            directory.mkdir(parents=True, exist_ok=True)

    @classmethod
    def get_llm_config(cls) -> dict:
        """获取LLM配置"""
        if cls.AI_MODEL_TYPE == "local":
            return {
                "type": "local",
                "base_url": cls.OLLAMA_BASE_URL,
                "model": cls.OLLAMA_MODEL,
            }
        else:
            return {
                "type": "cloud",
                "api_key": cls.OPENAI_API_KEY,
                "api_base": cls.OPENAI_API_BASE,
                "model": cls.OPENAI_MODEL,
            }


# 初始化目录
Config.init_directories()
