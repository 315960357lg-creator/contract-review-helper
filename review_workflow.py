"""
合同审查工作流编排
整合所有模块，实现完整的审查流程
"""
import logging
from pathlib import Path
from typing import Dict, Any, Optional, Callable
from datetime import datetime
import json

from config import Config
from document_parser import DocumentParserFactory
from ai_engine import ContractReviewerAI, LLMFactory
from report_generator import ReportGeneratorFactory

logger = logging.getLogger(__name__)


class ReviewWorkflow:
    """合同审查工作流"""

    def __init__(self, progress_callback: Optional[Callable] = None):
        """
        初始化工作流

        Args:
            progress_callback: 进度回调函数，签名为 (message: str, progress: int)
        """
        self.ai_engine = ContractReviewerAI()
        self.progress_callback = progress_callback
        self.current_step = 0
        self.total_steps = 5

        logger.info("合同审查工作流初始化完成")

    def _update_progress(self, message: str, step_increment: bool = True):
        """更新进度"""
        if step_increment:
            self.current_step += 1

        progress = int((self.current_step / self.total_steps) * 100)
        logger.info(f"[{progress}%] {message}")

        if self.progress_callback:
            self.progress_callback(message, progress)

    def review_contract(
        self,
        contract_file: str,
        client_role: str,
        contract_type: str,
        user_concerns: str,
        output_format: str = "word"
    ) -> Dict[str, Any]:
        """
        执行完整的合同审查流程

        Args:
            contract_file: 合同文件路径
            client_role: 客户身份 (甲方/乙方)
            contract_type: 合同类型
            user_concerns: 用户关注点
            output_format: 输出格式

        Returns:
            包含审查结果和报告路径的字典
        """
        try:
            self.current_step = 0
            result = {
                "success": False,
                "message": "",
                "data": {}
            }

            # 步骤1: 解析文档
            self._update_progress("正在解析合同文档...")
            contract_data = self._parse_document(contract_file)
            contract_text = contract_data["text"]

            # 步骤2: 生成审查清单
            self._update_progress("AI正在分析需求，生成审查清单...")
            checklist = self.ai_engine.generate_checklist(
                client_role=client_role,
                contract_type=contract_type,
                user_concerns=user_concerns
            )

            # 步骤3: 执行合同审查
            self._update_progress("AI正在深度审查合同条款（可能需要1-2分钟）...")
            try:
                review_report = self.ai_engine.review_contract(
                    client_role=client_role,
                    checklist=checklist,
                    contract_text=contract_text
                )
            except Exception as e:
                # 如果审查失败，尝试提供部分结果
                logger.error(f"深度审查失败: {e}")
                review_report = f"""# 审查报告

## ⚠️ 注意
由于合同内容较长或网络问题，AI深度审查未能完成。以下是已生成的审查清单：

## 审查清单

### 审查维度
{chr(10).join(f"- {focus}" for focus in checklist.get('contract_focus', []))}

### 具体审查点
{chr(10).join(f"- **{check['point']}**: {check['logic']}" for check in checklist.get('specific_checks', []))}

## 建议
由于完整审查未能完成，建议：
1. 缩短合同文本后重新审查
2. 检查网络连接
3. 或者使用本地Ollama模型

---
错误信息: {str(e)}
"""

            # 步骤4: 生成审查报告
            self._update_progress("正在生成审查报告...")

            # 准备元数据
            metadata = {
                "contract_name": Path(contract_file).stem,
                "contract_file": contract_file,
                "client_role": client_role,
                "contract_type": contract_type,
                "user_concerns": user_concerns,
                "checklist": checklist,
                "document_info": contract_data.get("metadata", {})
            }

            report_path = ReportGeneratorFactory.generate_report(
                review_result=review_report,
                metadata=metadata,
                output_format=output_format
            )

            # 步骤5: 完成
            self._update_progress("审查完成！", step_increment=False)

            result["success"] = True
            result["message"] = "合同审查成功完成"
            result["data"] = {
                "checklist": checklist,
                "review_report": review_report,
                "report_path": report_path,
                "metadata": metadata
            }

            return result

        except Exception as e:
            error_msg = f"审查流程出错: {str(e)}"
            logger.error(error_msg, exc_info=True)
            self._update_progress(error_msg, step_increment=False)

            result["success"] = False
            result["message"] = error_msg
            return result

    def _parse_document(self, file_path: str) -> Dict[str, Any]:
        """
        解析文档

        Args:
            file_path: 文件路径

        Returns:
            解析结果
        """
        try:
            result = DocumentParserFactory.parse_document(file_path)

            # 验证文本长度
            text_length = len(result.get("text", ""))
            if text_length == 0:
                raise ValueError("文档解析失败：未提取到文本内容")

            if text_length < 100:
                logger.warning(f"文档文本较短: {text_length} 字符")

            logger.info(f"文档解析成功，提取文本: {text_length} 字符")
            return result

        except Exception as e:
            logger.error(f"文档解析失败: {e}")
            raise

    def quick_review(
        self,
        contract_file: str,
        client_role: str,
        focus_areas: list = None
    ) -> Dict[str, Any]:
        """
        快速审查（跳过清单生成步骤）

        Args:
            contract_file: 合同文件路径
            client_role: 客户身份
            focus_areas: 关注领域列表

        Returns:
            审查结果
        """
        try:
            self.current_step = 0
            self.total_steps = 3

            # 解析文档
            self._update_progress("正在解析合同文档...")
            contract_data = self._parse_document(contract_file)

            # 使用预设清单
            self._update_progress("AI正在审查合同...")
            default_checklist = {
                "contract_focus": focus_areas or ["通用条款", "核心条款"],
                "specific_checks": [
                    {"point": "合规性审查", "logic": "检查条款是否符合法律法规"},
                    {"point": "风险识别", "logic": "识别对客户不利的条款"}
                ]
            }

            review_report = self.ai_engine.review_contract(
                client_role=client_role,
                checklist=default_checklist,
                contract_text=contract_data["text"]
            )

            # 生成报告
            self._update_progress("正在生成报告...")
            metadata = {
                "contract_name": Path(contract_file).stem,
                "client_role": client_role,
                "checklist": default_checklist
            }

            report_path = ReportGeneratorFactory.generate_report(
                review_result=review_report,
                metadata=metadata,
                output_format="markdown"
            )

            self._update_progress("快速审查完成！", step_increment=False)

            return {
                "success": True,
                "message": "快速审查完成",
                "data": {
                    "review_report": review_report,
                    "report_path": report_path
                }
            }

        except Exception as e:
            logger.error(f"快速审查失败: {e}")
            return {
                "success": False,
                "message": f"快速审查失败: {str(e)}"
            }


