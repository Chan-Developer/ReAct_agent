# -*- coding: utf-8 -*-
"""Message and conversation helpers."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class Role(str, Enum):
    """Conversation roles."""

    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"
    SYSTEM = "system"


@dataclass
class Message:
    """Structured conversation message."""

    role: Role
    content: Optional[str] = None
    tool_calls: List[dict] = field(default_factory=list)
    name: Optional[str] = None
    tool_call_id: Optional[str] = None

    def to_dict(self, compatible: bool = True) -> Dict[str, Any]:
        """Convert to provider-friendly message dict."""
        if compatible and self.role == Role.TOOL:
            return {
                "role": "user",
                "content": f"[tool {self.name} result]\n{self.content}",
            }

        data = {"role": self.role.value}
        if self.content is not None:
            data["content"] = self.content
        if self.tool_calls:
            data["tool_calls"] = self.tool_calls
        if self.name:
            data["name"] = self.name
        if self.tool_call_id:
            data["tool_call_id"] = self.tool_call_id
        return data

    @classmethod
    def user(cls, content: str) -> "Message":
        return cls(Role.USER, content)

    @classmethod
    def assistant(cls, content: str = None, tool_calls: list = None) -> "Message":
        return cls(Role.ASSISTANT, content, tool_calls or [])

    @classmethod
    def tool(cls, name: str, content: str, tool_call_id: str = None) -> "Message":
        return cls(Role.TOOL, content, name=name, tool_call_id=tool_call_id)


@dataclass
class Conversation:
    """In-memory conversation store."""

    messages: List[Message] = field(default_factory=list)

    def add(self, msg: Message) -> None:
        self.messages.append(msg)

    def add_user(self, content: str) -> None:
        self.add(Message.user(content))

    def add_assistant(self, content: str = None, tool_calls: list = None) -> None:
        self.add(Message.assistant(content, tool_calls))

    def add_tool_result(self, name: str, content: str, tool_call_id: str = None) -> None:
        self.add(Message.tool(name, content, tool_call_id=tool_call_id))

    def to_list(self, compatible: bool = True) -> List[Dict[str, Any]]:
        return [m.to_dict(compatible=compatible) for m in self.messages]

    def clear(self) -> None:
        self.messages.clear()

    def __len__(self) -> int:
        return len(self.messages)
