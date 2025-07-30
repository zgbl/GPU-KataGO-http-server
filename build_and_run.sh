#!/bin/bash

# KataGo 整合版 HTTP Server 构建和运行脚本
# Linux/macOS 版本

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 输出函数
info() { echo -e "${BLUE}[INFO]${NC} $1"; }
success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; }

# 默认参数
ACTION="build"
PORT="8080"
GPU=true
LOGS=false

# 参数解析
while [[ $# -gt 0 ]]; do
    case $1 in
        -p|--port)
            PORT="$2"
            shift 2
            ;;
        --no-gpu)
            GPU=false
            shift
            ;;
        --logs)
            LOGS=true
            shift
            ;;
        -h|--help)
            echo "用法: $0 [ACTION] [选项]"
            echo ""
            echo "Actions:"
            echo "  build    - 构建 Docker 镜像"
            echo "  run      - 运行容器"
            echo "  compose  - 使用 Docker Compose 启动"
            echo "  stop     - 停止服务"
            echo "  logs     - 查看日志"
            echo "  test     - 测试 API"
            echo "  clean    - 清理资源"
            echo ""
            echo "选项:"
            echo "  -p, --port PORT    - HTTP 端口 (默认: 8080)"
            echo "  --no-gpu          - 禁用 GPU 支持"
            echo "  --logs            - 显示实时日志"
            echo "  -h, --help        - 显示帮助信息"
            echo ""
            echo "示例:"
            echo "  $0 build"
            echo "  $0 run --port 8080"
            echo "  $0 test"
            exit 0
            ;;
        *)
            ACTION="$1"
            shift
            ;;
    esac
done

info "=== KataGo 整合版 HTTP Server ==="
info "结合最新GPU KataGo引擎和HTTP API服务器"
echo ""

# 检查Docker是否安装
if ! command -v docker &> /dev/null; then
    error "Docker 未安装或不在PATH中"
    info "请先安装 Docker:"
    info "  Ubuntu/Debian: sudo apt-get install docker.io"
    info "  CentOS/RHEL: sudo yum install docker"
    info "  macOS: brew install --cask docker"
    info "  或访问: https://docs.docker.com/get-docker/"
    exit 1
fi

# 检查Docker是否运行
if ! docker version &> /dev/null; then
    error "Docker 未运行"
    info "请启动 Docker 服务:"
    info "  Linux: sudo systemctl start docker"
    info "  macOS: 启动 Docker Desktop"
    exit 1
fi

# 检查NVIDIA Docker支持（如果使用GPU）
if [ "$GPU" = true ]; then
    if docker run --rm --gpus all nvidia/cuda:11.0-base nvidia-smi &> /dev/null; then
        success "✓ NVIDIA Docker 支持已启用"
    else
        warning "⚠️  警告: NVIDIA Docker 支持可能未正确配置"
        info "请确保已安装 NVIDIA Container Toolkit"
        info "参考: https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html"
    fi
fi

# 检查必要文件
required_files=(
    "Dockerfile.integrated"
    "docker-compose.integrated.yml"
    "katago_integrated_server.py"
    "configs/katago_gtp.cfg"
)

for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        error "缺少必要文件: $file"
        exit 1
    fi
done
success "✓ 所有必要文件检查通过"

# 检查模型文件
if [ ! -d "KataGo-BlackRice/models" ]; then
    warning "⚠️  警告: 模型目录不存在: KataGo-BlackRice/models"
    info "请确保已下载KataGo模型文件到该目录"
fi

