from enum import Enum
from typing import List, Dict, Any

from llm_interface import VllmLLM
from .tools.base import BaseTool

__all__ = ["Role", "Message", "Agent"]


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

    def __init__(self, tools: list[BaseTool], llm: VllmLLM, max_rounds: int = 5):
        self.tools = {t.name: t for t in tools}
        self.llm = llm
        self.max_rounds = max_rounds
        self.conversation: list[Message] = []

    # --------- 公共接口 ---------
    def run(self, user_input: str) -> str:
        """整体执行流程：think/act 交替，直到 LLM 不再要求工具调用或达到迭代上限。"""
        self.conversation.append(Message.user("<question>"+user_input+"</question>"))

        for _ in range(self.max_rounds):
            llm_resp = self._think()
            print("llm_think_resp:",llm_resp)

            # 若包含工具调用
            tool_calls = llm_resp.get("tool_calls")
            print("tool_calls:",tool_calls)

            if tool_calls:
                self.conversation.append(
                    Message.assistant(llm_resp.get("content"), tool_calls)
                )
                self._act(tool_calls)
                print("self.conversation:",self.conversation)
                # 继续下一轮
                continue

            if "<final_answer>" in llm_resp.get("content"):
                self.conversation.append(Message.assistant(llm_resp.get("content")))
                return llm_resp.get("content", "")


        return "达到最大迭代次数，任务可能未完成"

    # --------- 内部方法 ---------
    def _think(self) -> dict:
        system_prompt = (
            """你需要解决一个问题。为此，你需要将任务分解为多个步骤，对于每个步骤，首先使用<thought> 思考要做什么，
               然后使用<action>调用一个工具，工具的执行结果会通过<observation>返回给你。持续这个思考和行动的过程，
               直到你有足够的信息来提供<final_answer>。
               所有步骤请严格使用以下json标签格式输出：
               <task>:用户提出的任务</task>
               <thought>:思考</thought>
               <action>:采取的工作操作</action>
               <observation>:工具或环境返回的结果</observation>
               <final_answer>:最终答案</final_answer>

              下面给出一个示例：
              <task>: "查询天气"</task>
              <thought>: "我需要获取北京今日天气"</thought>
              <action>: {"name":"get_weather","arguments":{"city":"北京","date":"2025-09-24"}}</action>
              <observation>: "北京晴 25℃"</observation>
              <thought>: "已获得天气，可以回答用户"</thought>
              <final_answer>: "北京今日天气为晴，气温约25℃"</final_answer>
              请严格遵守上述格式，不要添加任何其他内容。

              注意：
               <task>标签由用户提供，请不要擅自生成
               你每次回答都要包含两个标签，第一个是<thought>，第二个是<action>或<final_answer>
               如果<action>中的某个工具参数有多行的话，请使用\n来表示，如：
               <action>write_to_file("test.txt","a\nb\nc\n")</action>
            """
        )

        messages = []
        messages.append({"role": "system", "content": system_prompt})
        messages.extend([m.to_dict() for m in self.conversation])
        tools_info = [t.as_function_spec() for t in self.tools.values()]
        print("messages:",messages,"\n")
        print("tools_info:",tools_info,"\n")

        response = self.llm.chat(messages, tools_info)
        print("response:",response)
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
                except Exception as e:
                    result = f"工具执行失败: {e}"

            # 将工具结果写入对话历史
            self.conversation.append(Message.tool(name, str(result)))
