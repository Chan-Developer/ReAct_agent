# -*- coding: utf-8 -*-
"""简历生成流程完整测试。

测试新的三阶段流水线：
1. 内容优化 (ContentOptimizerTool)
2. 模板选择 (StyleSelectorTool)
3. 布局设计 + 智能分页 (LayoutDesignerTool)
4. 文档生成 (ResumeGenerator)
"""
import json
import os
import tempfile
import pytest
from unittest.mock import MagicMock, patch


# =============================================================================
# 测试数据
# =============================================================================

SAMPLE_RESUME = {
    "name": "张三",
    "phone": "13800138000",
    "email": "zhangsan@example.com",
    "location": "北京市",
    "github": "https://github.com/zhangsan",
    "summary": "5年Python开发经验，擅长后端架构设计",
    "education": [
        {
            "school": "北京大学",
            "degree": "硕士",
            "major": "计算机科学",
            "start_date": "2015-09",
            "end_date": "2018-06",
            "gpa": "3.8/4.0"
        }
    ],
    "experience": [
        {
            "company": "阿里巴巴",
            "position": "高级后端工程师",
            "start_date": "2020-03",
            "end_date": "至今",
            "description": "负责核心交易系统开发",
            "highlights": [
                "主导重构订单系统，QPS提升300%",
                "设计分布式缓存方案，节省服务器成本50万/年",
                "带领5人团队完成微服务拆分"
            ]
        },
        {
            "company": "字节跳动",
            "position": "后端工程师",
            "start_date": "2018-07",
            "end_date": "2020-02",
            "description": "参与推荐系统开发",
            "highlights": [
                "开发用户画像服务，日处理数据10亿条",
                "优化推荐算法接口，延迟降低60%"
            ]
        }
    ],
    "projects": [
        {
            "name": "分布式任务调度平台",
            "role": "技术负责人",
            "start_date": "2021-06",
            "end_date": "2022-03",
            "description": "基于K8s的分布式任务调度平台",
            "highlights": [
                "支持百万级任务调度",
                "自研调度算法，资源利用率提升40%"
            ],
            "tech_stack": ["Python", "Kubernetes", "Redis", "MySQL"]
        }
    ],
    "skills": [
        "Python", "Go", "Java",
        "Django", "Flask", "FastAPI",
        "MySQL", "PostgreSQL", "Redis", "MongoDB",
        "Docker", "Kubernetes", "AWS"
    ],
    "certificates": ["AWS认证架构师"],
    "awards": ["2021年度优秀员工"]
}

SAMPLE_JOB_DESCRIPTION = """
招聘：高级Python后端工程师

岗位职责：
- 负责核心业务系统的架构设计和开发
- 参与技术方案评审和代码Review
- 指导初级工程师成长

任职要求：
- 5年以上Python开发经验
- 熟悉Django/Flask等Web框架
- 精通MySQL、Redis等存储技术
- 有微服务架构经验者优先
- 有大型互联网公司经验者优先
"""


# =============================================================================
# 模板系统测试
# =============================================================================

class TestTemplateSystem:
    """模板系统测试"""
    
    def test_template_registry_load(self):
        """测试模板注册表加载"""
        from tools.templates import get_registry
        
        registry = get_registry()
        
        # 验证预设模板已加载
        assert len(registry) >= 5, "应至少有5个预设模板"
        assert "tech_modern" in registry
        assert "tech_classic" in registry
        assert "management" in registry
        assert "creative" in registry
        assert "fresh_graduate" in registry
    
    def test_template_config_from_json(self):
        """测试从JSON加载模板配置"""
        from tools.templates.base import TemplateConfig
        
        # 创建临时JSON文件
        config_data = {
            "name": "test_template",
            "display_name": "测试模板",
            "tags": ["测试"],
            "job_keywords": ["工程师"],
            "page_preference": "one_page",
            "font_config": {"body_size": 10}
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config_data, f)
            temp_path = f.name
        
        try:
            config = TemplateConfig.from_json(temp_path)
            assert config.name == "test_template"
            assert config.display_name == "测试模板"
            assert config.font_config.body_size == 10
        finally:
            os.unlink(temp_path)
    
    def test_template_job_matching(self):
        """测试模板职位匹配"""
        from tools.templates import get_registry
        
        registry = get_registry()
        
        # 技术岗位应该匹配 tech_modern
        matches = registry.match_job("招聘Python后端工程师，熟悉Django", top_k=3)
        
        assert len(matches) > 0
        # 第一个应该是技术相关模板
        top_match_name = matches[0][0]
        assert "tech" in top_match_name or matches[0][1] > 0
    
    def test_template_to_layout_config(self):
        """测试模板转换为布局配置"""
        from tools.templates import get_registry
        
        registry = get_registry()
        config = registry.get("tech_modern")
        
        layout_config = config.to_layout_config()
        
        assert "section_order" in layout_config
        assert "font_config" in layout_config
        assert "spacing_config" in layout_config
        assert "visual_elements" in layout_config


