# 🔧 KataGo GPU HTTP Server 故障排除指南

## 📋 问题分析

根据错误日志，KataGo 进程不断崩溃并尝试重启，主要问题可能包括：

- GPU/CUDA 配置问题
- 模型文件路径或格式问题
- 配置文件参数不兼容
- Docker 容器内 GPU 访问权限问题

## 🚨 立即诊断步骤

### 1. 检查容器状态和详细错误

```bash
# 查看容器详细日志
docker logs katago-integrated-server --tail 100

# 进入容器检查环境
docker exec -it katago-integrated-server /bin/bash

# 在容器内检查文件存在性
ls -la /app/bin/katago
ls -la /app/models/
ls -la /app/configs/katago_gtp.cfg
```

### 2. 验证 GPU 访问

```bash
# 在容器内检查 GPU
docker exec -it katago-integrated-server nvidia-smi

# 检查 CUDA 版本
docker exec -it katago-integrated-server nvcc --version
```

### 3. 手动测试 KataGo 命令

```bash
# 进入容器并手动运行 KataGo
docker exec -it katago-integrated-server /bin/bash

# 在容器内手动测试
cd /app
./bin/katago gtp -model /app/models/model.bin.gz -config /app/configs/katago_gtp.cfg
```

## 🛠️ 常见问题和解决方案

### 问题1: 模型文件问题

**症状:** KataGo 启动失败，提示模型文件相关错误

**解决方案:**
```bash
# 检查模型文件是否存在和可读
docker exec -it katago-integrated-server ls -la /app/models/

# 如果模型文件不存在，需要下载
# 常用的 KataGo 模型：
wget https://github.com/lightvector/KataGo/releases/download/v1.4.5/g170-b20c256x2-s5303129600-d1228401921.bin.gz
```

### 问题2: 配置文件不兼容

**症状:** KataGo 启动时配置解析错误

**解决方案:**
创建适合 GPU 的配置文件 `/configs/katago_gtp.cfg`:

```ini
# KataGo GTP 配置文件
logFile = /app/logs/katago_gtp.log
logAllGTPCommunication = true
logSearchInfo = false
logToStderr = false

# CUDA 设置
cudaUseFP16 = true
cudaUseNHWC = true
numSearchThreads = 8

# 搜索设置
maxVisits = 1000
maxPlayouts = 1000
maxTime = 10.0

# 内存设置
nnMaxBatchSize = 32
nnCacheSizePowerOfTwo = 20
nnMutexPoolSizePowerOfTwo = 16
```

### 问题3: GPU 访问权限问题

**症状:** 容器内无法访问 GPU

**解决方案:**
检查 Docker 运行命令是否正确包含了 GPU 参数：

```bash
docker run -d \
    --name katago-integrated-server \
    --gpus all \
    --runtime=nvidia \
    -e NVIDIA_VISIBLE_DEVICES=all \
    -e NVIDIA_DRIVER_CAPABILITIES=compute,utility \
    -p 8080:8080 \
    -v "$(pwd)/KataGo-BlackRice/models:/app/models:ro" \
    -v "$(pwd)/logs:/app/logs" \
    -v "$(pwd)/configs:/app/configs/custom:ro" \
    katago-integrated:latest
```

### 问题4: 内存不足

**症状:** KataGo 进程因 OOM 被杀死

**解决方案:**
```bash
# 调整 Docker 内存限制
docker run -d \
    --name katago-integrated-server \
    --gpus all \
    --memory=8g \
    -p 8080:8080 \
    katago-integrated:latest
```

### 问题5: 配置文件重复键错误

**症状:** `ConfigParsingError: Key 'nnCacheSizePowerOfTwo' was specified multiple times`

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

### 问题6: 规则配置冲突错误

**症状:** `Cannot both specify 'rules' and individual rules like koRule/scoringRule/multiStoneSuicideLegal`

**原因:** KataGo不允许同时指定统一的`rules`设置和单独的规则项（如`koRule`、`scoringRule`、`taxRule`、`multiStoneSuicideLegal`、`hasButton`、`whiteHandicapBonus`等）。

**解决方案:**
```bash
# 方法1: 只使用统一的rules设置（推荐）
# 编辑配置文件，删除所有单独的规则项，只保留：
rules = tromp-taylor

# 方法2: 或者删除rules设置，使用单独的规则项
# 删除 rules = tromp-taylor 行，保留单独的规则设置

# 检查配置文件中的规则冲突
grep -E "^(rules|koRule|scoringRule|taxRule|multiStoneSuicideLegal|hasButton|whiteHandicapBonus)" configs/katago_gtp.cfg

# 重启容器使配置生效
docker-compose -f docker-compose.integrated.yml restart
```

**预防措施:**
- 在修改配置文件时，避免同时使用`rules`和单独规则项
- 推荐使用统一的`rules = tromp-taylor`设置
- 定期检查配置文件的一致性

## 🔧 修复建议

### 1. 更新 katago_integrated_server.py

在初始化 KataGo 前添加更详细的验证：

