# -*- coding: utf-8 -*-
"""工具测试模块。"""
import pytest
from tools.builtin import Calculator, Search, AddFile, ReadFile
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


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

