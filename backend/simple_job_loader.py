#!/usr/bin/env python3
"""
Simple job data loader that bypasses import issues.
"""
import json
import sqlite3
import os

def create_job_table():
    """Create job_listings table directly in SQLite."""
    conn = sqlite3.connect('zjia_job.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS job_listings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source TEXT NOT NULL,
            job_id TEXT NOT NULL UNIQUE,
            title TEXT NOT NULL,
            company_name TEXT,
            location TEXT,
            education TEXT,
            experience TEXT,
            description TEXT,
            requirements TEXT,
            raw_data TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

def load_jobs_from_json():
    """Load jobs from JSON file into database."""
    json_file = "jobonline_internship_positions_20250529_005328.json"
    
    if not os.path.exists(json_file):
        print(f"文件不存在: {json_file}")
        return
        
    with open(json_file, 'r', encoding='utf-8') as f:
        jobs_data = json.load(f)
        
    print(f"加载了 {len(jobs_data)} 个职位数据")
    
    conn = sqlite3.connect('zjia_job.db')
    cursor = conn.cursor()
    
    created_count = 0
    for i, job_data in enumerate(jobs_data[:20]):  # Take first 20 jobs
        job_id = f"jobonline_{i}_{job_data.get('id', i)}"
        title = job_data.get('title', '未知职位')
        company = job_data.get('company', '未知公司')
        location = job_data.get('location', '')
        education = job_data.get('education', '')
        experience = job_data.get('experience', '')
        description = job_data.get('description', '')
        requirements = job_data.get('requirements', '')
        
        try:
            cursor.execute('''
                INSERT OR IGNORE INTO job_listings 
                (source, job_id, title, company_name, location, education, experience, description, requirements, raw_data)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', ('jobonline', job_id, title, company, location, education, experience, description, requirements, json.dumps(job_data)))
            
            if cursor.rowcount > 0:
                created_count += 1
                
        except Exception as e:
            print(f"插入职位 {title} 时出错: {e}")
            
    conn.commit()
    
    cursor.execute('SELECT COUNT(*) FROM job_listings')
    total_count = cursor.fetchone()[0]
    
    cursor.execute('SELECT title, company_name, education, experience FROM job_listings LIMIT 3')
    samples = cursor.fetchall()
    
    conn.close()
    
    print(f"成功创建 {created_count} 个职位")
    print(f"数据库中现有职位总数: {total_count}")
    print("\n样本职位:")
    for title, company, edu, exp in samples:
        print(f"- {title} ({company}) - 学历:{edu} 经验:{exp}")

if __name__ == "__main__":
    create_job_table()
    load_jobs_from_json()
