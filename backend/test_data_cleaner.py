"""
Test script for the data cleaning module.
"""
import json
import logging
import sys
import os
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.data_processing.cleaner import (
    clean_html, 
    clean_special_chars, 
    clean_job_listing,
    clean_job_listings,
    normalize_job_data,
    process_job_listings
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_html_cleaning():
    """Test HTML cleaning function"""
    test_cases = [
        ("<p>This is a test</p>", "This is a test"),
        ("No HTML here", "No HTML here"),
        ("<div><span>Nested</span> tags</div>", "Nested tags"),
        ("<a href='test.html'>Link</a>", "Link"),
        ("", ""),
        (None, ""),
        ("<p>Special &amp; chars</p>", "Special & chars"),
    ]
    
    for input_text, expected in test_cases:
        result = clean_html(input_text)
        assert result == expected, f"Expected '{expected}', got '{result}' for input '{input_text}'"
    
    logger.info("HTML cleaning tests passed")

def test_special_char_cleaning():
    """Test special character cleaning function"""
    test_cases = [
        ("Multiple    spaces", "Multiple spaces"),
        ("Tabs\tand\tnewlines\n", "Tabs and newlines"),
        ("  Leading/trailing spaces  ", "Leading/trailing spaces"),
        ("", ""),
        (None, ""),
        ("Control\x01chars", "Controlchars"),
    ]
    
    for input_text, expected in test_cases:
        result = clean_special_chars(input_text)
        assert result == expected, f"Expected '{expected}', got '{result}' for input '{input_text}'"
    
    logger.info("Special character cleaning tests passed")

def test_job_cleaning():
    """Test job listing cleaning function"""
    test_job = {
        "job_name": "<p>Software Engineer</p>",
        "company_name": "Tech   Company",
        "description": "<div>Job\ndescription with\ttabs</div>",
        "requirements": ["<li>Skill 1</li>", "<li>Skill 2</li>"],
        "salary": 100000,
        "nested": {
            "field1": "<span>Nested HTML</span>",
            "field2": "  Nested   spaces  "
        }
    }
    
    cleaned_job = clean_job_listing(test_job)
    
    assert cleaned_job["job_name"] == "Software Engineer"
    assert cleaned_job["company_name"] == "Tech Company"
    assert cleaned_job["description"] == "Job description with tabs"
    assert cleaned_job["requirements"] == ["Skill 1", "Skill 2"]
    assert cleaned_job["salary"] == 100000  # Non-string should remain unchanged
    assert cleaned_job["nested"]["field1"] == "Nested HTML"
    assert cleaned_job["nested"]["field2"] == "Nested spaces"
    
    logger.info("Job cleaning tests passed")

def test_with_real_data():
    """Test with real job data from the scraper"""
    json_files = [f for f in os.listdir('.') if f.startswith('iguopin_') and f.endswith('.json')]
    if not json_files:
        logger.error("No job data files found")
        return
    
    json_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
    latest_file = json_files[0]
    
    logger.info(f"Testing with real data from {latest_file}")
    
    try:
        with open(latest_file, 'r', encoding='utf-8') as f:
            jobs = json.load(f)
        
        test_jobs = jobs[:10]
        
        processed_jobs = process_job_listings(test_jobs, source="iguopin")
        
        assert len(processed_jobs) == len(test_jobs)
        
        for job in processed_jobs:
            assert "title" in job
            assert "company_name" in job
            assert "salary_min" in job
            assert "salary_max" in job
            assert "education" in job
            assert "experience" in job
            assert "raw_data" in job
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        test_output = f"test_processed_jobs_{timestamp}.json"
        
        with open(test_output, 'w', encoding='utf-8') as f:
            json.dump(processed_jobs, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Saved processed test jobs to {test_output}")
        logger.info(f"Sample processed job: {processed_jobs[0]}")
        
    except Exception as e:
        logger.error(f"Error testing with real data: {e}")
        raise
    
    logger.info("Real data tests passed")

def main():
    """Run all tests"""
    logger.info("Starting data cleaner tests")
    
    test_html_cleaning()
    test_special_char_cleaning()
    test_job_cleaning()
    test_with_real_data()
    
    logger.info("All data cleaner tests passed")
    return 0

if __name__ == "__main__":
    sys.exit(main())
