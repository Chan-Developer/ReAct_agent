# -*- coding: utf-8 -*-
"""消息和对话管理。"""
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class Role(str, Enum):
    """对话角色"""
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"
    SYSTEM = "system"


@dataclass
class Message:
    """对话消息"""
    role: Role
    content: Optional[str] = None
    tool_calls: List[dict] = field(default_factory=list)
    name: Optional[str] = None  # 工具名

    def to_dict(self, compatible: bool = True) -> Dict[str, Any]:
        """转为 API 格式"""
        if compatible and self.role == Role.TOOL:
            return {
                "role": "user",
                "content": f"[工具 {self.name} 返回结果]\n{self.content}"
            }
        
        data = {"role": self.role.value}
        if self.content:
            data["content"] = self.content
        return data

    @classmethod
    def user(cls, content: str) -> "Message":
        return cls(Role.USER, content)

    @classmethod
    def assistant(cls, content: str = None, tool_calls: list = None) -> "Message":
        return cls(Role.ASSISTANT, content, tool_calls or [])

    @classmethod
    def tool(cls, name: str, content: str) -> "Message":
        return cls(Role.TOOL, content, name=name)


@dataclass
class Conversation:
    """对话管理器"""
    messages: List[Message] = field(default_factory=list)
    
    def add(self, msg: Message) -> None:
        self.messages.append(msg)
    
    def add_user(self, content: str) -> None:
        self.add(Message.user(content))
    
    def add_assistant(self, content: str = None, tool_calls: list = None) -> None:
        self.add(Message.assistant(content, tool_calls))
    
    def add_tool_result(self, name: str, content: str) -> None:
        self.add(Message.tool(name, content))
    
    def to_list(self) -> List[Dict]:
        return [m.to_dict() for m in self.messages]
    
    def clear(self) -> None:
        self.messages.clear()
    
    def __len__(self) -> int:
        return len(self.messages)