# =============================================================================
# 分页系统测试
# =============================================================================

class TestPaginationSystem:
    """分页系统测试"""
    
    def test_content_estimator(self):
        """测试内容估算器"""
        from tools.generators.pagination import ContentEstimator
        
        estimator = ContentEstimator()
        
        style_config = {
            "font_config": {"body_size": 9},
            "spacing_config": {"margin": 0.4, "section_gap": 4}
        }
        
        # 估算页数
        pages = estimator.estimate_pages(SAMPLE_RESUME, style_config)
        
        assert pages > 0
        assert pages < 5  # 不应超过5页
        print(f"估算页数: {pages:.2f}")
    
    def test_content_density(self):
        """测试内容密度计算"""
        from tools.generators.pagination import ContentEstimator
        
        estimator = ContentEstimator()
        
        density = estimator.get_content_density(SAMPLE_RESUME)
        
        assert density in ["low", "medium", "high", "very_high"]
        print(f"内容密度: {density}")
    
    def test_layout_optimizer_compress(self):
        """测试布局优化器压缩"""
        from tools.generators.pagination import LayoutOptimizer
        import copy
        
        optimizer = LayoutOptimizer()
        
        # 创建一个内容较多的简历
        large_resume = copy.deepcopy(SAMPLE_RESUME)
        # 添加更多经历
        for i in range(3):
            large_resume["experience"].append({
                "company": f"公司{i}",
                "position": "工程师",
                "highlights": ["成就1", "成就2", "成就3", "成就4", "成就5"]
            })
        
        style_config = {
            "font_config": {"body_size": 9},
            "spacing_config": {"margin": 0.4, "section_gap": 6, "item_gap": 2}
        }
        
        # 优化为一页
        data, style, notes = optimizer.optimize_for_pages(
            large_resume, style_config, target="one_page"
        )
        
        assert notes != ""
        print(f"优化说明: {notes}")
    
    def test_page_splitter(self):
        """测试分页器"""
        from tools.generators.pagination import PageSplitter
        
        splitter = PageSplitter()
        
        style_config = {
            "font_config": {"body_size": 9},
            "spacing_config": {"margin": 0.4}
        }
        
        # 获取分页建议
        recommendation = splitter.get_page_break_recommendation(
            SAMPLE_RESUME, style_config
        )
        
        assert "estimated_pages" in recommendation
        assert "recommendation" in recommendation
        print(f"分页建议: {recommendation}")


# =============================================================================
# StyleSelectorTool 测试
# =============================================================================

class TestStyleSelectorTool:
    """模板选择工具测试"""
    
    def test_list_templates(self):
        """测试列出模板"""
        from tools.agent_wrappers.style_selector import StyleSelectorTool
        
        tool = StyleSelectorTool()
        result = tool.execute(action="list")
        
        assert "可用模板列表" in result
        assert "tech_modern" in result
    
    def test_select_template(self):
        """测试手动选择模板"""
        from tools.agent_wrappers.style_selector import StyleSelectorTool
        
        tool = StyleSelectorTool()
        result = tool.execute(action="select", template_name="tech_modern")
        
        assert "已选择模板" in result
        assert "技术岗-现代风格" in result
    
    def test_match_template_with_jd(self):
        """测试根据JD匹配模板"""
        from tools.agent_wrappers.style_selector import StyleSelectorTool
        
        tool = StyleSelectorTool()
        result = tool.execute(
            action="match",
            job_description=SAMPLE_JOB_DESCRIPTION
        )
        
        assert "模板匹配完成" in result or "推荐模板" in result
    
    def test_custom_overrides(self):
        """测试自定义配置覆盖"""
        from tools.agent_wrappers.style_selector import StyleSelectorTool
        
        tool = StyleSelectorTool()
        
        overrides = json.dumps({
            "font_config": {"body_size": 8},
            "page_preference": "one_page"
        })
        
        result = tool.execute(
            template_name="tech_modern",
            custom_overrides=overrides
        )
        
        assert "已选择模板" in result


