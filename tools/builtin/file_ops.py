# -*- coding: utf-8 -*-
"""文件操作工具。"""
from __future__ import annotations

import os
from pathlib import Path

from ..base import BaseTool


class AddFile(BaseTool):
    """创建文件并写入内容。
    
    Example:
        >>> tool = AddFile()
        >>> tool.execute(filename="test.txt", content="Hello World")
        '✅ 已创建文件 test.txt，写入 11 字符。'
    """

    def __init__(self) -> None:
        super().__init__(
            name="addFile",
            description="创建文件并写入内容",
            parameters={
                "type": "object",
                "properties": {
                    "filename": {
                        "type": "string",
                        "description": "文件名（可包含相对路径）",
                    },
                    "content": {
                        "type": "string",
                        "description": "文件内容",
                    },
                },
                "required": ["filename", "content"],
            },
        )

    def execute(self, filename: str, content: str) -> str:
        """创建文件并写入内容。
        
        Args:
            filename: 文件名
            content: 文件内容
            
        Returns:
            操作结果信息
        """
        try:
            # 确保父目录存在
            path = Path(filename)
            if path.parent and not path.parent.exists():
                path.parent.mkdir(parents=True, exist_ok=True)
            
            # 写入文件
            with open(filename, "w", encoding="utf-8") as f:
                f.write(content)
            
            return f"✅ 已创建文件 {filename}，写入 {len(content)} 字符。"
            
        except PermissionError:
            return f"❌ 权限不足：无法写入 {filename}"
        except Exception as e:
            return f"❌ 创建文件失败: {e}"


class ReadFile(BaseTool):
    """读取文件内容。
    
    Example:
        >>> tool = ReadFile()
        >>> tool.execute(filename="test.txt")
        'Hello World'
    """

    def __init__(self) -> None:
        super().__init__(
            name="read_file",
            description="读取文件内容",
            parameters={
                "type": "object",
                "properties": {
                    "filename": {
                        "type": "string",
                        "description": "文件路径",
                    },
                },
                "required": ["filename"],
            },
        )

    def execute(self, filename: str) -> str:
        """读取文件内容。
        
        Args:
            filename: 文件路径
            
        Returns:
            文件内容或错误信息
        """
        try:
            with open(filename, "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            return f"❌ 文件不存在: {filename}"
        except PermissionError:
            return f"❌ 权限不足：无法读取 {filename}"
        except Exception as e:
            return f"❌ 读取文件失败: {e}"

