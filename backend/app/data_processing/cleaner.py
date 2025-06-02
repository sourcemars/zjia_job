"""
Data cleaning utilities for job listings.
Removes HTML tags, cleans special characters, and normalizes data for database storage.
"""
import re
import html
import logging
from typing import Dict, List, Any, Union

logger = logging.getLogger(__name__)

def clean_html(text: str) -> str:
    """
    Remove HTML tags from text.
    
    Args:
        text: String that may contain HTML tags
        
    Returns:
        String with HTML tags removed
    """
    if not text or not isinstance(text, str):
        return ""
    
    clean_text = re.sub(r'<[^>]+>', '', text)
    
    clean_text = html.unescape(clean_text)
    
    return clean_text

def clean_special_chars(text: str) -> str:
    """
    Clean special characters and normalize whitespace.
    
    Args:
        text: String that may contain special characters
        
    Returns:
        Cleaned string
    """
    if not text or not isinstance(text, str):
        return ""
    
    clean_text = re.sub(r'\s+', ' ', text)
    
    clean_text = re.sub(r'[\x00-\x1F\x7F]', '', clean_text)
    
    clean_text = clean_text.strip()
    
    return clean_text

def clean_job_field(value: Any) -> Any:
    """
    Clean a single job field value.
    
    Args:
        value: Field value to clean
        
    Returns:
        Cleaned value
    """
    if isinstance(value, str):
        cleaned = clean_html(value)
        cleaned = clean_special_chars(cleaned)
        return cleaned
    elif isinstance(value, (list, tuple)):
        return [clean_job_field(item) for item in value]
    elif isinstance(value, dict):
        return {k: clean_job_field(v) for k, v in value.items()}
    else:
        return value

def clean_job_listing(job: Dict[str, Any]) -> Dict[str, Any]:
    """
    Clean all fields in a job listing.
    
    Args:
        job: Dictionary containing job listing data
        
    Returns:
        Dictionary with cleaned job listing data
    """
    if not job or not isinstance(job, dict):
        return {}
    
    cleaned_job = {}
    
    for key, value in job.items():
        cleaned_job[key] = clean_job_field(value)
    
    return cleaned_job

def clean_job_listings(jobs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Clean all job listings in a list.
    
    Args:
        jobs: List of job listing dictionaries
        
    Returns:
        List of cleaned job listing dictionaries
    """
    if not jobs or not isinstance(jobs, list):
        return []
    
    cleaned_jobs = []
    
    for job in jobs:
        try:
            cleaned_job = clean_job_listing(job)
            cleaned_jobs.append(cleaned_job)
        except Exception as e:
            logger.error(f"Error cleaning job: {e}")
            continue
    
    return cleaned_jobs

def normalize_job_data(job: Dict[str, Any], source: str = None) -> Dict[str, Any]:
    """
    Normalize job data to a standard format for database storage.
    
    Args:
        job: Dictionary containing job listing data
        source: Source of the job listing (e.g., 'iguopin', 'jobonline')
        
    Returns:
        Dictionary with normalized job data
    """
    normalized = {
        "source": source or job.get("_source", "unknown"),
        "job_id": job.get("job_id", ""),
        "title": job.get("job_name", ""),
        "company_id": job.get("company_id", ""),
        "company_name": job.get("company_name", ""),
        "location": job.get("address", ""),
        "salary_min": job.get("min_wage", 0),
        "salary_max": job.get("max_wage", 0),
        "salary_unit": job.get("wage_unit_cn", ""),
        "education": job.get("education_cn", ""),
        "experience": job.get("experience_cn", ""),
        "job_type": job.get("recruitment_type_cn", ""),
        "job_category": job.get("category_cn", ""),
        "company_type": job.get("nature_cn", ""),
        "description": job.get("description", ""),
        "requirements": job.get("requirements", ""),
        "benefits": job.get("welfare", ""),
        "contact": job.get("contact", ""),
        "publish_date": job.get("publish_time", ""),
        "update_date": job.get("update_time", ""),
        "raw_data": job  # Store the original data for reference
    }
    
    return normalized

def normalize_job_listings(jobs: List[Dict[str, Any]], source: str = None) -> List[Dict[str, Any]]:
    """
    Normalize all job listings in a list.
    
    Args:
        jobs: List of job listing dictionaries
        source: Source of the job listings
        
    Returns:
        List of normalized job listing dictionaries
    """
    if not jobs or not isinstance(jobs, list):
        return []
    
    normalized_jobs = []
    
    for job in jobs:
        try:
            normalized_job = normalize_job_data(job, source)
            normalized_jobs.append(normalized_job)
        except Exception as e:
            logger.error(f"Error normalizing job: {e}")
            continue
    
    return normalized_jobs

def process_job_listings(jobs: List[Dict[str, Any]], source: str = None) -> List[Dict[str, Any]]:
    """
    Process job listings by cleaning and normalizing them.
    
    Args:
        jobs: List of job listing dictionaries
        source: Source of the job listings
        
    Returns:
        List of processed job listing dictionaries
    """
    cleaned_jobs = clean_job_listings(jobs)
    
    normalized_jobs = normalize_job_listings(cleaned_jobs, source)
    
    return normalized_jobs
