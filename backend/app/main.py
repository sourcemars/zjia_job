from fastapi import FastAPI, File, UploadFile, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from typing import Optional
import logging
import os
from datetime import datetime

from app.db.session import get_db, engine
from app.db.base import Base
from app.models.resume import Resume
from app.models.user import User
from app.services.resume_service import create_resume, get_resume_by_id, get_user_resumes

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="ZJia Job API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/api/")
async def root():
    return {"message": "ZJia Job API is running"}

@app.get("/")
async def frontend():
    from fastapi.responses import FileResponse
    return FileResponse("static/index.html")



@app.post("/api/resumes/upload")
async def upload_resume(
    file: UploadFile = File(...),
    user_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    Upload a resume file and store it in the database.
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    allowed_extensions = {'.pdf', '.doc', '.docx', '.txt'}
    file_extension = os.path.splitext(file.filename)[1].lower()
    
    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=400, 
            detail=f"File type not allowed. Supported types: {', '.join(allowed_extensions)}"
        )
    
    try:
        content = await file.read()
        content_str = content.decode('utf-8') if file_extension == '.txt' else str(content)
        
        resume_data = {
            "user_id": user_id,
            "content": content_str,
            "parsed_data": f'{{"filename": "{file.filename}", "size": {len(content)}, "type": "{file.content_type}"}}'
        }
        
        resume = create_resume(db, resume_data)
        
        if not resume:
            raise HTTPException(status_code=500, detail="Failed to create resume")
        
        return {
            "message": "Resume uploaded successfully",
            "resume_id": resume.id,
            "filename": file.filename,
            "size": len(content)
        }
        
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="Unable to read file content")
    except Exception as e:
        logger.error(f"Error uploading resume: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/resumes/{resume_id}")
async def get_resume(resume_id: int, db: Session = Depends(get_db)):
    """
    Get a resume by ID.
    """
    resume = get_resume_by_id(db, resume_id)
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    return {
        "id": resume.id,
        "user_id": resume.user_id,
        "created_at": resume.created_at,
        "updated_at": resume.updated_at,
        "parsed_data": resume.parsed_data
    }

@app.get("/api/users/{user_id}/resumes")
async def get_user_resumes_endpoint(user_id: int, db: Session = Depends(get_db)):
    """
    Get all resumes for a specific user.
    """
    resumes = get_user_resumes(db, user_id)
    
    return {
        "user_id": user_id,
        "resumes": [
            {
                "id": resume.id,
                "created_at": resume.created_at,
                "updated_at": resume.updated_at,
                "parsed_data": resume.parsed_data
            }
            for resume in resumes
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
