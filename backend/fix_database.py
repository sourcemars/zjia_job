#!/usr/bin/env python3
"""
Database fix script to resolve schema mismatch issues.
Deletes existing database and recreates with proper schema.
"""
import os
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

def fix_database():
    """Fix database by removing old file and recreating with proper schema."""
    db_file = "zjia_job.db"
    
    if os.path.exists(db_file):
        print(f"删除现有数据库文件: {db_file}")
        os.remove(db_file)
    
    from init_db import init_db
    print("使用SQLAlchemy模型创建数据库表...")
    init_db()
    
    from simple_job_loader import load_jobs_from_json
    print("加载示例职位数据...")
    load_jobs_from_json()
    
    print("\n数据库修复完成！")
    print("现在可以正常使用简历匹配功能了。")

if __name__ == "__main__":
    fix_database()
