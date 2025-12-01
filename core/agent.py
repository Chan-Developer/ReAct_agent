from enum import Enum
from typing import List, Dict, Any, Optional
import logging
import re
import json

from llm_interface import VllmLLM
from .tools.base import BaseTool
from .tool_registry import ToolRegistry
from .prompt import react_system_prompt_template

__all__ = ["Role", "Message", "Agent"]

import os
from string import Template
import platform

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

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
        self.tool_calls: List[dict] = []
        self.name: Optional[str] = None  # tool message 专用
        self.tool_call_id: Optional[str] = None  # tool message 专用

    # ---------- 工具方法 ----------
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式，用于发送给 LLM。
        
        注意: vllm 不支持 tool 角色和相关字段。
        - tool 角色会转换为 user 角色，内容添加前缀说明
        - 不包含 tool_calls 和 tool_call_id
        """
        # vllm 不支持 tool 角色，转换为 user 角色
        if self.role == Role.TOOL:
            role = "user"
            # 添加工具结果的前缀，让模型知道这是工具返回
            tool_name = self.name or "unknown"
            content = f"[工具 {tool_name} 返回结果]\n{self.content}"
        else:
            role = self.role.value
            content = self.content
        
        data: Dict[str, Any] = {
            "role": role,
        }
        
        # content 必须存在
        if content is not None:
            data["content"] = content
            
        # 以下字段 vllm 不支持，不添加到 data 中
        # if self.name:
        #     data["name"] = self.name
        # if self.tool_calls:
        #     data["tool_calls"] = self.tool_calls
        # if self.tool_call_id:
        #     data["tool_call_id"] = self.tool_call_id
            
        return data

    # ---------- 工厂方法 ----------
    @classmethod
    def user(cls, content: str) -> "Message":
        return cls(Role.USER, content)

    @classmethod
    def assistant(cls, content: str | None, tool_calls: List[dict] | None = None) -> "Message":
        msg = cls(Role.ASSISTANT, content)
        if tool_calls:
            msg.tool_calls = tool_calls
        return msg

    @classmethod
    def tool(cls, name: str, content: str, tool_call_id: str | None = None) -> "Message":
        msg = cls(Role.TOOL, content)
        msg.name = name
        if tool_call_id:
            msg.tool_call_id = tool_call_id
        return msg


class Agent:
    """ReAct 风格、支持函数调用的简易 Agent。
    
    支持两种初始化方式:
    1. 直接传入工具列表: Agent(tools=[tool1, tool2], llm=llm)
    2. 使用工具注册器: Agent(tool_registry=registry, llm=llm)
    """
    def __init__(
        self, 
        llm: VllmLLM,
        tools: Optional[List[BaseTool]] = None,
        tool_registry: Optional[ToolRegistry] = None,
        max_rounds: int = 5, 
        project_directory: str = "."
    ):
        """
        初始化 Agent。
        
        参数:
            llm: LLM 接口实例
            tools: 工具列表（可选，与 tool_registry 二选一）
            tool_registry: 工具注册器（可选，与 tools 二选一）
            max_rounds: 最大思考轮数
            project_directory: 项目目录
        """
        self.llm = llm
        self.max_rounds = max_rounds
        self.project_directory = project_directory
        
        # 工具管理
        if tool_registry is not None:
            self.tool_registry = tool_registry
        elif tools is not None:
            self.tool_registry = ToolRegistry()
            self.tool_registry.register_tools(tools)
        else:
            # 如果都没提供，创建空的注册器
            self.tool_registry = ToolRegistry()
            logger.warning("未提供工具，Agent 将在无工具模式下运行")
        
        # 对话历史
        self.conversation: List[Message] = []
        self.system_prompt = None
        
        logger.info(f"Agent 初始化完成，已注册 {len(self.tool_registry)} 个工具: {self.tool_registry}")

    # --------- 工具调用解析 ---------
    def _extract_tool_calls_from_native(self, llm_response: dict) -> Optional[List[dict]]:
        """从 LLM 响应中提取工具调用信息。
        
        支持两种方式：
        1. 原生 tool_calls 字段（OpenAI API 标准格式）
        2. 从文本内容中解析 JSON 格式的工具调用
        """
        # 方式1: 尝试从 tool_calls 字段提取（标准 OpenAI 格式）
        tool_calls = llm_response.get("tool_calls")
        if tool_calls:
            parsed_calls = []
            for tc in tool_calls:
                try:
                    func_info = tc.get("function", {})
                    name = func_info.get("name")
                    arguments_str = func_info.get("arguments", "{}")
                    
                    # 解析 JSON 参数
                    if isinstance(arguments_str, str):
                        arguments = json.loads(arguments_str)
                    else:
                        arguments = arguments_str
                    
                    parsed_calls.append({
                        "id": tc.get("id"),
                        "name": name,
                        "arguments": arguments
                    })
                    logger.info(f"解析到工具调用: {name}({arguments})")
                except json.JSONDecodeError as e:
                    logger.error(f"工具调用参数解析失败: {e}, 原始数据: {tc}")
                    continue
            
            return parsed_calls if parsed_calls else None
        
        # 方式2: 从文本内容中解析工具调用
        content = llm_response.get("content", "")
        if not content:
            return None
        
        # 尝试匹配 JSON 格式的函数调用
        # 格式: {"name": "tool_name", "arguments": {"arg1": "value1"}}
        import re
        
        # 匹配 JSON 对象的模式，支持嵌套
        # 使用更宽松的匹配，允许换行和空格
        json_pattern = r'\{\s*"name"\s*:\s*"([^"]+)"\s*,\s*"arguments"\s*:\s*(\{[^}]*\})\s*\}'
        matches = re.findall(json_pattern, content, re.DOTALL)
        
        if matches:
            parsed_calls = []
            for match in matches:
                try:
                    tool_name = match[0]
                    args_str = match[1]
                    
                    # 解析参数 JSON
                    arguments = json.loads(args_str) if args_str.strip() else {}
                    
                    parsed_calls.append({
                        "id": None,
                        "name": tool_name,
                        "arguments": arguments
                    })
                    logger.info(f"从文本解析到工具调用: {tool_name}({arguments})")
                except (json.JSONDecodeError, IndexError) as e:
                    logger.warning(f"解析工具调用失败: {e}, 原始匹配: {match}")
                    continue
            
            return parsed_calls if parsed_calls else None
        
        # 如果上面的模式没匹配到，尝试更简单的模式
        # 匹配整个 JSON 对象
        simple_pattern = r'\{[^}]*"name"[^}]*\}'
        for match in re.finditer(simple_pattern, content):
            try:
                json_str = match.group(0)
                call_data = json.loads(json_str)
                if "name" in call_data:
                    logger.info(f"从文本解析到工具调用: {call_data['name']}({call_data.get('arguments', {})})")
                    return [{
                        "id": None,
                        "name": call_data["name"],
                        "arguments": call_data.get("arguments", {})
                    }]
            except json.JSONDecodeError:
                continue
        
        return None
    

    def get_operating_system_name(self):
        os_map = {
            "Darwin": "macOS",
            "Windows": "Windows",
            "Linux": "Linux"
        }

        return os_map.get(platform.system(), "Unknown")

    def render_system_prompt(self, system_prompt_template: str) -> str:
        """渲染系统提示模板，替换变量"""
        # 从工具注册器获取工具列表
        tools = self.tool_registry.get_all_tools()
        
        # 格式化工具列表为可读的字符串
        tool_descriptions = []
        for tool in tools:
            spec = tool.as_function_spec()
            params = spec.get('parameters', {}).get('properties', {})
            param_list = []
            for param_name, param_info in params.items():
                param_desc = param_info.get('description', '')
                param_list.append(f"{param_name}: {param_desc}")
            param_str = ", ".join(param_list) if param_list else "无参数"
            tool_descriptions.append(
                f"- {spec['name']}: {spec['description']}\n  参数: {param_str}"
            )
        tool_list = "\n".join(tool_descriptions) if tool_descriptions else "无可用工具"
        
        try:
            file_list = ", ".join(
                os.path.abspath(os.path.join(self.project_directory, f))
                for f in os.listdir(self.project_directory)
                if os.path.isfile(os.path.join(self.project_directory, f))
            )
        except Exception as e:
            logger.warning(f"获取文件列表失败: {e}")
            file_list = "无法获取文件列表"
            
        return Template(system_prompt_template).substitute(
            operating_system=self.get_operating_system_name(),
            tool_list=tool_list,
            file_list=file_list
        )
    # --------- 主运行流程 ---------
    def run(self, user_input: str) -> str:
        """
        整体执行流程：think/act 交替，直到 LLM 不再要求工具调用或达到迭代上限。
        
        参数:
            user_input: 用户输入的问题
            
        返回:
            str: Agent 的最终回答
        """
        logger.info(f"开始处理用户输入: {user_input}")
        
        # 添加用户消息
        self.conversation.append(Message.user(user_input))
        
        # 渲染系统提示
        system_prompt = self.render_system_prompt(react_system_prompt_template)
        self.system_prompt = system_prompt
        logger.debug(f"System Prompt: {system_prompt}")

        # 迭代思考-行动循环
        for round_num in range(1, self.max_rounds + 1):
            logger.info(f"====== 第 {round_num}/{self.max_rounds} 轮 ======")
            
            try:
                llm_resp = self._think()
            except Exception as e:
                logger.error(f"LLM 调用失败: {e}", exc_info=True)
                return f"抱歉，处理过程中出现错误: {e}"

            content = llm_resp.get("content", "")
            logger.info(f"LLM 响应: {content}")
            
            # 尝试提取工具调用
            tool_calls = self._extract_tool_calls_from_native(llm_resp)

            # 如果有工具调用，执行工具
            if tool_calls:
                assistant_msg = Message.assistant(content, tool_calls)
                self.conversation.append(assistant_msg)
                
                logger.info(f"检测到 {len(tool_calls)} 个工具调用")
                self._act(tool_calls)
                continue  

            # 检查是否有最终答案
            if "final_answer" in content.lower():
                self.conversation.append(Message.assistant(content))
                logger.info("任务完成，返回最终答案")
                return content

            # 如果没有工具调用也没有最终答案
            # 在最后一轮或者模型给出了有意义的回答时，直接返回
            self.conversation.append(Message.assistant(content))
            
            # 如果是最后一轮，返回当前内容
            if round_num == self.max_rounds:
                logger.info("达到最大轮数，返回当前回答")
                return content
            

        logger.warning("达到最大迭代次数，任务可能未完成")
        return "达到最大迭代次数，任务可能未完成。请尝试简化问题或增加 max_rounds 参数。"

    # --------- 内部方法 ---------
    def _think(self) -> dict:
        """调用 LLM 进行思考。"""
        messages = []
        messages.append({"role": "system", "content": self.system_prompt})
        messages.extend([m.to_dict() for m in self.conversation])

        try:
            response = self.llm.chat(messages)
            logger.debug(f"LLM 返回: {response}")
            return response
        except Exception as e:
            logger.error(f"LLM 调用失败: {e}", exc_info=True)
            raise

    def _act(self, tool_calls: List[dict]):
        """执行工具调用。"""
        for tc in tool_calls:
            name = tc["name"]
            args = tc.get("arguments", {})
            tool_call_id = tc.get("id")
            
            logger.info(f"执行工具: {name}, 参数: {args}")
            
            tool = self.tool_registry.get_tool(name)
            
            if tool is None:
                result = f"❌ 错误: 未找到工具 '{name}'。可用工具: {list(self.tool_registry._tools.keys())}"
                logger.error(result)
            else:
                try:
                    result = tool.execute(**args)
                    logger.info(f"工具 {name} 执行成功: {result}")
                except TypeError as e:
                    result = f"❌ 参数错误: {e}。工具 '{name}' 需要的参数: {tool.parameters}"
                    logger.error(result, exc_info=True)
                except Exception as e:
                    result = f"❌ 工具执行失败: {type(e).__name__}: {e}"
                    logger.error(result, exc_info=True)

            # 将工具结果写入对话历史
            tool_msg = Message.tool(name, str(result))
            if tool_call_id:
                # 如果有 tool_call_id，添加到消息中（OpenAI 格式要求）
                tool_msg.tool_call_id = tool_call_id
            self.conversation.append(tool_msg)

