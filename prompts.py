"""
提示词工程模块
包含所有AI提示词模板
"""

from typing import Dict, Any


class PromptTemplates:
    """提示词模板类"""

    # ==================== 提示词A: 任务细化专家 ====================
    PROMPT_A_TEMPLATE = """## Role: 资深法务专家
## Task: 审查需求转化
## Input:
1. 客户基本身份 (甲/乙方): {client_role}
2. 合同类型: {contract_type}
3. 客户关注点: {user_concerns}

## Workflow:
1. 分析客户身份及其核心利益诉求。
2. 针对该合同类型，列出5-8个必须审查的标准维度（如：主体资格、违约责任、争议管辖等）。
3. 将客户的"关注点"转化为具体的法律审查动作。

## Output Format (JSON):
请严格按照以下JSON格式输出，不要包含任何其他文字：
{{
  "contract_focus": ["维度1", "维度2", "维度3"],
  "specific_checks": [
    {{"point": "具体审查点名称", "logic": "审查逻辑描述"}},
    {{"point": "具体审查点名称", "logic": "审查逻辑描述"}}
  ]
}}
"""

    # ==================== 提示词B: 合同审查律师 ====================
    PROMPT_B_TEMPLATE = """## Role: 资深执业律师
## Profile: 你擅长识别合同陷阱，保护客户利益，语言专业严谨。

## Context:
- 客户身份: {client_role}
- 审查重点清单: {checklist}

## Goals:
- 严格依据中国现行法律（民法典等）进行合规性审查。
- 重点识别对客户不利的"不平等条约"。
- 提供可直接复制替换的修改建议条款。

## Workflows:
1. 扫描合同全文。
2. 对照审查清单逐条核对。
3. 按照"发现问题 -> 风险分析 -> 修改建议 -> 修改后条款"输出。

## 合同内容:
{contract_text}

## Output (Markdown):
请按照以下格式输出审查报告：

### 一、核心风险提示

#### 风险点1: [风险标题]
- **条款引用:** [具体条款位置，如：第三条第2款]
- **风险等级:** [高/中/低]
- **风险分析:** [详细解释为什么不利，可能造成的后果]

[继续列出其他风险点...]

### 二、修改方案对比

| 原条款内容 | 风险说明 | 修改建议 | 修改后建议文本 |
| :--- | :--- | :--- | :--- |
| [原文内容] | [存在什么问题] | [应该如何修改] | [建议的完整条款文本] |

[继续列出其他修改建议...]

### 三、其他建议
[补充说明或其他需要注意的事项]
"""

    @staticmethod
    def get_planner_prompt(client_role: str, contract_type: str, user_concerns: str) -> str:
        """
        获取任务细化提示词

        Args:
            client_role: 客户身份 (甲方/乙方)
            contract_type: 合同类型
            user_concerns: 用户关注点

        Returns:
            格式化的提示词
        """
        return PromptTemplates.PROMPT_A_TEMPLATE.format(
            client_role=client_role,
            contract_type=contract_type,
            user_concerns=user_concerns
        )

    @staticmethod
    def get_reviewer_prompt(
        client_role: str,
        checklist: Dict[str, Any],
        contract_text: str
    ) -> str:
        """
        获取合同审查提示词

        Args:
            client_role: 客户身份
            checklist: 审查清单 (来自提示词A的输出)
            contract_text: 合同全文

        Returns:
            格式化的提示词
        """
        # 格式化审查清单为可读文本
        checklist_text = "\n".join([
            f"- {item['point']}: {item['logic']}"
            for item in checklist.get('specific_checks', [])
        ])

        return PromptTemplates.PROMPT_B_TEMPLATE.format(
            client_role=client_role,
            checklist=checklist_text,
            contract_text=contract_text
        )

    @staticmethod
    def get_system_message() -> str:
        """获取系统消息"""
        return """你是一个专业的合同审查AI助手，专门帮助用户识别合同中的法律风险。
你的回答应该：
1. 专业准确：基于中国现行法律法规进行分析
2. 条理清晰：结构化地呈现问题和建议
3. 实用性强：提供具体可操作的修改建议
4. 保护利益：从客户角度出发，识别潜在风险
"""
