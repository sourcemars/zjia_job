"""
Database initialization script.
Creates all tables needed for the application.
"""
import os
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

from app.models.user import User
from app.models.resume import Resume
from app.models.job import Job
from app.models.job_listing import JobListing
from app.models.match import Match

from app.db.session import engine
from app.db.base import Base

def init_db():
    """Initialize the database by creating all tables."""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")

if __name__ == "__main__":
    init_db()
