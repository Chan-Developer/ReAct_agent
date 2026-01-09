<p align="center">
  <img src="https://img.shields.io/badge/🤖-Agent_Framework-blue?style=for-the-badge&labelColor=1a1a2e" alt="Agent Framework"/>
</p>

<h1 align="center">Agent Framework</h1>

<p align="center">
  <strong>🚀 轻量级、可扩展的 Multi-Agent 智能协作框架</strong>
</p>

<p align="center">
  <a href="#-特性">特性</a> •
  <a href="#-快速开始">快速开始</a> •
  <a href="#-架构">架构</a> •
  <a href="#-扩展">扩展</a> •
  <a href="#-文档">文档</a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.10+-blue.svg" alt="Python"/>
  <img src="https://img.shields.io/badge/license-MIT-green.svg" alt="License"/>
  <img src="https://img.shields.io/badge/PRs-welcome-brightgreen.svg" alt="PRs Welcome"/>
</p>

---

## 🎯 Why Agent Framework?

构建智能 Agent 应该像搭积木一样简单。Agent Framework 提供：

- **极简 API** - 3 行代码启动 Agent
- **即插即用** - 工具、LLM、知识库随意组合
- **生产就绪** - 完善的日志、错误处理、可观测性

```python
from core import Task, Orchestrator
from agents.crews import ResumeCrew

orchestrator = Orchestrator(llm)
orchestrator.register(ResumeCrew)
result = orchestrator.run(Task(name="resume", input_data=data))
```

---

## ✨ 特性

<table>
<tr>
<td width="50%">

### 🧠 Solo 模式
单 Agent + ReAct 循环，适合通用任务
```bash
python main.py solo -p "计算 3*7+2"
```

</td>
<td width="50%">

### 👥 Crew 模式
多 Agent 协作，专业分工
```bash
python main.py crew --name "张三"
```

</td>
</tr>
<tr>
<td>

### 📚 RAG 知识库
向量检索 + 上下文增强
```python
kb = VectorKnowledgeBase(milvus, embedding)
orchestrator = Orchestrator(llm, kb)
```

</td>
<td>

### 🔌 多 LLM 支持
云端 API / 本地 vLLM 无缝切换
```python
llm = ModelScopeOpenAI()  # 云端
llm = VllmLLM()           # 本地
```

</td>
</tr>
</table>

---

## 🚀 快速开始

### 安装

```bash
pip install -r requirements.txt
```

### 配置

```bash
export MODELSCOPE_API_KEY="your-api-key"
```

### 运行

```bash
# Solo: 单 Agent 对话
python main.py solo --prompt "帮我分析这段代码"

# Crew: 多 Agent 协作生成简历
python main.py crew --name "张三" --school "清华大学"
```

---

## 🏗️ 架构

```
┌────────────────────────────────────────────────────────────────┐
│                        Orchestrator                            │
│                     (任务路由 & 协调)                           │
└───────────────────────────┬────────────────────────────────────┘
                            │
            ┌───────────────┼───────────────┐
            ▼               ▼               ▼
     ┌────────────┐  ┌────────────┐  ┌────────────┐
     │ ResumeCrew │  │ CodeCrew   │  │  YourCrew  │
     │ ┌────────┐ │  │ ┌────────┐ │  │            │
     │ │Content │ │  │ │Review  │ │  │   ...      │
     │ │Agent   │ │  │ │Agent   │ │  │            │
     │ ├────────┤ │  │ ├────────┤ │  │            │
     │ │Layout  │ │  │ │Fix     │ │  │            │
     │ │Agent   │ │  │ │Agent   │ │  │            │
     │ └────────┘ │  │ └────────┘ │  │            │
     └─────┬──────┘  └────────────┘  └────────────┘
           │
           ▼
┌────────────────────────────────────────────────────────────────┐
│                     Shared Infrastructure                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ KnowledgeBase│  │ ToolRegistry │  │     LLM      │          │
│  │    (RAG)     │  │              │  │              │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└────────────────────────────────────────────────────────────────┘
```

---

## 📁 项目结构

```
agent/
├── core/                    # 核心框架
│   ├── task.py             # Task, TaskResult
│   ├── orchestrator.py     # 通用协调器
│   └── knowledge.py        # 知识库接口
│
├── agents/                  # Agent 实现
│   ├── base.py             # Agent 基类
│   ├── react_agent.py      # Solo 模式
│   └── crews/              # 多 Agent 团队
│       ├── base.py         # Crew 基类
│       └── resume/         # 简历 Crew
│
├── knowledge/              # 知识库
│   └── vector_kb.py        # Milvus 实现
│
├── tools/                  # 工具
├── llm/                    # LLM 接口
└── main.py                 # CLI 入口
```

---

## 🔧 扩展

### 创建自定义 Crew

```python
from agents.crews.base import BaseCrew
from core.task import TaskResult

class MyCustomCrew(BaseCrew):
    CREW_NAME = "my_task"
    
    def _init_agents(self):
        self.agent_a = MyAgentA(self.llm)
        self.agent_b = MyAgentB(self.llm)
        self.agents = [self.agent_a, self.agent_b]
    
    def _execute(self, task):
        # 定义协作流程
        result_a = self.agent_a.run(task.input_data)
        result_b = self.agent_b.run(result_a.data)
        return TaskResult(success=True, output=result_b.data)

# 注册并使用
orchestrator.register(MyCustomCrew)
orchestrator.run(Task(name="my_task", input_data={...}))
```

### 创建自定义工具

```python
from tools.base import BaseTool

class MyTool(BaseTool):
    def __init__(self):
        super().__init__(
            name="my_tool",
            description="工具描述",
            parameters={"type": "object", "properties": {...}}
        )
    
    def execute(self, **kwargs) -> str:
        return "result"
```

---

## 📖 文档

| 文档 | 说明 |
|------|------|
| [快速开始](docs/quickstart.md) | 5 分钟上手 |
| [核心概念](docs/concepts.md) | Task, Agent, Crew, Orchestrator |
| [API 参考](docs/api.md) | 完整 API 文档 |
| [示例](examples/) | 完整示例代码 |

---

## 🤝 贡献

欢迎贡献！请查看 [CONTRIBUTING.md](CONTRIBUTING.md)

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/amazing`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送分支 (`git push origin feature/amazing`)
5. 提交 Pull Request

---

## 📄 License

[MIT](LICENSE) © 2024

---

<p align="center">
  <sub>Built with ❤️ for the AI community</sub>
</p>
