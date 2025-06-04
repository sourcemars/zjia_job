"""
Extensible job matching service with configurable rule engine.
Implements mandatory pre-screening filters and weighted scoring algorithm.
"""
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from abc import ABC, abstractmethod
from sqlalchemy.orm import Session

from app.models.job_listing import JobListing
from app.models.match import Match
from app.services.job_service import get_job_listings

logger = logging.getLogger(__name__)

@dataclass
class MatchResult:
    """Result of a job match with score and explanation."""
    job_id: str
    job_title: str
    company_name: str
    match_score: float
    explanation: str
    details: Dict[str, Any]

class MatchingRule(ABC):
    """Abstract base class for matching rules."""
    
    @abstractmethod
    def evaluate(self, resume_data: Dict[str, Any], job: JobListing) -> Tuple[bool, str]:
        """
        Evaluate if resume matches job based on this rule.
        
        Returns:
            Tuple of (passes_rule, explanation)
        """
        pass

class EducationRule(MatchingRule):
    """Mandatory education requirement rule - one vote veto."""
    
    EDUCATION_LEVELS = {
        '高中': 1, '中专': 1,
        '大专': 2, '专科': 2,
        '本科': 3, '学士': 3,
        '硕士': 4, '研究生': 4,
        '博士': 5, '博士后': 6
    }
    
    def evaluate(self, resume_data: Dict[str, Any], job: JobListing) -> Tuple[bool, str]:
        """Check if resume education meets job minimum requirement."""
        if not job.education:
            return True, "职位无学历要求"
            
        job_edu_level = self._parse_education_level(job.education)
        if job_edu_level == 0:
            return True, "无法解析职位学历要求"
            
        resume_education = resume_data.get('education', [])
        if not resume_education:
            return False, "简历中未找到学历信息"
            
        max_resume_level = 0
        for edu in resume_education:
            if isinstance(edu, str):
                level = self._parse_education_level(edu)
                max_resume_level = max(max_resume_level, level)
                
        if max_resume_level >= job_edu_level:
            return True, f"学历符合要求 (简历:{max_resume_level} >= 要求:{job_edu_level})"
        else:
            return False, f"学历不符合要求 (简历:{max_resume_level} < 要求:{job_edu_level})"
    
    def _parse_education_level(self, education_text: str) -> int:
        """Parse education level from text."""
        if not education_text:
            return 0
            
        education_text = education_text.lower()
        for edu_name, level in self.EDUCATION_LEVELS.items():
            if edu_name in education_text:
                return level
        return 0

class JobSeekerStatusRule(MatchingRule):
    """Mandatory job seeker status rule - one vote veto."""
    
    def evaluate(self, resume_data: Dict[str, Any], job: JobListing) -> Tuple[bool, str]:
        """Check if job seeker status matches job requirements."""
        if not job.experience:
            return True, "职位无经验要求"
            
        requires_experience = self._job_requires_experience(job.experience)
        if not requires_experience:
            return True, "职位接受应届生"
            
        is_student = self._is_candidate_student(resume_data)
        if is_student:
            return False, "职位要求工作经验，但求职者尚未毕业"
            
        return True, "求职者状态符合职位要求"
    
    def _job_requires_experience(self, experience_text: str) -> bool:
        """Check if job requires work experience."""
        if not experience_text:
            return False
            
        experience_text = experience_text.lower()
        no_exp_keywords = ['应届', '无经验', '不限', '0年', '实习']
        
        for keyword in no_exp_keywords:
            if keyword in experience_text:
                return False
                
        return True
    
    def _is_candidate_student(self, resume_data: Dict[str, Any]) -> bool:
        """Check if candidate is still a student."""
        education = resume_data.get('education', [])
        summary = resume_data.get('summary', '')
        
        student_keywords = ['在读', '在校', '即将毕业', '预计毕业', '学生']
        
        if summary:
            for keyword in student_keywords:
                if keyword in summary:
                    return True
                    
        for edu in education:
            if isinstance(edu, str):
                for keyword in student_keywords:
                    if keyword in edu:
                        return True
                        
        return False

