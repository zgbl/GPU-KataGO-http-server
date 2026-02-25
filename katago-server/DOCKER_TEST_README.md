# KataGo HTTP服务器 Docker测试指南

这个指南将帮助你在Windows上使用Docker测试KataGo HTTP服务器。

## 前提条件

1. **安装Docker Desktop for Windows**
   - 下载地址: https://www.docker.com/products/docker-desktop
   - 安装后确保Docker服务正在运行

2. **确保Docker可以正常工作**
   ```powershell
   docker --version
   docker-compose --version
   ```

## 快速开始

### 方法1: 使用Docker Compose (推荐)

1. **构建并启动服务**
   ```powershell
   docker-compose up --build
   ```

2. **在另一个终端窗口测试服务**
   ```powershell
   python test_server.py
   ```

3. **停止服务**
   ```powershell
   docker-compose down
   ```

### 方法2: 使用Docker命令

1. **构建镜像**
   ```powershell
   docker build -t katago-server .
   ```

2. **运行容器**
   ```powershell
   docker run -p 2718:2718 katago-server
   ```

3. **测试服务**
   ```powershell
   python test_server.py
   ```

## 手动测试API

### 使用curl测试 (如果安装了curl)

1. **获取最佳走法**
   ```powershell
   curl -d '{"board_size":19, "moves":["R4", "D16"]}' -H "Content-Type: application/json" -X POST http://localhost:2718/select-move/katago_gtp_bot
   ```

2. **获取局面评估**
   ```powershell
   curl -d '{"board_size":19, "moves":["R4", "D16"]}' -H "Content-Type: application/json" -X POST http://localhost:2718/score/katago_gtp_bot
   ```

### 使用PowerShell测试

```powershell
# 测试获取走法
$body = @{
    board_size = 19
    moves = @("R4", "D16")
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:2718/select-move/katago_gtp_bot" -Method Post -Body $body -ContentType "application/json"
```

## 故障排除

### 常见问题

1. **端口被占用**
   - 错误: `bind: address already in use`
   - 解决: 更改docker-compose.yml中的端口映射，例如改为 `"2719:2718"`

2. **Docker内存不足**
   - 错误: 容器启动失败或KataGo崩溃
   - 解决: 在Docker Desktop设置中增加内存分配 (推荐至少4GB)

3. **KataGo启动慢**
   - 现象: 测试脚本超时
   - 解决: 等待更长时间，KataGo首次启动需要初始化神经网络

### 查看日志

```powershell
# 查看容器日志
docker-compose logs -f

# 或者
docker logs katago-http-server
```

### 进入容器调试

```powershell
# 进入运行中的容器
docker exec -it katago-http-server bash

# 手动运行KataGo测试
./katago_eigen benchmark
```

## 性能说明

- 这个Docker版本使用CPU版本的KataGo (`katago_eigen`)
- 性能会比GPU版本慢，但足够用于测试和开发
- 如果需要更好的性能，建议在有GPU的Linux服务器上部署

## 项目结构说明

- `katago_eigen`: KataGo的CPU版本可执行文件
- `g170e-b10c128-s1141046784-d204142634.bin.gz`: 神经网络模型文件
- `gtp_ahn_eigen.cfg`: KataGo配置文件
- `katago_server_eigen.py`: HTTP服务器主程序
- `test_server.py`: 测试脚本

## 下一步

测试成功后，你可以：
1. 修改配置文件调整KataGo参数
2. 集成到你的应用程序中
3. 部署到生产环境 (推荐使用GPU版本)