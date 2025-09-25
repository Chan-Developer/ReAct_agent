import requests

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

if __name__ == "__main__":
    llm = VllmLLM()
    messages = [
        {"role": "user", "content": "Hello, how are you?"}
    ]
    print(llm.chat(messages))


