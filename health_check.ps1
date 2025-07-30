# health_check.ps1 - KataGo HTTP Server 健康检查脚本 (Windows PowerShell)

Write-Host "=== KataGo HTTP Server 健康检查 ===" -ForegroundColor Cyan
Write-Host "检查时间: $(Get-Date)" -ForegroundColor Gray
Write-Host

# 检查容器状态
Write-Host "1. 容器状态:" -ForegroundColor Yellow
try {
    $containerStatus = docker ps --filter "name=katago-integrated-server" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
    if ($containerStatus -match "katago-integrated-server") {
        Write-Host "✅ 容器正在运行" -ForegroundColor Green
        Write-Host $containerStatus
    } else {
        Write-Host "❌ 容器未运行" -ForegroundColor Red
        Write-Host "尝试查看已停止的容器:"
        docker ps -a --filter "name=katago-integrated-server" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
    }
} catch {
    Write-Host "❌ 无法检查容器状态: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host

# 检查 HTTP 服务
Write-Host "2. HTTP 服务状态:" -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "http://localhost:8080/health" -TimeoutSec 5 -ErrorAction Stop
    Write-Host "✅ HTTP 服务正常" -ForegroundColor Green
    Write-Host "健康检查响应:"
    $response | ConvertTo-Json -Depth 3
} catch {
    Write-Host "❌ HTTP 服务不可用" -ForegroundColor Red
    Write-Host "请检查容器是否正在运行，端口是否正确映射"
    Write-Host "错误详情: $($_.Exception.Message)"
}
Write-Host

# 检查 GPU 状态
Write-Host "3. GPU 状态:" -ForegroundColor Yellow
try {
    $gpuInfo = nvidia-smi --query-gpu=name,memory.used,memory.total,utilization.gpu --format=csv,noheader,nounits 2>$null
    if ($gpuInfo) {
        Write-Host "✅ NVIDIA 驱动可用" -ForegroundColor Green
        Write-Host "GPU 信息:"
        Write-Host $gpuInfo
    } else {
        Write-Host "❌ nvidia-smi 不可用，请检查 NVIDIA 驱动安装" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ nvidia-smi 不可用，请检查 NVIDIA 驱动安装" -ForegroundColor Red
}
Write-Host

# 检查容器内 GPU 访问
Write-Host "4. 容器内 GPU 访问:" -ForegroundColor Yellow
try {
    $containerRunning = docker ps --filter "name=katago-integrated-server" --quiet
    if ($containerRunning) {
        docker exec katago-integrated-server nvidia-smi 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ 容器可以访问 GPU" -ForegroundColor Green
        } else {
            Write-Host "❌ 容器无法访问 GPU" -ForegroundColor Red
            Write-Host "请检查 Docker 是否使用了 --gpus all 参数"
        }
    } else {
        Write-Host "⚠️ 容器未运行，无法检查 GPU 访问" -ForegroundColor Yellow
    }
} catch {
    Write-Host "❌ 检查容器 GPU 访问时出错: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host

# 检查最近错误日志
Write-Host "5. 最近错误日志:" -ForegroundColor Yellow
try {
    $containerRunning = docker ps --filter "name=katago-integrated-server" --quiet
    if ($containerRunning) {
        $errorLogs = docker logs katago-integrated-server --tail 50 2>$null | Select-String -Pattern "error" -CaseSensitive:$false | Select-Object -Last 10
        if ($errorLogs) {
            Write-Host "最近 10 行包含 'error' 的日志:" -ForegroundColor Red
            $errorLogs | ForEach-Object { Write-Host $_.Line -ForegroundColor Red }
        } else {
            Write-Host "✅ 最近日志中未发现错误" -ForegroundColor Green
        }
    } else {
        Write-Host "⚠️ 容器未运行，无法检查日志" -ForegroundColor Yellow
    }
} catch {
    Write-Host "❌ 检查日志时出错: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host

# 检查端口占用
Write-Host "6. 端口状态:" -ForegroundColor Yellow
try {
    $portInfo = netstat -an | Select-String ":8080"
    if ($portInfo) {
        Write-Host "✅ 端口 8080 正在监听" -ForegroundColor Green
        $portInfo | ForEach-Object { Write-Host $_.Line }
    } else {
        Write-Host "❌ 端口 8080 未在监听" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ 无法检查端口状态: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host

# 总结
Write-Host "=== 健康检查完成 ===" -ForegroundColor Cyan
Write-Host "如果发现问题，请参考 TROUBLESHOOTING.md 获取详细的故障排除指南" -ForegroundColor Gray
Write-Host "或运行 'docker logs katago-integrated-server' 查看完整日志" -ForegroundColor Gray