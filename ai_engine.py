"""
AI引擎模块
支持本地(Ollama)和云端(OpenAI/DeepSeek)模型调用
"""
import json
import logging
from typing import Dict, Any, Optional, List
from abc import ABC, abstractmethod

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None
    print("警告: openai 未安装")

import requests

from config import Config

logger = logging.getLogger(__name__)


class BaseLLM(ABC):
    """LLM基类"""

    def __init__(self):
        self.client = None

    @abstractmethod
    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """
        聊天接口

        Args:
            messages: 消息列表
            **kwargs: 其他参数

        Returns:
            模型响应文本
        """
        pass

    @abstractmethod
    def chat_stream(self, messages: List[Dict[str, str]], **kwargs):
        """
        流式聊天接口

        Args:
            messages: 消息列表
            **kwargs: 其他参数

        Yields:
            模型响应文本片段
        """
        pass


class OllamaLLM(BaseLLM):
    """Ollama本地模型"""

    def __init__(self, base_url: str = None, model: str = None):
        super().__init__()
        self.base_url = base_url or Config.OLLAMA_BASE_URL
        self.model = model or Config.OLLAMA_MODEL
        self.api_url = f"{self.base_url}/api/chat"

        logger.info(f"初始化Ollama模型: {self.model} @ {self.base_url}")

    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """发送聊天请求"""
        try:
            payload = {
                "model": self.model,
                "messages": messages,
                "stream": False,
                "options": {
                    "temperature": kwargs.get("temperature", 0.7),
                    "num_predict": kwargs.get("max_tokens", 4096),
                }
            }

            response = requests.post(self.api_url, json=payload, timeout=120)
            response.raise_for_status()

            result = response.json()
            return result.get("message", {}).get("content", "")

        except Exception as e:
            logger.error(f"Ollama请求失败: {e}")
            raise

    def chat_stream(self, messages: List[Dict[str, str]], **kwargs):
        """流式聊天请求"""
        try:
            payload = {
                "model": self.model,
                "messages": messages,
                "stream": True,
                "options": {
                    "temperature": kwargs.get("temperature", 0.7),
                }
            }

            response = requests.post(self.api_url, json=payload, stream=True, timeout=120)
            response.raise_for_status()

            for line in response.iter_lines():
                if line:
                    data = json.loads(line)
                    if "message" in data:
                        yield data["message"].get("content", "")

        except Exception as e:
            logger.error(f"Ollama流式请求失败: {e}")
            raise


class OpenAILLM(BaseLLM):
    """OpenAI/兼容API模型"""

    def __init__(
        self,
        api_key: str = None,
        base_url: str = None,
        model: str = None
    ):
        super().__init__()
        if OpenAI is None:
            raise ImportError("openai 包未安装")

        self.api_key = api_key or Config.OPENAI_API_KEY
        self.base_url = base_url or Config.OPENAI_API_BASE
        self.model = model or Config.OPENAI_MODEL

        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )

        logger.info(f"初始化OpenAI模型: {self.model} @ {self.base_url}")

    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """发送聊天请求"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=kwargs.get("temperature", 0.7),
                max_tokens=kwargs.get("max_tokens", 4096),
                timeout=120.0,  # 增加超时时间到120秒
            )

            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"OpenAI请求失败: {e}")
            raise

    def chat_stream(self, messages: List[Dict[str, str]], **kwargs):
        """流式聊天请求"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=kwargs.get("temperature", 0.7),
                max_tokens=kwargs.get("max_tokens", 4096),
                stream=True
            )

            for chunk in response:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

        except Exception as e:
            logger.error(f"OpenAI流式请求失败: {e}")
            raise


class LLMFactory:
    """LLM工厂类"""

    @staticmethod
    def create_llm(llm_config: Dict[str, Any] = None) -> BaseLLM:
        """
        创建LLM实例

        Args:
            llm_config: LLM配置字典

        Returns:
            LLM实例
        """
        if llm_config is None:
            llm_config = Config.get_llm_config()

        model_type = llm_config.get("type", "local")

        if model_type == "local":
            return OllamaLLM(
                base_url=llm_config.get("base_url"),
                model=llm_config.get("model")
            )
        else:  # cloud
            return OpenAILLM(
                api_key=llm_config.get("api_key"),
                base_url=llm_config.get("api_base"),
                model=llm_config.get("model")
            )


