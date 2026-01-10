<h1 align="center">Agent Framework</h1>

<p align="center"><b>Build AI Agents. Ship Fast.</b></p>

<p align="center">
  <a href="https://python.org"><img src="https://img.shields.io/badge/Python-3.10+-3776ab?logo=python&logoColor=white" alt="Python"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-green.svg" alt="License"></a>
  <a href="CONTRIBUTING.md"><img src="https://img.shields.io/badge/PRs-welcome-brightgreen.svg" alt="PRs Welcome"></a>
</p>

<p align="center">
  <a href="#quick-start">Quick Start</a> •
  <a href="#modes">运行模式</a> •
  <a href="#architecture">Architecture</a> •
  <a href="#roadmap">Roadmap</a>
</p>

---

### Why

写 Agent 不该比写业务代码还复杂。三行代码，跑起来再说。

```python
from agent import ReactAgent

agent = ReactAgent(llm, tools=[content_optimizer, layout_designer, generate_resume])
result = agent.run("请优化简历并生成 Word 文档")  # Done.
```

---

## Quick Start

```bash
pip install -r requirements.txt
export MODELSCOPE_API_KEY="sk-xxx"  # 或用本地 vLLM
python main.py solo -p "Hello"
```

---

## Modes

### Solo 模式（推荐）

**ReactAgent + Agent-as-Tool 架构**：ReactAgent 作为协调者，调用封装为工具的专业 Agent。

```bash
# 基础对话
python main.py solo -p "帮我算 127 * 38"

# 简历生成（完整流程：内容优化 - 布局设计 - 生成文档）
python main.py solo -p "请优化简历并生成Word文档" --resume @data/resumes/my_resume.json
```

**执行流程**：

```
ReactAgent (协调者)
    |
    +-- 第1轮: content_optimizer
    |         ContentAgent (Think-Execute-Reflect)
    |         保存优化结果 -> @optimized
    |
    +-- 第2轮: layout_designer with "@optimized"
    |         LayoutAgent (Think-Execute-Reflect)  
    |         保存布局配置 -> @layout
    |
    +-- 第3轮: generate_resume with "@layout"
              纯渲染器，使用 LayoutAgent 的配置生成 .docx
```

**数据引用机制**：避免 LLM 传递长 JSON 出错

| 引用 | 说明 |
|------|------|
| `@optimized` | content_optimizer 保存的优化数据 |
| `@layout` | layout_designer 保存的布局数据 |

### Workflow 模式

硬编码的顺序工作流，适合固定流程：

```bash
python main.py workflow --task resume --data @data/resumes/my_resume.json
```

---

## Architecture

```
+------------------------------------------------------------------+
|                          USER REQUEST                             |
+----------------------------------+-------------------------------+
                                   |
                                   v
+------------------------------------------------------------------+
|                         ReactAgent                                |
|                     (ReAct: Reason + Act)                         |
|                                                                   |
|    User Query --> Think --> Select Tool --> Execute --> Reflect   |
|                                                                   |
+----------------------------------+-------------------------------+
                                   |
          +------------------------+------------------------+
          |                        |                        |
          v                        v                        v
+------------------+    +------------------+    +------------------+
|   Agent Tools    |    |  Generator Tools |    |   Basic Tools    |
|                  |    |                  |    |                  |
|  +-----------+   |    |  +------------+  |    |  +------------+  |
|  | Content   |   |    |  | Resume     |  |    |  | Calculator |  |
|  | Optimizer |   |    |  | Generator  |  |    |  +------------+  |
|  +-----------+   |    |  +------------+  |    |  | Search     |  |
|  | Layout    |   |    |                  |    |  +------------+  |
|  | Designer  |   |    |                  |    |  | FileOps    |  |
|  +-----------+   |    |                  |    |  +------------+  |
+--------+---------+    +--------+---------+    +------------------+
         |                       |
         v                       v
+------------------+    +------------------+
|  ContentAgent    |    |  ResumeGenerator |
|  (BaseLLMAgent)  |    |  (python-docx)   |
|                  |    |                  |
|  Think-Execute   |    |  Pure Renderer   |
|  -Reflect        |    |  (no LLM calls)  |
+------------------+    +------------------+
|  LayoutAgent     |
|  (BaseLLMAgent)  |
+------------------+
```

<details>
<summary><b>目录结构</b></summary>

