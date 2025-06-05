"""
Resume parser main interface for handling Word and PDF files.
"""
import json
import logging
from typing import Dict, Any, Optional
from pathlib import Path

from .word_parser import WordParser
from .pdf_parser import PDFParser

logger = logging.getLogger(__name__)


class ResumeParser:
    """Main resume parser that handles both Word and PDF files."""
    
    def __init__(self):
        self.word_parser = WordParser()
        self.pdf_parser = PDFParser()
    
    def parse_file(self, file_path: str) -> Dict[str, Any]:
        """
        Parse a resume file and extract structured data.
        
        Args:
            file_path: Path to the resume file
            
        Returns:
            Dictionary containing parsed resume data
            
        Raises:
            ValueError: If file format is not supported
            FileNotFoundError: If file doesn't exist
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        file_extension = file_path.suffix.lower()
        
        try:
            if file_extension in ['.doc', '.docx']:
                raw_text = self.word_parser.extract_text(str(file_path))
            elif file_extension == '.pdf':
                raw_text = self.pdf_parser.extract_text(str(file_path))
            elif file_extension == '.txt':
                with open(file_path, 'r', encoding='utf-8') as f:
                    raw_text = f.read()
            else:
                raise ValueError(f"Unsupported file format: {file_extension}")
            
            parsed_data = self._extract_structured_data(raw_text)
            
            return {
                'raw_text': raw_text,
                'parsed_data': parsed_data,
                'file_type': file_extension,
                'file_name': file_path.name
            }
            
        except Exception as e:
            logger.error(f"Error parsing file {file_path}: {e}")
            raise
    
    def _extract_structured_data(self, text: str) -> Dict[str, Any]:
        """
        Extract structured information from resume text.
        
        Args:
            text: Raw resume text
            
        Returns:
            Dictionary with structured resume data
        """
        import re
        
        structured_data = {
            'name': self._extract_name(text),
            'email': self._extract_email(text),
            'phone': self._extract_phone(text),
            'education': self._extract_education(text),
            'experience': self._extract_experience(text),
            'skills': self._extract_skills(text),
            'summary': self._extract_summary(text)
        }
        
        return structured_data
    
    def _extract_name(self, text: str) -> Optional[str]:
        """Extract name from resume text."""
        lines = text.strip().split('\n')
        for line in lines[:5]:
            line = line.strip()
            if line and len(line.split()) <= 4 and len(line) > 2:
                if not any(char.isdigit() for char in line) and '@' not in line:
                    return line
        return None
    
    def _extract_email(self, text: str) -> Optional[str]:
        """Extract email from resume text."""
        import re
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        matches = re.findall(email_pattern, text)
        return matches[0] if matches else None
    
    def _extract_phone(self, text: str) -> Optional[str]:
        """Extract phone number from resume text."""
        import re
        phone_patterns = [
            r'1[3-9]\d{9}',  # Chinese mobile numbers
            r'\+86\s*1[3-9]\d{9}',  # Chinese mobile with country code
            r'(\d{3,4}[-\s]?\d{7,8})',  # Landline numbers
        ]
        
        for pattern in phone_patterns:
            matches = re.findall(pattern, text)
            if matches:
                return matches[0] if isinstance(matches[0], str) else matches[0][0]
        return None
    
    def _extract_education(self, text: str) -> list:
        """Extract education information from resume text."""
        import re
        education_keywords = ['大学', '学院', '本科', '硕士', '博士', '学士', '专科', '毕业']
        education_info = []
        
        lines = text.split('\n')
        for line in lines:
            if any(keyword in line for keyword in education_keywords):
                education_info.append(line.strip())
        
        return education_info
    
    def _extract_experience(self, text: str) -> list:
        """Extract work experience from resume text."""
        import re
        experience_keywords = ['工作经历', '工作经验', '项目经验', '实习经历', '职业经历']
        experience_info = []
        
        lines = text.split('\n')
        in_experience_section = False
        
        for line in lines:
            line = line.strip()
            if any(keyword in line for keyword in experience_keywords):
                in_experience_section = True
                continue
            
            if in_experience_section and line:
                if any(keyword in line for keyword in ['技能', '教育', '个人信息', '联系方式']):
                    break
                experience_info.append(line)
        
        return experience_info
    
    def _extract_skills(self, text: str) -> list:
        """Extract skills from resume text."""
        import re
        skills_keywords = ['技能', '专业技能', '技术技能', '掌握']
        skills_info = []
        
        lines = text.split('\n')
        in_skills_section = False
        
        for line in lines:
            line = line.strip()
            if any(keyword in line for keyword in skills_keywords):
                in_skills_section = True
                continue
            
            if in_skills_section and line:
                if any(keyword in line for keyword in ['工作经历', '教育', '个人信息', '联系方式']):
                    break
                skills_info.append(line)
        
        return skills_info
    
    def _extract_summary(self, text: str) -> Optional[str]:
        """Extract summary or objective from resume text."""
        summary_keywords = ['个人简介', '自我介绍', '个人总结', '求职意向', '职业目标']
        
        lines = text.split('\n')
        for i, line in enumerate(lines):
            if any(keyword in line for keyword in summary_keywords):
                summary_lines = []
                for j in range(i + 1, min(i + 5, len(lines))):
                    next_line = lines[j].strip()
                    if next_line and not any(keyword in next_line for keyword in ['工作经历', '教育', '技能']):
                        summary_lines.append(next_line)
                    else:
                        break
                return ' '.join(summary_lines) if summary_lines else None
        
        return None
