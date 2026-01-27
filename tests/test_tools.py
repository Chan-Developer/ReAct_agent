# -*- coding: utf-8 -*-
"""工具测试模块。"""
import pytest
from unittest.mock import patch, MagicMock
from tools.builtin import Calculator, Search, AddFile, ReadFile
from tools.builtin import TavilySearch, DuckDuckGoSearch, WebSearch
from tools import ToolRegistry


class TestCalculator:
    """计算器工具测试"""
    
    def setup_method(self):
        self.calc = Calculator()
    
    def test_basic_addition(self):
        result = self.calc.execute("1+1")
        assert "= 2" in result
    
    def test_multiplication(self):
        result = self.calc.execute("3*7+2")
        assert "= 23" in result
    
    def test_division(self):
        result = self.calc.execute("10/2")
        assert "= 5" in result
    
    def test_parentheses(self):
        result = self.calc.execute("(10+5)/3")
        assert "= 5" in result
    
    def test_unsafe_expression(self):
        result = self.calc.execute("import os")
        assert "不安全" in result


class TestSearch:
    """搜索工具测试"""
    
    def setup_method(self):
        self.search = Search()
    
    def test_known_query(self):
        result = self.search.execute("python")
        assert "Python" in result
    
    def test_unknown_query(self):
        result = self.search.execute("unknown_query")
        assert "未找到" in result


class TestToolRegistry:
    """工具注册器测试"""
    
    def setup_method(self):
        self.registry = ToolRegistry()
    
    def test_register_tool(self):
        calc = Calculator()
        self.registry.register(calc)
        assert "calculator" in self.registry
    
    def test_get_tool(self):
        calc = Calculator()
        self.registry.register(calc)
        tool = self.registry.get("calculator")
        assert tool is calc
    
    def test_get_nonexistent_tool(self):
        tool = self.registry.get("nonexistent")
        assert tool is None
    
    def test_register_duplicate(self):
        calc1 = Calculator()
        calc2 = Calculator()
        self.registry.register(calc1)
        with pytest.raises(ValueError):
            self.registry.register(calc2)


class TestTavilySearch:
    """Tavily 搜索工具测试"""
    
    def setup_method(self):
        self.search = TavilySearch(api_key="test-api-key")
    
    def test_init_with_api_key(self):
        assert self.search.api_key == "test-api-key"
        assert self.search.name == "tavily_search"
    
    def test_init_without_api_key(self):
        with patch.dict("os.environ", {}, clear=True):
            search = TavilySearch()
            assert search.api_key == ""
    
    def test_execute_without_api_key(self):
        with patch.dict("os.environ", {}, clear=True):
            search = TavilySearch(api_key="")
            result = search.execute("test query")
            assert "未配置 TAVILY_API_KEY" in result
    
    @patch("tools.builtin.web_search.requests.post")
    def test_execute_success(self, mock_post):
        """测试成功搜索"""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "answer": "Python 是一种编程语言",
            "results": [
                {
                    "title": "Python 官网",
                    "url": "https://python.org",
                    "content": "Python is a programming language."
                }
            ]
        }
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response
        
        result = self.search.execute("Python")
        
        assert "搜索: Python" in result
        assert "Python 是一种编程语言" in result
        assert "Python 官网" in result
    
    @patch("tools.builtin.web_search.requests.post")
    def test_execute_timeout(self, mock_post):
        """测试超时处理"""
        import requests
        mock_post.side_effect = requests.exceptions.Timeout()
        
        result = self.search.execute("test")
        assert "超时" in result
    
    @patch("tools.builtin.web_search.requests.post")
    def test_execute_request_error(self, mock_post):
        """测试请求错误处理"""
        import requests
        mock_post.side_effect = requests.exceptions.RequestException("Network error")
        
        result = self.search.execute("test")
        assert "请求失败" in result
    
    def test_as_function_spec(self):
        """测试函数规格导出"""
        spec = self.search.as_function_spec()
        assert spec["name"] == "tavily_search"
        assert "query" in spec["parameters"]["properties"]


