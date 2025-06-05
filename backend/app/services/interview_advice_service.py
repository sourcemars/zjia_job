"""
Interview advice service for generating resume optimization and technical preparation suggestions.
"""
import json
import logging
from typing import Dict, Any, List
from dataclasses import dataclass

from app.models.job_listing import JobListing
from app.services.matching_service import MatchResult, SkillMatchingRule

logger = logging.getLogger(__name__)

@dataclass
class InterviewAdvice:
    """Interview advice data structure."""
    job_id: str
    job_title: str
    company_name: str
    resume_optimization: Dict[str, Any]
    technical_preparation: Dict[str, Any]
    overall_suggestions: List[str]

class InterviewAdviceService:
    """Service for generating interview advice based on job matches."""
    
    def __init__(self):
        self.skill_matcher = SkillMatchingRule()
    
    def generate_advice(
        self, 
        resume_data: Dict[str, Any], 
        match_result: MatchResult,
        job: JobListing
    ) -> InterviewAdvice:
        """Generate comprehensive interview advice for a job match."""
        
        resume_optimization = self._generate_resume_optimization(resume_data, job)
        technical_preparation = self._generate_technical_preparation(resume_data, job)
        overall_suggestions = self._generate_overall_suggestions(match_result, resume_optimization, technical_preparation)
        
        return InterviewAdvice(
            job_id=match_result.job_id,
            job_title=match_result.job_title,
            company_name=match_result.company_name,
            resume_optimization=resume_optimization,
            technical_preparation=technical_preparation,
            overall_suggestions=overall_suggestions
        )
    
    def _generate_resume_optimization(self, resume_data: Dict[str, Any], job: JobListing) -> Dict[str, Any]:
        """Generate resume optimization suggestions."""
        suggestions = {
            "missing_skills": [],
            "skill_improvements": [],
            "experience_gaps": [],
            "education_recommendations": []
        }
        
        resume_skills = self.skill_matcher._extract_resume_skills(resume_data)
        job_skills = self.skill_matcher._extract_job_skills(job)
        
        missing_skills = job_skills - resume_skills
        if missing_skills:
            suggestions["missing_skills"] = list(missing_skills)
        
        if job.experience and resume_data.get('experience'):
            suggestions["experience_gaps"] = self._analyze_experience_gaps(resume_data, job)
        
        if job.education:
            suggestions["education_recommendations"] = self._analyze_education_gaps(resume_data, job)
        
        return suggestions
    
    def _generate_technical_preparation(self, resume_data: Dict[str, Any], job: JobListing) -> Dict[str, Any]:
        """Generate technical preparation checklist."""
        preparation = {
            "key_technologies": [],
            "study_topics": [],
            "practice_areas": [],
            "interview_questions": []
        }
        
        job_skills = self.skill_matcher._extract_job_skills(job)
        
        preparation["key_technologies"] = list(job_skills)
        
        if job.requirements:
            preparation["study_topics"] = self._extract_study_topics(job.requirements)
        
        preparation["practice_areas"] = self._generate_practice_areas(job_skills)
        
        preparation["interview_questions"] = self._generate_interview_questions(job)
        
        return preparation
    
    def _analyze_experience_gaps(self, resume_data: Dict[str, Any], job: JobListing) -> List[str]:
        """Analyze experience gaps between resume and job requirements."""
        gaps = []
        
        job_exp = job.experience.lower() if job.experience else ""
        resume_exp = resume_data.get('experience', [])
        
        if '年' in job_exp or 'year' in job_exp:
            gaps.append("确保简历中明确标注工作年限")
        
        if '项目' in job_exp or 'project' in job_exp:
            gaps.append("突出项目经验和具体成果")
        
        return gaps
    
    def _analyze_education_gaps(self, resume_data: Dict[str, Any], job: JobListing) -> List[str]:
        """Analyze education gaps and provide recommendations."""
        recommendations = []
        
        if job.education:
            job_edu = job.education.lower()
            if '本科' in job_edu or '学士' in job_edu:
                recommendations.append("确保简历中突出本科学历和相关专业")
            elif '硕士' in job_edu or '研究生' in job_edu:
                recommendations.append("如有研究生学历，请在简历中突出显示")
        
        return recommendations
    
    def _extract_study_topics(self, requirements: str) -> List[str]:
        """Extract study topics from job requirements."""
        topics = []
        
        requirements_lower = requirements.lower()
        
        topic_keywords = {
            'algorithm': '算法和数据结构',
            'database': '数据库设计和优化',
            'system': '系统设计',
            'network': '网络协议',
            'security': '信息安全',
            'performance': '性能优化'
        }
        
        for keyword, topic in topic_keywords.items():
            if keyword in requirements_lower:
                topics.append(topic)
        
        return topics
    
    def _generate_practice_areas(self, job_skills: set) -> List[str]:
        """Generate practice areas based on job skills."""
        practice_areas = []
        
        skill_to_practice = {
            'python': 'Python编程练习和项目实战',
            'java': 'Java核心概念和框架应用',
            'javascript': 'JavaScript和前端框架练习',
            'sql': 'SQL查询优化和数据库设计',
            'git': 'Git版本控制和协作流程',
            'docker': 'Docker容器化部署实践'
        }
        
        for skill in job_skills:
            if skill in skill_to_practice:
                practice_areas.append(skill_to_practice[skill])
        
        return practice_areas
    
    def _generate_interview_questions(self, job: JobListing) -> List[str]:
        """Generate common interview questions based on job."""
        questions = [
            "请介绍一下您最有挑战性的项目经验",
            "您如何处理工作中遇到的技术难题？",
            "请描述您的团队协作经验"
        ]
        
        if job.requirements:
            req_lower = job.requirements.lower()
            if 'leadership' in req_lower or '领导' in req_lower:
                questions.append("请分享您的团队领导经验")
            if 'innovation' in req_lower or '创新' in req_lower:
                questions.append("请举例说明您的创新思维")
        
        return questions
    
    def _generate_overall_suggestions(
        self, 
        match_result: MatchResult, 
        resume_optimization: Dict[str, Any], 
        technical_preparation: Dict[str, Any]
    ) -> List[str]:
        """Generate overall interview suggestions."""
        suggestions = []
        
        if match_result.match_score < 0.7:
            suggestions.append("建议重点提升简历与职位的匹配度")
        
        if resume_optimization.get("missing_skills"):
            suggestions.append("面试前重点学习缺失的技能")
        
        suggestions.extend([
            "准备具体的项目案例和成果数据",
            "了解公司文化和发展方向",
            "准备针对性的问题向面试官提问"
        ])
        
        return suggestions
