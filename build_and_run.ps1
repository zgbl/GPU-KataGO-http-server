# KataGo 整合版 HTTP Server 构建和运行脚本
# PowerShell 版本

Param(
    [string]$Action = "build",
    [string]$Port = "8080",
    [switch]$GPU = $true,
    [switch]$Logs = $false
)

# 颜色输出函数
function Write-ColorOutput($ForegroundColor) {
    $fc = $host.UI.RawUI.ForegroundColor
    $host.UI.RawUI.ForegroundColor = $ForegroundColor
    if ($args) {
        Write-Output $args
    } else {
        $input | Write-Output
    }
    $host.UI.RawUI.ForegroundColor = $fc
}

function Write-Info { Write-ColorOutput Cyan $args }
function Write-Success { Write-ColorOutput Green $args }
function Write-Warning { Write-ColorOutput Yellow $args }
function Write-Error { Write-ColorOutput Red $args }

Write-Info "=== KataGo 整合版 HTTP Server ==="
Write-Info "结合最新GPU KataGo引擎和HTTP API服务器"
Write-Info ""

# 检查Docker是否安装
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Error "错误: Docker 未安装或不在PATH中"
    Write-Info "请先安装 Docker Desktop for Windows"
    Write-Info "下载地址: https://docs.docker.com/desktop/windows/install/"
    exit 1
}

# 检查Docker是否运行
try {
    docker version | Out-Null
} catch {
    Write-Error "错误: Docker 未运行"
    Write-Info "请启动 Docker Desktop"
    exit 1
}

# 检查NVIDIA Docker支持（如果使用GPU）
if ($GPU) {
    try {
        docker run --rm --gpus all nvidia/cuda:12.0-base nvidia-smi | Out-Null
        Write-Success "✓ NVIDIA Docker 支持已启用"
    } catch {
        Write-Warning "⚠️  警告: NVIDIA Docker 支持可能未正确配置"
        Write-Info "请确保已安装 NVIDIA Container Toolkit"
        Write-Info "参考: https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html"
    }
}

# 检查必要文件
$requiredFiles = @(
    "Dockerfile.integrated",
    "docker-compose.integrated.yml",
    "katago_integrated_server.py",
    "configs/katago_gtp.cfg"
)

foreach ($file in $requiredFiles) {
    if (-not (Test-Path $file)) {
        Write-Error "错误: 缺少必要文件: $file"
        exit 1
    }
}
Write-Success "✓ 所有必要文件检查通过"

# 检查模型文件
if (-not (Test-Path "KataGo-BlackRice/models")) {
    Write-Warning "⚠️  警告: 模型目录不存在: KataGo-BlackRice/models"
    Write-Info "请确保已下载KataGo模型文件到该目录"
}

