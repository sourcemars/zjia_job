#!/usr/bin/env python3
"""
Test script to demonstrate job matching functionality with 靳博's resume data.
"""
import sys
import sqlite3
import json
sys.path.append('.')

JINBO_RESUME_DATA = {
    "name": "靳博",
    "phone": "17710151557",
    "email": "",
    "education": ["本科学历"],
    "experience": [
        "北京克克美电子商务科技有限公司 - 技术服务中心技术总监",
        "北京必普电子商务有限公司 - 软件研发部技术经理", 
        "吉林省文化国际旅行社北京分公司 - 软件研发部技术经理",
        "北京盛邦人力资源有限公司 - 研发部项目经理",
        "微软中国 - 软件研发部技术总监"
    ],
    "skills": [
        "Html5.0, CSS3.0, DIV, Bootstrap, Javascript, VUE",
        "PHP, Mysql, SQLServer, Mariadb", 
        "Windows Server 2008/2012/2016, Linux, 服务器安全",
        "WEB安全, 软件架构, 分布式架构, 高并发处理, 主从分离",
        "人员招聘, 团队管理, 项目管理, 项目预算, 需求分析"
    ],
    "summary": "工作认真负责，有较强的思维能力、学习能力和团队管理能力。拥有多年的软件管理经验和团队管理经验，曾经带领团队研发过CMP项目、ERP项目、OA项目、CRM项目、电商项目等大型软件，做过千万级的项目有5个。现已离职可随时到岗。10年经验。"
}

