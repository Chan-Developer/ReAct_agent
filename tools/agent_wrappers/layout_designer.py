# -*- coding: utf-8 -*-
"""布局设计工具。

将 LayoutAgent 包装为 Tool，供 ReactAgent 调用。
内部保留完整的 Think-Execute-Reflect 流程。

新增功能：
- 支持模板系统（@selected 引用）
- 智能分页（自动决定一页/两页）
- 页面偏好设置
"""
from __future__ import annotations

import json
import os
import re
import tempfile
from typing import TYPE_CHECKING, Any, Dict, Optional

from tools.base import BaseTool
from common.logger import get_logger

if TYPE_CHECKING:
    from agents.base import LLMProtocol

logger = get_logger(__name__)


class LayoutDesignerTool(BaseTool):
    """简历布局设计工具。
    
    包装 LayoutAgent，保留完整的 Think-Execute-Reflect 流程。
    
    工作流程：
        1. 加载模板配置（如果指定）
        2. Think: 分析内容密度，确定布局策略
        3. Execute: 生成布局配置（章节顺序、样式、间距等）
        4. 智能分页优化（根据 page_preference）
        5. Reflect: 提取设计说明
    
    Example:
        >>> from llm import ModelScopeOpenAI
        >>> llm = ModelScopeOpenAI()
        >>> tool = LayoutDesignerTool(llm)
        >>> # 使用模板
        >>> result = tool.execute(resume_json='@optimized', template='@selected')
        >>> # 指定页面偏好
        >>> result = tool.execute(resume_json='@optimized', page_preference='one_page')
    """
    
    def __init__(self, llm: "LLMProtocol"):
        """初始化工具。
        
        Args:
            llm: LLM 实例，用于初始化内部 Agent
        """
        super().__init__(
            name="layout_designer",
            description="设计简历布局，支持模板选择和智能分页",
            parameters={
                "type": "object",
                "properties": {
                    "resume_json": {
                        "type": "string",
                        "description": "JSON 格式的简历数据，或使用 @optimized/@original 引用",
                    },
                    "template": {
                        "type": "string",
                        "description": "模板名称或 @selected 使用已选模板",
                        "default": "",
                    },
                    "style": {
                        "type": "string",
                        "description": "样式偏好（模板未指定时使用）: modern, classic, minimal",
                        "enum": ["modern", "classic", "minimal"],
                        "default": "modern",
                    },
                    "page_preference": {
                        "type": "string",
                        "description": "页面偏好: one_page(尽量一页), two_pages, auto(自动)",
                        "enum": ["one_page", "two_pages", "auto"],
                        "default": "auto",
                    },
                },
                "required": ["resume_json"],
            },
        )
        self.llm = llm
        self._agent = None
        self._optimizer = None
    
    @property
    def agent(self):
        """延迟加载 LayoutAgent。"""
        if self._agent is None:
            from agents.crews.resume.layout_agent import LayoutAgent
            self._agent = LayoutAgent(self.llm)
        return self._agent
    
    @property
    def optimizer(self):
        """延迟加载 LayoutOptimizer。"""
        if self._optimizer is None:
            from tools.generators.pagination import LayoutOptimizer
            self._optimizer = LayoutOptimizer()
        return self._optimizer
    
    def _try_fix_json(self, json_str: str) -> Optional[Dict[str, Any]]:
        """尝试修复损坏的 JSON"""
        for end_pos in range(len(json_str), max(0, len(json_str) - 200), -1):
            try:
                truncated = json_str[:end_pos]
                last_brace = truncated.rfind('}')
                if last_brace > 0:
                    test_str = truncated[:last_brace + 1]
                    result = json.loads(test_str)
                    logger.info(f"[LayoutDesignerTool] JSON 修复成功")
                    return result
            except:
                continue
        
        try:
            name_match = re.search(r'"name"\s*:\s*"([^"]+)"', json_str)
            if name_match:
                return {"name": name_match.group(1), "_partial": True}
        except:
            pass
        
        return None
    
    def _load_resume_data(self, resume_json: str) -> tuple:
        """加载简历数据
        
        Returns:
            (数据字典, 错误消息) - 成功时错误消息为 None
        """
        temp_dir = tempfile.gettempdir()
        ref = resume_json.strip()
        
        ref_map = {
            "@optimized": "optimized_resume.json",
            "@original": "original_resume.json",
            "@layout": "layout_resume.json",
        }
        
        if ref in ref_map:
            temp_file = os.path.join(temp_dir, ref_map[ref])
            if os.path.exists(temp_file):
                with open(temp_file, 'r', encoding='utf-8') as f:
                    return json.load(f), None
            else:
                return None, f"❌ 未找到数据文件，请先调用相应工具"
        
        # 解析 JSON
        try:
            return json.loads(resume_json), None
        except json.JSONDecodeError as e:
            logger.warning(f"[LayoutDesignerTool] JSON 解析失败: {e}")
            fixed = self._try_fix_json(resume_json)
            if fixed:
                return fixed, None
            return None, "❌ JSON 解析失败。提示：可使用 @optimized 引用优化后的数据"
    
    def _load_template_config(self, template: str) -> Optional[Dict[str, Any]]:
        """加载模板配置
        
        Args:
            template: 模板名称或 @selected
            
        Returns:
            布局配置字典，或 None
        """
        if not template:
            return None
        
        temp_dir = tempfile.gettempdir()
        
        # 使用已选模板
        if template.strip() == "@selected":
            layout_file = os.path.join(temp_dir, "template_layout.json")
            if os.path.exists(layout_file):
                with open(layout_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                logger.info("[LayoutDesignerTool] 使用已选模板配置")
                return config
            else:
                logger.warning("[LayoutDesignerTool] 未找到已选模板，使用默认配置")
                return None
        
        # 从注册表加载
        try:
            from tools.templates import get_registry
            registry = get_registry()
            template_config = registry.get(template)
            if template_config:
                return template_config.to_layout_config()
        except Exception as e:
            logger.warning(f"[LayoutDesignerTool] 加载模板失败: {e}")
        
        return None
    
    def execute(
        self,
        resume_json: str,
        template: str = "",
        style: str = "modern",
        page_preference: str = "auto",
    ) -> str:
        """执行布局设计。
        
        Args:
            resume_json: JSON 格式的简历数据或引用
            template: 模板名称或 @selected
            style: 样式偏好（备选）
            page_preference: 页面偏好
            
        Returns:
            布局配置和精简后的简历数据
        """
        # 1. 加载简历数据
        resume_data, error = self._load_resume_data(resume_json)
        if error:
            return error
        
        # 2. 加载模板配置
        template_config = self._load_template_config(template)
        
        # 3. 确定页面偏好
        if template_config and page_preference == "auto":
            # 从模板获取页面偏好
            page_pref = template_config.get("page_preference", "auto")
            if page_pref != "auto":
                page_preference = page_pref
        
        logger.info(f"[LayoutDesignerTool] 开始布局设计，样式: {style}, 页面: {page_preference}")
        
        # 4. 调用 Agent 或使用模板配置
        layout_config = {}
        suggestions = []
        
        if template_config:
            # 使用模板配置作为基础
            layout_config = template_config.copy()
            suggestions.append(f"使用模板配置")
        else:
            # 调用 Agent
            try:
                result = self.agent.run(resume_data)
                if result.success:
                    result_data = result.data
                    layout_config = result_data.get("layout_config", {})
                    resume_data = result_data.get("resume_data", resume_data)
                    suggestions.extend(result.suggestions)
                else:
                    logger.warning(f"[LayoutDesignerTool] Agent 执行失败: {result.error}")
            except Exception as e:
                logger.error(f"[LayoutDesignerTool] Agent 异常: {e}")
        
        # 应用样式偏好（如果模板未指定）
        if not template_config and style != "modern":
            style_config = self.agent.generate_style_config(style)
            layout_config.update(style_config)
        
        # 5. 智能分页优化
        if page_preference != "auto" or self._should_optimize(resume_data, layout_config):
            try:
                optimized_data, optimized_style, notes = self.optimizer.optimize_for_pages(
                    resume_data,
                    layout_config,
                    target=page_preference,
                )
                resume_data = optimized_data
                layout_config.update(optimized_style)
                suggestions.append(notes)
                logger.info(f"[LayoutDesignerTool] 分页优化: {notes}")
            except Exception as e:
                logger.warning(f"[LayoutDesignerTool] 分页优化失败: {e}")
        
        # 6. 嵌入布局配置
        resume_data["_layout_config"] = layout_config
        
        # 7. 保存结果
        temp_dir = tempfile.gettempdir()
        temp_file = os.path.join(temp_dir, "layout_resume.json")
        with open(temp_file, 'w', encoding='utf-8') as f:
            json.dump(resume_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"[LayoutDesignerTool] 布局设计完成")
        
        # 8. 构建返回消息
        design_notes = suggestions[:3] if suggestions else ["专业现代风格"]
        style_name = layout_config.get("style", style)
        page_info = "一页" if page_preference == "one_page" else (
            "两页" if page_preference == "two_pages" else "自动"
        )
        
        return f"""✅ 布局设计完成！

📐 配置:
  - 样式: {style_name}
  - 页面: {page_info}
  - 模板: {'已应用' if template_config else '默认'}

📝 设计说明:
{chr(10).join(f"  - {s}" for s in design_notes)}

调用 generate_resume 时可使用 resume_data="@layout" 来使用设计后的数据。"""
    
    def _should_optimize(self, resume_data: Dict, layout_config: Dict) -> bool:
        """判断是否需要分页优化"""
        try:
            from tools.generators.pagination import ContentEstimator
            estimator = ContentEstimator()
            pages = estimator.estimate_pages(resume_data, layout_config)
            # 如果超过 1.1 页，需要优化
            return pages > 1.1
        except Exception:
            return False
