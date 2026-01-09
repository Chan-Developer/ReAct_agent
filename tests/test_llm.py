# -*- coding: utf-8 -*-
"""LLM 模块测试。

测试内容：
- VllmLLM
- ModelScopeOpenAI
"""
import pytest
from unittest.mock import MagicMock, patch


# =============================================================================
# VllmLLM 测试
# =============================================================================

class TestVllmLLM:
    """VllmLLM 测试"""
    
    def test_init(self):
        """测试初始化"""
        from llm import VllmLLM
        
        llm = VllmLLM(
            base_url="http://localhost:8000/v1",
            model="test-model",
            timeout=60
        )
        
        assert llm.base_url == "http://localhost:8000/v1"
        assert llm.model == "test-model"
        assert llm.timeout == 60
    
    def test_init_default(self):
        """测试默认初始化"""
        from llm import VllmLLM
        
        llm = VllmLLM()
        
        assert "localhost:8000" in llm.base_url
    
    @patch('requests.post')
    def test_chat(self, mock_post):
        """测试 chat 方法"""
        from llm import VllmLLM
        
        # 模拟响应
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [
                {"message": {"role": "assistant", "content": "你好！"}}
            ]
        }
        mock_post.return_value = mock_response
        
        llm = VllmLLM()
        result = llm.chat([{"role": "user", "content": "你好"}])
        
        assert result["content"] == "你好！"
        mock_post.assert_called_once()
    
    @patch('requests.post')
    def test_chat_with_params(self, mock_post):
        """测试带参数的 chat"""
        from llm import VllmLLM
        
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "response"}}]
        }
        mock_post.return_value = mock_response
        
        llm = VllmLLM()
        llm.chat(
            messages=[{"role": "user", "content": "test"}],
            temperature=0.5,
            max_tokens=100,
        )
        
        # 验证参数传递
        call_args = mock_post.call_args
        payload = call_args.kwargs.get('json') or call_args[1].get('json')
        assert payload["temperature"] == 0.5
        assert payload["max_tokens"] == 100
    
    @patch('requests.post')
    def test_chat_timeout(self, mock_post):
        """测试超时处理"""
        from llm import VllmLLM
        import requests
        
        mock_post.side_effect = requests.exceptions.Timeout()
        
        llm = VllmLLM(timeout=1)
        
        with pytest.raises(RuntimeError) as exc_info:
            llm.chat([{"role": "user", "content": "test"}])
        
        assert "超时" in str(exc_info.value)
    
    @patch('requests.post')
    def test_chat_connection_error(self, mock_post):
        """测试连接错误"""
        from llm import VllmLLM
        import requests
        
        mock_post.side_effect = requests.exceptions.ConnectionError()
        
        llm = VllmLLM()
        
        with pytest.raises(RuntimeError) as exc_info:
            llm.chat([{"role": "user", "content": "test"}])
        
        assert "连接失败" in str(exc_info.value)
    
    @patch('requests.post')
    def test_chat_empty_response(self, mock_post):
        """测试空响应处理"""
        from llm import VllmLLM
        
        mock_response = MagicMock()
        mock_response.json.return_value = {"choices": []}
        mock_post.return_value = mock_response
        
        llm = VllmLLM()
        
        with pytest.raises(RuntimeError) as exc_info:
            llm.chat([{"role": "user", "content": "test"}])
        
        assert "异常" in str(exc_info.value)


# =============================================================================
# ModelScopeOpenAI 测试
# =============================================================================

class TestModelScopeOpenAI:
    """ModelScopeOpenAI 测试"""
    
    def test_init_with_param(self):
        """测试带参数初始化"""
        from llm import ModelScopeOpenAI
        
        llm = ModelScopeOpenAI(api_key="my-key", model="Qwen-7B")
        
        assert llm.api_key == "my-key"
        assert llm.model == "Qwen-7B"
    
    def test_api_key_priority(self):
        """测试 API Key 优先级：参数 > 配置"""
        from llm import ModelScopeOpenAI
        
        # 显式传入的参数应该覆盖配置
        llm = ModelScopeOpenAI(api_key="explicit-key")
        assert llm.api_key == "explicit-key"
    
    def test_model_can_be_set(self):
        """测试可以设置模型"""
        from llm import ModelScopeOpenAI
        
        llm = ModelScopeOpenAI(api_key="test", model="custom-model")
        assert llm.model == "custom-model"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