def create_sample_jobs():
    """Create sample technical jobs for testing matching."""
    sample_jobs = [
        {
            "job_id": "tech_001",
            "title": "PHP高级开发工程师",
            "company_name": "北京科技有限公司",
            "location": "北京",
            "education": "本科及以上",
            "experience": "3-5年",
            "description": "负责PHP后端开发，MySQL数据库设计，参与系统架构设计",
            "requirements": "熟练掌握PHP、MySQL、Linux，有电商项目经验优先"
        },
        {
            "job_id": "tech_002", 
            "title": "技术总监",
            "company_name": "互联网公司",
            "location": "北京",
            "education": "本科及以上",
            "experience": "8年以上",
            "description": "负责技术团队管理，技术架构设计，项目管理",
            "requirements": "8年以上开发经验，有团队管理经验，熟悉分布式架构"
        },
        {
            "job_id": "tech_003",
            "title": "前端开发工程师", 
            "company_name": "创业公司",
            "location": "上海",
            "education": "大专及以上",
            "experience": "1-3年",
            "description": "负责前端页面开发，Vue.js框架使用",
            "requirements": "熟练掌握HTML、CSS、JavaScript、Vue.js"
        },
        {
            "job_id": "tech_004",
            "title": "软件架构师",
            "company_name": "大型企业",
            "location": "北京", 
            "education": "硕士及以上",
            "experience": "10年以上",
            "description": "负责企业级软件架构设计，技术选型",
            "requirements": "10年以上开发经验，精通软件架构设计，有大型项目经验"
        },
        {
            "job_id": "intern_001",
            "title": "Java开发实习生",
            "company_name": "科技公司",
            "location": "北京",
            "education": "本科在读",
            "experience": "应届生/实习",
            "description": "参与Java项目开发，学习企业开发流程",
            "requirements": "计算机相关专业在读学生，熟悉Java基础"
        }
    ]
    
    conn = sqlite3.connect('zjia_job.db')
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM job_listings')
    
    for job in sample_jobs:
        cursor.execute('''
            INSERT INTO job_listings 
            (source, job_id, title, company_name, location, education, experience, description, requirements, raw_data)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', ('test', job['job_id'], job['title'], job['company_name'], job['location'], 
              job['education'], job['experience'], job['description'], job['requirements'], json.dumps(job)))
    
    conn.commit()
    conn.close()
    print(f"创建了 {len(sample_jobs)} 个测试职位")

def test_education_rule():
    """Test education matching rule."""
    print("\n=== 测试学历匹配规则 ===")
    
    test_cases = [
        (["本科学历"], "本科及以上", True),
        (["本科学历"], "硕士及以上", False), 
        (["大专学历"], "本科及以上", False),
        (["硕士学历"], "本科及以上", True),
        ([], "本科及以上", False)
    ]
    
    for resume_edu, job_edu, expected in test_cases:
        edu_levels = {'大专': 2, '本科': 3, '硕士': 4, '博士': 5}
        
        resume_level = 0
        for edu in resume_edu:
            for level_name, level_val in edu_levels.items():
                if level_name in edu:
                    resume_level = max(resume_level, level_val)
        
        job_level = 0
        for level_name, level_val in edu_levels.items():
            if level_name in job_edu:
                job_level = level_val
                break
                
        passes = resume_level >= job_level if job_level > 0 else True
        status = "✓" if passes == expected else "✗"
        print(f"{status} 简历学历:{resume_edu} vs 职位要求:{job_edu} -> {passes}")

def test_job_seeker_status_rule():
    """Test job seeker status rule."""
    print("\n=== 测试求职者状态规则 ===")
    
    test_cases = [
        ("现已离职可随时到岗。10年经验", "3-5年", True),
        ("在校学生，即将毕业", "3-5年", False),
        ("应届毕业生", "应届生/实习", True),
        ("10年工作经验", "8年以上", True)
    ]
    
    for resume_summary, job_exp, expected in test_cases:
        is_student = any(keyword in resume_summary for keyword in ['在读', '在校', '即将毕业', '学生'])
        
        requires_exp = not any(keyword in job_exp for keyword in ['应届', '实习', '0年'])
        
        passes = not (is_student and requires_exp)
        status = "✓" if passes == expected else "✗"
        print(f"{status} 求职者状态:'{resume_summary}' vs 职位要求:'{job_exp}' -> {passes}")

def test_skill_matching():
    """Test skill matching algorithm."""
    print("\n=== 测试技能匹配算法 ===")
    
    resume_skills = {"php", "mysql", "vue", "javascript", "linux", "架构"}
    
    job_requirements = [
        ("熟练掌握PHP、MySQL、Linux，有电商项目经验优先", {"php", "mysql", "linux"}),
        ("熟练掌握HTML、CSS、JavaScript、Vue.js", {"javascript", "vue"}),
        ("精通软件架构设计，有大型项目经验", {"架构"}),
        ("熟悉Java基础", {"java"})
    ]
    
    for req_text, job_skills in job_requirements:
        matched_skills = resume_skills.intersection(job_skills)
        match_ratio = len(matched_skills) / len(job_skills) if job_skills else 0
        print(f"职位要求: {req_text}")
        print(f"  匹配技能: {matched_skills}")
        print(f"  匹配度: {match_ratio:.2%} ({len(matched_skills)}/{len(job_skills)})")

def test_full_matching():
    """Test full matching process with 靳博's resume."""
    print("\n=== 完整匹配测试 - 靳博简历 ===")
    
    conn = sqlite3.connect('zjia_job.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT job_id, title, company_name, education, experience, requirements FROM job_listings')
    jobs = cursor.fetchall()
    
    matches = []
    
    for job_id, title, company, education, experience, requirements in jobs:
        print(f"\n评估职位: {title} ({company})")
        
        resume_edu_level = 3  # 本科 = 3
        job_edu_level = 3 if "本科" in education else 4 if "硕士" in education else 2
        
        if resume_edu_level < job_edu_level:
            print(f"  ✗ 学历不符合: 简历本科 < 要求{education}")
            continue
        else:
            print(f"  ✓ 学历符合: 简历本科 >= 要求{education}")
        
        is_student = "在读" in JINBO_RESUME_DATA["summary"] or "学生" in JINBO_RESUME_DATA["summary"]
        requires_exp = not any(keyword in experience for keyword in ['应届', '实习', '0年'])
        
        if is_student and requires_exp:
            print(f"  ✗ 状态不符合: 在校学生但职位要求经验")
            continue
        else:
            print(f"  ✓ 状态符合: 有工作经验，满足{experience}要求")
        
        resume_skills = {"php", "mysql", "vue", "javascript", "linux", "架构", "管理"}
        job_skills = set()
        
        if requirements:
            req_lower = requirements.lower()
            for skill in resume_skills:
                if skill in req_lower:
                    job_skills.add(skill)
        
        if job_skills:
            matched_skills = resume_skills.intersection(job_skills)
            skill_score = len(matched_skills) / len(job_skills)
        else:
            skill_score = 0.5  # Default score when no specific skills mentioned
            
        total_score = 0.4 + skill_score * 0.6  # Base 40% + skill matching 60%
        
        print(f"  技能匹配: {skill_score:.2%}")
        print(f"  总分: {total_score:.2%}")
        
        matches.append((total_score, title, company, f"学历符合，状态符合，技能匹配度{skill_score:.2%}"))
    
    matches.sort(reverse=True)
    
    print(f"\n=== 匹配结果排序 (共{len(matches)}个职位通过筛选) ===")
    for i, (score, title, company, explanation) in enumerate(matches, 1):
        print(f"{i}. {title} ({company}) - 匹配度:{score:.2%}")
        print(f"   原因: {explanation}")
    
    conn.close()

def main():
    print("开始测试职位匹配功能...")
    
    create_sample_jobs()
    
    test_education_rule()
    test_job_seeker_status_rule() 
    test_skill_matching()
    
    test_full_matching()

if __name__ == "__main__":
    main()