```python
def _init_katago(self):
    """初始化KataGo GTP引擎"""
    try:
        # 先测试 KataGo 二进制文件
        test_cmd = [self.katago_binary, "version"]
        result = subprocess.run(test_cmd, capture_output=True, text=True, timeout=10)
        
        if result.returncode != 0:
            raise RuntimeError(f"KataGo 二进制文件测试失败: {result.stderr}")
        
        logger.info(f"KataGo 版本: {result.stdout.strip()}")
        
        # 构建完整命令
        katago_cmd = [
            self.katago_binary,
            "gtp",
            "-model", self.model_file,
            "-config", self.config_file,
            "-override-config", "logToStderr=true"
        ]
        
        logger.info(f"启动KataGo命令: {' '.join(katago_cmd)}")
        
        self.katago_bot = KataGTPBot(katago_cmd)
        logger.info("✓ KataGo引擎初始化成功")
        
    except subprocess.TimeoutExpired:
        error_msg = "KataGo 二进制文件响应超时"
        logger.error(error_msg)
        raise RuntimeError(error_msg)
    except Exception as e:
        error_msg = f"KataGo引擎初始化失败: {str(e)}"
        logger.error(error_msg)
        raise RuntimeError(error_msg)
```

### 2. 创建调试脚本

创建 `debug_katago.sh` 脚本：

```bash
#!/bin/bash

echo "=== KataGo 调试信息 ==="

echo "1. 检查 GPU 状态:"
nvidia-smi

echo -e "\n2. 检查文件存在性:"
ls -la /app/bin/katago
ls -la /app/models/
ls -la /app/configs/katago_gtp.cfg

echo -e "\n3. 测试 KataGo 版本:"
/app/bin/katago version

echo -e "\n4. 测试 KataGo 基本功能:"
echo "quit" | timeout 30 /app/bin/katago gtp -model /app/models/model.bin.gz -config /app/configs/katago_gtp.cfg

echo -e "\n5. 检查配置文件内容:"
head -20 /app/configs/katago_gtp.cfg
```

### 3. 逐步启动测试

```bash
# 1. 停止现有容器
docker stop katago-integrated-server
docker rm katago-integrated-server

# 2. 重新构建镜像
docker build -f Dockerfile.integrated -t katago-integrated:latest .

# 3. 以交互模式启动容器进行调试
docker run -it --gpus all \
    -v "$(pwd)/KataGo-BlackRice/models:/app/models:ro" \
    -v "$(pwd)/logs:/app/logs" \
    -v "$(pwd)/configs:/app/configs/custom:ro" \
    katago-integrated:latest /bin/bash

# 4. 在容器内运行调试脚本
./debug_katago.sh
```

## 🛡️ 预防措施

1. **确保模型文件完整**: 验证下载的模型文件没有损坏
2. **使用兼容的配置**: 使用与 KataGo 版本匹配的配置文件
3. **监控资源使用**: 确保有足够的 GPU 内存和系统内存
4. **日志收集**: 启用详细日志以便问题排查

## 📊 监控和诊断工具

### 快速诊断脚本

项目提供了两个便捷的诊断脚本：

#### 1. 健康检查脚本
```bash
# Linux/macOS
./health_check.sh

# Windows PowerShell
.\health_check.ps1
```

#### 2. 容器内调试脚本
```bash
# 在容器内运行详细诊断
docker exec -it katago-integrated-server ./debug_katago.sh

# 或者进入容器后运行
docker exec -it katago-integrated-server /bin/bash
./debug_katago.sh
```

### 实时监控命令

```bash
# 监控容器资源使用
docker stats katago-integrated-server

# 监控 GPU 使用情况
watch -n 1 nvidia-smi

# 实时查看容器日志
docker logs -f katago-integrated-server

# 检查 KataGo 进程状态
docker exec katago-integrated-server ps aux | grep katago
```

### 健康检查脚本

```bash
#!/bin/bash
# health_check.sh

echo "=== 系统健康检查 ==="

# 检查容器状态
echo "1. 容器状态:"
docker ps | grep katago-integrated-server

# 检查 HTTP 服务
echo -e "\n2. HTTP 服务状态:"
curl -s http://localhost:8080/health || echo "HTTP 服务不可用"

# 检查 GPU 状态
echo -e "\n3. GPU 状态:"
nvidia-smi --query-gpu=name,memory.used,memory.total --format=csv,noheader,nounits

# 检查日志错误
echo -e "\n4. 最近错误日志:"
docker logs katago-integrated-server --tail 10 | grep -i error
```

## 🎯 下一步行动

1. **运行上述诊断步骤**
2. **根据具体错误信息调整配置**
3. **如果问题仍然存在，提供详细的错误日志以便进一步分析**

## 📞 获取帮助

如果按照本指南仍无法解决问题，请：

1. 运行完整的诊断脚本
2. 收集详细的错误日志
3. 提供系统环境信息（GPU 型号、CUDA 版本、Docker 版本等）
4. 在项目 GitHub 仓库提交 Issue

---

**💡 提示:** 大多数 KataGo 启动问题都与 GPU 配置、模型文件或配置文件相关。按照本指南逐步排查，通常能够快速定位和解决问题。