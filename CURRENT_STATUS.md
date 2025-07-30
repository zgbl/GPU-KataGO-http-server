# GPU-KataGO HTTP Server 当前状态文档

## 概述

本项目现在使用**新的Analysis服务器架构**，专门为KataGo Analysis模式优化，能够返回完整的分析数据。

## 核心文件说明

### 主要服务器文件

1. **katago_analysis_server.py** - **新的Analysis服务器** (主要文件)
   - 专门处理KataGo Analysis模式的JSON通信协议
   - 支持完整的分析数据返回
   - 修复了moves格式和analyzeTurns参数问题
   - 包含完整的分析参数配置

2. **katago_integrated_server.py** - 集成服务器
   - 整合Analysis服务器和其他功能
   - 提供统一的HTTP接口

### 配置文件

- **docker-compose.integrated.yml** - Docker Compose配置
- **Dockerfile.integrated** - Docker镜像构建文件
- **configs/katago_gtp.cfg** - KataGo配置文件

### 测试文件

- **sgf_test_claude.py** - SGF测试工具 (推荐使用)
- **demo_sgf_tester.py** - 自动化SGF测试
- **sgf_http_tester.py** - 交互式SGF测试

## 完整工作流程

### 1. 构建和启动

```bash
# 停止现有容器
docker-compose -f docker-compose.integrated.yml down

# 构建并启动新容器
docker-compose -f docker-compose.integrated.yml up --build -d

# 检查容器状态
docker ps
```

### 2. 验证服务器状态

```bash
# 检查健康状态
curl http://localhost:8080/health

# 查看容器日志
docker logs katago-integrated-server2
```

### 3. 测试分析功能

#### 使用SGF测试工具 (推荐)

```bash
python sgf_test_claude.py
```

功能特点：
- 支持SGF内容输入和示例SGF
- 逐步分析功能
- 详细的分析结果显示
- 候选手和胜率信息
- 可配置分析间隔

#### 使用自动化测试

```bash
python demo_sgf_tester.py
```

#### 直接API调用测试

```bash
# PowerShell示例
$body = @{
    board_size = 19
    moves = @(
        @("B", "Q16"),
        @("W", "D16")
    )
} | ConvertTo-Json -Depth 3

Invoke-RestMethod -Uri "http://localhost:8080/select-move/katago_gtp_bot" -Method Post -Body $body -ContentType "application/json"
```

## API接口说明

### 主要端点

- `GET /health` - 健康检查
- `GET /info` - 服务器信息
- `POST /select-move/katago_gtp_bot` - 分析接口

### 分析接口格式

**请求格式：**
```json
{
    "board_size": 19,
    "moves": [
        ["B", "Q16"],
        ["W", "D16"],
        ["B", "Q3"]
    ]
}
```

**响应格式：**
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
            "scoreMean": -0.85,
            "pv": ["D4", "Q4", "D16"]
        }
    ]
}
```

## 问题修复记录

### 已解决的问题

1. **500错误问题** - 修复了moves格式转换错误
2. **analyzeTurns参数** - 正确设置为分析所有回合
3. **Analysis数据缺失** - 添加了完整的分析参数
4. **moves格式兼容** - 确保KataGo Analysis模式的正确格式

### 关键修复

在 `katago_analysis_server.py` 中：
- 修复了moves参数从 `['Q16', 'D16']` 到 `[['B', 'Q16'], ['W', 'D16']]` 的格式转换
- 添加了 `includeOwnership`、`includePolicy`、`includePVVisits` 参数
- 正确处理了 `analyzeTurns` 参数设置

## 当前状态

✅ **完全正常工作**
- Analysis服务器稳定运行
- 返回完整的分析数据
- SGF测试工具验证通过
- API调用正常响应

## 推荐使用方式

1. **日常测试**: 使用 `sgf_test_claude.py`
2. **自动化测试**: 使用 `demo_sgf_tester.py`
3. **开发调试**: 查看 `docker logs katago-integrated-server2`
4. **API集成**: 参考上述API接口格式

## 注意事项

- 确保Docker容器状态为 `healthy`
- 分析大量手数时建议设置合适的间隔时间
- 查看容器日志以监控服务器状态
- 使用新的Analysis服务器架构，不要使用旧的GTP模式文件

---

**最后更新**: 2024年当前日期
**状态**: 完全正常工作
**主要文件**: katago_analysis_server.py
**测试工具**: sgf_test_claude.py