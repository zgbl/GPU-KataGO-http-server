# KataGo 整合版 HTTP Server

## 🎯 项目概述

这是一个整合版的 KataGo HTTP 服务器，结合了：
- **KataGo-BlackRice**: 最新的 GPU KataGo 引擎 (2025.4 版本)
- **katago-server**: 成熟的 HTTP API 服务器实现

通过 Docker 容器化部署，提供高性能的围棋分析 HTTP API 服务。

## ✨ 主要特性

- 🚀 **最新 GPU KataGo 引擎**: 基于 CUDA 12.9.1 的最新版本
- 🌐 **RESTful API**: 简单易用的 HTTP 接口
- 🐳 **Docker 容器化**: 一键部署，环境隔离
- 🎮 **GPU 加速**: 充分利用 NVIDIA GPU 性能
- 📊 **实时监控**: 健康检查和性能监控
- 🔧 **灵活配置**: 支持自定义参数调整

## 📋 系统要求

### 硬件要求
- **GPU**: NVIDIA GPU (推荐 8GB+ 显存)
- **内存**: 8GB+ RAM
- **存储**: 10GB+ 可用空间

### 软件要求
- **操作系统**: Windows 10/11, Linux, macOS
- **Docker**: Docker Desktop 或 Docker Engine
- **NVIDIA Container Toolkit**: GPU 支持必需

## 🚀 快速开始

### 1. 准备工作

```powershell
# 克隆项目（如果还没有）
git clone <repository-url>
cd GPU-KataGO-http-server

# 确保模型文件存在
# 将 KataGo 模型文件放置到 KataGo-BlackRice/models/ 目录
# 例如: KataGo-BlackRice/models/model.bin.gz
```

### 2. 一键构建和运行

```powershell
# Windows PowerShell
.\build_and_run.ps1 build    # 构建镜像
.\build_and_run.ps1 run      # 运行服务
```

```bash
# Linux/macOS
./build_and_run.sh build     # 构建镜像
./build_and_run.sh run       # 运行服务
```

### 3. 使用 Docker Compose

```bash
# 启动服务
docker-compose -f docker-compose.integrated.yml up -d

# 查看日志
docker-compose -f docker-compose.integrated.yml logs -f

# 停止服务
docker-compose -f docker-compose.integrated.yml down
```

## 🔧 配置说明

### 环境变量

| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| `KATAGO_BINARY` | `/app/bin/katago` | KataGo 可执行文件路径 |
| `KATAGO_MODEL` | `/app/models/model.bin.gz` | 模型文件路径 |
| `KATAGO_CONFIG` | `/app/configs/katago_gtp.cfg` | 配置文件路径 |
| `HTTP_PORT` | `8080` | HTTP 服务端口 |
| `CUDA_VISIBLE_DEVICES` | `0` | 可见的 GPU 设备 |

### KataGo 配置

编辑 `configs/katago_gtp.cfg` 文件来调整 KataGo 参数：

```ini
# 搜索强度
maxVisits = 1600
maxTime = 10.0
numSearchThreads = 6

# GPU 批处理
nnMaxBatchSize = 16

# 其他参数...
```

## 📡 API 接口

### 健康检查

```http
GET /health
```

**响应示例:**
```json
{
  "status": "healthy",
  "timestamp": "2025-01-30T12:00:00",
  "version": "integrated-v1.0"
}
```

### 服务器信息

```http
GET /info
```

**响应示例:**
```json
{
  "name": "KataGo Integrated HTTP Server",
  "version": "integrated-v1.0",
  "katago_binary": "/app/bin/katago",
  "model_file": "model.bin.gz",
  "endpoints": ["/health", "/info", "/select-move/katago_gtp_bot", "/score/katago_gtp_bot"]
}
```

### 获取最佳走法

```http
POST /select-move/katago_gtp_bot
Content-Type: application/json

{
  "board_size": 19,
  "moves": ["R4", "D16"],
  "config": {
    "request_id": "optional_id"
  }
}
```

**响应示例:**
```json
{
  "bot_move": "Q4",
  "diagnostics": {
    "win_prob": 0.52,
    "score": 1.2
  },
  "request_id": "optional_id",
  "timestamp": "2025-01-30T12:00:00"
}
```

### 局面评估

```http
POST /score/katago_gtp_bot
Content-Type: application/json

{
  "board_size": 19,
  "moves": ["R4", "D16", "Q16"],
  "config": {
    "request_id": "optional_id"
  }
}
```

**响应示例:**
```json
{
  "probs": [0.1, 0.2, -0.1, ...],  // 361个点的归属概率
  "diagnostics": {
    "win_prob": 0.48,
    "score": -0.5
  },
  "request_id": "optional_id",
  "timestamp": "2025-01-30T12:00:00"
}
```

## 🧪 测试

### 自动化测试

