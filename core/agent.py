from enum import Enum
from typing import List, Dict, Any

import re, json

from llm_interface import VllmLLM
from .tools.base import BaseTool
from .prompt import react_system_prompt_template
__all__ = ["Role", "Message", "Agent"]
import os
from string import Template
import platform

class Role(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"
    SYSTEM = "system"


class Message:
    """统一的对话消息封装，可序列化为 OpenAI /chat/completions 接口格式。"""

    def __init__(self, role: Role, content: str | None = None):
        self.role = role
        self.content = content
        self.tool_calls: list[dict] = []
        self.name: str | None = None  # tool message 专用

    # ---------- 工具方法 ----------
    def to_dict(self) -> Dict[str, Any]:
        data: Dict[str, Any] = {
            "role": self.role.value,
            "content": self.content,
        }
        if self.tool_calls:
            data["tool_calls"] = self.tool_calls
        if self.name:
            data["name"] = self.name
        return data

    # ---------- 工厂方法 ----------
    @classmethod
    def user(cls, content: str) -> "Message":
        return cls(Role.USER, content)

    @classmethod
    def assistant(cls, content: str | None, tool_calls: list[dict] | None = None) -> "Message":
        msg = cls(Role.ASSISTANT, content)
        if tool_calls:
            msg.tool_calls = tool_calls
        return msg

    @classmethod
    def tool(cls, name: str, content: str) -> "Message":
        msg = cls(Role.TOOL, content)
        msg.name = name
        return msg


class Agent:
    """ReAct 风格、支持函数调用的简易 Agent。"""
    def __init__(self, tools: list[BaseTool], llm: VllmLLM, max_rounds: int = 5, project_directory: str = "."):
        self.tools = {t.name: t for t in tools}
        self.tools_info = [t.as_function_spec() for t in self.tools.values()]
        self.llm = llm
        self.max_rounds = max_rounds
        self.conversation: list[Message] = []
        self.system_prompt = None
        self.project_directory = project_directory

    # --------- 公共接口 ---------
    def _extract_tool_calls(self, content: str) -> list[dict]:
        """从 LLM 输出的 <action>...</action> 标签中解析工具调用信息。"""
        if not content:
            return []
        
        # 匹配 <action>function_name(arg1, arg2)</action> 格式
        match = re.search(r"<action>\s*([^<]+)\s*</action>", content)
        if not match:
            return []
        
        action_str = match.group(1).strip()
        print("action_str(待调用工具):", action_str, "\n")
        
        if not action_str:
            return []
            
        # 尝试解析函数调用格式：function_name(arg1="value1", arg2="value2")
        func_match = re.match(r'(\w+)\s*\((.*)\)$', action_str)
        if func_match:
            func_name = func_match.group(1)
            args_str = func_match.group(2).strip()
            
            # 简单解析参数（仅支持字符串参数）
            arguments = {}
            if args_str:
                # 分割参数，处理引号内的逗号
                import shlex
                try:
                    args_list = shlex.split(args_str.replace('=', ' '))
                    for i in range(0, len(args_list), 2):
                        if i + 1 < len(args_list):
                            key = args_list[i]
                            value = args_list[i + 1]
                            arguments[key] = value
                        else:
                            # 位置参数，根据实际工具名称映射参数
                            if func_name == "calculator" or func_name == "calculate_expression":
                                arguments["expression"] = args_list[i]
                            elif func_name == "search":
                                arguments["query"] = args_list[i]
                            elif func_name == "addFile":
                                if i == 0:
                                    arguments["filename"] = args_list[i]
                                elif i == 2:
                                    arguments["content"] = args_list[i]
                            else:
                                arguments[f"arg_{i//2}"] = args_list[i]
                except Exception:
                    # 简单情况：只有一个参数值，根据工具类型推断参数名
                    value = args_str.strip('"\'')
                    if func_name == "calculator" or func_name == "calculate_expression":
                        arguments["expression"] = value
                    elif func_name == "search":
                        arguments["query"] = value
                    else:
                        arguments["content"] = value
            
            # 规范化工具名称
            if func_name == "calculate_expression":
                func_name = "calculator"
                    
            return [{"name": func_name, "arguments": arguments}]
        
        # 如果无法解析，返回原始字符串
        return [{"name": "unknown", "arguments": {"raw": action_str}}]

    def get_operating_system_name(self):
        os_map = {
            "Darwin": "macOS",
            "Windows": "Windows",
            "Linux": "Linux"
        }

        return os_map.get(platform.system(), "Unknown")

    def render_system_prompt(self, system_prompt_template: str) -> str:
        """渲染系统提示模板，替换变量"""
        # 格式化工具列表为可读的字符串，包含实际的函数调用格式
        tool_descriptions = []
        for tool in self.tools_info:
            # 为每个工具生成详细的调用格式说明
            params = tool.get('parameters', {}).get('properties', {})
            param_list = []
            for param_name, param_info in params.items():
                param_list.append(f"{param_name}=\"value\"")
            param_str = ", ".join(param_list)
            tool_descriptions.append(f"- {tool['name']}({param_str}): {tool['description']}")
        tool_list = "\n".join(tool_descriptions)
        
        try:
            file_list = ", ".join(
                os.path.abspath(os.path.join(self.project_directory, f))
                for f in os.listdir(self.project_directory)
                if os.path.isfile(os.path.join(self.project_directory, f))
            )
        except Exception:
            file_list = "无法获取文件列表"
            
        return Template(system_prompt_template).substitute(
            operating_system=self.get_operating_system_name(),
            tool_list=tool_list,
            file_list=file_list
        )
    # 修改 run 方法中的逻辑
    def run(self, user_input: str) -> str:
        """整体执行流程：think/act 交替，直到 LLM 不再要求工具调用或达到迭代上限。"""
        self.conversation.append(Message.user(f"<question>{user_input}</question>"))
        system_prompt = self.render_system_prompt(react_system_prompt_template)
        self.system_prompt = system_prompt

        # print("-----","渲染系统提示模板","-----")
        # print("system_prompt:",system_prompt,"\n")

        for _ in range(self.max_rounds):
            print("------","执行think","------","\n")
            llm_resp = self._think()
            print("------","think完成","------","\n")

            content = llm_resp.get("content", "")
            print("content(LLM响应):",content,"\n")
            tool_calls = self._extract_tool_calls(content)

            if tool_calls:
                # 将原始内容存入对话（不包含tool_calls，因为格式不兼容OpenAI API）
                self.conversation.append(Message.assistant(content))
                print("------","执行act","------","\n")
                self._act(tool_calls)
                print("------","act完成","------","\n")
                continue  # 继续下一轮思考

            if "<final_answer>" in content:
                self.conversation.append(Message.assistant(content))
                return content

        return "达到最大迭代次数，任务可能未完成"

    # --------- 内部方法 ---------
    def _think(self) -> dict:
        
        messages = []
        messages.append({"role": "system", "content": self.system_prompt})
        messages.extend([m.to_dict() for m in self.conversation])

        response = self.llm.chat(messages)
        print("think_response:",response)
        return response

    def _act(self, tool_calls: list[dict]):
        
        for tc in tool_calls:
            name = tc["name"]
            args = tc.get("arguments", {})
            tool = self.tools.get(name)
            if tool is None:
                result = f"未找到工具: {name}"
            else:
                try:
                    result = tool.execute(**args)
                    print("tool_result:",result,"\n")
                except Exception as e:
                    result = f"工具执行失败: {e}"

            # 将工具结果写入对话历史
            self.conversation.append(Message.tool(name, str(result)))

