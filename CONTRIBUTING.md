# 贡献指南

感谢你对 Agent Framework 的关注！我们欢迎任何形式的贡献。

## 🚀 如何贡献

### 1. 报告 Bug

- 使用 [GitHub Issues](../../issues) 提交 Bug
- 描述复现步骤、期望行为、实际行为
- 附上环境信息（Python 版本、OS 等）

### 2. 提交功能建议

- 先在 Issues 中讨论你的想法
- 说明功能的使用场景和价值

### 3. 提交代码

```bash
# 1. Fork 并克隆
git clone https://github.com/YOUR_NAME/agent.git
cd agent

# 2. 创建分支
git checkout -b feature/your-feature

# 3. 安装开发依赖
pip install -r requirements.txt
pip install pytest

# 4. 开发 & 测试
python -m pytest tests/ -v

# 5. 提交
git add .
git commit -m "feat: 添加新功能"

# 6. 推送并创建 PR
git push origin feature/your-feature
```

## 📝 代码规范

### 命名

- 文件名：`snake_case.py`
- 类名：`PascalCase`
- 函数/变量：`snake_case`
- 常量：`UPPER_SNAKE_CASE`

### 结构

```python
# -*- coding: utf-8 -*-
"""模块说明。"""
from typing import List, Optional  # 标准库
import numpy as np                 # 第三方库
from core.task import Task         # 项目内部

class MyClass:
    """类说明。"""
    
    def my_method(self, param: str) -> bool:
        """方法说明。
        
        Args:
            param: 参数说明
            
        Returns:
            返回值说明
        """
        pass
```

### Commit 规范

使用 [Conventional Commits](https://www.conventionalcommits.org/):

| 类型 | 说明 |
|------|------|
| `feat` | 新功能 |
| `fix` | Bug 修复 |
| `docs` | 文档更新 |
| `refactor` | 重构 |
| `test` | 测试相关 |
| `chore` | 构建/工具 |

示例：
```
feat: 添加多模态 RAG 支持
fix: 修复 Embedding 维度不匹配问题
docs: 更新 README 快速开始部分
```

## 🧪 测试

提交 PR 前请确保：

```bash
# 运行所有测试
python -m pytest tests/ -v

# 检查覆盖率（可选）
python -m pytest tests/ --cov=. --cov-report=html
```

新功能请附带单元测试。

## 📁 项目结构

添加新功能时，请遵循现有结构：

```
agent/
├── core/           # 核心抽象（Task, Orchestrator）
├── agents/         # Agent 实现
│   └── crews/      # 多 Agent 团队
├── tools/          # 工具
├── llm/            # LLM 接口
├── knowledge/      # 知识库
└── tests/          # 测试
```

## 💬 联系

有问题？欢迎在 Issues 中讨论！

