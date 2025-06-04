#!/usr/bin/env python3
"""
Script to check existing job data structure and content in the database.
"""
import sys
import os
sys.path.append('.')

from app.db.session import SessionLocal, Base, engine
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, JSON
from sqlalchemy.sql import func

class JobListing(Base):
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

def main():
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        job_count = db.query(JobListing).count()
        print(f'数据库中职位总数: {job_count}')
        
        if job_count > 0:
            sample_jobs = db.query(JobListing).limit(5).all()
            
            print('\n=== 职位数据结构分析 ===')
            for i, job in enumerate(sample_jobs, 1):
                print(f'\n--- 样本职位 {i} ---')
                print(f'职位标题: {job.title}')
                print(f'公司名称: {job.company_name}')
                print(f'工作地点: {job.location}')
                print(f'学历要求: {job.education}')
                print(f'经验要求: {job.experience}')
                print(f'薪资范围: {job.salary_min}-{job.salary_max} {job.salary_unit}')
                print(f'职位类型: {job.job_type}')
                print(f'职位分类: {job.job_category}')
                print(f'公司类型: {job.company_type}')
                
                if job.requirements:
                    print(f'职位要求: {job.requirements[:200]}...')
                if job.description:
                    print(f'职位描述: {job.description[:200]}...')
                    
            print('\n=== 技术类职位统计 ===')
            tech_keywords = ['开发', '技术', '工程师', 'PHP', 'Java', 'Python', '前端', '后端']
            
            for keyword in tech_keywords:
                count = db.query(JobListing).filter(
                    JobListing.title.contains(keyword) | 
                    JobListing.description.contains(keyword)
                ).count()
                print(f'{keyword}相关职位: {count}个')
                
            print('\n=== 学历要求分布 ===')
            education_stats = db.query(JobListing.education, db.func.count(JobListing.id)).group_by(JobListing.education).all()
            for edu, count in education_stats:
                print(f'{edu}: {count}个职位')
                
            print('\n=== 经验要求分布 ===')
            experience_stats = db.query(JobListing.experience, db.func.count(JobListing.id)).group_by(JobListing.experience).all()
            for exp, count in experience_stats:
                print(f'{exp}: {count}个职位')
                
        else:
            print('数据库中暂无职位数据')
            
    except Exception as e:
        print(f'数据库查询错误: {e}')
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    main()
