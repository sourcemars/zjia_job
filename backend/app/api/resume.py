"""
FastAPI endpoints for resume parsing functionality.
"""
import os
import tempfile
from typing import Dict, Any
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.resume_service import ResumeService
from app.models.resume import Resume

router = APIRouter(prefix="/resumes", tags=["resumes"])
resume_service = ResumeService()


@router.post("/upload", response_model=Dict[str, Any])
async def upload_and_parse_resume(
    user_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload and parse a resume file (Word or PDF).
    
    Args:
        user_id: ID of the user uploading the resume
        file: Resume file to upload and parse
        db: Database session
        
    Returns:
        Dictionary containing resume ID and parsed data summary
    """
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No file provided"
        )
    
    file_extension = Path(file.filename).suffix.lower()
    if file_extension not in ['.pdf', '.doc', '.docx']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported file format. Only PDF, DOC, and DOCX files are supported."
        )
    
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        resume = resume_service.parse_and_store_resume(
            file_path=temp_file_path,
            user_id=user_id,
            db=db
        )
        
        parsed_data = resume_service.get_parsed_resume_data(resume.id, db)
        
        return {
            "resume_id": resume.id,
            "filename": file.filename,
            "file_type": file_extension,
            "parsed_data_summary": {
                "name": parsed_data.get("name") if parsed_data else None,
                "email": parsed_data.get("email") if parsed_data else None,
                "phone": parsed_data.get("phone") if parsed_data else None,
                "fields_extracted": parsed_data.get("fields_extracted", 0) if parsed_data else 0
            },
            "message": "Resume uploaded and parsed successfully"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing resume: {str(e)}"
        )
    finally:
        if 'temp_file_path' in locals() and os.path.exists(temp_file_path):
            os.unlink(temp_file_path)


@router.get("/{resume_id}/parsed-data", response_model=Dict[str, Any])
def get_resume_parsed_data(
    resume_id: int,
    db: Session = Depends(get_db)
):
    """
    Get parsed data for a specific resume.
    
    Args:
        resume_id: ID of the resume
        db: Database session
        
    Returns:
        Parsed resume data
    """
    parsed_data = resume_service.get_parsed_resume_data(resume_id, db)
    
    if not parsed_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found or no parsed data available"
        )
    
    return parsed_data


@router.put("/{resume_id}/reparse", response_model=Dict[str, Any])
async def reparse_resume(
    resume_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Re-parse an existing resume with a new file.
    
    Args:
        resume_id: ID of the resume to update
        file: New resume file to parse
        db: Database session
        
    Returns:
        Updated resume information
    """
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No file provided"
        )
    
    file_extension = Path(file.filename).suffix.lower()
    if file_extension not in ['.pdf', '.doc', '.docx']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported file format. Only PDF, DOC, and DOCX files are supported."
        )
    
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        resume = resume_service.update_resume_parsing(
            resume_id=resume_id,
            file_path=temp_file_path,
            db=db
        )
        
        parsed_data = resume_service.get_parsed_resume_data(resume.id, db)
        
        return {
            "resume_id": resume.id,
            "filename": file.filename,
            "file_type": file_extension,
            "parsed_data_summary": {
                "name": parsed_data.get("name") if parsed_data else None,
                "email": parsed_data.get("email") if parsed_data else None,
                "phone": parsed_data.get("phone") if parsed_data else None,
                "fields_extracted": parsed_data.get("fields_extracted", 0) if parsed_data else 0
            },
            "message": "Resume re-parsed successfully"
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error re-parsing resume: {str(e)}"
        )
    finally:
        if 'temp_file_path' in locals() and os.path.exists(temp_file_path):
            os.unlink(temp_file_path)


@router.get("/{resume_id}", response_model=Dict[str, Any])
def get_resume(
    resume_id: int,
    db: Session = Depends(get_db)
):
    """
    Get resume information including raw content and parsed data.
    
    Args:
        resume_id: ID of the resume
        db: Database session
        
    Returns:
        Complete resume information
    """
    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found"
        )
    
    parsed_data = resume_service.get_parsed_resume_data(resume_id, db)
    
    return {
        "id": resume.id,
        "user_id": resume.user_id,
        "content": resume.content,
        "parsed_data": parsed_data,
        "created_at": resume.created_at,
        "updated_at": resume.updated_at
    }