```bash
# 运行完整测试套件
python test_integrated_server.py

# 测试特定功能
python test_integrated_server.py --test health
python test_integrated_server.py --test move
python test_integrated_server.py --test score

# 测试不同端口
python test_integrated_server.py --url http://localhost:8080
```

### 手动测试

```powershell
# PowerShell 测试
.\build_and_run.ps1 test

# 或者使用 curl
curl -X POST http://localhost:8080/select-move/katago_gtp_bot \
  -H "Content-Type: application/json" \
  -d '{"board_size": 19, "moves": []}'
```

## 📊 监控和日志

### 查看日志

```bash
# 容器日志
docker logs -f katago-integrated-server

# 应用日志
tail -f logs/http_server.log
```

### 性能监控

```bash
# 容器资源使用
docker stats katago-integrated-server

# GPU 使用情况
nvidia-smi
```

## 🔧 故障排除

### 常见问题

1. **容器启动失败**
   ```bash
   # 检查日志
   docker logs katago-integrated-server
   
   # 检查 GPU 支持
   docker run --rm --gpus all nvidia/cuda:11.0-base nvidia-smi
   ```

2. **模型文件未找到**
   ```bash
   # 确保模型文件存在
   ls -la KataGo-BlackRice/models/
   
   # 检查文件权限
   chmod 644 KataGo-BlackRice/models/*.bin.gz
   ```

3. **API 响应慢**
   - 调整 `configs/katago_gtp.cfg` 中的 `maxVisits` 参数
   - 增加 `nnMaxBatchSize` 以提高 GPU 利用率
   - 确保 GPU 有足够显存

4. **内存不足**
   ```bash
   # 增加 Docker 内存限制
   docker run --memory=8g ...
   ```

### 调试模式

```bash
# 进入容器调试
docker exec -it katago-integrated-server bash

# 手动运行 KataGo
/app/bin/katago benchmark
/app/bin/katago gtp -model /app/models/model.bin.gz -config /app/configs/katago_gtp.cfg
```

## 🚀 性能优化

### GPU 优化

1. **调整批处理大小**
   ```ini
   # configs/katago_gtp.cfg
   nnMaxBatchSize = 32  # 根据显存调整
   ```

2. **多 GPU 支持**
   ```bash
   # 使用多个 GPU
   docker run --gpus "device=0,1" ...
   ```

### 并发优化

1. **增加搜索线程**
   ```ini
   # configs/katago_gtp.cfg
   numSearchThreads = 8  # 根据 CPU 核心数调整
   ```

2. **负载均衡**
   - 使用多个容器实例
   - 配置 Nginx 反向代理

## 📚 开发指南

### 项目结构

```
GPU-KataGO-http-server/
├── KataGo-BlackRice/          # 最新 GPU KataGo 源码
├── katago-server/             # HTTP 服务器代码
├── Dockerfile.integrated      # 整合版 Dockerfile
├── docker-compose.integrated.yml
├── katago_integrated_server.py # 整合版服务器脚本
├── configs/                   # 配置文件
├── build_and_run.ps1         # Windows 构建脚本
├── test_integrated_server.py  # 测试脚本
└── README_INTEGRATED.md       # 本文档
```

### 自定义开发

1. **修改 HTTP 接口**
   - 编辑 `katago_integrated_server.py`
   - 添加新的路由和功能

2. **调整 KataGo 参数**
   - 修改 `configs/katago_gtp.cfg`
   - 重新构建镜像

3. **扩展功能**
   - 添加认证和授权
   - 实现请求限流
   - 添加 WebSocket 支持

## 📄 许可证

本项目遵循相应的开源许可证。详见各子项目的许可证文件。

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 🔧 配置验证

在构建和运行之前，建议验证配置文件：

```powershell
# Windows PowerShell
.\validate_config.ps1

# 验证特定配置文件
.\validate_config.ps1 -ConfigPath "configs\katago_gtp.cfg"
```

```bash
# Linux/macOS
# 手动检查配置文件中的常见问题
grep -E "^(rules|koRule|scoringRule|taxRule|multiStoneSuicideLegal|hasButton|whiteHandicapBonus)" configs/katago_gtp.cfg
```

**常见配置问题:**
- ❌ 重复的配置键（如 `nnCacheSizePowerOfTwo` 出现多次）
- ❌ 规则冲突（同时指定 `rules` 和单独规则项）
- ⚠️ 缺少必要的配置项

## 📞 支持

如有问题，请：
1. **首先运行配置验证**: `.\validate_config.ps1`
2. 查看 [快速启动指南](QUICK_START.md)
3. 参考 [详细故障排除指南](TROUBLESHOOTING.md)
4. 运行健康检查脚本: `./health_check.sh`
5. 运行调试脚本: `docker exec -it katago-integrated-server ./debug_katago.sh`
6. 检查项目 Issues
7. 提交新的 Issue 描述问题

---

**享受使用 KataGo 整合版 HTTP Server！** 🎉