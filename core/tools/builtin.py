# -*- coding: utf-8 -*-
"""常用内置工具集合。

后续扩展的新工具也建议放在本文件，或在本包新建子模块。"""
from __future__ import annotations

import re
from .base import BaseTool

__all__ = [
    "Calculator",
    "Search",
    "FileOperations",
    "AddFile",
]


class Calculator(BaseTool):
    """执行简单数学表达式计算。"""

    def __init__(self) -> None:
        super().__init__(
            name="calculator",
            description="执行数学计算",
            parameters={
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "数学表达式"
                    }
                },
                "required": ["expression"],
            },
        )

    def execute(self, expression: str):  # type: ignore[override]
        if re.match(r"^[0-9+\-*/().\s]+$", expression):
            try:
                result = eval(expression)
            except Exception as exc:  # pragma: no cover
                return f"错误：表达式计算失败 => {exc}"
            return f"{expression} = {result}"
        return "错误：表达式包含不安全字符"


class Search(BaseTool):
    """离线演示搜索工具（示例）。"""

    _mock_results: dict[str, str] = {
        "python": "Python 是一种编程语言。",
        "ai": "人工智能相关信息。",
        "天气": "今天天气晴朗。",
    }

    def __init__(self) -> None:
        super().__init__(
            name="search",
            description="搜索信息",
            parameters={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "搜索关键词",
                    }
                },
                "required": ["query"],
            },
        )

    def execute(self, query: str):  # type: ignore[override]
        return self._mock_results.get(query.lower(), f"未找到关于 '{query}' 的信息")


# ---------------------------------------------------------------------------
# 新增：AddFile 工具 – 在当前工作目录创建文件并写入内容
# ---------------------------------------------------------------------------

class AddFile(BaseTool):
    """在当前目录创建文件并写入内容。"""

    def __init__(self) -> None:
        super().__init__(
            name="addFile",
            description="在当前工作目录创建文件并写入内容",
            parameters={
                "type": "object",
                "properties": {
                    "filename": {
                        "type": "string",
                        "description": "要创建的文件名（可包含相对路径）",
                    },
                    "content": {
                        "type": "string",
                        "description": "要写入文件的内容",
                    },
                },
                "required": ["filename", "content"],
            },
        )

    def execute(self, filename: str, content: str):  # type: ignore[override]
        try:
            with open(filename, "w", encoding="utf-8") as f:
                f.write(content)
            return f"✅ 已创建文件 {filename}，写入 {len(content)} 字符。"
        except Exception as exc:  # pragma: no cover
            return f"❌ 创建文件失败: {exc}"

class read_file(BaseTool):
    """读取文件内容。"""
    def __init__(self) -> None:
        super().__init__(
            name="read_file",
            description="读取文件内容",
        )
    def execute(self, filename: str):  # type: ignore[override]
        with open(filename, "r", encoding="utf-8") as f:
            return f.read()

if __name__ == "__main__":
    # addFile = AddFile()
    # result = addFile.execute("test.txt", "Hello, world!")
    result = eval("7*99+234-89")
    print(result)