# 执行操作
case "$ACTION" in
    "build")
        info "🔨 构建整合版 Docker 镜像..."
        docker build -f Dockerfile.integrated -t katago-integrated:latest .
        if [ $? -eq 0 ]; then
            success "✅ 镜像构建成功"
        else
            error "❌ 镜像构建失败"
            exit 1
        fi
        ;;
    
    "run")
        info "🚀 启动整合版 KataGo HTTP 服务器..."
        info "端口: $PORT"
        
        # 停止现有容器（如果存在）
        docker stop katago-integrated-server 2>/dev/null || true
        docker rm katago-integrated-server 2>/dev/null || true
        
        # 创建日志目录
        mkdir -p logs
        
        # 启动新容器
        if [ "$GPU" = true ]; then
            docker run -d \
                --name katago-integrated-server \
                --gpus all \
                -p "${PORT}:8080" \
                -v "$(pwd)/KataGo-BlackRice/models:/app/models:ro" \
                -v "$(pwd)/logs:/app/logs" \
                -v "$(pwd)/configs:/app/configs/custom:ro" \
                -e CUDA_VISIBLE_DEVICES=0 \
                -e NVIDIA_VISIBLE_DEVICES=all \
                -e NVIDIA_DRIVER_CAPABILITIES=compute,utility \
                katago-integrated:latest
        else
            docker run -d \
                --name katago-integrated-server \
                -p "${PORT}:8080" \
                -v "$(pwd)/KataGo-BlackRice/models:/app/models:ro" \
                -v "$(pwd)/logs:/app/logs" \
                -v "$(pwd)/configs:/app/configs/custom:ro" \
                katago-integrated:latest
        fi
        
        if [ $? -eq 0 ]; then
            success "✅ 容器启动成功"
            info "HTTP API 地址: http://localhost:$PORT"
            info "健康检查: http://localhost:$PORT/health"
            info "服务信息: http://localhost:$PORT/info"
        else
            error "❌ 容器启动失败"
            exit 1
        fi
        ;;
    
    "compose")
        info "🐳 使用 Docker Compose 启动服务..."
        docker-compose -f docker-compose.integrated.yml up -d
        if [ $? -eq 0 ]; then
            success "✅ 服务启动成功"
            info "HTTP API 地址: http://localhost:8080"
        else
            error "❌ 服务启动失败"
            exit 1
        fi
        ;;
    
    "stop")
        info "🛑 停止服务..."
        docker stop katago-integrated-server 2>/dev/null || true
        docker-compose -f docker-compose.integrated.yml down 2>/dev/null || true
        success "✅ 服务已停止"
        ;;
    
    "logs")
        info "📋 查看容器日志..."
        docker logs -f katago-integrated-server
        ;;
    
    "test")
        info "🧪 测试 HTTP API..."
        test_url="http://localhost:$PORT"
        
        # 检查Python是否可用
        if command -v python3 &> /dev/null; then
            python3 test_integrated_server.py --url "$test_url"
        elif command -v python &> /dev/null; then
            python test_integrated_server.py --url "$test_url"
        else
            # 使用curl进行基本测试
            info "Python不可用，使用curl进行基本测试..."
            
            # 测试健康检查
            if curl -f "$test_url/health" &> /dev/null; then
                success "✅ 健康检查通过"
            else
                error "❌ 健康检查失败"
            fi
            
            # 测试获取走法
            if curl -f -X POST "$test_url/select-move/katago_gtp_bot" \
                -H "Content-Type: application/json" \
                -d '{"board_size": 19, "moves": []}' \
                --max-time 30 &> /dev/null; then
                success "✅ 获取走法测试通过"
            else
                error "❌ 获取走法测试失败"
            fi
        fi
        ;;
    
    "clean")
        info "🧹 清理 Docker 资源..."
        docker stop katago-integrated-server 2>/dev/null || true
        docker rm katago-integrated-server 2>/dev/null || true
        docker rmi katago-integrated:latest 2>/dev/null || true
        success "✅ 清理完成"
        ;;
    
    *)
        error "未知操作: $ACTION"
        info "使用 $0 --help 查看帮助信息"
        exit 1
        ;;
esac

# 显示实时日志（如果请求）
if [ "$LOGS" = true ] && [ "$ACTION" != "logs" ]; then
    info "📋 显示实时日志..."
    docker logs -f katago-integrated-server
fi