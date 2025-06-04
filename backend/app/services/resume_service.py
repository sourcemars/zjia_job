"""
Resume service for handling resume parsing and storage operations.
"""
import json
import logging
from typing import Dict, Any, Optional
from pathlib import Path

from sqlalchemy.orm import Session
from app.models.resume import Resume
from app.resume_parser import ResumeParser
from app.data_processing.cleaner import clean_job_field

logger = logging.getLogger(__name__)


class ResumeService:
    """Service for resume parsing and database operations."""
    
    def __init__(self):
        self.parser = ResumeParser()
    
    def parse_and_store_resume(
        self, 
        file_path: str, 
        user_id: int, 
        db: Session
    ) -> Resume:
        """
        Parse a resume file and store it in the database.
        
        Args:
            file_path: Path to the resume file
            user_id: ID of the user who owns the resume
            db: Database session
            
        Returns:
            Created Resume object
            
        Raises:
            ValueError: If file format is not supported
            FileNotFoundError: If file doesn't exist
        """
        try:
            parsed_result = self.parser.parse_file(file_path)
            
            cleaned_text = clean_job_field(parsed_result['raw_text'])
            
            cleaned_parsed_data = self._clean_parsed_data(parsed_result['parsed_data'])
            
            resume = Resume(
                user_id=user_id,
                content=cleaned_text,
                parsed_data=json.dumps(cleaned_parsed_data, ensure_ascii=False, indent=2)
            )
            
            db.add(resume)
            db.commit()
            db.refresh(resume)
            
            logger.info(f"Successfully parsed and stored resume for user {user_id}")
            return resume
            
        except Exception as e:
            logger.error(f"Error parsing and storing resume: {e}")
            db.rollback()
            raise
    
    def update_resume_parsing(
        self, 
        resume_id: int, 
        file_path: str, 
        db: Session
    ) -> Resume:
        """
        Re-parse an existing resume file and update the database record.
        
        Args:
            resume_id: ID of the resume to update
            file_path: Path to the new resume file
            db: Database session
            
        Returns:
            Updated Resume object
            
        Raises:
            ValueError: If resume not found or file format not supported
        """
        try:
            resume = db.query(Resume).filter(Resume.id == resume_id).first()
            if not resume:
                raise ValueError(f"Resume with ID {resume_id} not found")
            
            parsed_result = self.parser.parse_file(file_path)
            
            cleaned_text = clean_job_field(parsed_result['raw_text'])
            
            cleaned_parsed_data = self._clean_parsed_data(parsed_result['parsed_data'])
            
            resume.content = cleaned_text
            resume.parsed_data = json.dumps(cleaned_parsed_data, ensure_ascii=False, indent=2)
            
            db.commit()
            db.refresh(resume)
            
            logger.info(f"Successfully updated resume {resume_id}")
            return resume
            
        except Exception as e:
            logger.error(f"Error updating resume parsing: {e}")
            db.rollback()
            raise
    
    def get_parsed_resume_data(self, resume_id: int, db: Session) -> Optional[Dict[str, Any]]:
        """
        Get parsed resume data from database.
        
        Args:
            resume_id: ID of the resume
            db: Database session
            
        Returns:
            Parsed resume data as dictionary, or None if not found
        """
        try:
            resume = db.query(Resume).filter(Resume.id == resume_id).first()
            if not resume or not resume.parsed_data:
                return None
            
            return json.loads(resume.parsed_data)
            
        except Exception as e:
            logger.error(f"Error getting parsed resume data: {e}")
            return None
    
    def _clean_parsed_data(self, parsed_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Clean and validate parsed resume data.
        
        Args:
            parsed_data: Raw parsed data from resume parser
            
        Returns:
            Cleaned and validated parsed data
        """
        cleaned_data = {}
        
        for key, value in parsed_data.items():
            if value is not None:
                cleaned_data[key] = clean_job_field(value)
        
        required_fields = ['name', 'email', 'phone', 'education', 'experience', 'skills', 'summary']
        for field in required_fields:
            if field not in cleaned_data:
                cleaned_data[field] = None
        
        cleaned_data['parsing_version'] = '1.0'
        cleaned_data['fields_extracted'] = len([v for v in cleaned_data.values() if v is not None])
        
        return cleaned_data
