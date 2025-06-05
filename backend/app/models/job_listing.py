"""
Job listing model for the application.
"""
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, JSON
from sqlalchemy.sql import func

from app.db.base import Base

class JobListing(Base):
    """
    Job listing model.
    """
    __tablename__ = "job_listings"

    id = Column(Integer, primary_key=True, index=True)
    source = Column(String(50), nullable=False, index=True)
    job_id = Column(String(100), nullable=False, index=True, unique=True)
    title = Column(String(200), nullable=False, index=True)
    company_id = Column(String(100), index=True)
    company_name = Column(String(200), index=True)
    location = Column(String(200))
    salary_min = Column(Float, default=0)
    salary_max = Column(Float, default=0)
    salary_unit = Column(String(50))
    education = Column(String(50))
    experience = Column(String(50))
    job_type = Column(String(50))
    job_category = Column(String(100))
    company_type = Column(String(50))
    description = Column(Text)
    requirements = Column(Text)
    benefits = Column(Text)
    contact = Column(String(200))
    publish_date = Column(String(50))
    update_date = Column(String(50))
    raw_data = Column(JSON)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<JobListing(id={self.id}, title='{self.title}', company='{self.company_name}')>"
