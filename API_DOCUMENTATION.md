# KataGo HTTP Server API 文档

## 概述

这个项目包含多个KataGo HTTP服务器实现，提供围棋分析和走法选择的REST API服务。主要有以下几种服务器实现：

1. **katago-server** - 基于GTP协议的Flask服务器
2. **katago_analysis_server.py** - 基于Analysis Engine的服务器
3. **KataGo-BlackRice** - 原生KataGo HTTP服务
4. **katago_integrated_server.py** - 集成服务器

## 服务器端口配置

- **主服务器**: 端口 8080 (默认)
- **备用服务器**: 端口 2718, 2818 (katago-server变体)
- **分析服务器**: 端口 8080 (katago_analysis_server.py)

## API 端点总览

### 1. 健康检查和信息端点

#### GET /health
**功能**: 检查服务器健康状态
**响应示例**:
```json
{
  "status": "healthy",
  "timestamp": "2025-01-27T10:30:00",
  "version": "analysis-v1.0",
  "engine_running": true
}
```

#### GET /info
**功能**: 获取服务器信息
**响应示例**:
```json
{
  "server": "KataGo HTTP Server",
  "version": "2.0.0",
  "katago_binary": "/usr/local/bin/katago",
  "katago_model": "model.bin.gz",
  "katago_config": "katago_gtp.cfg",
  "endpoints": [
    "/health",
    "/info",
    "/select-move/katago_gtp_bot",
    "/score/katago_gtp_bot"
  ]
}
```

### 2. 走法选择端点

#### POST /select-move/katago_gtp_bot
**功能**: 请求KataGo选择最佳走法

**请求格式**:
```json
{
  "board_size": 19,
  "moves": ["R4", "D16", "Q16"],
  "config": {
    "komi": 7.5,
    "max_visits": 1000,
    "request_id": "optional_id"
  }
}
```

**或者使用颜色+位置格式**:
```json
{
  "board_size": 19,
  "moves": [["B", "R4"], ["W", "D16"], ["B", "Q16"]],
  "config": {
    "komi": 7.5,
    "max_visits": 1000
  }
}
```

**响应示例**:
```json
{
  "bot_move": "Q4",
  "winrate": 0.523,
  "score": 1.2,
  "visits": 1000,
  "analysis": [
    {
      "move": "Q4",
      "winrate": 0.523,
      "visits": 245,
      "scoreMean": 1.2,
      "pv": ["Q4", "C16", "R16"]
    }
  ],
  "diagnostics": {
    "time_taken": 2.5,
    "nodes_searched": 1000
  },
  "request_id": "optional_id",
  "timestamp": "2025-01-27 10:30:00"
}
```

### 3. 局面评估端点

#### POST /score/katago_gtp_bot
**功能**: 评估当前局面，返回领域信息

**请求格式**: 与 `/select-move` 相同

**响应示例**:
```json
{
  "probs": [
    [0.8, 0.2, 0.1, ...],
    [0.7, 0.3, 0.0, ...],
    ...
  ],
  "diagnostics": {
    "time_taken": 1.8,
    "nodes_searched": 1000
  },
  "request_id": "optional_id",
  "timestamp": "2025-01-27 10:30:00"
}
```

### 4. KataGo 原生分析端点

#### POST /analyze
**功能**: KataGo原生分析接口 (仅在KataGo-BlackRice HTTP服务中可用)

**请求格式**:
```json
{
  "id": "analysis_1643284800",
  "moves": [["B", "R4"], ["W", "D16"]],
  "rules": "tromp-taylor",
  "komi": 7.5,
  "boardXSize": 19,
  "boardYSize": 19,
  "analyzeTurns": [2],
  "maxVisits": 1000,
  "includeOwnership": true,
  "includePVVisits": true
}
```

**响应示例**:
```json
{
  "id": "analysis_1643284800",
  "turnInfos": [
    {
      "turnNumber": 2,
      "rootInfo": {
        "winrate": 0.523,
        "scoreMean": 1.2,
        "visits": 1000
      },
      "moveInfos": [
        {
          "move": "Q4",
          "winrate": 0.523,
          "visits": 245,
          "scoreMean": 1.2,
          "pv": ["Q4", "C16", "R16"],
          "order": 0
        }
      ],
      "ownership": [0.8, 0.2, 0.1, ...]
    }
  ]
}
```

