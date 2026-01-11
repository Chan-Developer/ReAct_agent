# -*- coding: utf-8 -*-
"""模板选择工具。

根据职位描述自动匹配最佳模板，或列出可用模板供用户选择。
"""
from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from tools.base import BaseTool
from tools.templates import TemplateRegistry, get_registry, TemplateConfig
from common.logger import get_logger

if TYPE_CHECKING:
    from agents.base import LLMProtocol

logger = get_logger(__name__)


class StyleSelectorTool(BaseTool):
    """模板选择工具
    
    功能：
    1. 根据职位描述自动推荐模板
    2. 列出可用模板供用户选择
    3. 支持自定义模板参数覆盖
    
    Example:
        >>> tool = StyleSelectorTool()
        >>> # 自动匹配
        >>> result = tool.execute(job_description="招聘Python后端工程师...")
        >>> # 手动选择
        >>> result = tool.execute(template_name="tech_modern")
        >>> # 列出所有模板
        >>> result = tool.execute(action="list")
    """
    
    def __init__(self, llm: Optional["LLMProtocol"] = None):
        """初始化工具。
        
        Args:
            llm: 可选的 LLM 实例，用于智能分析职位描述
        """
        super().__init__(
            name="style_selector",
            description="选择简历模板样式。可根据职位描述自动推荐，或手动指定模板",
            parameters={
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "description": "操作类型: list(列出模板), select(选择模板), match(自动匹配)",
                        "enum": ["list", "select", "match"],
                        "default": "match",
                    },
                    "job_description": {
                        "type": "string",
                        "description": "职位描述文本，用于自动匹配最佳模板",
                    },
                    "template_name": {
                        "type": "string",
                        "description": "模板名称（手动选择时使用）",
                    },
                    "page_preference": {
                        "type": "string",
                        "description": "页面偏好: one_page(尽量一页), two_pages(两页), auto(自动)",
                        "enum": ["one_page", "two_pages", "auto"],
                        "default": "auto",
                    },
                    "custom_overrides": {
                        "type": "string",
                        "description": "自定义配置覆盖（JSON格式），如调整字体大小、间距等",
                    },
                },
                "required": [],
            },
        )
        self.llm = llm
        self._registry: Optional[TemplateRegistry] = None
    
    @property
    def registry(self) -> TemplateRegistry:
        """延迟加载模板注册表"""
        if self._registry is None:
            self._registry = get_registry()
        return self._registry
    
    def execute(
        self,
        action: str = "match",
        job_description: str = "",
        template_name: str = "",
        page_preference: str = "auto",
        custom_overrides: str = "",
    ) -> str:
        """执行模板选择。
        
        Args:
            action: 操作类型
            job_description: 职位描述
            template_name: 模板名称
            page_preference: 页面偏好
            custom_overrides: 自定义配置覆盖
            
        Returns:
            操作结果
        """
        if action == "list":
            return self._list_templates()
        
        if action == "select" or template_name:
            return self._select_template(template_name, page_preference, custom_overrides)
        
        if action == "match" or job_description:
            return self._match_template(job_description, page_preference, custom_overrides)
        
        return self._list_templates()
    
    def _list_templates(self) -> str:
        """列出所有可用模板"""
        templates = self.registry.list_all()
        
        if not templates:
            return "❌ 没有可用的模板。请检查 tools/templates/presets/ 目录。"
        
        lines = ["📋 可用模板列表：\n"]
        for t in templates:
            tags_str = ", ".join(t["tags"][:3]) if t["tags"] else "通用"
            lines.append(f"  • **{t['name']}** - {t['display_name']}")
            lines.append(f"    标签: {tags_str} | 页面: {t['page_preference']}")
            if t["description"]:
                lines.append(f"    {t['description']}")
            lines.append("")
        
        lines.append("💡 使用方法：")
        lines.append("  - 手动选择: template_name=\"tech_modern\"")
        lines.append("  - 自动匹配: job_description=\"职位描述...\"")
        
        return "\n".join(lines)
    
    def _select_template(
        self,
        template_name: str,
        page_preference: str,
        custom_overrides: str,
    ) -> str:
        """选择指定模板"""
        if not template_name:
            return "❌ 请指定模板名称 (template_name)"
        
        config = self.registry.get(template_name)
        if not config:
            available = ", ".join(self.registry.available_templates)
            return f"❌ 未找到模板 '{template_name}'。可用模板: {available}"
        
        # 应用页面偏好覆盖
        if page_preference != "auto":
            config.page_preference = page_preference
        
        # 应用自定义覆盖
        if custom_overrides:
            config = self._apply_overrides(config, custom_overrides)
        
        # 保存到临时文件
        self._save_template_config(config)
        
        return f"""✅ 已选择模板: {config.display_name}

📝 模板配置:
  - 样式: {config.style}
  - 页面偏好: {config.page_preference}
  - 章节顺序: {' → '.join(config.section_order[:5])}
  
调用 layout_designer 或 generate_resume 时可使用 template="@selected" 来应用此模板。"""
    
    def _match_template(
        self,
        job_description: str,
        page_preference: str,
        custom_overrides: str,
    ) -> str:
        """根据职位描述匹配模板"""
        if not job_description:
            return self._list_templates()
        
        # 获取匹配结果
        matches = self.registry.match_job(job_description, top_k=3)
        
        if not matches or matches[0][1] < 0.1:
            # 没有好的匹配，使用默认模板
            config = self.registry.get("tech_modern")
            if not config:
                config = TemplateConfig()  # 使用默认配置
            match_info = "未找到精确匹配，使用默认模板"
        else:
            best_name, best_score = matches[0]
            config = self.registry.get(best_name)
            match_info = f"匹配度: {best_score:.0%}"
        
        # 应用页面偏好
        if page_preference != "auto":
            config.page_preference = page_preference
        
        # 应用自定义覆盖
        if custom_overrides:
            config = self._apply_overrides(config, custom_overrides)
        
        # 保存到临时文件
        self._save_template_config(config)
        
        # 构建其他推荐
        other_recommendations = ""
        if len(matches) > 1:
            others = [f"{name}({score:.0%})" for name, score in matches[1:3]]
            other_recommendations = f"\n📌 其他推荐: {', '.join(others)}"
        
        return f"""✅ 模板匹配完成！

🎯 推荐模板: {config.display_name}
  - {match_info}
  - 样式: {config.style}
  - 页面偏好: {config.page_preference}
  - 适用标签: {', '.join(config.tags[:3])}
{other_recommendations}

调用 layout_designer 或 generate_resume 时可使用 template="@selected" 来应用此模板。
如需更换模板，请使用 template_name="模板名" 手动选择。"""
    
    def _apply_overrides(self, config: TemplateConfig, overrides_json: str) -> TemplateConfig:
        """应用自定义配置覆盖"""
        try:
            overrides = json.loads(overrides_json)
        except json.JSONDecodeError:
            logger.warning(f"[StyleSelectorTool] 无法解析自定义配置: {overrides_json}")
            return config
        
        # 转换为字典并应用覆盖
        config_dict = config.to_dict()
        
        # 递归合并
        def merge(base: dict, override: dict):
            for key, value in override.items():
                if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                    merge(base[key], value)
                else:
                    base[key] = value
        
        merge(config_dict, overrides)
        
        return TemplateConfig.from_dict(config_dict)
    
    def _save_template_config(self, config: TemplateConfig) -> None:
        """保存模板配置到临时文件"""
        import tempfile
        import os
        
        temp_dir = tempfile.gettempdir()
        temp_file = os.path.join(temp_dir, "selected_template.json")
        
        with open(temp_file, 'w', encoding='utf-8') as f:
            json.dump(config.to_dict(), f, ensure_ascii=False, indent=2)
        
        # 同时保存布局配置格式
        layout_file = os.path.join(temp_dir, "template_layout.json")
        with open(layout_file, 'w', encoding='utf-8') as f:
            json.dump(config.to_layout_config(), f, ensure_ascii=False, indent=2)
        
        logger.info(f"[StyleSelectorTool] 模板配置已保存: {temp_file}")
    
    def get_selected_config(self) -> Optional[TemplateConfig]:
        """获取当前选中的模板配置（供其他工具使用）"""
        import tempfile
        import os
        
        temp_file = os.path.join(tempfile.gettempdir(), "selected_template.json")
        
        if os.path.exists(temp_file):
            try:
                with open(temp_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                return TemplateConfig.from_dict(data)
            except Exception as e:
                logger.error(f"[StyleSelectorTool] 加载模板配置失败: {e}")
        
        return None