class ContractReviewerAI:
    """合同审查AI引擎"""

    def __init__(self, llm: BaseLLM = None):
        """
        初始化AI引擎

        Args:
            llm: LLM实例，如果为None则自动创建
        """
        self.llm = llm or LLMFactory.create_llm()
        logger.info("合同审查AI引擎初始化完成")

    def generate_checklist(
        self,
        client_role: str,
        contract_type: str,
        user_concerns: str
    ) -> Dict[str, Any]:
        """
        生成审查清单 (提示词A)

        Args:
            client_role: 客户身份
            contract_type: 合同类型
            user_concerns: 用户关注点

        Returns:
            审查清单字典
        """
        from prompts import PromptTemplates

        prompt = PromptTemplates.get_planner_prompt(
            client_role=client_role,
            contract_type=contract_type,
            user_concerns=user_concerns
        )

        messages = [
            {"role": "system", "content": PromptTemplates.get_system_message()},
            {"role": "user", "content": prompt}
        ]

        logger.info("开始生成审查清单...")
        response = self.llm.chat(messages, temperature=0.3)

        # 解析JSON响应
        try:
            # 尝试提取JSON部分
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                response = response.split("```")[1].split("```")[0].strip()

            checklist = json.loads(response)
            logger.info(f"审查清单生成成功: {len(checklist.get('specific_checks', []))} 个审查点")
            return checklist

        except json.JSONDecodeError as e:
            logger.error(f"解析审查清单JSON失败: {e}")
            logger.error(f"原始响应: {response}")
            raise ValueError("AI生成的审查清单格式错误")

    def review_contract(
        self,
        client_role: str,
        checklist: Dict[str, Any],
        contract_text: str,
        stream: bool = False
    ) -> str:
        """
        审查合同 (提示词B)

        Args:
            client_role: 客户身份
            checklist: 审查清单
            contract_text: 合同全文
            stream: 是否使用流式输出

        Returns:
            审查报告文本
        """
        from prompts import PromptTemplates

        # 如果合同文本过长，进行截断（避免超过token限制）
        max_length = 12000  # 约3000个汉字
        if len(contract_text) > max_length:
            logger.warning(f"合同文本过长({len(contract_text)}字符)，截断到{max_length}字符")
            contract_text = contract_text[:max_length] + "\n\n[注意：合同文本较长，已截断前部分进行审查]"

        prompt = PromptTemplates.get_reviewer_prompt(
            client_role=client_role,
            checklist=checklist,
            contract_text=contract_text
        )

        messages = [
            {"role": "system", "content": PromptTemplates.get_system_message()},
            {"role": "user", "content": prompt}
        ]

        logger.info("开始审查合同...")
        logger.info(f"提示词长度: {len(prompt)}字符")

        if stream:
            # 返回生成器
            return self.llm.chat_stream(messages, temperature=0.5)
        else:
            try:
                response = self.llm.chat(messages, temperature=0.5)
                logger.info("合同审查完成")
                return response
            except Exception as e:
                logger.error(f"合同审查失败: {e}")
                raise


# 测试代码
if __name__ == "__main__":
    logging.basicConfig(level=Config.LOG_LEVEL)

    # 测试AI引擎
    try:
        ai = ContractReviewerAI()

        # 测试生成审查清单
        checklist = ai.generate_checklist(
            client_role="乙方",
            contract_type="软件开发合同",
            user_concerns="关注付款周期和知识产权"
        )
        print("\n=== 审查清单 ===")
        print(json.dumps(checklist, ensure_ascii=False, indent=2))

        # 测试合同审查（需要真实的合同文本）
        # contract_text = "这是测试合同文本..."
        # report = ai.review_contract("乙方", checklist, contract_text)
        # print("\n=== 审查报告 ===")
        # print(report)

    except Exception as e:
        print(f"测试失败: {e}")
        logger.exception(e)
