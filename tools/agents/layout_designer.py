# -*- coding: utf-8 -*-
"""布局设计工具。

将 LayoutAgent 包装为 Tool，供 ReactAgent 调用。
内部保留完整的 Think-Execute-Reflect 流程。
"""
from __future__ import annotations

import json
import re
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
        1. Think: 分析内容密度，确定布局策略
        2. Execute: 生成布局配置（章节顺序、样式、间距等）
        3. Reflect: 提取设计说明
    
    Example:
        >>> from llm import ModelScopeOpenAI
        >>> llm = ModelScopeOpenAI()
        >>> tool = LayoutDesignerTool(llm)
        >>> result = tool.execute(resume_json='{"name": "张三", ...}')
    """
    
    def __init__(self, llm: "LLMProtocol"):
        """初始化工具。
        
        Args:
            llm: LLM 实例，用于初始化内部 Agent
        """
        super().__init__(
            name="layout_designer",
            description="设计简历布局，包括：章节排序、视觉层次、样式配置",
            parameters={
                "type": "object",
                "properties": {
                    "resume_json": {
                        "type": "string",
                        "description": "JSON 格式的简历数据（建议使用优化后的数据）",
                    },
                    "style": {
                        "type": "string",
                        "description": "样式偏好: modern(现代), classic(经典), minimal(简约)",
                        "enum": ["modern", "classic", "minimal"],
                        "default": "modern",
                    },
                },
                "required": ["resume_json"],
            },
        )
        self.llm = llm
        self._agent = None  # 延迟初始化
    
    @property
    def agent(self):
        """延迟加载 LayoutAgent。"""
        if self._agent is None:
            from agents.crews.resume.layout_agent import LayoutAgent
            self._agent = LayoutAgent(self.llm)
        return self._agent
    
    def _try_fix_json(self, json_str: str) -> Optional[Dict[str, Any]]:
        """尝试修复损坏的 JSON
        
        Args:
            json_str: 可能损坏的 JSON 字符串
            
        Returns:
            解析后的字典，或 None 表示无法修复
        """
        # 方法1：从后向前尝试截断
        for end_pos in range(len(json_str), max(0, len(json_str) - 200), -1):
            try:
                truncated = json_str[:end_pos]
                last_brace = truncated.rfind('}')
                if last_brace > 0:
                    test_str = truncated[:last_brace + 1]
                    result = json.loads(test_str)
                    logger.info(f"[LayoutDesignerTool] JSON 修复成功（截断到 {last_brace + 1} 字符）")
                    return result
            except:
                continue
        
        # 方法2：提取核心字段构建最小数据集
        try:
            name_match = re.search(r'"name"\s*:\s*"([^"]+)"', json_str)
            if name_match:
                logger.info("[LayoutDesignerTool] 使用最小数据集")
                return {"name": name_match.group(1), "_partial": True}
        except:
            pass
        
        return None
    
    def execute(self, resume_json: str, style: str = "modern") -> str:
        """执行布局设计。
        
        Args:
            resume_json: JSON 格式的简历数据
            style: 样式偏好
            
        Returns:
            布局配置和精简后的简历数据
        """
        # 检查是否使用优化后的数据
        if resume_json.strip() == "@optimized":
            import tempfile
            import os
            temp_file = os.path.join(tempfile.gettempdir(), "optimized_resume.json")
            if os.path.exists(temp_file):
                with open(temp_file, 'r', encoding='utf-8') as f:
                    resume_data = json.load(f)
                logger.info("[LayoutDesignerTool] 使用优化后的数据")
            else:
                return "❌ 未找到优化后的数据，请先调用 content_optimizer"
        else:
            # 解析输入（带修复尝试）
            try:
                resume_data = json.loads(resume_json)
            except json.JSONDecodeError as e:
                logger.warning(f"[LayoutDesignerTool] JSON 解析失败: {e}，尝试修复...")
                resume_data = self._try_fix_json(resume_json)
                if resume_data is None:
                    logger.error(f"[LayoutDesignerTool] 无法修复 JSON: {resume_json[:200]}...")
                    return f"❌ JSON 解析失败。提示：可以使用 resume_json=\"@optimized\" 来使用之前优化的数据。"
        
        logger.info(f"[LayoutDesignerTool] 开始布局设计，样式: {style}")
        
        # 调用 Agent 的完整流程（Think -> Execute -> Reflect）
        try:
            result = self.agent.run(resume_data)
        except Exception as e:
            logger.error(f"[LayoutDesignerTool] 执行失败: {e}")
            return f"❌ 布局设计失败: {e}"
        
        if not result.success:
            return f"❌ 布局设计失败: {result.error}"
        
        # 获取结果
        result_data = result.data
        layout_config = result_data.get("layout_config", {})
        trimmed_resume = result_data.get("resume_data", resume_data)
        
        # 应用样式偏好
        if style != "modern":
            style_config = self.agent.generate_style_config(style)
            layout_config.update(style_config)
        
        # 将 layout_config 嵌入到 resume_data 中
        trimmed_resume["_layout_config"] = layout_config
        
        # 保存到临时文件（避免 LLM 传递长 JSON）
        import tempfile
        import os
        temp_dir = tempfile.gettempdir()
        temp_file = os.path.join(temp_dir, "layout_resume.json")
        with open(temp_file, 'w', encoding='utf-8') as f:
            json.dump(trimmed_resume, f, ensure_ascii=False, indent=2)
        
        logger.info(f"[LayoutDesignerTool] 布局设计完成，数据已保存到: {temp_file}")
        
        # 返回简短的成功消息
        design_notes = result.suggestions[:2] if result.suggestions else ["专业现代风格"]
        return f"""✅ 布局设计完成！

样式: {layout_config.get('style', 'modern')}
设计说明：
{chr(10).join(f"- {s}" for s in design_notes)}

调用 generate_resume 时可使用 resume_data="@layout" 来使用设计后的数据。"""
