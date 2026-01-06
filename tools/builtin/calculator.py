# -*- coding: utf-8 -*-
"""计算器工具。"""
from __future__ import annotations

import re

from ..base import BaseTool


class Calculator(BaseTool):
    """数学表达式计算器。
    
    支持基本的四则运算和括号。
    
    Example:
        >>> calc = Calculator()
        >>> calc.execute(expression="3*7+2")
        '3*7+2 = 23'
    """

    # 允许的字符正则
    SAFE_PATTERN = re.compile(r"^[0-9+\-*/().\s]+$")

    def __init__(self) -> None:
        super().__init__(
            name="calculator",
            description="执行数学计算，支持四则运算和括号",
            parameters={
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "数学表达式，如 '3*7+2' 或 '(10+5)/3'",
                    }
                },
                "required": ["expression"],
            },
        )

    def execute(self, expression: str) -> str:
        """执行数学计算。
        
        Args:
            expression: 数学表达式
            
        Returns:
            计算结果或错误信息
        """
        # 安全检查
        if not self.SAFE_PATTERN.match(expression):
            return "❌ 错误：表达式包含不安全字符"
        
        try:
            # 使用 eval 计算（已通过正则验证安全性）
            result = eval(expression)
            return f"{expression} = {result}"
        except ZeroDivisionError:
            return "❌ 错误：除数不能为零"
        except Exception as e:
            return f"❌ 错误：表达式计算失败 - {e}"

