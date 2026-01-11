# 简历模板系统

## 新工作流程

```
简历数据 + 职位描述(可选)
        ↓
    1. 内容优化 (ContentOptimizerTool)
        - 量化成就、STAR法则
        - 根据JD调整内容侧重点
        ↓
    2. 模板选择 (StyleSelectorTool)
        - 根据JD自动推荐模板
        - 或手动选择模板
        ↓
    3. 布局设计 (LayoutDesignerTool)
        - 应用模板配置
        - 智能分页优化
        ↓
    4. 生成文档 (ResumeGenerator)
        - 生成Word文档
```

## 快速使用

### 1. 基础流程（无职位匹配）

```python
from tools.agent_wrappers import ContentOptimizerTool, LayoutDesignerTool
from tools.generators import ResumeGenerator

# 初始化工具
content_optimizer = ContentOptimizerTool(llm)
layout_designer = LayoutDesignerTool(llm)
resume_generator = ResumeGenerator(output_dir="./output")

# 1. 优化内容
result = content_optimizer.execute(resume_json='{"name": "张三", ...}')

# 2. 设计布局
result = layout_designer.execute(resume_json="@optimized", page_preference="one_page")

# 3. 生成文档
result = resume_generator.execute(resume_data="@layout", filename="my_resume")
```

### 2. 带职位匹配的流程

```python
from tools.agent_wrappers import ContentOptimizerTool, StyleSelectorTool, LayoutDesignerTool
from tools.generators import ResumeGenerator

# 初始化
content_optimizer = ContentOptimizerTool(llm)
style_selector = StyleSelectorTool(llm)
layout_designer = LayoutDesignerTool(llm)
resume_generator = ResumeGenerator(output_dir="./output")

# 职位描述
job_description = """
招聘 Python 后端工程师
要求：
- 3年以上 Python 开发经验
- 熟悉 Django/Flask 框架
- 了解 MySQL、Redis
- 有微服务架构经验者优先
"""

# 1. 优化内容（带JD匹配）
result = content_optimizer.execute(
    resume_json='{"name": "张三", ...}',
    job_description=job_description
)

# 2. 选择模板（根据JD自动匹配）
result = style_selector.execute(
    action="match",
    job_description=job_description,
    page_preference="one_page"
)

# 3. 设计布局（使用选中的模板）
result = layout_designer.execute(
    resume_json="@optimized",
    template="@selected"
)

# 4. 生成文档
result = resume_generator.execute(
    resume_data="@layout",
    filename="张三_Python工程师"
)
```

## 可用模板

| 模板名称 | 适用岗位 | 页面偏好 |
|---------|---------|---------|
| `tech_modern` | 互联网技术岗 | 一页 |
| `tech_classic` | 传统企业技术岗 | 一页 |
| `management` | 产品/项目管理 | 自动 |
| `creative` | 设计/创意岗 | 一页 |
| `fresh_graduate` | 应届生/实习 | 一页 |
| `research` | 科研/学术岗 | 两页 |

## 自定义模板

### 方式1：JSON配置文件

在 `tools/templates/presets/` 目录创建 JSON 文件：

```json
{
  "name": "my_template",
  "display_name": "我的模板",
  "tags": ["技术", "互联网"],
  "job_keywords": ["工程师", "开发"],
  "page_preference": "one_page",
  "section_order": ["header", "summary", "experience", "projects", "skills", "education"],
  "font_config": {
    "title_size": 16,
    "body_size": 9
  },
  "spacing_config": {
    "margin": 0.4,
    "section_gap": 4
  }
}
```

### 方式2：Python类

在 `tools/templates/custom/` 目录创建 Python 文件：

```python
from tools.templates import BaseTemplate, TemplateConfig

class MyTemplate(BaseTemplate):
    @property
    def name(self) -> str:
        return "my_template"
    
    def get_default_config(self) -> TemplateConfig:
        return TemplateConfig(
            name="my_template",
            display_name="我的模板",
            # ... 其他配置
        )
    
    def preprocess_resume(self, resume_data):
        # 自定义预处理逻辑
        return resume_data
```

## 智能分页

系统会自动估算内容占用的页面空间，并根据 `page_preference` 进行优化：

- `one_page`: 尽量压缩到一页（调整间距、字体、精简内容）
- `two_pages`: 适合两页布局
- `auto`: 根据内容量自动决定

```python
# 强制一页
result = layout_designer.execute(
    resume_json="@optimized",
    page_preference="one_page"
)
```
