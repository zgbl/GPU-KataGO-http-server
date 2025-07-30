# GPU-KataGO HTTP Server

## 🎯 当前状态 (2024年最新)

✅ **完全正常工作** - 使用新的Analysis服务器架构

- 🚀 **一键启动**: `docker-compose -f docker-compose.integrated.yml up --build -d`
- 🧪 **测试工具**: `python sgf_test_claude.py`
- 📊 **完整分析**: 返回胜率、分数、候选手等完整数据
- 🔧 **核心文件**: `katago_analysis_server.py` (新的Analysis服务器)

## 📚 文档导航

| 文档 | 用途 |
|------|------|
| [QUICK_START_CURRENT.md](QUICK_START_CURRENT.md) | 🚀 **快速开始** (推荐) |
| [CURRENT_STATUS.md](CURRENT_STATUS.md) | 📋 **详细状态说明** |
| [README_INTEGRATED.md](README_INTEGRATED.md) | 🔧 技术文档 |
| [SGF_TESTER_README.md](SGF_TESTER_README.md) | 🧪 测试工具说明 |

## 🚀 快速开始

### 1. 启动服务器
```bash
docker-compose -f docker-compose.integrated.yml up --build -d
```

### 2. 验证运行
```bash
# 检查容器状态
docker ps

# 健康检查
curl http://localhost:8080/health
```

### 3. 测试分析
```bash
python sgf_test_claude.py
```

## 🎯 主要特性

- ✅ **KataGo Analysis模式**: 专门优化的JSON通信协议
- ✅ **完整分析数据**: 胜率、分数、候选手、变化等
- ✅ **SGF支持**: 完整的SGF解析和逐步分析
- ✅ **Docker集成**: 一键部署和运行
- ✅ **多种测试工具**: 自动化和交互式测试

## 📊 API示例

**请求**:
```json
{
    "board_size": 19,
    "moves": [
        ["B", "Q16"],
        ["W", "D16"]
    ]
}
```

**响应**:
```json
{
    "bot_move": "D4",
    "winrate": 0.359,
    "score": -0.87,
    "visits": 118,
    "analysis": [
        {
            "move": "D4",
            "winrate": 0.359,
            "visits": 118,
            "scoreLead": -0.87,
            "pv": ["D4", "Q4", "D16"]
        }
    ]
}
```

## 🔧 核心文件

| 文件 | 用途 | 状态 |
|------|------|------|
| `katago_analysis_server.py` | **主服务器** | ✅ 当前使用 |
| `sgf_test_claude.py` | **测试工具** | ✅ 推荐 |
| `docker-compose.integrated.yml` | Docker配置 | ✅ 当前配置 |
| `demo_sgf_tester.py` | 自动化测试 | ✅ 可用 |

## 🆘 故障排除

### 常见问题

1. **端口8080被占用**
   ```bash
   netstat -an | findstr :8080
   ```

2. **容器启动失败**
   ```bash
   docker logs katago-integrated-server2
   ```

3. **分析返回错误**
   - 检查容器状态是否为 `healthy`
   - 查看容器日志排查问题

### 获取帮助

- 📋 查看 [CURRENT_STATUS.md](CURRENT_STATUS.md) 了解详细状态
- 🚀 查看 [QUICK_START_CURRENT.md](QUICK_START_CURRENT.md) 获取快速指南
- 🧪 使用 `sgf_test_claude.py` 进行测试验证

## 📈 项目历史

- **最新版本**: 使用 `katago_analysis_server.py` 的Analysis服务器架构
- **主要改进**: 修复了moves格式、analyzeTurns参数等关键问题
- **测试验证**: 通过SGF测试工具验证，返回完整分析数据

---

**🎯 推荐**: 新用户请直接查看 [QUICK_START_CURRENT.md](QUICK_START_CURRENT.md) 快速开始使用！