# 快速开始指南

## 🚀 一键启动

```bash
# 1. 启动服务器
docker-compose -f docker-compose.integrated.yml up --build -d

# 2. 检查状态
docker ps

# 3. 测试分析
python http_test.py
```

## 📁 关键文件

| 文件 | 用途 | 状态 |
|------|------|------|
| `katago_analysis_server.py` | **主服务器** | ✅ 正常工作 |
| `http_test.py` | **测试工具** | ✅ 推荐使用 |
| `docker-compose.integrated.yml` | Docker配置 | ✅ 当前使用 |
| `CURRENT_STATUS.md` | 详细文档 | 📋 完整说明 |

## 🧪 测试步骤

### 1. 基本测试
```bash
# 健康检查
curl http://localhost:8080/health

# 应该返回: {"status": "healthy"}
```

### 🧪 SGF分析测试

```bash
python http_test.py
```

选择选项：
- `2` - 使用示例SGF
- 输入分析范围 (如: `1-5`)
- 选择详细模式 (`y`)

### 3. API直接测试
```bash
# PowerShell
$body = @{
    board_size = 19
    moves = @(@("B", "Q16"), @("W", "D16"))
} | ConvertTo-Json -Depth 3

Invoke-RestMethod -Uri "http://localhost:8080/select-move/katago_gtp_bot" -Method Post -Body $body -ContentType "application/json"
```

## 📊 预期结果

成功的分析应该返回：
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
            "scoreLead": -0.87
        }
    ]
}
```

## 🔧 故障排除

### 容器问题
```bash
# 查看日志
docker logs katago-integrated-server2

# 重启容器
docker-compose -f docker-compose.integrated.yml restart
```

### 端口问题
```bash
# 检查端口占用
netstat -an | findstr :8080
```

### 测试失败
1. 确认容器状态为 `healthy`
2. 检查 `docker logs` 输出
3. 验证端口8080可访问

## ✅ 验证清单

- [ ] Docker容器运行正常
- [ ] 健康检查返回 `healthy`
- [ ] SGF测试工具能正常分析
- [ ] API返回完整分析数据
- [ ] 胜率、分数、访问次数都有数值
   ```

2. **安装 NVIDIA Container Toolkit**
   ```bash
   # 添加 NVIDIA 仓库
   distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
   curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
   curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list
   
   # 安装 nvidia-docker2
   sudo apt-get update
   sudo apt-get install -y nvidia-docker2
   sudo systemctl restart docker
   ```

## 📥 获取项目

```bash
# 克隆项目（如果还没有）
git clone <your-repository-url>
cd GPU-KataGO-http-server
```

## 🧠 准备模型文件

1. **下载 KataGo 模型**
   ```bash
   # 创建模型目录
   mkdir -p KataGo-BlackRice/models
   
   # 下载最新模型（示例）
   # 请从 https://katagotraining.org/ 下载最新模型
   # 将模型文件放置到 KataGo-BlackRice/models/ 目录
   ```

2. **验证模型文件**
   ```bash
   ls -la KataGo-BlackRice/models/
   # 应该看到类似 model.bin.gz 的文件
   ```

## 🏗️ 构建和启动

### 方法一：使用自动化脚本（推荐）

#### Windows PowerShell
```powershell
# 构建 Docker 镜像
.\build_and_run.ps1 build

# 启动服务
.\build_and_run.ps1 run

# 测试服务
.\build_and_run.ps1 test
```

#### Linux/macOS
```bash
# 构建 Docker 镜像
./build_and_run.sh build

# 启动服务
./build_and_run.sh run

# 测试服务
./build_and_run.sh test
```

### 方法二：使用 Docker Compose

```bash
# 启动服务
docker-compose -f docker-compose.integrated.yml up -d

# 查看日志
docker-compose -f docker-compose.integrated.yml logs -f

# 停止服务
docker-compose -f docker-compose.integrated.yml down
```

### 方法三：手动 Docker 命令