```
agent/
├── core/                   # 核心抽象
│   ├── task.py            #   Task, TaskResult
│   ├── orchestrator.py    #   任务路由
│   ├── parser.py          #   工具调用解析
│   └── knowledge.py       #   RAG 接口
│
├── agents/                 # Agent 层
│   ├── base.py            #   BaseLLMAgent (Think-Execute-Reflect)
│   ├── react_agent.py     #   ReactAgent (Solo 模式协调者)
│   └── crews/             #   专业 Agent 实现
│       └── resume/        #       简历相关
│           ├── content_agent.py  # 内容优化 Agent
│           └── layout_agent.py   # 布局设计 Agent
│
├── tools/                  # 工具集
│   ├── base.py            #   BaseTool 抽象
│   ├── registry.py        #   工具注册器
│   ├── agents/            #   Agent 工具包装器
│   │   ├── content_optimizer.py  # ContentAgent -> Tool
│   │   └── layout_designer.py    # LayoutAgent -> Tool
│   └── generators/        #   生成器工具
│       └── resume.py      #       Word 文档生成
│
├── llm/                    # LLM 后端
│   ├── base.py            #   BaseLLM
│   ├── modelscope.py      #   ModelScope API
│   └── vllm_client.py     #   本地 vLLM
│
├── knowledge/              # RAG 实现
│   └── vector_kb.py       #   Milvus 向量检索
│
├── configs/                # 配置文件
│   └── config.yaml        #   LLM/Agent 配置
│
├── data/                   # 数据目录
│   └── resumes/           #   简历 JSON 模板
│
├── output/                 # 输出目录
│   └── *.docx             #   生成的简历
│
└── main.py                 # CLI 入口
```

</details>

<details>
<summary><b>Agent-as-Tool 模式</b></summary>

将完整的 Agent（含 Think-Execute-Reflect 循环）封装为工具，供 ReactAgent 调用：

```python
# tools/agents/content_optimizer.py
class ContentOptimizerTool(BaseTool):
    name = "content_optimizer"
    description = "优化简历内容"
    
    def execute(self, resume_json: str) -> str:
        # 初始化专业 Agent
        agent = ContentAgent(self.llm)
        # 执行完整的 Think-Execute-Reflect 流程
        result = agent.run(resume_data)
        # 保存结果供后续工具使用
        save_to_temp("optimized_resume.json", result.data)
        return "优化完成，使用 @optimized 引用结果"
```

**优势**：
- ReactAgent 专注于任务拆解和工具选择
- 专业 Agent 专注于特定领域的深度处理
- 数据引用机制避免 LLM 传递长 JSON

</details>

---

## Extend

**添加 Agent 工具**

```python
# 1. 实现专业 Agent
class MyAgent(BaseLLMAgent):
    AGENT_NAME = "my_agent"
    
    def _get_role_prompt(self):
        return "你是一个专业的..."
    
    def _execute_task(self, context):
        # Think - Execute - Reflect
        return AgentResult(success=True, data=result)

# 2. 封装为工具
class MyTool(BaseTool):
    name = "my_tool"
    description = "执行特定任务"
    parameters = {...}
    
    def execute(self, **kwargs) -> str:
        agent = MyAgent(self.llm)
        result = agent.run(kwargs)
        return result.to_json()
```

**添加基础工具**

```python
class CalculatorTool(BaseTool):
    name = "calculator"
    description = "执行数学计算"
    parameters = {
        "type": "object",
        "properties": {
            "expression": {"type": "string", "description": "数学表达式"}
        },
        "required": ["expression"]
    }
    
    def execute(self, expression: str) -> str:
        return str(eval(expression))
```

---

## Roadmap

| Status | Feature | Description |
|:------:|---------|-------------|
| Done | Solo Mode | ReactAgent + Agent-as-Tool 架构 |
| Done | Workflow Mode | 硬编码顺序工作流 |
| Done | Resume Generation | 内容优化 - 布局设计 - Word 生成 |
| Done | RAG | Milvus 向量检索 |
| Done | Tools | 工具注册器 + 数据引用机制 |
| WIP | True Multi-Agent | 动态编排器，自主规划创建 Agent |
| WIP | Multimodal | 图片/PDF/表格检索、YOLO、SAM |
| WIP | Memory | 短期上下文 + 长期向量记忆 |
| WIP | Web UI | 交互面板、执行可视化 |

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