# =============================================================================
# 工作流程集成测试
# =============================================================================

class TestWorkflowIntegration:
    """工作流程集成测试（需要 Mock LLM）"""
    
    @pytest.fixture
    def mock_llm(self):
        """创建模拟的LLM"""
        llm = MagicMock()
        
        # 模拟 think 响应
        llm.chat.return_value = json.dumps({
            "analysis": {
                "summary_score": 7,
                "experience_score": 8,
                "project_score": 7,
                "skills_score": 8,
                "overall_score": 7.5
            },
            "weaknesses": ["可以更加量化成就"],
            "opportunities": ["添加更多技术细节"],
            "reasoning": "简历整体质量良好"
        })
        
        return llm
    
    def test_data_flow_through_temp_files(self):
        """测试数据通过临时文件传递"""
        temp_dir = tempfile.gettempdir()
        
        # 保存原始数据
        original_file = os.path.join(temp_dir, "original_resume.json")
        with open(original_file, 'w', encoding='utf-8') as f:
            json.dump(SAMPLE_RESUME, f, ensure_ascii=False)
        
        # 验证可以读取
        with open(original_file, 'r', encoding='utf-8') as f:
            loaded = json.load(f)
        
        assert loaded["name"] == "张三"
        
        # 清理
        os.unlink(original_file)
    
    def test_template_selection_saves_config(self):
        """测试模板选择保存配置"""
        from tools.agent_wrappers.style_selector import StyleSelectorTool
        
        tool = StyleSelectorTool()
        tool.execute(template_name="tech_modern")
        
        # 验证配置已保存
        temp_dir = tempfile.gettempdir()
        config_file = os.path.join(temp_dir, "selected_template.json")
        layout_file = os.path.join(temp_dir, "template_layout.json")
        
        assert os.path.exists(config_file)
        assert os.path.exists(layout_file)
        
        # 验证内容
        with open(layout_file, 'r', encoding='utf-8') as f:
            layout = json.load(f)
        
        assert "section_order" in layout
        assert "font_config" in layout


# =============================================================================
# 边界情况测试
# =============================================================================

class TestEdgeCases:
    """边界情况测试"""
    
    def test_empty_resume(self):
        """测试空简历"""
        from tools.generators.pagination import ContentEstimator
        
        estimator = ContentEstimator()
        
        empty_resume = {"name": "测试"}
        style_config = {"font_config": {}, "spacing_config": {}}
        
        pages = estimator.estimate_pages(empty_resume, style_config)
        
        assert pages > 0
        assert pages < 1  # 空简历应该不到一页
    
    def test_very_large_resume(self):
        """测试超大简历"""
        from tools.generators.pagination import ContentEstimator, LayoutOptimizer
        import copy
        
        # 创建超大简历
        large_resume = copy.deepcopy(SAMPLE_RESUME)
        for i in range(10):
            large_resume["experience"].append({
                "company": f"公司{i}",
                "position": "工程师",
                "highlights": [f"成就{j}" for j in range(10)]
            })
            large_resume["projects"].append({
                "name": f"项目{i}",
                "highlights": [f"亮点{j}" for j in range(5)]
            })
        
        estimator = ContentEstimator()
        optimizer = LayoutOptimizer()
        
        style_config = {"font_config": {"body_size": 9}, "spacing_config": {"margin": 0.4}}
        
        # 估算应该超过2页
        pages = estimator.estimate_pages(large_resume, style_config)
        assert pages > 2
        
        # 优化后应该有所改善
        data, style, notes = optimizer.optimize_for_pages(
            large_resume, style_config, target="one_page"
        )
        assert notes != ""
    
    def test_missing_template(self):
        """测试不存在的模板"""
        from tools.agent_wrappers.style_selector import StyleSelectorTool
        
        tool = StyleSelectorTool()
        result = tool.execute(template_name="nonexistent_template")
        
        assert "未找到模板" in result
    
    def test_invalid_json_override(self):
        """测试无效的JSON覆盖"""
        from tools.agent_wrappers.style_selector import StyleSelectorTool
        
        tool = StyleSelectorTool()
        result = tool.execute(
            template_name="tech_modern",
            custom_overrides="invalid json {"
        )
        
        # 应该仍然成功，只是忽略无效的覆盖
        assert "已选择模板" in result


# =============================================================================
# 运行测试
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
