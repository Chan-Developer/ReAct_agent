"""
Base LLM Agent 基础类

定义所有简历处理Agent的通用接口和行为。
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Protocol
import json
import re

from common.logger import get_logger

logger = get_logger(__name__)


class LLMProtocol(Protocol):
    """LLM 协议接口"""
    def chat(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        ...


@dataclass
class AgentMessage:
    """Agent 消息"""
    role: str  # "system", "user", "assistant"
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentResult:
    """Agent 执行结果"""
    success: bool
    data: Dict[str, Any]
    reasoning: str = ""
    suggestions: List[str] = field(default_factory=list)
    error: Optional[str] = None


class BaseLLMAgent(ABC):
    """
    基础 LLM Agent 抽象类
    
    定义了 Agent 的通用行为：
    - 思考 (think): 分析输入并生成推理
    - 执行 (execute): 根据推理执行具体任务
    - 反思 (reflect): 评估执行结果并提供改进建议
    """
    
    def __init__(
        self,
        llm: LLMProtocol,
        name: str,
        role: str,
        system_prompt: str,
        max_retries: int = 2,
    ):
        self.llm = llm
        self.name = name
        self.role = role
        self.system_prompt = system_prompt
        self.max_retries = max_retries
        self.conversation_history: List[AgentMessage] = []
        
        logger.info(f"[{self.name}] Agent 初始化完成，角色: {self.role}")
    
    def _call_llm(self, prompt: str, use_system_prompt: bool = True) -> str:
        """调用 LLM
        
        自动适配不同 LLM 接口:
        - 如果 LLM 有 chat(messages) 方法，使用 messages 格式
        - 如果 LLM 有 chat(prompt, system_prompt) 方法，使用简单格式
        """
        try:
            # 构建消息列表
            messages = []
            if use_system_prompt and self.system_prompt:
                messages.append({"role": "system", "content": self.system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            # 尝试使用 messages 格式调用
            try:
                response = self.llm.chat(messages)
                # 处理返回值可能是 dict 或 str
                if isinstance(response, dict):
                    content = response.get("content", "")
                else:
                    content = str(response)
            except TypeError:
                # 回退到简单格式
                system = self.system_prompt if use_system_prompt else None
                response = self.llm.chat(prompt, system_prompt=system)
                content = str(response)
            
            # 记录对话历史
            self.conversation_history.append(AgentMessage(role="user", content=prompt))
            self.conversation_history.append(AgentMessage(role="assistant", content=content))
            
            return content
        except Exception as e:
            logger.error(f"[{self.name}] LLM 调用失败: {e}")
            raise
    
    def _parse_json_response(self, response: str) -> Dict[str, Any]:
        """从 LLM 响应中解析 JSON"""
        # 尝试提取 JSON 块
        json_patterns = [
            r"```json\s*([\s\S]*?)\s*```",
            r"```\s*([\s\S]*?)\s*```",
            r"\{[\s\S]*\}",
        ]
        
        for pattern in json_patterns:
            match = re.search(pattern, response)
            if match:
                try:
                    json_str = match.group(1) if "```" in pattern else match.group(0)
                    return json.loads(json_str)
                except json.JSONDecodeError:
                    continue
        
        # 如果无法解析，返回原始响应
        logger.warning(f"[{self.name}] 无法解析 JSON 响应，返回原始文本")
        return {"raw_response": response}
    
    @abstractmethod
    def think(self, input_data: Dict[str, Any]) -> str:
        """
        思考阶段：分析输入数据，生成推理过程
        
        Args:
            input_data: 输入数据
            
        Returns:
            推理过程描述
        """
        pass
    
    @abstractmethod
    def execute(self, input_data: Dict[str, Any], reasoning: str) -> AgentResult:
        """
        执行阶段：根据推理结果执行具体任务
        
        Args:
            input_data: 输入数据
            reasoning: 思考阶段的推理结果
            
        Returns:
            执行结果
        """
        pass
    
    def reflect(self, result: AgentResult) -> List[str]:
        """
        反思阶段：评估执行结果，提供改进建议
        
        Args:
            result: 执行结果
            
        Returns:
            改进建议列表
        """
        return result.suggestions
    
    def run(self, input_data: Dict[str, Any]) -> AgentResult:
        """
        运行 Agent 的完整流程：Think -> Execute -> Reflect
        
        Args:
            input_data: 输入数据
            
        Returns:
            最终执行结果
        """
        logger.info(f"[{self.name}] 开始执行任务...")
        
        for attempt in range(self.max_retries + 1):
            try:
                # Step 1: Think
                logger.debug(f"[{self.name}] 思考阶段 (尝试 {attempt + 1}/{self.max_retries + 1})")
                reasoning = self.think(input_data)
                
                # Step 2: Execute
                logger.debug(f"[{self.name}] 执行阶段")
                result = self.execute(input_data, reasoning)
                
                if result.success:
                    # Step 3: Reflect
                    suggestions = self.reflect(result)
                    result.suggestions = suggestions
                    logger.info(f"[{self.name}] 任务完成")
                    return result
                    
            except Exception as e:
                logger.warning(f"[{self.name}] 执行失败 (尝试 {attempt + 1}): {e}")
                if attempt == self.max_retries:
                    return AgentResult(
                        success=False,
                        data={},
                        error=str(e)
                    )
        
        return AgentResult(success=False, data={}, error="Max retries exceeded")
    
    def reset(self):
        """重置 Agent 状态"""
        self.conversation_history.clear()
        logger.debug(f"[{self.name}] 状态已重置")
