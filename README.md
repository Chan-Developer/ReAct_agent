# 🤖 ReAct Agent

基于 ReAct（Reasoning + Acting）模式的智能代理框架，支持工具调用和多轮对话。

## ✨ 特性

- 🧠 **ReAct 模式**：思考 → 行动 → 观察 → 最终答案
- 🤖 **多 Agent 协作**：ContentAgent + LayoutAgent 智能简历优化
- 🔧 **工具调用**：支持计算器、搜索、文件操作、文档生成等
- 🔌 **多 LLM 支持**：ModelScope 云端 / 本地 vLLM
- 📝 **简历生成**：AI 优化内容 + 智能布局编排
- 🏗️ **模块化设计**：易于扩展和定制

## 📁 项目结构

```
agent/
├── core/                   # 核心业务逻辑
│   ├── agent.py           # Agent 核心类
│   ├── message.py         # 消息和对话
│   └── parser.py          # 工具调用解析
│
├── agents/                 # 多 Agent 系统 ⭐ NEW
│   ├── base.py            # Agent 基类 (Think→Execute→Reflect)
│   ├── content_agent.py   # 内容优化专家
│   ├── layout_agent.py    # 布局编排专家
│   └── orchestrator.py    # 多 Agent 协调器
│
├── common/                 # 基础设施
│   ├── config.py          # 配置管理
│   ├── logger.py          # 日志管理
│   └── exceptions.py      # 自定义异常
│
├── prompts/                # 提示词模板
│   ├── agent.py           # Agent 系统提示
│   └── resume.py          # 简历优化提示
│
├── llm/                    # LLM 接口
│   ├── base.py            # LLM 抽象基类
│   ├── vllm.py            # vLLM 本地服务
│   └── modelscope.py      # ModelScope 云端
│
├── tools/                  # 工具模块
│   ├── base.py            # 工具基类
│   ├── registry.py        # 工具注册器
│   ├── builtin/           # 内置工具
│   └── generators/        # 生成器工具
│
├── tests/                  # 测试
├── configs/                # 配置文件
├── scripts/                # 脚本
├── output/                 # 输出目录
│
├── main.py                 # CLI 入口
├── pyproject.toml          # 项目配置
└── requirements.txt        # 依赖
```

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt

# 如需生成 Word 简历
pip install python-docx
```

### 2. 配置 API Key

```bash
export MODELSCOPE_API_KEY="your-api-key"
```

### 3. 运行

```bash
# 基本使用
python main.py --prompt "计算 3*7+2 的结果"

# 生成简历
python main.py --prompt "帮我生成一份简历，我叫张三，电子科技大学硕士"

# 调试模式
python main.py --prompt "你好" --debug

# 使用本地 vLLM
python main.py --local --prompt "你好"
```

## 🤖 多 Agent 简历生成

### 快速启动

```bash
# 多 Agent 模式（推荐）
python scripts/run_resume_agent.py --name "陈亮江" --school "电子科技大学" --major "电子信息"

# 自定义样式
python scripts/run_resume_agent.py --name "张三" --style professional

# 简单模式（不使用 AI）
python scripts/run_resume_agent.py --name "李四" --simple
```

### 参数说明

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `--name` | 陈亮江 | 姓名 |
| `--school` | 电子科技大学 | 学校 |
| `--major` | 电子信息 | 专业 |
| `--output` | ./output | 输出目录 |
| `--style` | modern | 样式 (modern/classic/minimal/professional) |
| `--simple` | - | 简单模式，跳过 AI 优化 |

### 多 Agent 架构

```
┌─────────────────────────────────────────────────────────┐
│              ResumeAgentOrchestrator                     │
│                   (多 Agent 协调器)                       │
└────────────────────────┬────────────────────────────────┘
                         │
         ┌───────────────┴───────────────┐
         │                               │
         ▼                               ▼
