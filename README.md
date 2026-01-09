<div align="center">

```
     _                    _     _____ 
    / \   __ _  ___ _ __ | |_  |  ___|
   / _ \ / _` |/ _ \ '_ \| __| | |_   
  / ___ \ (_| |  __/ | | | |_  |  _|  
 /_/   \_\__, |\___|_| |_|\__| |_|    
         |___/                        
```

**Build AI Agents. Ship Fast.**

[![Python](https://img.shields.io/badge/Python-3.10+-3776ab?logo=python&logoColor=white)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

[Quick Start](#quick-start) · [Docs](#architecture) · [Roadmap](#roadmap) · [Contributing](#contributing)

</div>

---

### Why

写 Agent 不该比写业务代码还复杂。三行代码，跑起来再说。

```python
from agent import Orchestrator, Task

agent = Orchestrator(llm)
agent.register(YourCrew)
result = agent.run(Task("your_task", data))  # Done.
```

---

## Quick Start

```bash
pip install -r requirements.txt
export MODELSCOPE_API_KEY="sk-xxx"  # 或用本地 vLLM
python main.py solo -p "Hello"
```

<details>
<summary><b>更多示例</b></summary>

```bash
# 单 Agent 模式
python main.py solo -p "帮我算 127 * 38"

# 多 Agent 协作
python main.py crew --name "张三" --school "清华大学"
```

</details>

---

## Architecture

```
+------------------------------------------------------------------+
|                          USER REQUEST                             |
+----------------------------------+-------------------------------+
                                   |
                                   v
+------------------------------------------------------------------+
|                         ORCHESTRATOR                              |
|                                                                   |
|    task.name ---> Crew Registry ---> Select Crew                  |
|                                                                   |
+----------------------------------+-------------------------------+
                                   |
          +------------------------+------------------------+
          |                        |                        |
          v                        v                        v
+------------------+    +------------------+    +------------------+
|   Resume Crew    |    |    Code Crew     |    |    Your Crew     |
|                  |    |                  |    |                  |
|  +------------+  |    |  +------------+  |    |                  |
|  |  Content   |  |    |  |  Review    |  |    |    Extend me!    |
|  |   Agent    |  |    |  |   Agent    |  |    |                  |
|  +-----+------+  |    |  +------------+  |    |                  |
|        |         |    |                  |    |                  |
|        v         |    |                  |    |                  |
|  +------------+  |    |                  |    |                  |
|  |  Layout    |  |    |                  |    |                  |
|  |   Agent    |  |    |                  |    |                  |
|  +------------+  |    |                  |    |                  |
+--------+---------+    +------------------+    +------------------+
         |
         v
+------------------------------------------------------------------+
|                       INFRASTRUCTURE                              |
|                                                                   |
|   +----------------+  +----------------+  +----------------+      |
|   |      RAG       |  |     Tools      |  |      LLM       |      |
|   |   Knowledge    |  |    Registry    |  |    Backend     |      |
|   |                |  |                |  |                |      |
|   |  - search()    |  |  - calculator  |  |  - vLLM        |      |
|   |  - add()       |  |  - search      |  |  - ModelScope  |      |
|   |  - delete()    |  |  - file_ops    |  |  - OpenAI      |      |
|   |                |  |  - custom...   |  |                |      |
|   |   [Milvus]     |  |                |  |                |      |
|   +----------------+  +----------------+  +----------------+      |
|                                                                   |
+----------------------------------+-------------------------------+
                                   |
                                   v
+------------------------------------------------------------------+
|                         TASK RESULT                               |
+------------------------------------------------------------------+
```

<details>
<summary><b>数据流</b></summary>

```
  ┌──────┐      ┌──────────────┐      ┌────────┐      ┌────────────┐
  │ Task │ ───► │ Orchestrator │ ───► │  Crew  │ ───► │ TaskResult │
  └──────┘      └──────────────┘      └───┬────┘      └────────────┘
                                          │
                         ┌────────────────┼────────────────┐
                         ▼                ▼                ▼
                    ┌─────────┐      ┌─────────┐      ┌─────────┐
                    │ Agent 1 │ ───► │ Agent 2 │ ───► │ Agent N │
                    └────┬────┘      └────┬────┘      └────┬────┘
                         │                │                │
                         └────────────────┴────────────────┘
                                          │
                              ┌───────────┴───────────┐
                              ▼                       ▼
                         ┌─────────┐            ┌──────────┐
                         │   LLM   │            │  Tools   │
                         └─────────┘            └──────────┘
```

</details>

<details>
<summary><b>目录结构</b></summary>

```
agent/
├── core/               # 核心抽象
│   ├── task.py        #   └─ Task, TaskResult
│   ├── orchestrator.py#   └─ 任务路由
│   └── knowledge.py   #   └─ RAG 接口
│
├── agents/             # Agent 层
│   ├── base.py        #   └─ BaseLLMAgent
│   ├── react_agent.py #   └─ Solo 模式
│   └── crews/         #   └─ 多 Agent 团队
│       ├── base.py    #       └─ BaseCrew
│       └── resume/    #       └─ 简历优化
│
├── knowledge/          # RAG 实现
│   └── vector_kb.py   #   └─ Milvus
│
├── tools/              # 工具集
├── llm/                # LLM 后端
└── main.py             # CLI
```

</details>

---

## Extend

**Add a Crew**

```python
class MyCrew(BaseCrew):
    CREW_NAME = "my_task"
    
    def _init_agents(self):
        self.agents = [AgentA(self.llm), AgentB(self.llm)]
    
    def _execute(self, task):
        # Your workflow here
        return TaskResult(success=True, output=result)
```

**Add a Tool**

```python
class MyTool(BaseTool):
    name = "my_tool"
    description = "Does something useful"
    
    def execute(self, **kwargs) -> str:
        return "result"
```

---

## Roadmap

| Status | Feature | Description |
|:------:|---------|-------------|
| ✅ | Multi-Agent | Orchestrator + Crew 架构 |
| ✅ | RAG | Milvus 向量检索 |
| ✅ | Tools | 工具注册器 |
| 🚧 | Multimodal | 图片/PDF/表格检索、YOLO、SAM |
| 🚧 | Memory | 短期上下文 + 长期向量记忆 |
| 🚧 | Workflow | DAG 编排、条件分支、可视化 |
| 🚧 | Skills | 技能抽象、插件化 |
| 🚧 | Web UI | 交互面板、执行可视化、调试工具 |

---

## Contributing

```bash
git checkout -b feat/xxx
python -m pytest tests/ -v
git commit -m "feat: xxx"
```

详见 [CONTRIBUTING.md](CONTRIBUTING.md)

---

<div align="center">

**[MIT License](LICENSE)**

<sub>Made with focus, not frameworks.</sub>

</div>