class ReviewSession:
    """审查会话管理"""

    def __init__(self):
        self.sessions = {}  # session_id -> session_data

    def create_session(self, contract_file: str) -> str:
        """
        创建新的审查会话

        Args:
            contract_file: 合同文件路径

        Returns:
            会话ID
        """
        session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.sessions[session_id] = {
            "contract_file": contract_file,
            "created_at": datetime.now(),
            "status": "created"
        }
        return session_id

    def update_session(self, session_id: str, **kwargs):
        """更新会话数据"""
        if session_id in self.sessions:
            self.sessions[session_id].update(kwargs)

    def get_session(self, session_id: str) -> Optional[Dict]:
        """获取会话数据"""
        return self.sessions.get(session_id)

    def save_session(self, session_id: str, file_path: str = None):
        """
        保存会话到文件

        Args:
            session_id: 会话ID
            file_path: 保存路径，默认使用缓存目录
        """
        if session_id not in self.sessions:
            raise ValueError(f"会话不存在: {session_id}")

        if file_path is None:
            file_path = Config.CACHE_DIR / f"session_{session_id}.json"

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(self.sessions[session_id], f, ensure_ascii=False, indent=2, default=str)

        logger.info(f"会话已保存: {file_path}")


# 测试代码
if __name__ == "__main__":
    logging.basicConfig(
        level=Config.LOG_LEVEL,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    def test_progress(message, progress):
        print(f"进度: {progress}% - {message}")

    # 测试完整流程
    print("=" * 50)
    print("测试合同审查工作流")
    print("=" * 50)

    workflow = ReviewWorkflow(progress_callback=test_progress)

    # 这里需要一个真实的测试文件
    test_contract = "test_contract.docx"  # 替换为实际文件路径

    if Path(test_contract).exists():
        result = workflow.review_contract(
            contract_file=test_contract,
            client_role="乙方",
            contract_type="软件开发合同",
            user_concerns="关注付款周期和知识产权保护",
            output_format="word"
        )

        print("\n" + "=" * 50)
        print("审查结果:")
        print("=" * 50)
        print(f"成功: {result['success']}")
        print(f"消息: {result['message']}")
        if result['success']:
            print(f"报告路径: {result['data']['report_path']}")
            print(f"审查点数量: {len(result['data']['checklist']['specific_checks'])}")
    else:
        print(f"测试文件不存在: {test_contract}")
        print("请将测试合同文件放在项目根目录，并修改 test_contract 变量")