┌─────────────────────┐       ┌─────────────────────┐
│    ContentAgent     │       │    LayoutAgent      │
│   (内容优化专家)     │       │   (布局编排专家)     │
├─────────────────────┤       ├─────────────────────┤
│ • 成就量化           │       │ • 章节排序优化       │
│ • STAR 法则重构      │       │ • 视觉层次设计       │
│ • 关键词优化         │       │ • 内容密度调整       │
│ • 个人简介润色       │       │ • 样式配置生成       │
└─────────────────────┘       └─────────────────────┘
         │                               │
         └───────────────┬───────────────┘
                         ▼
              ┌─────────────────────┐
              │   优化后的简历数据    │
              │   + 布局配置         │
              │   + 改进建议         │
              └─────────────────────┘
```

### 代码示例

```python
from llm import ModelScopeOpenAI
from agents import ResumeAgentOrchestrator

# 创建 LLM 和协调器
llm = ModelScopeOpenAI()
orchestrator = ResumeAgentOrchestrator(
    llm=llm,
    enable_content_optimization=True,
    enable_layout_optimization=True,
)

# 原始简历数据
resume_data = {
    "name": "张三",
    "summary": "软件工程师",
    "projects": [{"name": "项目A", "description": "做了一些事情"}]
}

# 运行优化
result = orchestrator.optimize(resume_data)

if result.success:
    print(f"优化耗时: {result.execution_time:.2f}s")
    print(f"优化后简历: {result.optimized_resume}")
    print(f"布局配置: {result.layout_config}")
    print(f"内容建议: {result.content_suggestions}")
```

## 🔧 扩展工具

### 创建自定义工具

```python
from tools.base import BaseTool

class MyTool(BaseTool):
    def __init__(self):
        super().__init__(
            name="my_tool",
            description="我的自定义工具",
            parameters={
                "type": "object",
                "properties": {
                    "param1": {
                        "type": "string",
                        "description": "参数说明"
                    }
                },
                "required": ["param1"]
            }
        )

    def execute(self, param1: str) -> str:
        return f"处理结果: {param1}"
```

### 注册工具

```python
from tools import ToolRegistry, Calculator
from my_tools import MyTool

registry = ToolRegistry()
registry.register_tools([
    Calculator(),
    MyTool(),
])
```

## 🏗️ 架构设计

```
┌─────────────────────────────────────────────────┐
│                   main.py                       │
│                  (CLI 入口)                      │
└──────────────────────┬──────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────┐
│                    Agent                         │
│  ┌─────────────────────────────────────────┐    │
│  │  思考(Think) → 行动(Act) → 观察(Observe) │    │
│  └─────────────────────────────────────────┘    │
└───────┬────────────────────────────┬────────────┘
        │                            │
┌───────▼───────┐          ┌─────────▼─────────┐
│      LLM      │          │   ToolRegistry    │
│  ┌─────────┐  │          │  ┌─────────────┐  │
│  │ vLLM    │  │          │  │ Calculator  │  │
│  ├─────────┤  │          │  ├─────────────┤  │
│  │ModelScope│ │          │  │ Search      │  │
│  └─────────┘  │          │  ├─────────────┤  │
└───────────────┘          │  │ AddFile     │  │
                           │  ├─────────────┤  │
                           │  │ Resume Gen  │◄─┼── 多 Agent 优化
                           │  └─────────────┘  │
                           └───────────────────┘
```

## 📋 配置说明

### 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `MODELSCOPE_API_KEY` | ModelScope API 密钥 | (必填) |
| `MODELSCOPE_MODEL` | 模型 ID | `Qwen/Qwen3-32B` |
| `LOG_LEVEL` | 日志级别 | `INFO` |
| `AGENT_MAX_ROUNDS` | 最大迭代轮数 | `5` |

## 🧪 测试

```bash
# 运行所有测试
python -m pytest tests/ -v

# 运行特定测试
python -m pytest tests/test_agents.py -v

# 运行并显示覆盖率
python -m pytest --cov=.
```

## 📄 License

MIT License
