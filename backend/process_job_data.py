"""
Script to process job data by cleaning HTML tags and special characters,
and normalizing the data structure for database storage.
"""
import json
import logging
import sys
import os
from datetime import datetime
import argparse
from pathlib import Path

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.data_processing.cleaner import process_job_listings

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def process_file(input_file, output_file=None, source=None):
    """
    Process a job data file by cleaning and normalizing the data.
    
    Args:
        input_file: Path to the input JSON file
        output_file: Path to the output JSON file (optional)
        source: Source of the job listings (optional)
        
    Returns:
        List of processed job listings
    """
    logger.info(f"Processing job data from {input_file}")
    
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            jobs = json.load(f)
        
        logger.info(f"Loaded {len(jobs)} jobs from {input_file}")
        
        if not source:
            filename = os.path.basename(input_file)
            if "iguopin" in filename:
                source = "iguopin"
            elif "jobonline" in filename:
                source = "jobonline"
            else:
                source = "unknown"
        
        processed_jobs = process_job_listings(jobs, source)
        
        logger.info(f"Processed {len(processed_jobs)} jobs")
        
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(processed_jobs, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Saved processed jobs to {output_file}")
        
        return processed_jobs
        
    except Exception as e:
        logger.error(f"Error processing job data: {e}")
        raise

def main():
    """
    Main function to process job data files.
    """
    parser = argparse.ArgumentParser(description='Process job data files')
    parser.add_argument('--input', '-i', required=True, help='Input JSON file or directory')
    parser.add_argument('--output', '-o', help='Output JSON file or directory')
    parser.add_argument('--source', '-s', help='Source of the job listings')
    parser.add_argument('--recursive', '-r', action='store_true', help='Process all JSON files in directory recursively')
    
    args = parser.parse_args()
    
    input_path = Path(args.input)
    
    if not input_path.exists():
        logger.error(f"Input path {input_path} does not exist")
        return 1
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    if input_path.is_file():
        if args.output:
            output_file = args.output
        else:
            output_file = f"processed_{input_path.stem}_{timestamp}.json"
        
        process_file(str(input_path), output_file, args.source)
        
    elif input_path.is_dir():
        if args.recursive:
            json_files = list(input_path.glob('**/*.json'))
        else:
            json_files = list(input_path.glob('*.json'))
        
        if not json_files:
            logger.error(f"No JSON files found in {input_path}")
            return 1
        
        logger.info(f"Found {len(json_files)} JSON files to process")
        
        output_dir = Path(args.output) if args.output else input_path
        if not output_dir.exists():
            output_dir.mkdir(parents=True)
        
        for json_file in json_files:
            output_file = output_dir / f"processed_{json_file.stem}_{timestamp}.json"
            process_file(str(json_file), str(output_file), args.source)
    
    logger.info("Job data processing completed")
    return 0

if __name__ == "__main__":
    sys.exit(main())
