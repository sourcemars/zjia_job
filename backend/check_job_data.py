import sqlite3
import json
from datetime import datetime

def check_job_database():
    """Check the job database for scraped data"""
    try:
        conn = sqlite3.connect('zjia_job.db')
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print("Available tables:")
        for table in tables:
            print(f"  - {table[0]}")
        
        if ('job_listings',) in tables:
            cursor.execute("SELECT COUNT(*) FROM job_listings;")
            total_jobs = cursor.fetchone()[0]
            print(f"\nTotal job listings in database: {total_jobs}")
            
            cursor.execute("SELECT * FROM job_listings LIMIT 5;")
            sample_jobs = cursor.fetchall()
            
            cursor.execute("PRAGMA table_info(job_listings);")
            columns = [col[1] for col in cursor.fetchall()]
            print(f"\nJob listing columns: {columns}")
            
            if sample_jobs:
                print("\nSample job records:")
                for i, job in enumerate(sample_jobs, 1):
                    print(f"\nJob {i}:")
                    for col, val in zip(columns, job):
                        if val and len(str(val)) > 100:
                            print(f"  {col}: {str(val)[:100]}...")
                        else:
                            print(f"  {col}: {val}")
            
            cursor.execute("SELECT created_at FROM job_listings ORDER BY created_at DESC LIMIT 1;")
            latest_record = cursor.fetchone()
            if latest_record:
                print(f"\nLatest job record created: {latest_record[0]}")
                
        else:
            print("\nNo job_listings table found in database")
            
        job_related_tables = [t[0] for t in tables if 'job' in t[0].lower()]
        if job_related_tables:
            print(f"\nOther job-related tables: {job_related_tables}")
            for table in job_related_tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table};")
                count = cursor.fetchone()[0]
                print(f"  {table}: {count} records")
        
        conn.close()
        
    except Exception as e:
        print(f"Error checking database: {e}")

if __name__ == "__main__":
    check_job_database()
