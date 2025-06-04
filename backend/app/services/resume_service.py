"""
Resume service for the application.
Handles resume data processing and storage.
"""
import logging
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models.resume import Resume

logger = logging.getLogger(__name__)

def create_resume(db: Session, resume_data: Dict[str, Any]) -> Optional[Resume]:
    """
    Create a resume in the database.
    
    Args:
        db: Database session
        resume_data: Resume data
        
    Returns:
        Created resume or None if creation failed
    """
    try:
        resume = Resume(**resume_data)
        db.add(resume)
        db.commit()
        db.refresh(resume)
        return resume
    except IntegrityError as e:
        db.rollback()
        logger.error(f"Error creating resume: {e}")
        return None
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error creating resume: {e}")
        return None

def get_resume_by_id(db: Session, resume_id: int) -> Optional[Resume]:
    """
    Get a resume by its ID.
    
    Args:
        db: Database session
        resume_id: Resume ID
        
    Returns:
        Resume or None if not found
    """
    return db.query(Resume).filter(Resume.id == resume_id).first()

def get_user_resumes(db: Session, user_id: int) -> List[Resume]:
    """
    Get all resumes for a specific user.
    
    Args:
        db: Database session
        user_id: User ID
        
    Returns:
        List of resumes
    """
    return db.query(Resume).filter(Resume.user_id == user_id).all()

def delete_resume(db: Session, resume_id: int) -> bool:
    """
    Delete a resume by its ID.
    
    Args:
        db: Database session
        resume_id: Resume ID
        
    Returns:
        True if deletion was successful, False otherwise
    """
    resume = get_resume_by_id(db, resume_id)
    
    if not resume:
        return False
    
    try:
        db.delete(resume)
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting resume: {e}")
        return False

def update_resume(db: Session, resume_id: int, resume_data: Dict[str, Any]) -> Optional[Resume]:
    """
    Update a resume by its ID.
    
    Args:
        db: Database session
        resume_id: Resume ID
        resume_data: Updated resume data
        
    Returns:
        Updated resume or None if update failed
    """
    resume = get_resume_by_id(db, resume_id)
    
    if not resume:
        return None
    
    try:
        for key, value in resume_data.items():
            if hasattr(resume, key):
                setattr(resume, key, value)
        
        db.commit()
        db.refresh(resume)
        return resume
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating resume: {e}")
        return None
