"""
FastAPI endpoints for job matching functionality.
Integrates resume parsing with job matching service.
"""
import os
import tempfile
from typing import Dict, Any, List
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.resume_service import ResumeService
from app.services.matching_service import JobMatchingService, MatchResult
from app.services.interview_advice_service import InterviewAdviceService
from app.models.resume import Resume

router = APIRouter(prefix="/job-matching", tags=["job-matching"])
resume_service = ResumeService()
matching_service = JobMatchingService()
advice_service = InterviewAdviceService()


@router.post("/submit-resume", response_model=Dict[str, Any])
async def submit_resume_for_matching(
    file: UploadFile = File(...),
    user_id: int = Form(1),
    limit: int = Form(10),
    db: Session = Depends(get_db)
):
    """
    Submit a resume file and get matching job recommendations.
    
    Args:
        user_id: ID of the user submitting the resume
        file: Resume file to upload and parse (PDF, DOC, DOCX)
        limit: Maximum number of job matches to return
        db: Database session
        
    Returns:
        Dictionary containing resume info and ranked job matches
    """
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="未提供文件"
        )
    
    file_extension = Path(file.filename).suffix.lower()
    if file_extension not in ['.pdf', '.doc', '.docx', '.txt']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不支持的文件格式。仅支持 PDF、DOC、DOCX 和 TXT 文件。"
        )
    
    temp_file_path = None
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
        
        if not parsed_data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="简历解析失败，无法获取解析数据"
            )
        
        matches = matching_service.match_resume_to_jobs(
            resume_data=parsed_data,
            db=db,
            limit=limit
        )
        
        return {
            "resume_info": {
                "resume_id": resume.id,
                "filename": file.filename,
                "file_type": file_extension,
                "parsed_summary": {
                    "name": parsed_data.get("name"),
                    "email": parsed_data.get("email"),
                    "phone": parsed_data.get("phone"),
                    "fields_extracted": parsed_data.get("fields_extracted", 0)
                }
            },
            "job_matches": {
                "total_matches": len(matches),
                "matches": [
                    {
                        "job_id": match.job_id,
                        "job_title": match.job_title,
                        "company_name": match.company_name,
                        "match_score": round(match.match_score * 100, 1),
                        "match_percentage": f"{round(match.match_score * 100, 1)}%",
                        "explanation": match.explanation,
                        "details": match.details
                    }
                    for match in matches
                ]
            },
            "message": f"简历解析成功，找到 {len(matches)} 个匹配职位"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"处理简历时发生错误: {str(e)}"
        )
    finally:
        if temp_file_path and os.path.exists(temp_file_path):
            os.unlink(temp_file_path)


@router.get("/{resume_id}/matches", response_model=Dict[str, Any])
def get_resume_matches(
    resume_id: int,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """
    Get job matches for an existing resume.
    
    Args:
        resume_id: ID of the resume
        limit: Maximum number of job matches to return
        db: Database session
        
    Returns:
        Dictionary containing job matches for the resume
    """
    parsed_data = resume_service.get_parsed_resume_data(resume_id, db)
    
    if not parsed_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="简历未找到或无解析数据"
        )
    
    try:
        matches = matching_service.match_resume_to_jobs(
            resume_data=parsed_data,
            db=db,
            limit=limit
        )
        
        return {
            "resume_id": resume_id,
            "job_matches": {
                "total_matches": len(matches),
                "matches": [
                    {
                        "job_id": match.job_id,
                        "job_title": match.job_title,
                        "company_name": match.company_name,
                        "match_score": round(match.match_score * 100, 1),
                        "match_percentage": f"{round(match.match_score * 100, 1)}%",
                        "explanation": match.explanation,
                        "details": match.details
                    }
                    for match in matches
                ]
            },
            "message": f"找到 {len(matches)} 个匹配职位"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"职位匹配时发生错误: {str(e)}"
        )


@router.post("/quick-match", response_model=Dict[str, Any])
async def quick_resume_match(
    file: UploadFile = File(...),
    user_id: int = Form(0),
    limit: int = Form(5),
    db: Session = Depends(get_db)
):
    """
    Quick resume matching without storing the resume permanently.
    Useful for anonymous users or quick evaluations.
    
    Args:
        user_id: ID of the user (can be 0 for anonymous)
        file: Resume file to analyze
        limit: Maximum number of job matches to return
        db: Database session
        
    Returns:
        Dictionary containing job matches without storing resume
    """
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="未提供文件"
        )
    
    file_extension = Path(file.filename).suffix.lower()
    if file_extension not in ['.pdf', '.doc', '.docx', '.txt']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不支持的文件格式。仅支持 PDF、DOC、DOCX 和 TXT 文件。"
        )
    
    temp_file_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        parsed_result = resume_service.parser.parse_file(temp_file_path)
        parsed_data = resume_service._clean_parsed_data(parsed_result['parsed_data'])
        
        matches = matching_service.match_resume_to_jobs(
            resume_data=parsed_data,
            db=db,
            limit=limit
        )
        
        return {
            "filename": file.filename,
            "file_type": file_extension,
            "parsed_summary": {
                "name": parsed_data.get("name"),
                "email": parsed_data.get("email"),
                "phone": parsed_data.get("phone"),
                "fields_extracted": parsed_data.get("fields_extracted", 0)
            },
            "job_matches": {
                "total_matches": len(matches),
                "matches": [
                    {
                        "job_id": match.job_id,
                        "job_title": match.job_title,
                        "company_name": match.company_name,
                        "match_score": round(match.match_score * 100, 1),
                        "match_percentage": f"{round(match.match_score * 100, 1)}%",
                        "explanation": match.explanation,
                        "details": match.details
                    }
                    for match in matches
                ]
            },
            "message": f"快速匹配完成，找到 {len(matches)} 个匹配职位"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"快速匹配时发生错误: {str(e)}"
        )
    finally:
        if temp_file_path and os.path.exists(temp_file_path):
            os.unlink(temp_file_path)


@router.post("/{resume_id}/advice/{job_id}", response_model=Dict[str, Any])
def generate_interview_advice(
    resume_id: int,
    job_id: str,
    db: Session = Depends(get_db)
):
    """
    Generate interview advice for a specific job match.
    
    Args:
        resume_id: ID of the resume
        job_id: ID of the job to generate advice for
        db: Database session
        
    Returns:
        Dictionary containing interview advice
    """
    parsed_data = resume_service.get_parsed_resume_data(resume_id, db)
    if not parsed_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="简历未找到或无解析数据"
        )
    
    from app.services.job_service import get_job_listing_by_id
    job = get_job_listing_by_id(db, job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="职位未找到"
        )
    
    try:
        matches = matching_service.match_resume_to_jobs(
            resume_data=parsed_data,
            db=db,
            limit=100
        )
        
        target_match = None
        for match in matches:
            if match.job_id == job_id:
                target_match = match
                break
        
        if not target_match:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="该职位与简历匹配度过低"
            )
        
        advice = advice_service.generate_advice(parsed_data, target_match, job)
        
        return {
            "resume_id": resume_id,
            "job_id": job_id,
            "match_score": round(target_match.match_score * 100, 1),
            "advice": {
                "resume_optimization": advice.resume_optimization,
                "technical_preparation": advice.technical_preparation,
                "overall_suggestions": advice.overall_suggestions
            },
            "message": "面试建议生成成功"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"生成面试建议时发生错误: {str(e)}"
        )
