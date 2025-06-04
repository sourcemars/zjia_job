# 智佳招聘 (ZJia Job) - 职位匹配系统

## 项目概述

智佳招聘是一个基于人工智能的职位匹配平台，专注于中国技术人才市场。系统通过自动化爬取多个招聘网站的职位信息，结合智能简历解析和匹配算法，为求职者提供精准的职位推荐服务。

## 核心功能

### 🔍 职位数据采集
- **多源爬取**: 支持爱国聘(iguopin.com)、JobOnline等主流招聘网站
- **智能去重**: 自动识别和合并重复职位信息
- **实时更新**: 定期更新职位数据，确保信息时效性

### 📄 简历智能解析
- **多格式支持**: PDF、DOC、DOCX格式简历解析
- **中文优化**: 专门针对中文简历优化的解析算法
- **结构化提取**: 自动提取姓名、教育背景、工作经历、技能等关键信息

### 🎯 智能职位匹配
- **一票否决机制**: 学历要求和求职者状态的强制筛选
- **技能匹配算法**: 基于关键词和语义分析的技能匹配
- **综合评分系统**: 多维度评分，提供详细匹配解释

## 技术架构

### 后端技术栈
- **Python 3.12**: 主要开发语言
- **FastAPI**: 高性能Web框架
- **SQLAlchemy**: ORM数据库操作
- **Selenium**: 网页自动化爬取
- **SQLite**: 轻量级数据库存储

### 项目结构
```
backend/
├── app/
│   ├── api/              # API接口层
│   ├── models/           # 数据模型
│   ├── services/         # 业务逻辑层
│   ├── scrapers/         # 网页爬虫模块
│   ├── resume_parser/    # 简历解析模块
│   └── data_processing/  # 数据处理模块
├── tests/                # 测试文件
└── requirements.txt      # 项目依赖
```

## 快速开始

### 环境要求
- Python 3.12+
- pip 包管理器
- Chrome/Chromium 浏览器 (用于Selenium)

### 安装步骤

1. **克隆项目**
```bash
git clone https://github.com/sourcemars/zjia_job.git
cd zjia_job
```

2. **创建虚拟环境**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate     # Windows
```

3. **安装依赖**
```bash
cd backend
pip install -r requirements.txt
```

4. **初始化数据库**
```bash
python -c "from app.db.base import create_tables; create_tables()"
```

5. **运行测试**
```bash
# 测试简历解析功能
python test_resume_parser.py

# 测试职位匹配功能
python test_job_matching.py
```

## 使用示例

### 简历解析
```python
from app.resume_parser.parser import ResumeParser

parser = ResumeParser()
resume_data = parser.parse_file("path/to/resume.pdf")
print(f"姓名: {resume_data['name']}")
print(f"技能: {resume_data['skills']}")
```

### 职位匹配
```python
from app.services.matching_service import JobMatchingService

matching_service = JobMatchingService()
matches = matching_service.match_resume_to_jobs(resume_data)

for match in matches[:5]:  # 显示前5个匹配结果
    print(f"职位: {match.job_title}")
    print(f"匹配度: {match.score:.2%}")
    print(f"匹配原因: {match.explanation}")
```

## Git Flow 工作流程

本项目采用 Git Flow 工作流程进行版本管理：

- **master**: 生产分支，包含稳定的发布版本
- **develop**: 开发分支，包含最新的开发功能
- **feature/**: 功能分支，用于开发新功能
- **release/**: 发布分支，用于准备新版本发布
- **hotfix/**: 热修复分支，用于紧急修复

详细工作流程请参考 [GITFLOW.md](GITFLOW.md)

## 核心算法

### 职位匹配算法
```
总分 = 基础分(40%) + 技能匹配(60%)

其中：
- 基础分: 通过学历和状态筛选后的基础分数
- 技能匹配: 简历技能与职位要求的重合度
```

### 一票否决规则
1. **学历要求**: 简历学历低于职位最低要求时直接排除
2. **求职者状态**: 职位要求工作经验但求职者未毕业时直接排除

## 测试数据

项目包含完整的测试用例，使用真实简历数据验证匹配效果：

- **测试简历**: 靳博 - 10年技术管理经验
- **测试职位**: 5个真实数据库职位
- **匹配结果**: 80%通过率，97.5%平均匹配度

## 扩展性设计

系统采用模块化设计，支持灵活扩展：

```python
# 添加新的匹配规则
class SalaryMatchingRule:
    def evaluate(self, resume_data, job):
        # 自定义匹配逻辑
        return True, "薪资匹配说明"

matching_service.add_scoring_rule(SalaryMatchingRule())
```

## 贡献指南

1. Fork 项目到个人仓库
2. 创建功能分支: `git checkout -b feature/new-feature`
3. 提交更改: `git commit -m 'feat: add new feature'`
4. 推送分支: `git push origin feature/new-feature`
5. 创建 Pull Request

## 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## 联系方式

- 项目维护者: Mars
- 邮箱: source.mars@gmail.com
- GitHub: [sourcemars/zjia_job](https://github.com/sourcemars/zjia_job)

## 更新日志

### v1.0.0 (2025-06-04)
- ✅ 实现简历解析功能 (PDF/DOC/DOCX)
- ✅ 完成职位匹配算法
- ✅ 建立Git Flow工作流程
- ✅ 添加一票否决机制
- ✅ 支持中文匹配解释

---

**智佳招聘 - 让每个人都能找到合适的工作** 🚀