switch ($Action.ToLower()) {
    "build" {
        Write-Info "🔨 构建整合版 Docker 镜像..."
        docker build -f Dockerfile.integrated -t katago-integrated:latest .
        if ($LASTEXITCODE -eq 0) {
            Write-Success "✅ 镜像构建成功"
        } else {
            Write-Error "❌ 镜像构建失败"
            exit 1
        }
    }
    
    "run" {
        Write-Info "🚀 启动整合版 KataGo HTTP 服务器..."
        Write-Info "端口: $Port"
        
        # 停止现有容器（如果存在）
        docker stop katago-integrated-server 2>$null
        docker rm katago-integrated-server 2>$null
        
        # 启动新容器
        if ($GPU) {
            docker run -d `
                --name katago-integrated-server `
                --gpus all `
                -p "${Port}:8080" `
                -v "${PWD}/KataGo-BlackRice/models:/app/models:ro" `
                -v "${PWD}/logs:/app/logs" `
                -v "${PWD}/configs:/app/configs/custom:ro" `
                -e CUDA_VISIBLE_DEVICES=0 `
                -e NVIDIA_VISIBLE_DEVICES=all `
                -e NVIDIA_DRIVER_CAPABILITIES=compute,utility `
                katago-integrated:latest
        } else {
            docker run -d `
                --name katago-integrated-server `
                -p "${Port}:8080" `
                -v "${PWD}/KataGo-BlackRice/models:/app/models:ro" `
                -v "${PWD}/logs:/app/logs" `
                -v "${PWD}/configs:/app/configs/custom:ro" `
                katago-integrated:latest
        }
        
        if ($LASTEXITCODE -eq 0) {
            Write-Success "✅ 容器启动成功"
            Write-Info "HTTP API 地址: http://localhost:$Port"
            Write-Info "健康检查: http://localhost:$Port/health"
            Write-Info "服务信息: http://localhost:$Port/info"
        } else {
            Write-Error "❌ 容器启动失败"
            exit 1
        }
    }
    
    "compose" {
        Write-Info "🐳 使用 Docker Compose 启动服务..."
        docker-compose -f docker-compose.integrated.yml up -d
        if ($LASTEXITCODE -eq 0) {
            Write-Success "✅ 服务启动成功"
            Write-Info "HTTP API 地址: http://localhost:8080"
        } else {
            Write-Error "❌ 服务启动失败"
            exit 1
        }
    }
    
    "stop" {
        Write-Info "🛑 停止服务..."
        docker stop katago-integrated-server 2>$null
        docker-compose -f docker-compose.integrated.yml down 2>$null
        Write-Success "✅ 服务已停止"
    }
    
    "logs" {
        Write-Info "📋 查看容器日志..."
        docker logs -f katago-integrated-server
    }
    
    "test" {
        Write-Info "🧪 测试 HTTP API..."
        $testUrl = "http://localhost:$Port"
        
        # 测试健康检查
        try {
            $health = Invoke-RestMethod -Uri "$testUrl/health" -Method GET
            Write-Success "✅ 健康检查通过: $($health.status)"
        } catch {
            Write-Error "❌ 健康检查失败: $($_.Exception.Message)"
        }
        
        # 测试获取走法
        try {
            $body = @{
                board_size = 19
                moves = @("R4", "D16")
            } | ConvertTo-Json
            
            $response = Invoke-RestMethod -Uri "$testUrl/select-move/katago_gtp_bot" `
                -Method POST `
                -ContentType "application/json" `
                -Body $body
            
            Write-Success "✅ 获取走法测试通过: $($response.bot_move)"
        } catch {
            Write-Error "❌ 获取走法测试失败: $($_.Exception.Message)"
        }
    }
    
    "clean" {
        Write-Info "🧹 清理 Docker 资源..."
        docker stop katago-integrated-server 2>$null
        docker rm katago-integrated-server 2>$null
        docker rmi katago-integrated:latest 2>$null
        Write-Success "✅ 清理完成"
    }
    
    default {
        Write-Info "用法: .\build_and_run.ps1 [Action] [选项]"
        Write-Info ""
        Write-Info "Actions:"
        Write-Info "  build    - 构建 Docker 镜像"
        Write-Info "  run      - 运行容器"
        Write-Info "  compose  - 使用 Docker Compose 启动"
        Write-Info "  stop     - 停止服务"
        Write-Info "  logs     - 查看日志"
        Write-Info "  test     - 测试 API"
        Write-Info "  clean    - 清理资源"
        Write-Info ""
        Write-Info "选项:"
        Write-Info "  -Port    - HTTP 端口 (默认: 8080)"
        Write-Info "  -GPU     - 启用 GPU 支持 (默认: true)"
        Write-Info ""
        Write-Info "示例:"
        Write-Info "  .\build_and_run.ps1 build"
        Write-Info "  .\build_and_run.ps1 run -Port 8080"
        Write-Info "  .\build_and_run.ps1 test"
    }
}

if ($Logs -and $Action -ne "logs") {
    Write-Info "📋 显示实时日志..."
    docker logs -f katago-integrated-server
}