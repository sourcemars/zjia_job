#!/usr/bin/env python3
"""
Create sample database with proper schema and test data.
"""
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

from app.models.job_listing import JobListing
from app.db.session import SessionLocal, engine
from app.db.base import Base
import app.models  # Import all models to register them with Base

def create_sample_database():
    """Create database with sample job data."""
    print("Creating database tables...")
    print(f"Database URL: {engine.url}")
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")
    
    from sqlalchemy import inspect
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print(f"Tables in database: {tables}")
    
    if 'job_listings' in tables:
        columns = inspector.get_columns('job_listings')
        print(f"job_listings columns: {[col['name'] for col in columns]}")
    else:
        print("ERROR: job_listings table not found!")
        return
    
    sample_jobs = [
        {
            "source": "manual",
            "job_id": "job_001",
            "title": "PHP开发工程师",
            "company_id": "company_001",
            "company_name": "北京科技有限公司",
            "location": "北京",
            "salary_min": 8000,
            "salary_max": 15000,
            "salary_unit": "月",
            "education": "本科",
            "experience": "3-5年",
            "job_type": "全职",
            "job_category": "技术",
            "company_type": "互联网",
            "description": "负责PHP后端开发，维护现有系统，开发新功能模块。",
            "requirements": "熟练掌握PHP、MySQL、Linux等技术栈，有3年以上开发经验。",
            "benefits": "五险一金，弹性工作，技术培训",
            "raw_data": {"source": "manual_entry"}
        },
        {
            "source": "manual",
            "job_id": "job_002", 
            "title": "前端开发工程师",
            "company_id": "company_002",
            "company_name": "上海互联网公司",
            "location": "上海",
            "salary_min": 10000,
            "salary_max": 18000,
            "salary_unit": "月",
            "education": "本科",
            "experience": "2-4年",
            "job_type": "全职",
            "job_category": "技术",
            "company_type": "互联网",
            "description": "负责前端页面开发，与后端API对接，优化用户体验。",
            "requirements": "熟练掌握HTML5、CSS3、JavaScript、Vue.js等前端技术。",
            "benefits": "六险一金，年终奖，股票期权",
            "raw_data": {"source": "manual_entry"}
        },
        {
            "source": "manual",
            "job_id": "job_003",
            "title": "技术总监",
            "company_id": "company_003", 
            "company_name": "深圳电商科技",
            "location": "深圳",
            "salary_min": 25000,
            "salary_max": 40000,
            "salary_unit": "月",
            "education": "本科",
            "experience": "8-10年",
            "job_type": "全职",
            "job_category": "管理",
            "company_type": "电商",
            "description": "负责技术团队管理，制定技术架构，推动技术创新。",
            "requirements": "10年以上技术经验，5年以上团队管理经验，熟悉大型系统架构。",
            "benefits": "高薪酬，股权激励，团队建设预算",
            "raw_data": {"source": "manual_entry"}
        },
        {
            "source": "manual",
            "job_id": "job_004",
            "title": "软件研发工程师",
            "company_id": "company_004",
            "company_name": "广州软件公司",
            "location": "广州",
            "salary_min": 12000,
            "salary_max": 20000,
            "salary_unit": "月",
            "education": "本科",
            "experience": "3-6年",
            "job_type": "全职",
            "job_category": "技术",
            "company_type": "软件",
            "description": "参与软件产品研发，负责核心模块开发和维护。",
            "requirements": "熟练掌握Java、Spring、MySQL等技术，有软件开发经验。",
            "benefits": "五险一金，带薪年假，技能培训",
            "raw_data": {"source": "manual_entry"}
        },
        {
            "source": "manual",
            "job_id": "job_005",
            "title": "项目经理",
            "company_id": "company_005",
            "company_name": "杭州科技集团",
            "location": "杭州",
            "salary_min": 15000,
            "salary_max": 25000,
            "salary_unit": "月",
            "education": "本科",
            "experience": "5-8年",
            "job_type": "全职",
            "job_category": "管理",
            "company_type": "科技",
            "description": "负责项目管理，协调各部门资源，确保项目按时交付。",
            "requirements": "有项目管理经验，熟悉软件开发流程，具备良好的沟通能力。",
            "benefits": "六险一金，绩效奖金，管理津贴",
            "raw_data": {"source": "manual_entry"}
        }
    ]
    
    db = SessionLocal()
    try:
        db.query(JobListing).delete()
        db.commit()
        
        for job_data in sample_jobs:
            job = JobListing(**job_data)
            db.add(job)
        
        db.commit()
        
        total_count = db.query(JobListing).count()
        print(f"成功创建 {total_count} 个职位")
        
        jobs = db.query(JobListing).limit(3).all()
        print("\n样本职位:")
        for job in jobs:
            print(f"- {job.title} ({job.company_name}) - 学历:{job.education} 经验:{job.experience}")
            
    except Exception as e:
        print(f"创建数据时出错: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_sample_database()
