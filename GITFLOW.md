# Git Flow 工作流程指南

## 概述

本项目采用 Git Flow 工作流程来管理代码版本和发布流程。Git Flow 是一个基于 Git 的分支模型，适合有计划发布周期的项目。

## 分支结构

### 主要分支

- **master** - 生产分支，包含稳定的生产代码
- **develop** - 开发分支，包含最新的开发功能

### 辅助分支

- **feature/** - 功能分支，用于开发新功能
- **release/** - 发布分支，用于准备新版本发布
- **hotfix/** - 热修复分支，用于紧急修复生产问题

## 工作流程

### 1. 功能开发 (Feature)

```bash
# 创建功能分支
git checkout develop
git checkout -b feature/job-matching-enhancement

# 开发完成后合并到 develop
git checkout develop
git merge --no-ff feature/job-matching-enhancement
git branch -d feature/job-matching-enhancement
git push origin develop
```

### 2. 发布准备 (Release)

```bash
# 创建发布分支
git checkout develop
git checkout -b release/v1.0.0

# 发布准备完成后合并到 master 和 develop
git checkout master
git merge --no-ff release/v1.0.0
git tag -a v1.0.0 -m "Release version 1.0.0"

git checkout develop
git merge --no-ff release/v1.0.0
git branch -d release/v1.0.0
```

### 3. 热修复 (Hotfix)

```bash
# 创建热修复分支
git checkout master
git checkout -b hotfix/critical-bug-fix

# 修复完成后合并到 master 和 develop
git checkout master
git merge --no-ff hotfix/critical-bug-fix
git tag -a v1.0.1 -m "Hotfix version 1.0.1"

git checkout develop
git merge --no-ff hotfix/critical-bug-fix
git branch -d hotfix/critical-bug-fix
```

## 分支命名规范

### 功能分支 (feature/)
- `feature/resume-parser-enhancement` - 简历解析功能增强
- `feature/job-matching-algorithm` - 职位匹配算法
- `feature/api-optimization` - API 优化

### 发布分支 (release/)
- `release/v1.0.0` - 主要版本发布
- `release/v1.1.0` - 次要版本发布

### 热修复分支 (hotfix/)
- `hotfix/security-patch` - 安全补丁
- `hotfix/critical-bug` - 关键错误修复

## 提交信息规范

使用语义化提交信息：

```
feat: 添加新的职位匹配算法
fix: 修复简历解析中的编码问题
docs: 更新 API 文档
style: 代码格式化
refactor: 重构数据处理模块
test: 添加单元测试
chore: 更新依赖包
```

## Pull Request 流程

1. **功能开发**
   - 从 `develop` 创建 `feature/` 分支
   - 开发完成后创建 PR 到 `develop`
   - 代码审查通过后合并

2. **发布准备**
   - 从 `develop` 创建 `release/` 分支
   - 完成发布准备后创建 PR 到 `master`
   - 同时创建 PR 到 `develop` 同步更改

3. **热修复**
   - 从 `master` 创建 `hotfix/` 分支
   - 修复完成后创建 PR 到 `master` 和 `develop`

## 版本标签

使用语义化版本号：`v{major}.{minor}.{patch}`

- **major**: 不兼容的 API 更改
- **minor**: 向后兼容的功能添加
- **patch**: 向后兼容的错误修复

示例：`v1.0.0`, `v1.1.0`, `v1.1.1`

## 自动化工具

### Git Flow 扩展

安装 git-flow 扩展工具：

```bash
# Ubuntu/Debian
sudo apt-get install git-flow

# macOS
brew install git-flow

# 初始化
git flow init
```

### 常用命令

```bash
# 开始新功能
git flow feature start job-matching-enhancement

# 完成功能
git flow feature finish job-matching-enhancement

# 开始发布
git flow release start v1.0.0

# 完成发布
git flow release finish v1.0.0

# 开始热修复
git flow hotfix start critical-bug

# 完成热修复
git flow hotfix finish critical-bug
```

## 最佳实践

1. **保持 master 分支稳定** - 只有经过测试的代码才能合并到 master
2. **定期同步 develop** - 及时将 master 的更改同步到 develop
3. **小而频繁的提交** - 保持提交粒度适中，便于代码审查
4. **详细的提交信息** - 清楚描述更改内容和原因
5. **代码审查** - 所有 PR 都需要经过代码审查
6. **自动化测试** - 在合并前运行自动化测试

## 团队协作

1. **分支保护** - 设置 master 和 develop 分支保护规则
2. **权限管理** - 合理分配团队成员的仓库权限
3. **CI/CD 集成** - 配置持续集成和部署流程
4. **文档维护** - 及时更新项目文档和 API 文档

## 故障排除

### 常见问题

1. **合并冲突** - 及时同步上游分支，减少冲突
2. **分支混乱** - 严格按照 Git Flow 流程操作
3. **版本标签错误** - 使用统一的版本标签规范

### 紧急情况处理

1. **生产环境问题** - 立即创建 hotfix 分支
2. **发布回滚** - 使用 git revert 或重新部署上一个稳定版本
3. **数据恢复** - 按照数据备份策略进行恢复

---

遵循这个 Git Flow 工作流程将帮助团队更好地管理代码版本，提高开发效率和代码质量。