class SkillMatchingRule(MatchingRule):
    """Skill matching rule for scoring (not mandatory)."""
    
    def evaluate(self, resume_data: Dict[str, Any], job: JobListing) -> Tuple[bool, str]:
        """Calculate skill matching score."""
        resume_skills = self._extract_resume_skills(resume_data)
        job_skills = self._extract_job_skills(job)
        
        if not resume_skills or not job_skills:
            return True, "技能匹配度: 无法计算"
            
        matched_skills = resume_skills.intersection(job_skills)
        match_ratio = len(matched_skills) / len(job_skills) if job_skills else 0
        
        explanation = f"技能匹配度: {match_ratio:.2%} ({len(matched_skills)}/{len(job_skills)})"
        if matched_skills:
            explanation += f" 匹配技能: {', '.join(list(matched_skills)[:5])}"
            
        return True, explanation
    
    def _extract_resume_skills(self, resume_data: Dict[str, Any]) -> set:
        """Extract skills from resume data."""
        skills = set()
        
        resume_skills = resume_data.get('skills', [])
        for skill in resume_skills:
            if isinstance(skill, str):
                skills.update(self._parse_skills_text(skill))
                
        experience = resume_data.get('experience', [])
        for exp in experience:
            if isinstance(exp, str):
                skills.update(self._parse_skills_text(exp))
                
        return skills
    
    def _extract_job_skills(self, job: JobListing) -> set:
        """Extract required skills from job listing."""
        skills = set()
        
        if job.requirements:
            skills.update(self._parse_skills_text(job.requirements))
            
        if job.description:
            skills.update(self._parse_skills_text(job.description))
            
        return skills
    
    def _parse_skills_text(self, text: str) -> set:
        """Parse technical skills from text."""
        if not text:
            return set()
            
        tech_skills = {
            'php', 'java', 'python', 'javascript', 'js', 'vue', 'react', 'angular',
            'mysql', 'postgresql', 'mongodb', 'redis', 'elasticsearch',
            'html', 'css', 'bootstrap', 'jquery', 'nodejs', 'express',
            'spring', 'laravel', 'django', 'flask', 'docker', 'kubernetes',
            'git', 'svn', 'linux', 'windows', 'nginx', 'apache',
            'restful', 'api', 'microservice', 'distributed', 'cloud'
        }
        
        text_lower = text.lower()
        found_skills = set()
        
        for skill in tech_skills:
            if skill in text_lower:
                found_skills.add(skill)
                
        return found_skills

class JobMatchingService:
    """Main job matching service with configurable rules."""
    
    def __init__(self):
        self.mandatory_rules = [
            EducationRule(),
            JobSeekerStatusRule()
        ]
        self.scoring_rules = [
            SkillMatchingRule()
        ]
        
    def match_resume_to_jobs(
        self, 
        resume_data: Dict[str, Any], 
        db: Session,
        limit: int = 20
    ) -> List[MatchResult]:
        """
        Match resume to available jobs with pre-screening and scoring.
        
        Args:
            resume_data: Parsed resume data
            db: Database session
            limit: Maximum number of jobs to consider
            
        Returns:
            List of MatchResult objects sorted by score
        """
        logger.info("Starting job matching process")
        
        jobs = get_job_listings(db, limit=limit * 2)  # Get more for filtering
        logger.info(f"Found {len(jobs)} jobs to evaluate")
        
        matches = []
        
        for job in jobs:
            passes_screening, screening_reason = self._apply_mandatory_rules(resume_data, job)
            
            if not passes_screening:
                logger.debug(f"Job {job.title} failed screening: {screening_reason}")
                continue
                
            score, details = self._calculate_match_score(resume_data, job)
            
            match_result = MatchResult(
                job_id=job.job_id,
                job_title=job.title,
                company_name=job.company_name or "未知公司",
                match_score=score,
                explanation=self._generate_explanation(details),
                details=details
            )
            
            matches.append(match_result)
            
        matches.sort(key=lambda x: x.match_score, reverse=True)
        
        logger.info(f"Generated {len(matches)} job matches")
        return matches[:limit]
    
    def _apply_mandatory_rules(self, resume_data: Dict[str, Any], job: JobListing) -> Tuple[bool, str]:
        """Apply mandatory pre-screening rules."""
        for rule in self.mandatory_rules:
            passes, reason = rule.evaluate(resume_data, job)
            if not passes:
                return False, reason
        return True, "通过预筛选"
    
    def _calculate_match_score(self, resume_data: Dict[str, Any], job: JobListing) -> Tuple[float, Dict[str, Any]]:
        """Calculate overall match score."""
        details = {}
        total_score = 0.0
        
        for rule in self.scoring_rules:
            passes, explanation = rule.evaluate(resume_data, job)
            rule_name = rule.__class__.__name__
            details[rule_name] = explanation
            
            if "技能匹配度:" in explanation:
                try:
                    score_part = explanation.split("技能匹配度:")[1].split("%")[0].strip()
                    skill_score = float(score_part) / 100.0
                    total_score += skill_score * 0.6  # 60% weight for skills
                except:
                    pass
                    
        total_score += 0.4  # 40% base score for meeting requirements
        
        return min(total_score, 1.0), details
    
    def _generate_explanation(self, details: Dict[str, Any]) -> str:
        """Generate human-readable explanation."""
        explanations = []
        for rule_name, explanation in details.items():
            explanations.append(explanation)
        return "; ".join(explanations)
    
    def add_mandatory_rule(self, rule: MatchingRule):
        """Add a new mandatory rule."""
        self.mandatory_rules.append(rule)
        
    def add_scoring_rule(self, rule: MatchingRule):
        """Add a new scoring rule."""
        self.scoring_rules.append(rule)
