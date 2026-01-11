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
  <a href="#features">Features</a> •
  <a href="#architecture">Architecture</a> •
  <a href="#roadmap">Roadmap</a>
</p>

---

### Why

写 Agent 不该比写业务代码还复杂。三行代码，跑起来再说。

```python
from workflows import ResumePipeline

pipeline = ResumePipeline(llm)
result = pipeline.run(resume_data, job_description="招聘Python工程师...")  # Done.
```

---

## Quick Start

```bash
pip install -r requirements.txt
export MODELSCOPE_API_KEY="sk-xxx"  # 或用本地 vLLM

# Workflow 模式 - 专家流水线（推荐）
python main.py workflow -n resume -i @data/sample_resume.json

# Solo 模式 - LLM 自己决定
python main.py solo -p "优化简历" --resume @data/sample_resume.json
```

---

## Modes

### Workflow 模式（推荐）

**固定专家流水线**：每个专家调用 LLM 进行深度处理，顺序由代码固定。

```bash
# 基础使用
python main.py workflow -n resume -i @data/sample_resume.json

# 指定职位描述（自动匹配模板 + 内容优化）
python main.py workflow -n resume -i @data/sample_resume.json --jd data/sample_job.txt

# 指定模板和页面偏好
python main.py workflow -n resume -i @data/sample_resume.json --template tech_modern --page one_page
```

**执行流程**：

```
ResumePipeline (专家流水线)
    │
    ├── Step 1: ContentAgent (内容优化专家)
    │            📞 LLM: Think → Execute
    │            提取JD关键词、分析弱点、优化内容
    │
    ├── Step 2: StyleSelector (模板选择)
    │            根据 JD 自动匹配或手动指定
    │
    ├── Step 3: LayoutAgent (布局设计专家)
    │            📞 LLM: Think → Execute
    │            设计布局配置
    │
    ├── Step 4: LayoutOptimizer (分页优化)
    │            智能调整间距/字体，确保一页
    │
    └── Step 5: ResumeGenerator (生成文档)
                 生成 Word 文档
```

### Solo 模式

**ReactAgent + Agent-as-Tool**：LLM 自己决定调用工具的顺序。

```bash
python main.py solo -p "优化并生成简历" --resume @data/sample_resume.json --template tech_modern
```

**执行流程**：

```
ReactAgent (LLM 决策)
    │
    ├── LLM决定 → content_optimizer
    │              └─ ContentAgent (📞 LLM)
    │              └─ 保存 → @optimized
    │
    ├── LLM决定 → layout_designer with "@optimized"
    │              └─ 分页优化
    │              └─ 保存 → @layout
    │
    └── LLM决定 → generate_resume with "@layout"
                   └─ 生成 .docx
```

### 两种模式对比

| 特性 | Solo 模式 | Workflow 模式 |
|------|----------|---------------|
| 执行顺序 | LLM 自己决定 | 代码固定 |
| LLM 调用 | 每轮决策 + 工具内部 | 只有专家调用 |
| 稳定性 | 可能漏调/乱序 | 100% 按流程 |
| 适用场景 | 灵活对话 | 生产环境 |

---

## Features

### 🎨 模板系统

支持 6 种预设模板，可根据职位描述自动匹配：

| 模板 | 适用场景 |
|------|----------|
| `tech_modern` | 互联网/科技公司技术岗 |
| `tech_classic` | 外企/传统企业技术岗 |
| `management` | 产品经理/项目经理 |
| `creative` | UI设计师/创意岗 |
| `minimal` | 通用极简风格 |
| `fresh_graduate` | 应届生/实习生 |

```bash
# 列出所有模板
python -c "from tools.templates import get_registry; print(get_registry().available_templates)"

# 根据 JD 自动匹配
python main.py workflow -n resume -i @data/sample_resume.json --jd job.txt
```

### 📄 智能分页

自动调整布局确保简历适合目标页数：

```bash
# 强制一页
python main.py workflow -n resume -i @data/sample_resume.json --page one_page

# 自动判断（默认）
python main.py workflow -n resume -i @data/sample_resume.json --page auto
```

优化策略：
1. 调整章节间距
2. 调整字体大小
3. 精简内容（保留核心）

### 🎯 职位匹配

提供 JD 后自动：
- 提取关键词
- 匹配最佳模板
- 优化内容侧重点

```bash
python main.py workflow -n resume -i @data/sample_resume.json --jd data/sample_job.txt
```

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              USER REQUEST                                    │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
            ┌───────────────────────┴───────────────────────┐
            │                                               │
            ▼                                               ▼
┌───────────────────────┐                     ┌───────────────────────┐
│     Solo Mode         │                     │    Workflow Mode      │
│                       │                     │                       │
│  ReactAgent (LLM)     │                     │  ResumePipeline       │
│      │                │                     │      │                │
│      ▼                │                     │      ▼                │
│  Tool Selection       │                     │  Fixed Steps          │
│  (LLM decides)        │                     │  (Code defines)       │
└───────────┬───────────┘                     └───────────┬───────────┘
            │                                             │
            └─────────────────────┬───────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              Expert Agents                                   │