## 请求参数说明

### 通用参数

- **board_size** (int): 棋盘大小，支持 9-25，默认 19
- **moves** (array): 走法列表，支持两种格式：
  - 位置格式: `["R4", "D16", "Q16"]`
  - 颜色+位置格式: `[["B", "R4"], ["W", "D16"], ["B", "Q16"]]`
- **config** (object): 配置参数

### config 参数

- **komi** (float): 贴目，默认 7.5
- **max_visits** (int): 最大访问次数，默认 1000
- **request_id** (string): 可选的请求ID
- **rules** (string): 规则，如 "Chinese", "Japanese", "tromp-taylor"
- **include_ownership** (bool): 是否包含领域信息
- **include_policy** (bool): 是否包含策略信息
- **include_pv** (bool): 是否包含主要变化

## 错误处理

### 常见错误响应

```json
{
  "error": "错误描述",
  "message": "详细错误信息"
}
```

### HTTP状态码

- **200**: 成功
- **400**: 请求参数错误
- **500**: 服务器内部错误
- **503**: 服务不可用

## 测试和调试

### 使用 curl 测试

```bash
# 健康检查
curl http://localhost:8080/health

# 获取服务器信息
curl http://localhost:8080/info

# 请求走法选择
curl -X POST http://localhost:8080/select-move/katago_gtp_bot \
  -H "Content-Type: application/json" \
  -d '{
    "board_size": 19,
    "moves": ["R4", "D16"],
    "config": {"komi": 7.5, "max_visits": 1000}
  }'

# 请求局面评估
curl -X POST http://localhost:8080/score/katago_gtp_bot \
  -H "Content-Type: application/json" \
  -d '{
    "board_size": 19,
    "moves": ["R4", "D16"],
    "config": {"komi": 7.5}
  }'
```

### 使用 Python 测试

```python
import requests
import json

# 基本连接测试
response = requests.get('http://localhost:8080/health')
print(f"健康检查: {response.status_code}")
print(json.dumps(response.json(), indent=2))

# 走法选择测试
data = {
    "board_size": 19,
    "moves": ["R4", "D16"],
    "config": {"komi": 7.5, "max_visits": 1000}
}

response = requests.post(
    'http://localhost:8080/select-move/katago_gtp_bot',
    json=data,
    headers={'Content-Type': 'application/json'}
)

print(f"走法选择: {response.status_code}")
print(json.dumps(response.json(), indent=2))
```

## 性能和限制

### 性能参数

- **max_visits**: 控制分析深度，范围 100-10000
- **timeout**: 请求超时时间，建议 30-60 秒
- **并发连接**: 最大 100 个并发连接

### 资源限制

- **请求大小**: 最大 64MB
- **响应时间**: 根据 max_visits 参数，通常 1-30 秒
- **内存使用**: 取决于模型大小和批处理设置

## 故障排除

### 常见问题

1. **连接被拒绝**
   - 检查服务器是否启动
   - 确认端口号正确 (8080)
   - 检查防火墙设置

2. **请求超时**
   - 减少 max_visits 参数
   - 增加客户端超时时间
   - 检查服务器资源使用情况

3. **分析失败**
   - 检查走法格式是否正确
   - 确认棋盘大小在支持范围内
   - 查看服务器日志

### 日志位置

- **katago-server**: `/app/logs/katago_server.log`
- **analysis-server**: 控制台输出
- **KataGo-BlackRice**: `/app/logs/katago_http.log`

## 部署说明

### Docker 部署

```bash
# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

### 环境变量

- **PORT**: 服务端口，默认 8080
- **KATAGO_BINARY**: KataGo 可执行文件路径
- **KATAGO_MODEL**: 模型文件路径
- **KATAGO_CONFIG**: 配置文件路径
- **FLASK_DEBUG**: 调试模式，默认 False

## 版本信息

- **API版本**: v2.0.0
- **KataGo版本**: 支持 1.11.0+
- **更新日期**: 2025-01-27

---

**注意**: 不同的服务器实现可能支持不同的端点。建议首先访问 `/info` 端点获取当前服务器支持的完整端点列表。