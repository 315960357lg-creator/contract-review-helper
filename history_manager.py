"""
历史记录管理模块
管理合同审查的历史记录
"""
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
import hashlib

logger = logging.getLogger(__name__)


@dataclass
class ReviewRecord:
    """审查记录数据类"""
    id: str  # 唯一ID
    timestamp: str  # 审查时间
    file_name: str  # 合同文件名
    file_path: str  # 合同文件路径
    client_role: str  # 客户身份
    contract_type: str  # 合同类型
    user_concerns: str  # 用户关注点
    model_type: str  # 使用的模型类型
    model_name: str  # 使用的模型名称
    status: str  # 审查状态：success/error
    report_path: Optional[str] = None  # 报告文件路径
    error_message: Optional[str] = None  # 错误信息
    review_summary: Optional[str] = None  # 审查摘要

    def to_dict(self) -> dict:
        """转换为字典"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> 'ReviewRecord':
        """从字典创建实例"""
        return cls(**data)


class HistoryManager:
    """历史记录管理器"""

    def __init__(self, history_file: Path = None):
        """
        初始化历史记录管理器

        Args:
            history_file: 历史记录文件路径
        """
        if history_file is None:
            from config import Config
            history_file = Config.CACHE_DIR / "review_history.json"

        self.history_file = history_file
        self.records: List[ReviewRecord] = []
        self.max_records = 100  # 最多保存100条记录

        self.load_history()

    def _generate_id(self, file_path: str, timestamp: str) -> str:
        """生成记录ID"""
        content = f"{file_path}_{timestamp}"
        return hashlib.md5(content.encode()).hexdigest()[:12]

    def add_record(
        self,
        file_name: str,
        file_path: str,
        client_role: str,
        contract_type: str,
        user_concerns: str,
        model_type: str,
        model_name: str,
        status: str,
        report_path: str = None,
        error_message: str = None,
        review_summary: str = None
    ) -> ReviewRecord:
        """
        添加审查记录

        Args:
            file_name: 合同文件名
            file_path: 合同文件路径
            client_role: 客户身份
            contract_type: 合同类型
            user_concerns: 用户关注点
            model_type: 模型类型
            model_name: 模型名称
            status: 审查状态
            report_path: 报告路径
            error_message: 错误信息
            review_summary: 审查摘要

        Returns:
            创建的审查记录
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        record_id = self._generate_id(file_path, timestamp)

        record = ReviewRecord(
            id=record_id,
            timestamp=timestamp,
            file_name=file_name,
            file_path=file_path,
            client_role=client_role,
            contract_type=contract_type,
            user_concerns=user_concerns,
            model_type=model_type,
            model_name=model_name,
            status=status,
            report_path=report_path,
            error_message=error_message,
            review_summary=review_summary
        )

        # 添加到列表开头
        self.records.insert(0, record)

        # 限制记录数量
        if len(self.records) > self.max_records:
            self.records = self.records[:self.max_records]

        # 保存到文件
        self.save_history()

        logger.info(f"添加审查记录: {file_name} - {status}")
        return record

    def get_records(self, limit: int = None) -> List[ReviewRecord]:
        """
        获取历史记录

        Args:
            limit: 限制返回数量

        Returns:
            审查记录列表
        """
        if limit:
            return self.records[:limit]
        return self.records

    def get_record_by_id(self, record_id: str) -> Optional[ReviewRecord]:
        """
        根据ID获取记录

        Args:
            record_id: 记录ID

        Returns:
            审查记录或None
        """
        for record in self.records:
            if record.id == record_id:
                return record
        return None

    def search_records(self, keyword: str) -> List[ReviewRecord]:
        """
        搜索记录

        Args:
            keyword: 搜索关键词

        Returns:
            匹配的记录列表
        """
        keyword_lower = keyword.lower()
        results = []

        for record in self.records:
            # 在文件名、合同类型、关注点中搜索
            if (keyword_lower in record.file_name.lower() or
                keyword_lower in record.contract_type.lower() or
                keyword_lower in record.user_concerns.lower()):
                results.append(record)

        return results

    def delete_record(self, record_id: str) -> bool:
        """
        删除记录

        Args:
            record_id: 记录ID

        Returns:
            是否删除成功
        """
        for i, record in enumerate(self.records):
            if record.id == record_id:
                del self.records[i]
                self.save_history()
                logger.info(f"删除审查记录: {record_id}")
                return True
        return False

    def clear_all(self) -> bool:
        """
        清空所有记录

        Returns:
            是否清空成功
        """
        try:
            self.records = []
            self.save_history()
            logger.info("清空所有审查记录")
            return True
        except Exception as e:
            logger.error(f"清空记录失败: {e}")
            return False

    def save_history(self) -> bool:
        """
        保存历史记录到文件

        Returns:
            是否保存成功
        """
        try:
            # 确保目录存在
            self.history_file.parent.mkdir(parents=True, exist_ok=True)

            # 转换为字典列表
            data = [record.to_dict() for record in self.records]

            # 写入文件
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            return True

        except Exception as e:
            logger.error(f"保存历史记录失败: {e}")
            return False

    def load_history(self) -> bool:
        """
        从文件加载历史记录

        Returns:
            是否加载成功
        """
        try:
            if not self.history_file.exists():
                logger.info("历史记录文件不存在，创建新文件")
                return True

            # 读取文件
            with open(self.history_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # 转换为记录对象
            self.records = [ReviewRecord.from_dict(item) for item in data]

            logger.info(f"加载历史记录成功: {len(self.records)}条记录")
            return True

        except Exception as e:
            logger.error(f"加载历史记录失败: {e}")
            self.records = []
            return False

    def get_statistics(self) -> dict:
        """
        获取统计信息

        Returns:
            统计信息字典
        """
        total = len(self.records)
        success = sum(1 for r in self.records if r.status == "success")
        error = sum(1 for r in self.records if r.status == "error")

        # 按模型类型统计
        model_stats = {}
        for record in self.records:
            model_stats[record.model_name] = model_stats.get(record.model_name, 0) + 1

        return {
            "total": total,
            "success": success,
            "error": error,
            "model_stats": model_stats,
            "latest_record": self.records[0].timestamp if self.records else None
        }


# 全局单例
_history_manager = None


def get_history_manager() -> HistoryManager:
    """获取历史记录管理器单例"""
    global _history_manager
    if _history_manager is None:
        _history_manager = HistoryManager()
    return _history_manager
