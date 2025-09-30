import requests
from openai import OpenAI

class VllmLLM:
    """使用本地 vllm OpenAI 兼容接口的 LLM 封装。"""

    def __init__(self, base_url: str = "http://localhost:8000/v1", model: str = "Qwen2.5-VL-7B/", timeout: int = 120):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = timeout

    def chat(self, messages, tools_info=None, temperature: float = 0.7, max_tokens: int = 1024):
        """
        与 vllm OpenAI 兼容 /chat/completions 端点通信。

        参数:
            messages (list[dict]): OpenAI 风格的消息列表。
            tools_info (list[dict]|None): OpenAI tools 参数，将直接传递给接口。
            temperature (float): 采样温度。
            max_tokens (int): 最大生成 token 数。

        返回:
            dict: 单条 message，对齐 OpenAI 返回格式，例如 
            {"role": "assistant", "content": "...", "tool_call_id": ...}
        """
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        url = f"{self.base_url}/chat/completions"
        try:
            resp = requests.post(url, json=payload, timeout=self.timeout)
            resp.raise_for_status()
        except Exception as err:
            raise RuntimeError(f"VllmLLM 请求失败: {err}\nURL: {url}\nPayload: {payload}") from err

        data = resp.json()
        if not data.get("choices"):
            raise RuntimeError(f"VllmLLM 返回数据异常: {data}")

        return data["choices"][0]["message"]


class ModelScopeOpenAI:
    """使用 ModelScope 云平台 OpenAI 兼容接口的 LLM 封装。"""

    def __init__(self, 
                 base_url: str = "https://api-inference.modelscope.cn/v1",
                 api_key: str = "ms-bd4a1d0f-6a29-4267-8ce7-aa7d981bf371",
                 model: str = "Qwen/Qwen3-VL-235B-A22B-Instruct"):
        """
        初始化 ModelScope OpenAI 客户端。
        
        参数:
            base_url (str): ModelScope API 基础URL。
            api_key (str): ModelScope Token。
            model (str): 模型ID。
        """
        self.client = OpenAI(
            base_url=base_url,
            api_key=api_key
        )
        self.model = model

    def chat(self, messages, stream: bool = False, temperature: float = 0.7, max_tokens: int = 1024):
        """
        与 ModelScope OpenAI 兼容接口通信。
        
        参数:
            messages (list[dict]): OpenAI 风格的消息列表，支持文本和图像。
            stream (bool): 是否启用流式输出。
            temperature (float): 采样温度。
            max_tokens (int): 最大生成 token 数。
            
        返回:
            如果 stream=False: dict，单条 message
            如果 stream=True: generator，流式返回内容
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                stream=stream,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            if stream:
                return response
            else:
                return {
                    "role": "assistant",
                    "content": response.choices[0].message.content
                }
                
        except Exception as err:
            raise RuntimeError(f"ModelScopeOpenAI 请求失败: {err}") from err

    def chat_stream(self, messages, temperature: float = 0.7, max_tokens: int = 1024):
        """
        流式聊天方法，返回生成器。
        
        参数:
            messages (list[dict]): OpenAI 风格的消息列表。
            temperature (float): 采样温度。
            max_tokens (int): 最大生成 token 数。
            
        返回:
            generator: 逐块返回内容字符串
        """
        response = self.chat(messages, stream=True, temperature=temperature, max_tokens=max_tokens)
        
        for chunk in response:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content


if __name__ == "__main__":
    # 测试本地 vllm
    print("=== 测试本地 VllmLLM ===")
    llm = VllmLLM()
    messages = [
        {"role": "user", "content": "Hello, how are you?"}
    ]
    print(llm.chat(messages))
    
    # 测试 ModelScope 云平台 API
    print("\n=== 测试 ModelScope 云平台 API ===")
    cloud_llm = ModelScopeOpenAI()
    
    # 文本对话示例
    text_messages = [
        {"role": "user", "content": "你好，请介绍一下自己"}
    ]
    print("文本对话:")
    print(cloud_llm.chat(text_messages))
    
    # 多模态（文本+图像）示例
    multimodal_messages = [{
        "role": "user",
        "content": [
            {
                "type": "text",
                "text": "描述这幅图"
            },
            {
                "type": "image_url",
                "image_url": {
                    "url": "https://modelscope.oss-cn-beijing.aliyuncs.com/demo/images/audrey_hepburn.jpg"
                }
            }
        ]
    }]
    print("\n多模态对话:")
    print(cloud_llm.chat(multimodal_messages))
    
    # 流式输出示例
    print("\n流式输出:")
    for content in cloud_llm.chat_stream(text_messages):
        print(content, end='', flush=True)
    print()