```bash
# 构建镜像
docker build -f Dockerfile.integrated -t katago-integrated:latest .

# 启动容器
docker run -d \
  --name katago-integrated-server \
  --gpus all \
  -p 8080:8080 \
  -v "$(pwd)/KataGo-BlackRice/models:/app/models:ro" \
  -v "$(pwd)/logs:/app/logs" \
  katago-integrated:latest
```

## ✅ 验证安装

### 1. 检查容器状态
```bash
docker ps
# 应该看到 katago-integrated-server 容器正在运行
```

### 2. 健康检查
```bash
# 使用 curl
curl http://localhost:8080/health

# 或使用 PowerShell
Invoke-RestMethod -Uri "http://localhost:8080/health"
```

**预期响应:**
```json
{
  "status": "healthy",
  "timestamp": "2025-01-30T12:00:00",
  "version": "integrated-v1.0"
}
```

### 3. 测试 API
```bash
# 测试获取走法
curl -X POST http://localhost:8080/select-move/katago_gtp_bot \
  -H "Content-Type: application/json" \
  -d '{"board_size": 19, "moves": []}'
```

**预期响应:**
```json
{
  "bot_move": "R4",
  "diagnostics": {
    "win_prob": 0.5,
    "score": 0.0
  },
  "request_id": "",
  "timestamp": "2025-01-30T12:00:00"
}
```

### 4. 运行完整测试套件
```bash
# 运行集成测试脚本
python Pythontest/test_integrated_server.py
```

**测试结果说明:**
- ✅ 健康检查测试 - 验证服务器基本状态
- ✅ 服务器信息测试 - 验证 API 信息端点
- ✅ 空棋盘走法测试 - 验证基本走法生成
- ✅ 局面走法测试 - 验证复杂局面处理
- ✅ 错误处理测试 - 验证异常情况处理
- ⚠️ 局面评估测试 - 可能因 KataGo 引擎问题而失败

**注意:** 如果 KataGo 引擎启动失败，部分需要引擎计算的功能（如局面评估）可能不可用，但 HTTP 服务器本身仍然正常运行。

## 🎮 使用示例

### Python 客户端示例
```bash
# 运行基本演示
python example_client.py --mode demo

# 对局分析演示
python example_client.py --mode game

# 交互模式
python example_client.py --mode interactive
```

### 完整测试套件
```bash
# 运行所有测试
python Pythontest/test_integrated_server.py

# 测试特定功能
python Pythontest/test_integrated_server.py --test health
python Pythontest/test_integrated_server.py --test move
```

## 📊 监控和管理

### 查看日志
```bash
# 容器日志（实时）
docker logs -f katago-integrated-server

# 容器日志（最近30行）
docker logs katago-integrated-server --tail 30

# 应用日志
tail -f logs/http_server.log

# 检查 KataGo 引擎状态
docker exec katago-integrated-server ps aux | grep katago
```

### 性能监控
```bash
# 容器资源使用
docker stats katago-integrated-server

# GPU 使用情况
nvidia-smi
```

### 停止服务
```bash
# 使用脚本
./build_and_run.sh stop

# 或手动停止
docker stop katago-integrated-server
docker rm katago-integrated-server
```

## 🔧 常见问题

### 问题 1: 容器启动失败
**症状:** 容器无法启动或立即退出

**解决方案:**
```bash
# 查看详细日志
docker logs katago-integrated-server

# 检查模型文件
ls -la KataGo-BlackRice/models/

# 检查 GPU 支持
nvidia-smi
docker run --rm --gpus all nvidia/cuda:12.0-base nvidia-smi
```

### 问题 2: API 响应慢
**症状:** 请求超时或响应时间过长

**解决方案:**
1. 调整配置文件 `configs/katago_gtp.cfg`:
   ```ini
   maxVisits = 800  # 减少访问次数
   maxTime = 5.0    # 减少最大时间
   ```

