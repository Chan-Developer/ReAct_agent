# -*- coding: utf-8 -*-
"""简历本地增强器。

提供不依赖 LLM 的本地简历增强功能：
- 技能分类
- 格式规范化
- 内容补全建议

这些功能可以离线使用，适合快速预处理。
"""
from __future__ import annotations

from typing import Any, Dict, List


class ResumeEnhancer:
    """简历本地增强器。
    
    提供不需要 LLM 的本地增强功能，可用于：
    - 简历数据预处理
    - 快速内容检查
    - 技能自动分类
    
    Example:
        >>> enhancer = ResumeEnhancer()
        >>> categorized = enhancer.categorize_skills(["Python", "React", "MySQL"])
        >>> suggestions = enhancer.suggest_improvements(resume_data)
    """
    
    # 技能分类映射表
    SKILL_CATEGORIES: Dict[str, List[str]] = {
        "编程语言": [
            "Python", "Java", "C++", "C", "JavaScript", "TypeScript",
            "Go", "Rust", "Kotlin", "Swift", "Scala", "Ruby", "PHP",
        ],
        "前端技术": [
            "React", "Vue", "Angular", "HTML", "CSS", "SCSS", "Less",
            "Node.js", "Webpack", "Vite", "Next.js", "Nuxt.js",
        ],
        "后端框架": [
            "Django", "Flask", "FastAPI", "Spring", "SpringBoot",
            "Express", "Gin", "Echo", "Fiber", "NestJS",
        ],
        "数据库": [
            "MySQL", "PostgreSQL", "MongoDB", "Redis", "Elasticsearch",
            "SQLite", "Oracle", "SQL Server", "Cassandra", "Neo4j",
        ],
        "AI/ML": [
            "PyTorch", "TensorFlow", "Keras", "Scikit-learn", "Pandas",
            "NumPy", "机器学习", "深度学习", "NLP", "CV", "计算机视觉",
            "自然语言处理", "强化学习", "Transformer", "BERT", "GPT",
        ],
        "云原生": [
            "Docker", "Kubernetes", "K8s", "AWS", "Azure", "GCP",
            "云计算", "微服务", "Serverless", "Terraform", "Helm",
        ],
        "大数据": [
            "Hadoop", "Spark", "Flink", "Kafka", "Hive", "HBase",
            "数据仓库", "ETL", "数据分析",
        ],
        "工具": [
            "Git", "Linux", "Jenkins", "CI/CD", "Nginx", "GitLab",
            "GitHub Actions", "Jira", "Confluence",
        ],
    }
    
    # 简历质量检查规则
    QUALITY_RULES = {
        "summary_min_length": 30,
        "summary_max_length": 200,
        "min_skills_count": 3,
        "description_min_length": 20,
    }
    
    @classmethod
    def categorize_skills(cls, skills: List[str]) -> Dict[str, List[str]]:
        """将技能按类别分组。
        
        Args:
            skills: 技能列表
            
        Returns:
            分类后的技能字典，key 为类别名，value 为技能列表
            
        Example:
            >>> ResumeEnhancer.categorize_skills(["Python", "React", "MySQL"])
            {'编程语言': ['Python'], '前端技术': ['React'], '数据库': ['MySQL']}
        """
        categorized: Dict[str, List[str]] = {}
        uncategorized: List[str] = []
        
        for skill in skills:
            found = False
            skill_lower = skill.lower()
            
            for category, keywords in cls.SKILL_CATEGORIES.items():
                for keyword in keywords:
                    keyword_lower = keyword.lower()
                    # 双向匹配：技能包含关键词 或 关键词包含技能
                    if keyword_lower in skill_lower or skill_lower in keyword_lower:
                        if category not in categorized:
                            categorized[category] = []
                        if skill not in categorized[category]:
                            categorized[category].append(skill)
                        found = True
                        break
                if found:
                    break
            
            if not found:
                uncategorized.append(skill)
        
        if uncategorized:
            categorized["其他"] = uncategorized
        
        return categorized
    
    @classmethod
    def suggest_improvements(cls, resume_data: Dict[str, Any]) -> List[str]:
        """分析简历并给出改进建议。
        
        Args:
            resume_data: 简历数据字典
            
        Returns:
            改进建议列表，每条建议包含图标标识优先级
            
        Example:
            >>> suggestions = ResumeEnhancer.suggest_improvements({"name": "张三"})
            ['⚠️ 缺少联系方式（邮箱或电话）', '💡 建议添加个人简介，突出核心竞争力', ...]
        """
        suggestions: List[str] = []
        rules = cls.QUALITY_RULES
        
        # === 必填字段检查 ===
        if not resume_data.get("name"):
            suggestions.append("⚠️ 缺少姓名")
        
        if not resume_data.get("email") and not resume_data.get("phone"):
            suggestions.append("⚠️ 缺少联系方式（邮箱或电话）")
        
        # === 个人简介检查 ===
        summary = resume_data.get("summary", "")
        if not summary:
            suggestions.append("💡 建议添加个人简介，突出核心竞争力")
        elif len(summary) < rules["summary_min_length"]:
            suggestions.append(
                f"💡 个人简介过短（{len(summary)}字），建议扩充到50-100字"
            )
        elif len(summary) > rules["summary_max_length"]:
            suggestions.append(
                f"💡 个人简介过长（{len(summary)}字），建议精简到100字以内"
            )
        
        # === 教育背景检查 ===
        education = resume_data.get("education", [])
        if not education:
            suggestions.append("⚠️ 缺少教育背景")
        else:
            for i, edu in enumerate(education):
                if not edu.get("school"):
                    suggestions.append(f"⚠️ 教育经历 {i+1} 缺少学校名称")
                if not edu.get("major"):
                    suggestions.append(f"💡 教育经历 {i+1} 建议补充专业信息")
        
        # === 工作/项目经历检查 ===
        experience = resume_data.get("experience", [])
        projects = resume_data.get("projects", [])
        
        if not experience and not projects:
            suggestions.append("💡 建议添加实习经历或项目经验")
        
        for i, exp in enumerate(experience):
            desc = exp.get("description", "")
            if not desc:
                suggestions.append(f"💡 工作经历 {i+1} 缺少工作描述")
            elif len(desc) < rules["description_min_length"]:
                suggestions.append(f"💡 工作经历 {i+1} 描述过短，建议详细描述职责和成果")
        
        for i, proj in enumerate(projects):
            proj_name = proj.get("name", f"项目{i+1}")
            if not proj.get("description"):
                suggestions.append(f"💡 项目 '{proj_name}' 缺少项目描述")
            if not proj.get("highlights"):
                suggestions.append(f"💡 项目 '{proj_name}' 建议添加项目亮点/成果")
            if not proj.get("tech_stack"):
                suggestions.append(f"💡 项目 '{proj_name}' 建议补充技术栈")
        
        # === 技能检查 ===
        skills = resume_data.get("skills", [])
        if not skills:
            suggestions.append("⚠️ 缺少技能标签")
        elif len(skills) < rules["min_skills_count"]:
            suggestions.append(f"💡 技能较少（{len(skills)}项），建议补充更多相关技能")
        
        return suggestions
    
    @classmethod
    def normalize_data(cls, resume_data: Dict[str, Any]) -> Dict[str, Any]:
        """规范化简历数据。
        
        - 去除字符串首尾空格
        - 确保列表字段存在
        - 统一日期格式等
        
        Args:
            resume_data: 原始简历数据
            
        Returns:
            规范化后的简历数据
        """
        normalized = {}
        
        # 字符串字段处理
        string_fields = ["name", "phone", "email", "location", "summary", 
                        "github", "linkedin", "website"]
        for field in string_fields:
            value = resume_data.get(field, "")
            normalized[field] = value.strip() if isinstance(value, str) else ""
        
        # 列表字段确保存在
        list_fields = ["skills", "certificates", "awards", "languages", "interests"]
        for field in list_fields:
            value = resume_data.get(field, [])
            normalized[field] = value if isinstance(value, list) else []
        
        # 复杂对象字段
        for field in ["education", "experience", "projects", "skill_levels"]:
            normalized[field] = resume_data.get(field, [])
        
        return normalized
    
    @classmethod
    def calculate_completeness(cls, resume_data: Dict[str, Any]) -> float:
        """计算简历完整度。
        
        Args:
            resume_data: 简历数据
            
        Returns:
            完整度百分比（0-100）
        """
        total_weight = 0
        achieved_weight = 0
        
        # 权重配置
        weights = {
            "name": 10,
            "contact": 10,  # email or phone
            "summary": 15,
            "education": 20,
            "experience": 20,
            "projects": 15,
            "skills": 10,
        }
        
        # 姓名
        total_weight += weights["name"]
        if resume_data.get("name"):
            achieved_weight += weights["name"]
        
        # 联系方式
        total_weight += weights["contact"]
        if resume_data.get("email") or resume_data.get("phone"):
            achieved_weight += weights["contact"]
        
        # 个人简介
        total_weight += weights["summary"]
        summary = resume_data.get("summary", "")
        if len(summary) >= 30:
            achieved_weight += weights["summary"]
        elif summary:
            achieved_weight += weights["summary"] * 0.5
        
        # 教育背景
        total_weight += weights["education"]
        if resume_data.get("education"):
            achieved_weight += weights["education"]
        
        # 工作经历
        total_weight += weights["experience"]
        if resume_data.get("experience"):
            achieved_weight += weights["experience"]
        elif resume_data.get("projects"):  # 有项目也算部分分
            achieved_weight += weights["experience"] * 0.5
        
        # 项目经历
        total_weight += weights["projects"]
        if resume_data.get("projects"):
            achieved_weight += weights["projects"]
        
        # 技能
        total_weight += weights["skills"]
        skills = resume_data.get("skills", [])
        if len(skills) >= 5:
            achieved_weight += weights["skills"]
        elif len(skills) >= 3:
            achieved_weight += weights["skills"] * 0.7
        elif skills:
            achieved_weight += weights["skills"] * 0.4
        
        return round(achieved_weight / total_weight * 100, 1) if total_weight > 0 else 0

