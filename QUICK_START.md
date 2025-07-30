# 🚀 KataGo 整合版 HTTP Server 快速启动指南

## 📋 前置条件检查

### 1. 硬件要求
- ✅ NVIDIA GPU (推荐 8GB+ 显存)
- ✅ 8GB+ 系统内存
- ✅ 10GB+ 可用磁盘空间

### 2. 软件要求
- ✅ Docker Desktop (Windows) 或 Docker Engine (Linux)
- ✅ NVIDIA Container Toolkit
- ✅ Git (用于克隆项目)

## 🔧 环境准备

### Windows 用户

1. **安装 Docker Desktop**
   ```powershell
   # 下载并安装 Docker Desktop for Windows
   # https://docs.docker.com/desktop/windows/install/
   ```

2. **安装 NVIDIA Container Toolkit**
   ```powershell
   # 在 Docker Desktop 设置中启用 GPU 支持
   # 或参考: https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html
   ```

3. **验证 GPU 支持**
   ```powershell
   docker run --rm --gpus all nvidia/cuda:11.0-base nvidia-smi
   ```

### Linux 用户

1. **安装 Docker**
   ```bash
   # Ubuntu/Debian
   sudo apt-get update
   sudo apt-get install docker.io
   
   # CentOS/RHEL
   sudo yum install docker
   
   # 启动 Docker 服务
   sudo systemctl start docker
   sudo systemctl enable docker
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
python test_integrated_server.py

# 测试特定功能
python test_integrated_server.py --test health
python test_integrated_server.py --test move
```

## 📊 监控和管理

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
docker run --rm --gpus all nvidia/cuda:11.0-base nvidia-smi
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

## 🎯 下一步

1. **阅读完整文档**: [README_INTEGRATED.md](README_INTEGRATED.md)
2. **API 参考**: 查看 `/info` 端点获取完整 API 列表
3. **性能调优**: 根据硬件配置调整 `configs/katago_gtp.cfg`
4. **集成开发**: 使用 `example_client.py` 作为起点开发自己的应用

## 📞 获取帮助

- 📖 查看完整文档: [README_INTEGRATED.md](README_INTEGRATED.md)
- 🐛 报告问题: 提交 GitHub Issue
- 💬 讨论交流: 项目讨论区

---

**🎉 恭喜！你已经成功启动了 KataGo 整合版 HTTP Server！**