2. 重新构建镜像:
   ```bash
   ./build_and_run.sh build
   ./build_and_run.sh run
   ```

### 问题 3: 内存不足
**症状:** 容器被 OOM Killer 杀死

**解决方案:**
```bash
# 增加 Docker 内存限制
docker run --memory=8g --gpus all ...

# 或在 Docker Desktop 设置中增加内存分配
```

### 问题 4: 端口冲突
**症状:** 端口 8080 已被占用

**解决方案:**
```bash
# 使用不同端口
./build_and_run.sh run --port 8081

# 或停止占用端口的服务
netstat -ano | findstr :8080  # Windows
lsof -i :8080                 # Linux/macOS
```

### 问题 5: KataGo 配置文件错误
**症状:** KataGo 进程启动失败，日志显示 `ConfigParsingError: Key 'nnCacheSizePowerOfTwo' was specified multiple times`

**解决方案:**
```bash
# 检查配置文件中的重复键
grep -n "nnCacheSizePowerOfTwo" configs/katago_gtp.cfg

# 编辑配置文件，移除重复的配置项
# 确保每个配置键只出现一次

# 重新构建和启动容器
docker-compose -f docker-compose.integrated.yml down
docker-compose -f docker-compose.integrated.yml up -d
```

### 问题 6: KataGo 进程反复死亡
**症状:** 容器日志显示 "KataGo process died" 和 "Failed to resurrect KataGo process"

**可能原因和解决方案:**
1. **GPU 内存不足:**
   ```bash
   # 检查 GPU 内存使用
   nvidia-smi
   
   # 调整配置文件减少内存使用
   # 在 configs/katago_gtp.cfg 中:
   # nnCacheSizePowerOfTwo = 20  # 减少到更小的值
   ```

2. **CUDA 版本兼容性:**
   ```bash
   # 检查容器内 CUDA 版本
   docker exec katago-integrated-server nvidia-smi
   
   # 验证 KataGo 版本信息
   docker exec katago-integrated-server /app/bin/katago version
   ```

3. **模型文件问题:**
   ```bash
   # 验证模型文件完整性
   docker exec katago-integrated-server ls -la /app/models/
   
   # 尝试手动运行 KataGo 测试
    docker exec katago-integrated-server /app/bin/katago benchmark -model /app/models/model.bin.gz -config /app/configs/katago_gtp.cfg
    ```

**💡 更多故障排除方案:** 如需更详细的诊断步骤和解决方案，请参考 [故障排除指南](TROUBLESHOOTING.md)。

## 📋 当前版本状态

### ✅ 已验证功能
- Docker 镜像构建和容器启动
- HTTP 服务器基本功能
- 健康检查端点
- API 信息端点
- 基本走法生成
- 错误处理机制
- GPU 环境检测

### ⚠️ 已知问题
- KataGo 引擎可能出现启动失败和反复重启
- 局面评估功能可能不稳定
- 需要手动修复配置文件中的重复键问题

### 🔧 推荐配置
- 使用 CUDA 12.x 版本
- 确保 GPU 有足够内存（建议 4GB+）
- 定期检查容器日志以监控 KataGo 引擎状态

## 🎯 下一步

1. **阅读完整文档**: [README_INTEGRATED.md](README_INTEGRATED.md)
2. **API 参考**: 查看 `/info` 端点获取完整 API 列表
3. **性能调优**: 根据硬件配置调整 `configs/katago_gtp.cfg`
4. **集成开发**: 使用 `example_client.py` 作为起点开发自己的应用
5. **故障排查**: 参考常见问题部分解决 KataGo 引擎问题

## 📞 获取帮助

- 📖 查看完整文档: [README_INTEGRATED.md](README_INTEGRATED.md)
- 🔧 故障排除指南: [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- 🐛 报告问题: 提交 GitHub Issue
- 💬 讨论交流: 项目讨论区

---

**🎉 恭喜！你已经成功启动了 KataGo 整合版 HTTP Server！**