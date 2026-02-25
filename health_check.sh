#!/bin/bash
# health_check.sh - KataGo HTTP Server 健康检查脚本

echo "=== KataGo HTTP Server 健康检查 ==="
echo "检查时间: $(date)"
echo

# 检查容器状态
echo "1. 容器状态:"
if docker ps | grep -q katago-integrated-server; then
    echo "✅ 容器正在运行"
    docker ps | grep katago-integrated-server
else
    echo "❌ 容器未运行"
    echo "尝试查看已停止的容器:"
    docker ps -a | grep katago-integrated-server
fi
echo

# 检查 HTTP 服务
echo "2. HTTP 服务状态:"
if curl -s --max-time 5 http://localhost:8080/health > /dev/null; then
    echo "✅ HTTP 服务正常"
    echo "健康检查响应:"
    curl -s http://localhost:8080/health | python -m json.tool 2>/dev/null || curl -s http://localhost:8080/health
else
    echo "❌ HTTP 服务不可用"
    echo "请检查容器是否正在运行，端口是否正确映射"
fi
echo

# 检查 GPU 状态
echo "3. GPU 状态:"
if command -v nvidia-smi &> /dev/null; then
    echo "✅ NVIDIA 驱动可用"
    echo "GPU 信息:"
    nvidia-smi --query-gpu=name,memory.used,memory.total,utilization.gpu --format=csv,noheader,nounits
else
    echo "❌ nvidia-smi 不可用，请检查 NVIDIA 驱动安装"
fi
echo

# 检查容器内 GPU 访问
echo "4. 容器内 GPU 访问:"
if docker ps | grep -q katago-integrated-server; then
    if docker exec katago-integrated-server nvidia-smi &> /dev/null; then
        echo "✅ 容器可以访问 GPU"
    else
        echo "❌ 容器无法访问 GPU"
        echo "请检查 Docker 是否使用了 --gpus all 参数"
    fi
else
    echo "⚠️ 容器未运行，无法检查 GPU 访问"
fi
echo

# 检查最近错误日志
echo "5. 最近错误日志:"
if docker ps | grep -q katago-integrated-server; then
    echo "最近 10 行包含 'error' 的日志:"
    docker logs katago-integrated-server --tail 50 | grep -i error | tail -10
    if [ $? -ne 0 ]; then
        echo "✅ 最近日志中未发现错误"
    fi
else
    echo "⚠️ 容器未运行，无法检查日志"
fi
echo

# 检查端口占用
echo "6. 端口状态:"
if command -v netstat &> /dev/null; then
    if netstat -tlnp 2>/dev/null | grep -q :8080; then
        echo "✅ 端口 8080 正在监听"
        netstat -tlnp 2>/dev/null | grep :8080
    else
        echo "❌ 端口 8080 未在监听"
    fi
elif command -v ss &> /dev/null; then
    if ss -tlnp | grep -q :8080; then
        echo "✅ 端口 8080 正在监听"
        ss -tlnp | grep :8080
    else
        echo "❌ 端口 8080 未在监听"
    fi
else
    echo "⚠️ 无法检查端口状态（netstat 和 ss 都不可用）"
fi
echo

# 检查磁盘空间
echo "7. 磁盘空间:"
echo "当前目录磁盘使用情况:"
df -h . | tail -1
echo

# 总结
echo "=== 健康检查完成 ==="
echo "如果发现问题，请参考 TROUBLESHOOTING.md 获取详细的故障排除指南"
echo "或运行 'docker logs katago-integrated-server' 查看完整日志"
echo