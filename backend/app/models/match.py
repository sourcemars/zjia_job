from sqlalchemy import Column, Integer, String, Text, DateTime, Float, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base import Base

class Match(Base):
    __tablename__ = "matches"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    resume_id = Column(Integer, ForeignKey("resumes.id"))
    job_id = Column(Integer, ForeignKey("jobs.id"))
    score = Column(Float)  # Match score between 0 and 1
    suggestions = Column(Text)  # JSON string of suggestions
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    user = relationship("User")
    resume = relationship("Resume")
    job = relationship("Job")
