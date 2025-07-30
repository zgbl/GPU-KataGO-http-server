# 文件使用指南

## 🎯 当前正在使用的文件

### 核心服务器文件
- ✅ `katago_analysis_server.py` - **主要服务器** (新的Analysis架构)
- ✅ `katago_integrated_server.py` - 集成服务器
- ✅ `docker-compose.integrated.yml` - **当前Docker配置**
- ✅ `Dockerfile.integrated` - **当前Docker镜像**

### 配置文件
- ✅ `configs/katago_gtp.cfg` - KataGo配置

### 测试工具 (推荐使用)
- ✅ `sgf_test_claude.py` - **主要测试工具** (推荐)
- ✅ `demo_sgf_tester.py` - 自动化测试
- ✅ `sgf_http_tester.py` - 交互式测试

### 文档文件
- ✅ `README.md` - **主要文档**
- ✅ `CURRENT_STATUS.md` - **当前状态说明**
- ✅ `QUICK_START_CURRENT.md` - **快速开始指南**
- ✅ `README_INTEGRATED.md` - 技术文档
- ✅ `SGF_TESTER_README.md` - 测试工具说明
- ✅ `FILE_GUIDE.md` - 本文件

## 📁 历史/备用文件

### 旧版本文件 (不推荐使用)
- 📦 `katago-server/` - 旧版服务器目录
- 📦 `KataGo-BlackRice/` - KataGo源码目录
- 📦 各种 `test_*.py` 文件 - 旧版测试文件
- 📦 `claude_*.py` 文件 - 开发过程中的临时文件

### 工具脚本
- 🔧 `build_and_run.ps1` / `build_and_run.sh` - 构建脚本
- 🔧 `health_check.ps1` / `health_check.sh` - 健康检查脚本
- 🔧 `validate_config.ps1` - 配置验证脚本

## 🚀 推荐工作流程

### 1. 启动服务器
```bash
docker-compose -f docker-compose.integrated.yml up --build -d
```

### 2. 测试功能
```bash
python sgf_test_claude.py
```

### 3. 查看状态
```bash
docker ps
docker logs katago-integrated-server2
```

## 📋 文件优先级

### 必须使用
1. `katago_analysis_server.py` - 核心服务器
2. `docker-compose.integrated.yml` - Docker配置
3. `sgf_test_claude.py` - 测试工具

### 推荐阅读
1. `README.md` - 项目概述
2. `QUICK_START_CURRENT.md` - 快速开始
3. `CURRENT_STATUS.md` - 详细状态

### 可选参考
- 其他测试工具
- 历史文档
- 开发脚本

## 🧹 清理建议

如果想要清理项目目录，可以考虑移除或归档以下文件：

### 可以移除的文件
- `claude_*.py` - 开发临时文件
- `test_*.py` (除了当前使用的) - 旧版测试文件
- `simpy_test.py` - 临时测试文件

### 可以归档的目录
- `katago-server/` - 旧版服务器 (可移动到 `archive/` 目录)
- `logs2/` - 旧日志目录

## ⚠️ 注意事项

1. **不要删除** `KataGo-BlackRice/` 目录 - 包含KataGo源码和模型
2. **不要修改** `configs/` 目录中的配置文件，除非你知道在做什么
3. **保留** 所有 `.md` 文档文件 - 它们提供重要的使用说明
4. **备份** 重要的配置文件再进行任何清理操作

---

**建议**: 新用户只需要关注 "当前正在使用的文件" 部分，其他文件可以忽略。