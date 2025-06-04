#!/usr/bin/env python3
"""
Test job matching with real database job positions using 靳博's resume.
"""
import sqlite3
import sys
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

def check_database_jobs():
    """Check what job data exists in the database."""
    try:
        conn = sqlite3.connect('zjia_job.db')
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='job_listings'")
        table_exists = cursor.fetchone()
        
        if not table_exists:
            print("❌ 数据库中不存在 job_listings 表")
            return 0, []
            
        cursor.execute('SELECT COUNT(*) FROM job_listings')
        job_count = cursor.fetchone()[0]
        
        if job_count == 0:
            print("❌ 数据库中没有职位数据")
            return 0, []
            
        cursor.execute('''
            SELECT job_id, title, company_name, location, education, 
                   experience, description, requirements 
            FROM job_listings
        ''')
        jobs = cursor.fetchall()
        
        conn.close()
        return job_count, jobs
        
    except Exception as e:
        print(f"❌ 数据库查询错误: {e}")
        return 0, []

def simple_education_check(resume_education, job_education):
    """Simple education level check."""
    if not job_education:
        return True, "无学历要求"
        
    education_levels = {
        '高中': 1, '中专': 1,
        '大专': 2, '专科': 2,
        '本科': 3, '学士': 3,
        '硕士': 4, '研究生': 4,
        '博士': 5, '博士后': 6
    }
    
    job_level = 0
    for edu_name, level in education_levels.items():
        if edu_name in job_education.lower():
            job_level = max(job_level, level)
            
    resume_level = 0
    for edu in resume_education:
        for edu_name, level in education_levels.items():
            if edu_name in edu.lower():
                resume_level = max(resume_level, level)
                
    if job_level == 0:
        return True, "无法解析学历要求"
        
    if resume_level >= job_level:
        return True, f"学历符合 (简历:{resume_level} >= 要求:{job_level})"
    else:
        return False, f"学历不符合 (简历:{resume_level} < 要求:{job_level})"

def simple_skill_matching(resume_skills, job_text):
    """Simple skill matching."""
    if not job_text:
        return 0, []
        
    tech_skills = {
        'php', 'java', 'python', 'javascript', 'js', 'vue', 'react', 'angular',
        'mysql', 'postgresql', 'mongodb', 'redis', 'elasticsearch',
        'html', 'css', 'bootstrap', 'jquery', 'nodejs', 'express',
        'spring', 'laravel', 'django', 'flask', 'docker', 'kubernetes',
        'git', 'svn', 'linux', 'windows', 'nginx', 'apache',
        'restful', 'api', 'microservice', 'distributed', 'cloud', '架构', '管理'
    }
    
    resume_skill_set = set()
    for skill_text in resume_skills:
        text_lower = skill_text.lower()
        for skill in tech_skills:
            if skill in text_lower:
                resume_skill_set.add(skill)
                
    job_skill_set = set()
    job_text_lower = job_text.lower()
    for skill in tech_skills:
        if skill in job_text_lower:
            job_skill_set.add(skill)
            
    if not job_skill_set:
        return 0, []
        
    matched_skills = resume_skill_set.intersection(job_skill_set)
    match_ratio = len(matched_skills) / len(job_skill_set)
    
    return match_ratio, list(matched_skills)

def test_with_real_database():
    """Test matching with real database job positions."""
    print("=== 使用数据库真实职位数据进行匹配测试 ===\n")
    
    job_count, jobs = check_database_jobs()
    
    if job_count == 0:
        print("无法进行真实数据库测试，因为数据库中没有职位数据")
        return
        
    print(f"✅ 数据库中找到 {job_count} 个职位")
    print(f"📋 测试简历: {JINBO_RESUME_DATA['name']} (本科学历, 10年经验)")
    
    matches = []
    filtered_count = 0
    
    print(f"\n开始逐个评估 {len(jobs)} 个职位...")
    
    for i, job in enumerate(jobs, 1):
        job_id, title, company, location, education, experience, description, requirements = job
        
        print(f"\n{i}. 评估职位: {title}")
        print(f"   公司: {company or '未知公司'}")
        print(f"   学历要求: {education or '无要求'}")
        print(f"   经验要求: {experience or '无要求'}")
        
        edu_pass, edu_reason = simple_education_check(JINBO_RESUME_DATA['education'], education or '')
        
        if not edu_pass:
            print(f"   ❌ 学历筛选: {edu_reason}")
            filtered_count += 1
            continue
            
        print(f"   ✅ 学历筛选: {edu_reason}")
        
        job_text = f"{description or ''} {requirements or ''}"
        skill_ratio, matched_skills = simple_skill_matching(JINBO_RESUME_DATA['skills'], job_text)
        
        score = 0.4 + (skill_ratio * 0.6)  # Base 40% + skill matching 60%
        
        print(f"   📊 技能匹配度: {skill_ratio:.2%}")
        if matched_skills:
            print(f"   🎯 匹配技能: {', '.join(matched_skills[:5])}")
        print(f"   📈 综合评分: {score:.2%}")
        
        matches.append({
            'title': title,
            'company': company or '未知公司',
            'score': score,
            'skill_ratio': skill_ratio,
            'matched_skills': matched_skills,
            'location': location or '未知'
        })
    
    matches.sort(key=lambda x: x['score'], reverse=True)
    
    print(f"\n" + "="*60)
    print(f"📊 匹配结果统计")
    print(f"="*60)
    print(f"总职位数: {len(jobs)}")
    print(f"通过筛选: {len(matches)}")
    print(f"被过滤: {filtered_count}")
    print(f"筛选通过率: {len(matches)/len(jobs):.1%}")
    
    if matches:
        avg_score = sum(m['score'] for m in matches) / len(matches)
        print(f"平均匹配度: {avg_score:.2%}")
        print(f"最高匹配度: {max(m['score'] for m in matches):.2%}")
        
        print(f"\n🏆 前5名匹配职位:")
        for i, match in enumerate(matches[:5], 1):
            print(f"{i}. {match['title']} ({match['company']})")
            print(f"   匹配度: {match['score']:.2%}")
            print(f"   技能匹配: {match['skill_ratio']:.2%}")
            if match['matched_skills']:
                print(f"   匹配技能: {', '.join(match['matched_skills'][:3])}")
            print(f"   工作地点: {match['location']}")
    
    return len(jobs), len(matches) if matches else 0

def main():
    """Main function."""
    print("靳博简历与数据库职位匹配测试")
    print("="*60)
    
    total_jobs, matched_jobs = test_with_real_database()
    
    print(f"\n" + "="*60)
    print("✅ 数据库职位匹配测试完成")
    print("="*60)
    
    if total_jobs > 0:
        print(f"📈 测试规模: 靳博的简历与数据库中的 {total_jobs} 个真实职位进行了匹配")
        print(f"📊 匹配结果: {matched_jobs} 个职位通过了预筛选")
        print(f"🎯 这是基于真实数据库职位数据的完整匹配测试")
    else:
        print("⚠️  数据库中暂无职位数据，无法进行真实匹配测试")
        print("💡 建议先运行 simple_job_loader.py 加载职位数据")

if __name__ == "__main__":
    main()