class TestDuckDuckGoSearch:
    """DuckDuckGo 搜索工具测试"""
    
    def setup_method(self):
        self.search = DuckDuckGoSearch()
    
    def test_init(self):
        assert self.search.name == "duckduckgo_search"
        assert self.search.default_max_results == 5
    
    def test_init_with_max_results(self):
        search = DuckDuckGoSearch(max_results=10)
        assert search.default_max_results == 10
    
    @patch("ddgs.DDGS")
    def test_execute_success(self, mock_ddgs_class):
        """测试成功搜索"""
        # 设置 mock
        mock_ddgs = MagicMock()
        mock_ddgs.text.return_value = [
            {
                "title": "Python 教程",
                "href": "https://example.com/python",
                "body": "学习 Python 编程的教程。"
            },
            {
                "title": "Python 官网",
                "href": "https://python.org",
                "body": "Python 官方网站。"
            }
        ]
        mock_ddgs_class.return_value = mock_ddgs
        
        result = self.search.execute("Python 教程", max_results=2)
        
        assert "搜索: Python 教程" in result
        assert "Python 教程" in result
        assert "https://example.com/python" in result
    
    @patch("ddgs.DDGS")
    def test_execute_no_results(self, mock_ddgs_class):
        """测试无结果"""
        mock_ddgs = MagicMock()
        mock_ddgs.text.return_value = []
        mock_ddgs_class.return_value = mock_ddgs
        
        result = self.search.execute("xyzabc123456")
        assert "未找到相关结果" in result
    
    @patch("ddgs.DDGS")
    def test_execute_error(self, mock_ddgs_class):
        """测试异常处理"""
        mock_ddgs_class.side_effect = Exception("Search error")
        
        result = self.search.execute("test")
        assert "搜索出错" in result
    
    def test_as_function_spec(self):
        """测试函数规格导出"""
        spec = self.search.as_function_spec()
        assert spec["name"] == "duckduckgo_search"
        assert "query" in spec["parameters"]["properties"]
        assert "max_results" in spec["parameters"]["properties"]


class TestWebSearch:
    """统一搜索接口测试"""
    
    def test_auto_select_duckduckgo(self):
        """测试自动选择 DuckDuckGo（无 API Key）"""
        with patch.dict("os.environ", {}, clear=True):
            search = WebSearch()
            assert search.provider == "duckduckgo"
    
    def test_auto_select_tavily(self):
        """测试自动选择 Tavily（有 API Key）"""
        search = WebSearch(api_key="test-key")
        assert search.provider == "tavily"
    
    def test_explicit_provider_duckduckgo(self):
        """测试显式指定 DuckDuckGo"""
        search = WebSearch(provider="duckduckgo", api_key="test-key")
        assert search.provider == "duckduckgo"
    
    def test_explicit_provider_tavily(self):
        """测试显式指定 Tavily"""
        search = WebSearch(provider="tavily", api_key="test-key")
        assert search.provider == "tavily"
    
    def test_name_and_description(self):
        """测试工具名称和描述"""
        search = WebSearch()
        assert search.name == "web_search"
        assert "联网搜索" in search.description
    
    @patch.object(DuckDuckGoSearch, "execute")
    def test_execute_delegates_to_backend(self, mock_execute):
        """测试执行委托给后端"""
        mock_execute.return_value = "搜索结果"
        
        search = WebSearch(provider="duckduckgo")
        result = search.execute("test query")
        
        mock_execute.assert_called_once_with("test query", None)
        assert result == "搜索结果"


class TestWebSearchIntegration:
    """联网搜索集成测试（需要网络，可选跳过）"""
    
    @pytest.mark.skipif(
        True,  # 默认跳过，避免 CI 中的网络问题
        reason="跳过网络集成测试"
    )
    def test_real_duckduckgo_search(self):
        """真实 DuckDuckGo 搜索测试"""
        search = DuckDuckGoSearch()
        result = search.execute("Python programming", max_results=2)
        
        assert "搜索: Python programming" in result
        assert "搜索结果" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