│                                                                              │
│   ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐         │
│   │  ContentAgent   │    │  LayoutAgent    │    │ StyleSelector   │         │
│   │                 │    │                 │    │                 │         │
│   │  📞 LLM Call    │    │  📞 LLM Call    │    │  Rule-based     │         │
│   │  Think→Execute  │    │  Think→Execute  │    │  Matching       │         │
│   └─────────────────┘    └─────────────────┘    └─────────────────┘         │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              Output Layer                                    │
│                                                                              │
│   ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐         │
│   │ LayoutOptimizer │    │ TemplateRegistry│    │ ResumeGenerator │         │
│   │                 │    │                 │    │                 │         │
│   │  Pagination     │    │  6 Presets      │    │  python-docx    │         │
│   │  Algorithm      │    │  JSON + Python  │    │  .docx Output   │         │
│   └─────────────────┘    └─────────────────┘    └─────────────────┘         │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

<details>
<summary><b>目录结构</b></summary>

```
agent/
├── workflows/                 # 🆕 工作流模块
│   ├── base.py               #   工作流基类
│   └── resume_pipeline.py    #   简历生成流水线
│
├── agents/                    # Agent 层
│   ├── base.py               #   BaseLLMAgent (Think-Execute)
│   ├── react_agent.py        #   ReactAgent (Solo 模式)
│   └── crews/resume/         #   专家 Agent
│       ├── content_agent.py  #     内容优化专家
│       └── layout_agent.py   #     布局设计专家
│
├── tools/                     # 工具集
│   ├── agent_wrappers/       #   Agent 工具包装器
│   │   ├── content_optimizer.py
│   │   ├── layout_designer.py
│   │   └── style_selector.py
│   ├── generators/           #   生成器
│   │   ├── resume.py         #     Word 文档生成
│   │   └── pagination.py     #   🆕 智能分页
│   └── templates/            # 🆕 模板系统
│       ├── base.py           #     模板基类
│       ├── registry.py       #     模板注册表
│       ├── presets/          #     预设模板 (JSON)
│       │   ├── tech_modern.json
│       │   ├── tech_classic.json
│       │   ├── management.json
│       │   ├── creative.json
│       │   ├── minimal.json
│       │   └── fresh_graduate.json
│       └── custom/           #     自定义模板 (Python)
│
├── llm/                       # LLM 后端
│   ├── modelscope.py         #   ModelScope API
│   └── vllm.py               #   本地 vLLM
│
├── data/                      # 示例数据
│   ├── sample_resume.json    #   示例简历
│   └── sample_job.txt        #   示例职位描述
│
├── output/                    # 输出目录
│
└── main.py                    # CLI 入口
```

</details>

<details>
<summary><b>数据流详解</b></summary>

工具之间通过临时文件传递数据，使用 `@` 标签引用：

```
/tmp/
├── original_resume.json      # main.py 保存原始简历
│       ↓
│   ContentOptimizerTool 读取 (@original)
│       ↓
├── optimized_resume.json     # ContentAgent 优化后保存
│       ↓
│   LayoutDesignerTool 读取 (@optimized)
│       ↓
├── layout_resume.json        # 布局设计后保存（含 _layout_config）
│       ↓
│   ResumeGenerator 读取 (@layout)
│       ↓
output/*.docx                  # 最终输出
```

| 引用 | 说明 |
|------|------|
| `@original` | 原始简历数据 |
| `@optimized` | 内容优化后的数据 |
| `@layout` | 布局设计后的数据 |
| `@selected` | 已选择的模板配置 |

</details>

---

## Extend

**添加新的工作流**

```python
# workflows/my_pipeline.py
from workflows.base import BaseWorkflow, WorkflowResult, WorkflowContext

class MyPipeline(BaseWorkflow):
    WORKFLOW_NAME = "my_pipeline"
    WORKFLOW_STEPS = ["步骤1", "步骤2", "步骤3"]
    
    def _execute_steps(self, ctx: WorkflowContext) -> WorkflowResult:
        # Step 1
        self._step("步骤1")
        # ...
        
        return WorkflowResult(success=True, output={...})
```

**添加新的模板**

```json
// tools/templates/presets/my_template.json
{
  "name": "my_template",
  "display_name": "我的模板",
  "tags": ["标签1", "标签2"],
  "job_keywords": ["关键词1", "关键词2"],
  "page_preference": "one_page",
  "font_config": {"body_size": 10, "heading_size": 14},
  "spacing_config": {"margin": 0.5, "section_gap": 6}
}
```

---

## Roadmap

| Status | Feature | Description |
|:------:|---------|-------------|
| ✅ | Solo Mode | ReactAgent + Agent-as-Tool |
| ✅ | Workflow Mode | 专家流水线架构 |
| ✅ | Template System | 6种预设模板 + 自动匹配 |
| ✅ | Smart Pagination | 智能分页优化 |
| ✅ | Job Matching | 职位描述匹配 |
| 🚧 | Multi-Agent | 动态编排器 |
| 🚧 | Web UI | 交互面板 |
| 🚧 | Memory | 长期记忆 |

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
