#!/usr/bin/env python3
"""
Debug script to understand the actual structure of match data returned by the backend.
"""
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

from app.services.matching_service import JobMatchingService
from app.db.session import SessionLocal
import json

def debug_match_data():
    """Debug what the backend actually returns."""
    db = SessionLocal()
    service = JobMatchingService()
    sample_resume = {
        'name': '靳博',
        'skills': ['PHP', 'MySQL', 'JavaScript'],
        'experience': '10年',
        'education': '本科'
    }

    matches = service.match_resume_to_jobs(sample_resume, db, limit=2)
    for i, match in enumerate(matches):
        print(f'=== Match {i+1}: {match.job_title} ===')
        print(f'Explanation type: {type(match.explanation)}')
        print(f'Explanation: {match.explanation}')
        print(f'Details type: {type(match.details)}')
        print(f'Details: {match.details}')
        
        match_dict = {
            'job_title': match.job_title,
            'explanation': match.explanation,
            'details': match.details
        }
        print(f'JSON serializable: {json.dumps(match_dict, ensure_ascii=False)}')
        print('---')
    
    db.close()

if __name__ == "__main__":
    debug_match_data()
